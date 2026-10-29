import datetime
import glob
import json
import os
import sys
import threading

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

SCHEMA_VERSION = 4

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
    },
    "counters": {},      # free-form usage counters (remixUsed, tasksDeleted, konamiFound, ...)
    "settings": {"theme": "dark", "zoom": 72, "view": "day"},  # UI prefs persisted across launches
    # recurring tasks: {id,title,start,duration,category,days:[0-6],from,until,skip:[dates]}
    "routines": [],
    # regularity challenges: {id,title,category,keywords,length,start,status,...}
    "challenges": [],
    "quests": {"claimed": {}},  # weekly quests already rewarded: { "2026-10-26": ["move7", ...] }
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
        return _clone(DEFAULT_DATA)
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


class Api:
    def load(self):
        return _load_raw()

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
    _mutex_handle = kernel32.CreateMutexW(None, False, "Global\\RemontadaPlannerSingleInstance")
    return ctypes.get_last_error() == 183  # ERROR_ALREADY_EXISTS


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
