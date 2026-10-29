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

L'app vérifie au lancement s'il existe une nouvelle version (API GitHub
Releases du dépôt). Si oui, une fenêtre propose deux choix :
- **Mettre à jour maintenant** : l'app télécharge la nouvelle version, vérifie
  qu'elle n'est pas abîmée (somme de contrôle SHA-256 publiée par GitHub),
  remplace l'exe et redémarre toute seule. Tes données ne bougent pas (elles
  sont stockées à part, pas dans l'exe). Si quelque chose échoue, la version
  actuelle reste intacte et la fenêtre propose d'ouvrir la page de téléchargement.
- **Plus tard** : ferme la fenêtre ; elle ne réapparaîtra pas pour cette même
  version (mais réapparaîtra à la version suivante).

La mise à jour automatique existe à partir de la v1.2.1 : depuis une version
plus ancienne, il faut une dernière fois télécharger le zip et remplacer l'exe.

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
- Ajout rapide en une phrase : « sport demain 18h 45min #santé ! » crée la tâche
  (date, heure, durée, catégorie, priorité) sans ouvrir de fenêtre.
- Top 3 priorités par journée et jauge de charge avec capacité quotidienne.
- Bilan de la semaine (proposé le dimanche soir et le lundi) : stats de la
  semaine passée, tâches non finies à garder pour plus tard, et 3 priorités de
  la semaine affichées sous les priorités du jour.
- Mode concentration (menu ⋯ ou 🎯 dans une tâche) : minuteur 15 à 60 min,
  pause, pastille réduite dans un coin, pause café de 5 min, et la tâche se
  coche à la fin.
- Backlog « à planifier » : capture rapide, édition, planification en un clic
  ou par glisser-déposer sur la timeline.
- Recherche globale (Ctrl+K) sur les tâches, notes, liens, catégories, backlog,
  routines, modèles et actions.
- Notes et URL sur chaque tâche, affichées dans la timeline et la vue semaine.
- Rappels Windows optionnels (toast système + toast dans l'app) tant que l'app
  est ouverte, avec le son « Rappel » de Windows (désactivable dans les réglages),
  une notification qui reste affichée jusqu'à « OK » et un bouton « Plus tard »
  (5, 10 ou 15 min). L'app propose de les activer à la première tâche avec une
  heure. Le bouton « Tester la notification » (Profil → Réglages) vérifie
  qu'elles s'affichent ; si rien n'apparaît, regarde le mode Ne pas déranger.
- Récap hebdomadaire Discord via webhook (par exemple le salon de Luron) :
  envoi manuel, ou automatique le lundi si activé. Aucun ping.
- Idées de repas (bonus, désactivable) : dans une tâche de repas (déjeuner,
  dîner, petit-déj, goûter…), le bouton « 🍽️ Idée de repas » propose une recette
  parmi 1000 recettes de 47 cuisines, dont ~10 % de cheat meals : 104 écrites à
  la main (`ui/recipes.js`) et 896 générées par `scripts/build_recipes.py`
  (`ui/recipes_world.js`, ne pas modifier à la main). Filtres protéiné / léger /
  végétarien / rapide / cheat meal, et choix de la cuisine. On peut garder la recette dans la note de la tâche ou
  envoyer ses ingrédients dans « À planifier » comme liste de courses.
  **Menus de la semaine** (menu ⋯) : déjeuners et dîners des 7 jours, une
  liste de courses regroupée, et l'ajout des repas au planning.
- Séances de sport suggérées (bonus, désactivable) : dans une tâche de sport
  (sport, muscu, séance, course, yoga…), le bouton « 🏋️ Séance suggérée » propose
  une séance complète selon la durée de la tâche, la zone (tout le corps, haut,
  bas, abdos, cardio/HIIT, mobilité, course à pied), le niveau et le matériel :
  échauffement, exercices avec séries, répétitions, repos et consigne technique
  (supersets pour les séances longues), retour au calme et conseils. Générées par
  `ui/workouts.js` (bibliothèque d'exercices + générateur). On peut garder la
  séance dans la note de la tâche ou lancer le minuteur.
- Concentration : bouton « ▶ Focus » au survol de chaque tâche du jour, et zone
  « En ce moment » dans la barre du jour pour la tâche en cours.
- Sauvegarde de tes données (Profil → Réglages) : export dans un fichier et
  restauration, avec une copie de sécurité gardée avant chaque restauration.
- Barre du haut allégée : bilan, concentration, menus, récap, thème et sons
  sont dans le menu ⋯ ; le zoom apparaît en haut à droite du planning au survol.
- Insights locaux sur les 30 derniers jours : taux de complétion, charge vs
  capacité, meilleur créneau, catégorie la plus fiable, priorités tenues,
  reports et journées parfaites.
- Système de progression (XP, niveaux, pièces, succès, boutique de thèmes,
  d'avatars et de gels de série) : la série continue dès qu'une tâche est
  faite dans la journée, et un gel peut pardonner un jour manqué.
- Tutoriel de prise en main au tout premier lancement (rejouable depuis
  Profil → onglet Profil → "Revoir le tutoriel").
- Sons synthétisés (pas de fichiers audio à bundler) pour les actions clés ;
  réglables via l'icône 🔊 du menu ⋯.
- Interface en glassmorphism (panneaux et modales translucides avec flou)
  et animations sur les interactions.
- Sauvegarde automatique + 30 jours de backups locaux, récupération auto
  en cas de fichier de sauvegarde corrompu.
