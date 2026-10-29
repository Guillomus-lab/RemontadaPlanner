import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
import xml.sax.saxutils

# The launcher (.vbs) runs the BASE interpreter's pythonw.exe directly: the uv venv's
# pythonw.exe is a trampoline that spawns console python.exe, which either shows a
# black console window or — when started hidden — hides the app window too.
# So we add the venv's packages ourselves when not already running inside it.
_VENV_SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Lib", "site-packages")
if not getattr(sys, "frozen", False) and os.path.isdir(_VENV_SITE) and _VENV_SITE not in sys.path:
    import site
    site.addsitedir(_VENV_SITE)

import webview  # noqa: E402

APP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "DailyPlanner")
os.makedirs(APP_DIR, exist_ok=True)
DATA_FILE = os.path.join(APP_DIR, "plans.json")
BACKUP_DIR = os.path.join(APP_DIR, "backups")
BACKUPS_TO_KEEP = 30

SCHEMA_VERSION = 5

# Bump this on every release alongside a matching GitHub tag (vX.Y.Z) / Release.
APP_VERSION = "1.3.0"
UPDATE_CHECK_URL = "https://api.github.com/repos/Guillomus-lab/RemontadaPlanner/releases/latest"
RELEASES_PAGE_URL = "https://github.com/Guillomus-lab/RemontadaPlanner/releases/latest"

DEFAULT_DATA = {
    "schemaVersion": SCHEMA_VERSION,
    "days": {},          # { "2026-10-29": [ {id,title,start,duration,category,done}, ... ] }
    "categories": {
        "Travail": "#6366f1",
        "Personnel": "#f59e0b",
        "Santé": "#22c55e",
        "Courses": "#06b6d4",
        "Divers": "#6b7280",
    },
    "templates": {},     # { "Weekday": [ {title,start,duration,category}, ... ] }
    "unlockedAchievements": [],  # [ "first", "streak3", ... ] — ids already toasted once
    "profile": {"name": "", "avatar": "🙂"},
    "economy": {
        "coinsSpent": 0,
        "unlockedThemes": ["default"],
        "unlockedAvatars": ["🙂", "😎", "🦊", "🐱", "🐼", "🤖", "👾", "🌟"],
        "activeThemeId": "default",
        # consumable streak protection: a missed day is forgiven automatically
        "streakFreezes": 1,
        "frozenDays": [],
    },
    "counters": {},      # free-form usage counters (remixUsed, tasksDeleted, konamiFound, ...)
    "settings": {
        "theme": "dark", "zoom": 72, "view": "day",
        # realistic daily load target, in minutes (used by the charge indicator)
        "dayCapacity": 480,
        # Windows reminders + optional Discord weekly recap
        "reminders": False, "reminderLead": 10, "reminderSound": True,
        "mealIdeas": True, "reminderPromptSeen": False, "lastWeekReviewPrompt": "",
        "workoutIdeas": True, "workoutLevel": 1, "workoutEquip": "none",
        "discordWebhook": "", "discordWeekly": False, "lastDiscordRecap": "",
        "lastRolloverPrompt": "",
    },  # UI prefs persisted across launches
    # things captured but not scheduled yet: {id,title,duration,category,notes,url,createdAt}
    "backlog": [],
    # explicit end-of-day closes: { "2026-10-29": {closedAt, note, moved, backlogged, done, total} }
    "closedDays": {},
    # weekly reviews: { "2026-11-02": {priorities:[...], note, at} } (key = Monday)
    "weekReviews": {},
    # weekly menus: { "2026-11-02": {"0-dej": "<recipe name>", "0-din": ..., ...} } (0 = Monday)
    "mealPlans": {},
    # recurring tasks: {id,title,start,duration,category,days:[0-6],from,until,skip:[dates]}
    "routines": [],
    # regularity challenges: {id,title,category,keywords,length,start,status,...}
    "challenges": [],
    "quests": {"claimed": {}},  # weekly quests already rewarded: { "2026-10-26": ["move7", ...] }
    # True for every existing save migrating through _normalize()'s fill-missing-keys
    # loop (so current users never see the tutorial again); _load_raw() flips this to
    # False only on the genuine "no save file at all yet" branch (true first launch).
    "onboardingSeen": True,
}

