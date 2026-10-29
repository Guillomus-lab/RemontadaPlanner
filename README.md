# Remontada Planner

Un planner quotidien gamifié (XP, niveaux, pièces, succès, boutique de thèmes...)
en app de bureau Windows, construite avec [pywebview](https://pywebview.flowrl.com/)
(interface HTML/CSS/JS, logique Python).

## Installation

Deux façons d'utiliser l'app :

### 1. Version installée (.exe) — pour un usage courant

Aucune installation : double-clique sur `dist/RemontadaPlanner.exe` (ou le
raccourci fourni) pour lancer l'app. Windows peut afficher un avertissement
SmartScreen au premier lancement (exe non signé) — clique sur
"Informations complémentaires" puis "Exécuter quand même".

Tes données (planning, succès, avatar, pièces...) sont sauvegardées dans
`%APPDATA%\DailyPlanner\plans.json`, séparément de l'exe.

### 2. Depuis les sources — pour développer

```
uv venv .venv
.venv\Scripts\pip install pywebview
.venv\Scripts\python app.pyw
```

(ou lance `Lancer Remontada Planner.vbs` / `.bat`)

## Mise à jour

### Si tu utilises l'exe installé

L'app vérifie automatiquement s'il existe une nouvelle version au lancement
(appel à l'API GitHub Releases du dépôt). Si une mise à jour est disponible,
une popup s'affiche avec deux choix :
- **Mettre à jour** : ouvre la page de la release dans ton navigateur pour
  télécharger le nouvel exe.
- **Plus tard** : ferme la popup ; elle ne réapparaîtra pas pour cette même
  version (mais réapparaîtra à la version suivante).

Remplace simplement l'ancien `RemontadaPlanner.exe` par le nouveau : tes
données ne bougent pas (elles sont stockées à part, pas dans l'exe).

Pas de connexion internet ou API GitHub indisponible : la vérification échoue
silencieusement, l'app démarre normalement.

### Si tu utilises les sources (git)

```
git pull
```

C'est tout — pas de build, pas de migration manuelle : le schéma de données
(`plans.json`) se met à jour tout seul au premier lancement après un `git pull`
si le format a changé. Relance l'app avec `.venv\Scripts\python app.pyw` (ou
le `.vbs`/`.bat`) après le `git pull`.

### Publier une nouvelle version (pour le mainteneur)

1. Bump `APP_VERSION` dans `app.pyw`.
2. Commit, tag (`git tag vX.Y.Z`), push (`git push && git push --tags`).
3. `gh release create vX.Y.Z dist/RemontadaPlanner.exe --title "vX.Y.Z" --notes "..."`
   (ou crée la release depuis l'interface GitHub).

La vérification de mise à jour compare `APP_VERSION` au tag de la dernière
release publiée sur `Guillomus-lab/RemontadaPlanner` — pense à publier une
vraie *Release* GitHub (pas juste un tag) pour qu'elle soit détectée.

## Fonctionnalités notables

- Vue jour / semaine / mois, routines récurrentes, modèles de journée.
- Système de progression (XP, niveaux, pièces, succès, boutique de thèmes
  et d'avatars).
- Tutoriel de prise en main au tout premier lancement (rejouable depuis
  Profil → onglet Pseudo → "Revoir le tutoriel").
- Sons synthétisés (pas de fichiers audio à bundler) pour les actions clés ;
  réglables via l'icône 🔊 dans la barre d'outils.
- Interface en glassmorphism (panneaux et modales translucides avec flou)
  et animations sur les interactions.
- Sauvegarde automatique + 30 jours de backups locaux, récupération auto
  en cas de fichier de sauvegarde corrompu.
