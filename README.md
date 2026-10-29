# Remontada Planner

Un planner quotidien gamifié (XP, niveaux, pièces, succès, boutique de thèmes...)
pensé d'abord comme une vraie boucle quotidienne — capturer, prioriser,
exécuter, clôturer — en app de bureau Windows, construite avec
[pywebview](https://pywebview.flowrl.com/) (interface HTML/CSS/JS, logique Python).

## ⬇️ Télécharger l'app

**[Télécharger RemontadaPlanner.zip](https://github.com/Guillomus-lab/RemontadaPlanner/releases/latest/download/RemontadaPlanner.zip)**
(dernière version, Windows)

Dézippe, puis double-clique sur `RemontadaPlanner.exe`. C'est tout.

> ⚠️ N'utilise pas le bouton vert **Code → Download ZIP** : il donne le code
> source (pour développer), pas l'app.

## Installation

Deux façons d'utiliser l'app :

### 1. Version prête à l'emploi (.exe) — pour un usage courant

Aucune installation : télécharge le zip ci-dessus, dézippe-le et double-clique
sur `RemontadaPlanner.exe` pour lancer l'app. Windows peut afficher un avertissement
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

### Si tu utilises l'exe téléchargé

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

1. Bump `APP_VERSION` dans `app.pyw` (ex. `1.2.0`).
2. Optionnel : écris les nouveautés dans `packaging/notes/v1.2.0.md`
   (sinon le texte de `packaging/notes/default.md` est utilisé).
3. Commit sur `main`, puis lance la publication : onglet **Actions** du dépôt →
   **Release** → **Run workflow** (le tag `v1.2.0` est créé tout seul). Pousser
   le tag à la main (`git tag v1.2.0` puis `git push origin v1.2.0`) marche aussi.

GitHub Actions (`.github/workflows/release.yml`) construit l'exe sur Windows,
fait le zip (exe + `LISEZMOI.txt`) et publie la Release. Rien à builder en local.
Le workflow refuse de publier si `APP_VERSION` ne correspond pas au tag, ou si
la release de cette version existe déjà.

La vérification de mise à jour compare `APP_VERSION` au tag de la dernière
release publiée sur `Guillomus-lab/RemontadaPlanner` — pense à publier une
vraie *Release* GitHub (pas juste un tag) pour qu'elle soit détectée.

## La boucle quotidienne

1. **Capturer** — une idée sans heure ? Ajoute-la au backlog « 📥 À planifier »,
   sans lui inventer un créneau tout de suite.
2. **Prioriser** — choisis jusqu'à 3 priorités du jour (⭐). La jauge de charge
   compare les tâches planifiées à ta capacité réaliste, réglable dans
   Profil → Réglages.
3. **Exécuter** — timeline de 6h à minuit, notes et liens utiles sur chaque
   tâche, rappels Windows optionnels avant le début d'une tâche.
4. **Clôturer** — le bouton « 🌙 Clôturer la journée » ouvre un bilan : tâches
   finies, note du soir, et report des tâches non terminées à demain (même
   heure, prochain créneau libre, ou retour au backlog).

Si la veille n'a pas été clôturée, l'app propose au lancement de reporter les
tâches restantes. Les lignes du backlog peuvent être glissées directement sur la
timeline, ou planifiées au prochain créneau libre d'un clic sur 📅.

## Fonctionnalités notables

- Vue jour / semaine / mois, routines récurrentes, modèles de journée.
- Top 3 priorités par journée et jauge de charge avec capacité quotidienne.
- Backlog « à planifier » : capture rapide, édition, planification en un clic
  ou par glisser-déposer sur la timeline.
- Recherche globale (Ctrl+K) sur les tâches, notes, liens, catégories, backlog,
  routines, modèles et actions.
- Notes et URL sur chaque tâche, affichées dans la timeline et la vue semaine.
- Rappels Windows optionnels (toast système + toast dans l'app) tant que l'app
  est ouverte, avec le son « Rappel » de Windows (désactivable dans les réglages)
  et une notification qui reste affichée jusqu'à ce que tu cliques OK. Le bouton « Tester la notification » (Profil → Réglages) vérifie
  qu'elles s'affichent ; si rien n'apparaît, regarde le mode Ne pas déranger.
- Récap hebdomadaire Discord via webhook (par exemple le salon de Luron) :
  envoi manuel, ou automatique le lundi si activé. Aucun ping.
- Insights locaux sur les 30 derniers jours : taux de complétion, charge vs
  capacité, meilleur créneau, catégorie la plus fiable, priorités tenues,
  reports et journées parfaites.
- Système de progression (XP, niveaux, pièces, succès, boutique de thèmes,
  d'avatars et de gels de série) : la série continue dès qu'une tâche est
  faite dans la journée, et un gel peut pardonner un jour manqué.
- Tutoriel de prise en main au tout premier lancement (rejouable depuis
  Profil → onglet Pseudo → "Revoir le tutoriel").
- Sons synthétisés (pas de fichiers audio à bundler) pour les actions clés ;
  réglables via l'icône 🔊 dans la barre d'outils.
- Interface en glassmorphism (panneaux et modales translucides avec flou)
  et animations sur les interactions.
- Sauvegarde automatique + 30 jours de backups locaux, récupération auto
  en cas de fichier de sauvegarde corrompu.