# Old English category keys -> new French ones (migration from pre-v2 saves)
LEGACY_CATEGORY_MAP = {
    "work": "Travail",
    "personal": "Personnel",
    "health": "Santé",
    "errands": "Courses",
    "misc": "Divers",
}

# pywebview runs each js_api call on its own thread: serialize disk writes so two
# quick saves can't race on the same temp file.
_save_lock = threading.Lock()


def _clone(obj):
    return json.loads(json.dumps(obj))


def _migrate_categories(data):
    """Rename legacy English category keys to French, keeping colors and
    updating every task (in days + templates) that referenced them.
    Safe to run repeatedly: once migrated, legacy keys are gone so it's a no-op."""
    cats = data.get("categories", {})
    renamed = {}
    for old_key, new_key in LEGACY_CATEGORY_MAP.items():
        if old_key in cats:
            color = cats.pop(old_key)
            if new_key not in cats:
                cats[new_key] = color
            renamed[old_key] = new_key
    if not renamed:
        return data
    for day_tasks in data.get("days", {}).values():
        for task in day_tasks:
            if task.get("category") in renamed:
                task["category"] = renamed[task["category"]]
    for tpl_tasks in data.get("templates", {}).values():
        for task in tpl_tasks:
            if task.get("category") in renamed:
                task["category"] = renamed[task["category"]]
    data["categories"] = cats
    return data


def _ensure_nested_defaults(data):
    """Shallow top-level merge only fills whole missing keys — for dict-shaped
    keys we also backfill missing *sub*-keys so an old save upgrading to a new
    schema version gets new fields (e.g. profile.avatar) without losing data."""
    for key in ("profile", "economy", "counters", "settings", "quests"):
        default_sub = DEFAULT_DATA.get(key, {})
        if not isinstance(data.get(key), dict):
            data[key] = _clone(default_sub)
            continue
        for sub_k, sub_v in default_sub.items():
            if sub_k not in data[key]:
                data[key][sub_k] = _clone(sub_v)
    return data


def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("days", {}), dict):
        raise ValueError("unexpected data shape")
    return data


def _normalize(data):
    if "schemaVersion" not in data:
        data["schemaVersion"] = 1
    for k, v in DEFAULT_DATA.items():
        if k not in data:
            data[k] = _clone(v)  # deep copy: never share DEFAULT_DATA's nested objects
    data = _migrate_categories(data)
    data = _ensure_nested_defaults(data)
    data["schemaVersion"] = SCHEMA_VERSION
    return data


def _latest_backup():
    # normalize inside the loop: a backup that can't be normalized falls through to an older one
    for path in sorted(glob.glob(os.path.join(BACKUP_DIR, "plans-*.json")), reverse=True):
        try:
            return _normalize(_read_json(path))
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return None


def _load_raw():
    if not os.path.exists(DATA_FILE):
        # Genuine first run (no prior save of any kind): the only place that
        # should ever hand back onboardingSeen=False and trigger the tutorial.
        fresh = _clone(DEFAULT_DATA)
        fresh["onboardingSeen"] = False
        return fresh
    try:
        return _normalize(_read_json(DATA_FILE))
    except (OSError, ValueError, TypeError, AttributeError):
        # Keep the broken file aside (timestamped, never overwritten), then recover
        # from the newest readable daily backup instead of starting from scratch.
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        try:
            os.replace(DATA_FILE, f"{DATA_FILE}.corrupt-{stamp}")
        except OSError:
            pass
        backup = _latest_backup()
        return backup if backup else _clone(DEFAULT_DATA)


def _atomic_write(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _prune_backups():
    files = sorted(glob.glob(os.path.join(BACKUP_DIR, "plans-*.json")))
    for old in files[:-BACKUPS_TO_KEEP]:
        try:
            os.remove(old)
        except OSError:
            pass


def _parse_version(tag):
    """'v1.2.3' / '1.2.3' -> (1, 2, 3); non-numeric parts are dropped so a tag
    like 'v1.2.3-beta' still compares sanely against a plain '1.2.3'."""
    cleaned = tag.strip().lstrip("vV")
    parts = []
    for p in cleaned.split("."):
        digits = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def _fetch_latest_release():
    """Hits the GitHub API for the newest published release. Returns None on
    any failure (offline, rate-limited, no release published yet, ...) —
    the update check is best-effort and must never block or crash the app."""
    req = urllib.request.Request(
        UPDATE_CHECK_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "RemontadaPlanner"},
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None
    tag = payload.get("tag_name")
    if not tag:
        return None
    asset = next((a for a in payload.get("assets") or [] if a.get("name") == UPDATE_ASSET_NAME), None)
    return {
        "tag": tag,
        "name": payload.get("name") or tag,
        "url": payload.get("html_url") or RELEASES_PAGE_URL,
        "asset_url": (asset or {}).get("browser_download_url") or "",
        # GitHub publishes the asset's SHA-256: the download is checked against it
        "asset_sha256": ((asset or {}).get("digest") or "").replace("sha256:", "").lower(),
    }


# ---------- In-app update (exe only) ----------
# Windows can't overwrite a running .exe, but it can rename it: the new exe is
# extracted next to it, the running one is renamed to .old, the new one takes
# its name, then the app restarts on it. The .old file is deleted on next launch.
UPDATE_ASSET_NAME = "RemontadaPlanner.zip"
UPDATE_EXE_NAME = "RemontadaPlanner.exe"
_DOWNLOAD_PREFIXES = (
    "https://github.com/Guillomus-lab/RemontadaPlanner/releases/download/",
)
_latest_release = None  # filled by check_update, used by install_update


def _running_exe():
    """Path of the running RemontadaPlanner.exe, or None when run from sources."""
    if not getattr(sys, "frozen", False) or sys.platform != "win32":
        return None
    return os.path.abspath(sys.executable)


def _cleanup_old_exe():
    exe = _running_exe()
    if exe and os.path.exists(exe + ".old"):
        try:
            os.remove(exe + ".old")
        except OSError:
            pass  # still locked: retried on the next launch


def _download(url, dest, timeout=60):
    import hashlib

    req = urllib.request.Request(url, headers={"User-Agent": "RemontadaPlanner"})
    sha = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
        while True:
            chunk = resp.read(256 * 1024)
            if not chunk:
                break
            sha.update(chunk)
            f.write(chunk)
    return sha.hexdigest()


def _install_update(release):
    import tempfile
    import zipfile

    exe = _running_exe()
    if not exe:
        return {"ok": False, "manual": True, "error": "Mise à jour auto disponible seulement dans l'app installée (.exe)."}
    url = release.get("asset_url") or ""
    if not url.startswith(_DOWNLOAD_PREFIXES):
        return {"ok": False, "manual": True, "error": "Fichier de mise à jour introuvable."}
    exe_dir = os.path.dirname(exe)
    new_exe = exe + ".new"
    tmp_dir = tempfile.mkdtemp(prefix="remontada-update-")
    zip_path = os.path.join(tmp_dir, UPDATE_ASSET_NAME)
    try:
        digest = _download(url, zip_path)
        expected = release.get("asset_sha256") or ""
        if expected and digest != expected:
            return {"ok": False, "manual": True, "error": "Le téléchargement est abîmé (somme de contrôle différente)."}
        with zipfile.ZipFile(zip_path) as z:
            if UPDATE_EXE_NAME not in z.namelist():
                return {"ok": False, "manual": True, "error": "Le zip ne contient pas l'app."}
            with z.open(UPDATE_EXE_NAME) as src, open(new_exe, "wb") as dst:
                shutil.copyfileobj(src, dst)
            # keep the readme next to the exe up to date too
            if "LISEZMOI.txt" in z.namelist():
                try:
                    with z.open("LISEZMOI.txt") as src, open(os.path.join(exe_dir, "LISEZMOI.txt"), "wb") as dst:
                        dst.write(src.read())
                except OSError:
                    pass
        if os.path.exists(exe + ".old"):
            os.remove(exe + ".old")
        os.replace(exe, exe + ".old")  # allowed on a running exe
        try:
            os.replace(new_exe, exe)
        except OSError:
            os.replace(exe + ".old", exe)  # put the working version back
            raise
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, zipfile.BadZipFile) as e:
        try:
            if os.path.exists(new_exe):
                os.remove(new_exe)
        except OSError:
            pass
        return {"ok": False, "manual": True, "error": f"Mise à jour impossible : {e}"}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return {"ok": True, "exe": exe}


def _restart(exe):
    """Starts the new exe (it waits for this one to close, see
    _already_running) then closes this window."""
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    subprocess.Popen([exe, "--after-update"], cwd=os.path.dirname(exe), creationflags=flags, close_fds=True)

    def _close():
        for w in list(webview.windows):
            try:
                w.destroy()
            except Exception:
                pass

    threading.Timer(0.8, _close).start()


def _notification_text(value, limit=220):
    text = "".join(ch for ch in str(value or "") if ch in "\n\r\t" or ord(ch) >= 32)
    return text.strip()[:limit]


# Windows only shows toasts for an AppUserModelID it knows. An unknown id is
# dropped silently (no error), so we register ours under HKCU (no admin
# needed) with a display name and icon before the first toast.
TOAST_APP_ID = "Guillomus.RemontadaPlanner"
TOAST_ICON = os.path.join(APP_DIR, "app.ico")
_toast_registered = False


def _register_toast_app_id():
    global _toast_registered
    if _toast_registered or sys.platform != "win32":
        return _toast_registered
    try:
        import winreg

        # Copy the icon to a stable place: in the PyInstaller build, _MEIPASS
        # is a temp folder that changes on every launch.
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        src_icon = os.path.join(base_dir, "app.ico")
        if os.path.isfile(src_icon) and not os.path.isfile(TOAST_ICON):
            shutil.copyfile(src_icon, TOAST_ICON)
        key_path = rf"Software\Classes\AppUserModelId\{TOAST_APP_ID}"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Remontada Planner")
            if os.path.isfile(TOAST_ICON):
                winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, TOAST_ICON)
        _toast_registered = True
    except Exception:
        pass
    return _toast_registered


def _windows_toast(title, message, wait=False, sound=True):
    """Windows toast for task reminders, sent as a WinRT toast through
    PowerShell (ships with Windows, no dependency, same result on every PC).
    Reminders are fire-and-forget; `wait=True` (the "Tester" button) waits for PowerShell so a failure can be shown to the user.
    `sound` plays Windows' "Rappel" chime; False makes the toast silent."""
    title = _notification_text(title) or "Remontada Planner"
    message = _notification_text(message, 400)
    if sys.platform != "win32":
        return {"ok": False, "error": "notifications Windows uniquement"}
    _register_toast_app_id()

    audio_tag = (
        '<audio src="ms-winsoundevent:Notification.Reminder"/>' if sound else '<audio silent="true"/>'
    )
    # scenario="reminder" keeps the toast on screen until dismissed (instead of
    # sliding away after a few seconds); Windows requires a button for it.
    # The snooze/dismiss buttons are handled by Windows itself (system
    # activation): "Plus tard" brings the same toast back after the chosen delay.
    toast_xml = (
        '<toast scenario="reminder"><visual><binding template="ToastGeneric">'
        f"<text>{xml.sax.saxutils.escape(title)}</text>"
        f"<text>{xml.sax.saxutils.escape(message)}</text>"
        "</binding></visual>"
        "<actions>"
        '<input id="snoozeTime" type="selection" defaultInput="10">'
        '<selection id="5" content="Dans 5 minutes"/>'
        '<selection id="10" content="Dans 10 minutes"/>'
        '<selection id="15" content="Dans 15 minutes"/>'
        "</input>"
        '<action activationType="system" arguments="snooze" hint-inputId="snoozeTime" content="Plus tard"/>'
        '<action activationType="system" arguments="dismiss" content="OK"/>'
        "</actions>"
        f"{audio_tag}</toast>"
    )
    # The XML goes through an environment variable, never into the script
    # text: PowerShell also treats typographic quotes (’ ‘) as string
    # delimiters, so a title like "l’école" would break (or inject into) it.
    script = (
        "$ErrorActionPreference='Stop';"
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;"
        "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null;"
        "$xml = New-Object Windows.Data.Xml.Dom.XmlDocument;"
        "$xml.LoadXml($env:RP_TOAST_XML);"
        "$toast = New-Object Windows.UI.Notifications.ToastNotification $xml;"
        f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{TOAST_APP_ID}').Show($toast);"
    )
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", script]
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    env = dict(os.environ, RP_TOAST_XML=toast_xml)
    try:
        if not wait:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags, env=env)
            return {"ok": True, "mode": "powershell"}
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20, creationflags=flags, env=env)
        if res.returncode != 0:
            err = (res.stderr or res.stdout or "").strip().splitlines()
            return {"ok": False, "error": err[0][:200] if err else f"code {res.returncode}"}
        return {"ok": True, "mode": "powershell"}
    except (OSError, subprocess.SubprocessError) as e:
        return {"ok": False, "error": str(e)}


def _post_discord(webhook_url, content):
    """Posts a recap to a Discord webhook (Luron / any channel webhook). Only
    Discord webhook hosts are accepted so this endpoint can't be repurposed as
    a generic outbound POST from the app."""
    allowed = (
        "https://discord.com/api/webhooks/",
        "https://discordapp.com/api/webhooks/",
        "https://ptb.discord.com/api/webhooks/",
        "https://canary.discord.com/api/webhooks/",
    )
    if not isinstance(webhook_url, str) or not webhook_url.startswith(allowed):
        return {"ok": False, "error": "URL de webhook Discord invalide"}
    payload = {
        "content": _notification_text(content, 1900),
        "username": "Remontada Planner",
        "allowed_mentions": {"parse": []},
    }
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "RemontadaPlanner"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            if 200 <= resp.status < 300:
                return {"ok": True}
            return {"ok": False, "error": f"Discord a répondu {resp.status}"}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"Discord a répondu {e.code}"}
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
        return {"ok": False, "error": str(e)}



# pywebview dialog types (stable numeric values: FileDialog.OPEN / .SAVE)
_DIALOG_OPEN, _DIALOG_SAVE = 10, 30
_BACKUP_FILE_TYPES = ("Sauvegarde Remontada (*.json)", "Tous les fichiers (*.*)")


def _file_dialog(dialog_type, **kwargs):
    """Native open/save dialog. Returns one path, or None if cancelled."""
    if not webview.windows:
        return None
    result = webview.windows[0].create_file_dialog(dialog_type, **kwargs)
    if not result:
        return None
    return result if isinstance(result, str) else result[0]


def _looks_like_save(data):
    return isinstance(data, dict) and isinstance(data.get("days"), dict) and (
        "schemaVersion" in data or "economy" in data or "categories" in data
    )


class Api:
    def load(self):
        return _load_raw()

    def export_data(self, data):
        """'Sauvegarder mes données' in Settings: writes the current state to
        a JSON file the user picks (USB key, cloud folder, new PC...)."""
        if not _looks_like_save(data):
            return {"ok": False, "error": "données invalides"}
        name = f"remontada-sauvegarde-{datetime.date.today().isoformat()}.json"
        try:
            path = _file_dialog(_DIALOG_SAVE, save_filename=name, file_types=_BACKUP_FILE_TYPES)
            if not path:
                return {"ok": False, "cancelled": True}
            if not path.lower().endswith(".json"):
                path += ".json"
            _atomic_write(path, data)
        except Exception as e:  # dialog or disk error: report, never crash the UI
            return {"ok": False, "error": str(e)}
        return {"ok": True, "path": path}

    def import_data(self):
        """'Restaurer une sauvegarde': validates the chosen file, keeps a copy
        of the current data next to it, then replaces plans.json."""
        try:
            path = _file_dialog(_DIALOG_OPEN, allow_multiple=False, file_types=_BACKUP_FILE_TYPES)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not path:
            return {"ok": False, "cancelled": True}
        try:
            raw = _read_json(path)
            if not _looks_like_save(raw):
                raise ValueError("not a save")
            data = _normalize(raw)
            data["onboardingSeen"] = True
        except (OSError, ValueError, TypeError, AttributeError):
            return {"ok": False, "error": "Ce fichier n'est pas une sauvegarde Remontada valide."}
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        try:
            with _save_lock:
                if os.path.exists(DATA_FILE):
                    shutil.copyfile(DATA_FILE, f"{DATA_FILE}.avant-import-{stamp}")
                _atomic_write(DATA_FILE, data)
        except OSError as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True}

    def check_update(self):
        """Called once at launch by the UI. Runs on pywebview's own call
        thread (not the UI thread) so the network round-trip never freezes
        the window; any failure just means 'no update info available'."""
        global _latest_release
        release = _fetch_latest_release()
        if not release:
            return {"update_available": False}
        _latest_release = release
        is_newer = _parse_version(release["tag"]) > _parse_version(APP_VERSION)
        return {
            "update_available": is_newer,
            "current_version": APP_VERSION,
            "latest_version": release["tag"],
            "release_name": release["name"],
            "url": release["url"],
            # the app can download and install it by itself (exe + zip asset found)
            "can_auto_update": bool(_running_exe() and release.get("asset_url")),
        }

    def install_update(self):
        """'Mettre à jour' in the update popup: download, check, swap the exe,
        restart. Any failure leaves the current version untouched."""
        release = _latest_release or _fetch_latest_release()
        if not release or _parse_version(release["tag"]) <= _parse_version(APP_VERSION):
            return {"ok": False, "error": "Aucune mise à jour à installer."}
        result = _install_update(release)
        if result.get("ok"):
            try:
                _restart(result["exe"])
            except OSError as e:
                return {"ok": False, "manual": True, "error": f"Installée, mais redémarrage impossible : {e}. Relance l'app."}
            return {"ok": True}
        result["url"] = release.get("url") or RELEASES_PAGE_URL
        return result

    def open_url(self, url):
        """Opens a link (e.g. the release page) in the user's default
        browser — pywebview windows don't navigate external links on click."""
        if isinstance(url, str) and url.lower().startswith(("https://", "http://")):
            webbrowser.open(url)
        return {"ok": True}

    def notify(self, title, message, sound=True):
        """Windows toast used by task reminders. Fire-and-forget."""
        return _windows_toast(title, message, sound=bool(sound))

    def test_notify(self, sound=True):
        """'Tester' button in Settings: same toast, but waits for the result."""
        return _windows_toast("Remontada Planner", "Les rappels Windows fonctionnent ✅", wait=True, sound=bool(sound))

    def send_discord(self, webhook_url, content):
        """Weekly recap to a Discord webhook (e.g. the Luron bot's channel)."""
        return _post_discord(webhook_url, content)

    def get_category_recap(self, scope, ref_date):
        """Aggregate planned/done minutes per category for a day or ISO week
        (Monday-Sunday) around ref_date, for the camembert recap chart.
        Read-only: never touches the saved data."""
        data = _load_raw()
        ref = datetime.date.fromisoformat(ref_date)
        if scope == "week":
            start = ref - datetime.timedelta(days=ref.weekday())
            end = start + datetime.timedelta(days=6)
        else:
            start = end = ref

        buckets = {}
        total_minutes = 0
        day = start
        while day <= end:
            for task in data.get("days", {}).get(day.isoformat(), []):
                category = task.get("category", "")
                duration = task.get("duration", 0) or 0
                total_minutes += duration
                bucket = buckets.setdefault(category, {"doneMinutes": 0, "plannedMinutes": 0})
                if task.get("done"):
                    bucket["doneMinutes"] += duration
                else:
                    bucket["plannedMinutes"] += duration
            day += datetime.timedelta(days=1)

        colors = data.get("categories", {})
        categories = {}
        for name, bucket in buckets.items():
            cat_total = bucket["doneMinutes"] + bucket["plannedMinutes"]
            categories[name] = {
                "color": colors.get(name, "#6b7280"),
                "doneMinutes": bucket["doneMinutes"],
                "plannedMinutes": bucket["plannedMinutes"],
                "percentDone": (bucket["doneMinutes"] / cat_total * 100) if cat_total else 0.0,
                "percentOfTotal": (cat_total / total_minutes * 100) if total_minutes else 0.0,
            }

        return {
            "scope": scope,
            "range": {"from": start.isoformat(), "to": end.isoformat()},
            "totalMinutes": total_minutes,
            "categories": categories,
        }

    def save(self, data):
        # Refuse obviously broken payloads instead of overwriting good data with them.
        if not isinstance(data, dict) or not isinstance(data.get("days"), dict):
            return {"ok": False, "error": "données invalides, sauvegarde refusée"}
        try:
            with _save_lock:
                _atomic_write(DATA_FILE, data)
                # one backup per day (overwritten during the day), last 30 days kept
                os.makedirs(BACKUP_DIR, exist_ok=True)
                today = datetime.date.today().isoformat()
                _atomic_write(os.path.join(BACKUP_DIR, f"plans-{today}.json"), data)
                _prune_backups()
        except OSError as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True}


_mutex_handle = None


def _already_running():
    """A second window would hold a stale in-memory state and overwrite the first
    one's saves. A named mutex is released automatically if the process crashes
    (unlike a lock file)."""
    global _mutex_handle
    if sys.platform != "win32":
        return False
    import ctypes
    # use_last_error: ctypes.windll + GetLastError() is unreliable (ctypes can
    # clobber the thread's last-error value between the two calls).
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    # right after an update, the old version is still closing: wait for it
    tries = 40 if "--after-update" in sys.argv else 1
    for i in range(tries):
        _mutex_handle = kernel32.CreateMutexW(None, False, "Global\\RemontadaPlannerSingleInstance")
        if ctypes.get_last_error() != 183:  # ERROR_ALREADY_EXISTS
            return False
        if i < tries - 1:
            kernel32.CloseHandle(_mutex_handle)
            import time

            time.sleep(0.25)
    return True


def main():
    if _already_running():
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            None,
            "Remontada Planner est déjà ouvert.\n\n"
            "Une autre fenêtre tourne déjà — ferme-la avant d'en relancer une "
            "nouvelle, sinon tu risques de perdre de la progression.",
            "Remontada Planner",
            0x40,  # MB_ICONINFORMATION
        )
        sys.exit(0)
    _cleanup_old_exe()

    # Works both as a plain script and as a PyInstaller --onefile bundle
    # (PyInstaller extracts bundled data to sys._MEIPASS at runtime)
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(base_dir, "ui", "index.html")
    icon_path = os.path.join(base_dir, "app.ico")
    webview.create_window(
        "Remontada Planner",
        index_path,
        js_api=Api(),
        width=1100,
        height=760,
        min_size=(780, 560),
        background_color="#121018",
    )
    webview.start(icon=icon_path if os.path.isfile(icon_path) else None)


if __name__ == "__main__":
    main()
