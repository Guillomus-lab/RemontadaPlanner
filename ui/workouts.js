// Séances de sport suggérées (fonction bonus, désactivable dans Profil → Réglages).
// Bibliothèque d'exercices + générateur de séance « façon coach » :
// échauffement → corps de séance → retour au calme, adapté à la durée, la zone,
// le niveau et le matériel. Aucune donnée externe, tout est calculé ici.
//
// Exercice : n nom · p schéma de mouvement · eq matériel minimum (none < db < gym)
//            lv [niveau min, niveau max] (1 débutant, 2 intermédiaire, 3 confirmé)
//            c consigne technique · bw true = poids du corps (plus de répétitions)
//            side true = par côté · time true = en secondes plutôt qu'en répétitions
const EXERCISES = [
  // ----- squat
  {n:"Squat au poids du corps", p:"squat", eq:"none", lv:[1,2], bw:true, c:"Pieds largeur d'épaules, hanches en arrière, genoux dans l'axe des pieds, dos neutre."},
  {n:"Squat avec pause de 2 s en bas", p:"squat", eq:"none", lv:[2,3], bw:true, c:"Descends contrôlé, tiens 2 s en bas sans t'affaisser, remonte en poussant dans les talons."},
  {n:"Squat sauté", p:"squat", eq:"none", lv:[3,3], bw:true, c:"Réception souple et silencieuse, genoux qui ne rentrent pas vers l'intérieur."},
  {n:"Goblet squat", p:"squat", eq:"db", lv:[1,3], c:"Haltère contre la poitrine, coudes entre les genoux en bas, buste fier."},
  {n:"Squat avant aux haltères", p:"squat", eq:"db", lv:[2,3], c:"Haltères sur les épaules, coudes hauts, descends le plus bas possible en gardant le dos neutre."},
  {n:"Squat à la barre", p:"squat", eq:"gym", lv:[2,3], c:"Barre sur les trapèzes, gainage avant de descendre, cuisses au moins parallèles."},
  {n:"Presse à cuisses", p:"squat", eq:"gym", lv:[1,3], c:"Bas du dos collé au dossier, ne verrouille pas complètement les genoux en haut."},
  // ----- hip hinge
  {n:"Pont fessier", p:"hinge", eq:"none", lv:[1,2], bw:true, c:"Talons proches des fesses, pousse dans les talons, serre les fessiers 1 s en haut."},
  {n:"Pont fessier une jambe", p:"hinge", eq:"none", lv:[2,3], bw:true, side:true, c:"Bassin bien horizontal, ne laisse pas tomber la hanche du côté libre."},
  {n:"Good morning au poids du corps", p:"hinge", eq:"none", lv:[1,1], bw:true, c:"Mains derrière la tête, genoux légèrement fléchis, bascule le buste en reculant les hanches."},
  {n:"Soulevé de terre roumain aux haltères", p:"hinge", eq:"db", lv:[1,3], c:"Haltères qui glissent le long des cuisses, dos plat, sens l'étirement des ischios."},
  {n:"Hip thrust aux haltères", p:"hinge", eq:"db", lv:[2,3], c:"Haut du dos sur un canapé, haltère sur les hanches, menton rentré, verrouille avec les fessiers."},
  {n:"Soulevé de terre à la barre", p:"hinge", eq:"gym", lv:[2,3], c:"Barre contre les tibias, dos neutre, pousse le sol avec les jambes puis ouvre les hanches."},
  {n:"Hip thrust à la barre", p:"hinge", eq:"gym", lv:[2,3], c:"Coussin sur la barre, tibias verticaux en haut, pas d'hyperextension du bas du dos."},
  // ----- single leg
  {n:"Fentes arrière alternées", p:"lunge", eq:"none", lv:[1,2], bw:true, side:true, c:"Grand pas en arrière, genou arrière qui frôle le sol, buste droit."},
  {n:"Step-up sur une chaise", p:"lunge", eq:"none", lv:[1,2], bw:true, side:true, c:"Chaise stable contre un mur, pousse avec la jambe du haut sans t'aider de celle du bas."},
  {n:"Fentes bulgares", p:"lunge", eq:"none", lv:[2,3], bw:true, side:true, c:"Pied arrière sur une chaise, descends verticalement, genou avant au-dessus du pied."},
  {n:"Fentes sautées", p:"lunge", eq:"none", lv:[3,3], bw:true, c:"Change de jambe en l'air, réception amortie, reste gainé."},
  {n:"Fentes marchées aux haltères", p:"lunge", eq:"db", lv:[2,3], side:true, c:"Haltères le long du corps, pas assez grands pour garder le genou derrière la pointe du pied."},
  {n:"Fentes bulgares aux haltères", p:"lunge", eq:"db", lv:[2,3], side:true, c:"Buste légèrement penché vers l'avant pour cibler les fessiers."},
  // ----- horizontal push
  {n:"Pompes inclinées (mains sur une table)", p:"push_h", eq:"none", lv:[1,1], bw:true, c:"Corps gainé de la tête aux talons, coudes à 45° du buste."},
  {n:"Pompes sur les genoux", p:"push_h", eq:"none", lv:[1,1], bw:true, c:"Hanches dans l'alignement, la poitrine descend jusqu'à frôler le sol."},
  {n:"Pompes", p:"push_h", eq:"none", lv:[2,3], bw:true, c:"Mains sous les épaules, gainage serré, descends la poitrine, pas le menton."},
  {n:"Pompes déclinées (pieds sur une chaise)", p:"push_h", eq:"none", lv:[3,3], bw:true, c:"Plus dur pour le haut des pectoraux et les épaules : garde le gainage."},
  {n:"Développé au sol aux haltères", p:"push_h", eq:"db", lv:[1,2], c:"Allongé au sol, les coudes touchent le sol doucement à chaque répétition."},
  {n:"Développé couché aux haltères", p:"push_h", eq:"db", lv:[2,3], c:"Omoplates serrées sur le banc, descends les haltères au niveau de la poitrine."},
  {n:"Développé couché à la barre", p:"push_h", eq:"gym", lv:[2,3], c:"Pieds ancrés, omoplates serrées, barre qui touche le bas des pectoraux."},
  {n:"Chest press à la machine", p:"push_h", eq:"gym", lv:[1,2], c:"Poignées à hauteur de poitrine, pousse sans décoller le dos."},
  // ----- vertical push
  {n:"Pike push-up", p:"push_v", eq:"none", lv:[2,3], bw:true, c:"Hanches hautes en V inversé, la tête descend entre les mains."},
  {n:"Pike push-up sur les genoux", p:"push_v", eq:"none", lv:[1,1], bw:true, c:"Version facile : genoux au sol, hanches hautes, amplitude contrôlée."},
  {n:"Développé militaire aux haltères", p:"push_v", eq:"db", lv:[1,3], c:"Debout ou assis, gainage serré, pousse au-dessus de la tête sans cambrer."},
  {n:"Développé militaire à la barre", p:"push_v", eq:"gym", lv:[2,3], c:"Fessiers serrés, la tête passe sous la barre en haut du mouvement."},
  {n:"Shoulder press à la machine", p:"push_v", eq:"gym", lv:[1,2], c:"Dos collé au dossier, ne verrouille pas les coudes en haut."},
  // ----- horizontal pull
  {n:"Superman tirage", p:"pull_h", eq:"none", lv:[1,2], bw:true, c:"Allongé sur le ventre, poitrine légèrement décollée, tire les coudes vers les hanches et serre les omoplates."},
  {n:"Rowing inversé sous une table solide", p:"pull_h", eq:"none", lv:[2,3], bw:true, c:"Vérifie que la table est stable ! Corps gainé, tire la poitrine vers le bord."},
  {n:"Rowing un bras à l'haltère", p:"pull_h", eq:"db", lv:[1,3], side:true, c:"Main et genou sur une chaise, tire le coude vers la hanche, dos plat."},
  {n:"Rowing buste penché aux haltères", p:"pull_h", eq:"db", lv:[2,3], c:"Buste à 45°, dos plat, tire les haltères vers le nombril."},
  {n:"Tirage horizontal à la poulie", p:"pull_h", eq:"gym", lv:[1,3], c:"Buste fixe, tire vers le nombril en serrant les omoplates."},
  {n:"Rowing à la barre", p:"pull_h", eq:"gym", lv:[2,3], c:"Dos plat, barre tirée vers le bas du ventre, pas d'élan."},
  // ----- vertical pull
  {n:"Y-T-W au sol", p:"pull_v", eq:"none", lv:[1,2], bw:true, c:"Allongé sur le ventre, bras en Y, puis T, puis W, pouces vers le plafond : 1 répétition = les trois lettres."},
  {n:"Pull-over à l'haltère", p:"pull_v", eq:"db", lv:[1,3], c:"Allongé, bras presque tendus, descends l'haltère derrière la tête sans cambrer."},
  {n:"Tirage vertical à la poulie", p:"pull_v", eq:"gym", lv:[1,3], c:"Tire la barre vers le haut de la poitrine, coudes vers le bas, sans balancer."},
  {n:"Tractions assistées (machine ou élastique)", p:"pull_v", eq:"gym", lv:[1,2], c:"Monte le menton au-dessus de la barre, redescends bras presque tendus."},
  {n:"Tractions", p:"pull_v", eq:"gym", lv:[3,3], c:"Départ bras tendus, poitrine vers la barre, pas de balancier."},
  // ----- accessories
  {n:"Élévations latérales aux haltères", p:"shoulders", eq:"db", lv:[1,3], c:"Coudes légèrement fléchis, monte jusqu'à hauteur d'épaules, sans élan."},
  {n:"Face pull à la poulie", p:"shoulders", eq:"gym", lv:[1,3], c:"Corde vers le visage, coudes hauts, termine pouces vers l'arrière."},
  {n:"Cercles de bras tendus", p:"shoulders", eq:"none", lv:[1,2], bw:true, time:true, c:"Bras tendus sur les côtés, petits cercles : 15 s vers l'avant puis 15 s vers l'arrière."},
  {n:"Curl aux haltères", p:"biceps", eq:"db", lv:[1,3], c:"Coudes collés au corps, monte en supination, redescends lentement."},
  {n:"Curl marteau", p:"biceps", eq:"db", lv:[1,3], c:"Paumes face à face, pas de balancier du buste."},
  {n:"Dips sur une chaise", p:"triceps", eq:"none", lv:[1,3], bw:true, c:"Mains au bord d'une chaise stable, coudes vers l'arrière, épaules basses."},
  {n:"Pompes serrées", p:"triceps", eq:"none", lv:[2,3], bw:true, c:"Mains sous la poitrine, coudes qui frôlent les côtes."},
  {n:"Extension triceps à l'haltère au-dessus de la tête", p:"triceps", eq:"db", lv:[1,3], c:"Coudes pointés vers le plafond, seuls les avant-bras bougent."},
  {n:"Abduction de hanche allongé", p:"glute", eq:"none", lv:[1,2], bw:true, side:true, c:"Allongé sur le côté, monte la jambe tendue légèrement en arrière, sans rouler le bassin."},
  {n:"Donkey kicks", p:"glute", eq:"none", lv:[1,2], bw:true, side:true, c:"À quatre pattes, pousse le talon vers le plafond, dos immobile."},
  {n:"Mollets debout", p:"calf", eq:"none", lv:[1,3], bw:true, c:"Monte sur la pointe des pieds, tiens 1 s en haut, redescends lentement."},
  {n:"Mollets une jambe sur une marche", p:"calf", eq:"none", lv:[2,3], bw:true, side:true, c:"Talon qui descend sous la marche, amplitude complète."},
  // ----- core
  {n:"Gainage planche", p:"core", eq:"none", lv:[1,3], bw:true, time:true, c:"Coudes sous les épaules, fessiers serrés, ne creuse pas le bas du dos."},
  {n:"Gainage latéral", p:"core", eq:"none", lv:[1,3], bw:true, time:true, side:true, c:"Bassin haut, corps aligné de la tête aux pieds."},
  {n:"Dead bug", p:"core", eq:"none", lv:[1,2], bw:true, side:true, c:"Bas du dos plaqué au sol, étire bras et jambe opposés lentement."},
  {n:"Bird dog", p:"core", eq:"none", lv:[1,1], bw:true, side:true, c:"À quatre pattes, tends bras et jambe opposés sans bouger le bassin."},
  {n:"Planche avec touchers d'épaule", p:"core", eq:"none", lv:[2,3], bw:true, c:"Pieds écartés, bassin immobile pendant que tu touches l'épaule opposée."},
  {n:"Hollow hold", p:"core", eq:"none", lv:[2,3], bw:true, time:true, c:"Bas du dos collé au sol, bras et jambes tendus juste au-dessus du sol."},
  {n:"Crunch", p:"core_flex", eq:"none", lv:[1,2], bw:true, c:"Décolle les omoplates en expirant, sans tirer sur la nuque."},
  {n:"Crunch vélo", p:"core_flex", eq:"none", lv:[1,3], bw:true, c:"Coude vers genou opposé, lentement, l'autre jambe tendue."},
  {n:"Relevés de jambes", p:"core_flex", eq:"none", lv:[2,3], bw:true, c:"Mains sous les fesses, bas du dos au sol, redescends sans toucher le sol."},
  {n:"Russian twist", p:"core_flex", eq:"none", lv:[1,3], bw:true, c:"Buste incliné en arrière, dos droit, tourne les épaules (avec un haltère si tu en as)."},
  {n:"V-ups", p:"core_flex", eq:"none", lv:[3,3], bw:true, c:"Mains et pieds se rejoignent au-dessus des hanches, redescends contrôlé."},
  // ----- cardio
  {n:"Jumping jacks", p:"cardio", eq:"none", lv:[1,3], bw:true, c:"Rythme régulier, atterris sur l'avant du pied."},
  {n:"Step jacks (sans saut)", p:"cardio", eq:"none", lv:[1,1], bw:true, c:"Version sans impact : un pied sur le côté à la fois, bras au-dessus de la tête."},
  {n:"Montées de genoux", p:"cardio", eq:"none", lv:[1,3], bw:true, c:"Genoux à hauteur de hanches, bras actifs, reste sur l'avant des pieds."},
  {n:"Talons-fesses", p:"cardio", eq:"none", lv:[1,2], bw:true, c:"Rapide et léger, buste droit."},
  {n:"Mountain climbers", p:"cardio", eq:"none", lv:[2,3], bw:true, c:"Épaules au-dessus des mains, ramène les genoux vite sans lever les fesses."},
  {n:"Burpees sans saut", p:"cardio", eq:"none", lv:[1,2], bw:true, c:"Recule les pieds un par un, pas de pompe obligatoire, relève-toi sans sauter."},
  {n:"Burpees", p:"cardio", eq:"none", lv:[2,3], bw:true, c:"Planche, pompe, retour pieds aux mains, saut bras tendus."},
  {n:"Patineur (skater jumps)", p:"cardio", eq:"none", lv:[2,3], bw:true, c:"Saut latéral sur une jambe, réception stable, l'autre jambe croise derrière."},
  {n:"Shadow boxing", p:"cardio", eq:"none", lv:[1,3], bw:true, c:"Garde haute, enchaîne directs et crochets en restant léger sur les appuis."},
  {n:"Sprint sur place", p:"cardio", eq:"none", lv:[2,3], bw:true, c:"Le plus vite possible, bras qui pompent, buste légèrement penché."},
  {n:"Corde à sauter", p:"cardio", eq:"none", lv:[1,3], bw:true, c:"Petits sauts sur l'avant des pieds (sans corde : mime le mouvement)."},
  {n:"Rameur", p:"cardio", eq:"gym", lv:[1,3], c:"Jambes, puis buste, puis bras ; retour dans l'ordre inverse."},
  {n:"Vélo d'appartement à fond", p:"cardio", eq:"gym", lv:[1,3], c:"Résistance moyenne, cadence maximale sur l'effort."},
];

// Mobility / stretching moves (warm-up, cool-down and mobility sessions)
const MOBILITY = {
  catcow: {n:"Chat-vache", z:["core","full","mobility","lower","upper"], c:"À quatre pattes, enroule puis creuse le dos lentement avec la respiration."},
  child: {n:"Posture de l'enfant", z:["core","full","mobility","upper"], c:"Fesses sur les talons, bras loin devant, respire dans le dos."},
  hipflexor: {n:"Fente basse (étirement du psoas)", z:["lower","full","mobility","run"], side:true, c:"Genou arrière au sol, bascule le bassin vers l'avant, fessier serré."},
  thoracic: {n:"Ouverture thoracique (livre ouvert)", z:["upper","full","mobility"], side:true, c:"Allongé sur le côté, genoux pliés, ouvre le bras du dessus en suivant la main des yeux."},
  pigeon: {n:"Posture du pigeon", z:["lower","full","mobility","run"], side:true, c:"Jambe avant pliée devant toi, l'autre tendue derrière, bassin bien face au sol."},
  hip9090: {n:"Rotation de hanches 90/90", z:["lower","mobility"], c:"Assis, jambes à 90°, bascule les genoux d'un côté à l'autre lentement."},
  downdog: {n:"Chien tête en bas", z:["full","mobility","run","upper"], c:"Hanches hautes, pousse le sol avec les mains, talons vers le sol."},
  cobra: {n:"Cobra", z:["core","mobility"], c:"Allongé sur le ventre, pousse sur les mains, épaules basses, sans forcer le bas du dos."},
  hamstring: {n:"Étirement des ischios assis", z:["lower","full","mobility","run"], c:"Jambes tendues, penche-toi depuis les hanches, dos long."},
  spinaltwist: {n:"Torsion allongée", z:["core","full","mobility"], side:true, c:"Allongé sur le dos, genoux d'un côté, regard de l'autre."},
  calf: {n:"Étirement des mollets contre un mur", z:["lower","run","full"], side:true, c:"Jambe arrière tendue, talon au sol, pousse le mur."},
  quad: {n:"Étirement des quadriceps debout", z:["lower","run","full"], side:true, c:"Talon vers la fesse, genoux serrés, bassin en rétroversion."},
  shoulder: {n:"Étirement des épaules (bras croisé)", z:["upper","full","mobility"], side:true, c:"Bras tendu devant la poitrine, tire doucement avec l'autre main."},
  chest: {n:"Étirement des pectoraux contre un mur", z:["upper","full","mobility"], side:true, c:"Avant-bras sur le mur, tourne doucement le buste à l'opposé."},
  deepsquat: {n:"Squat profond tenu", z:["lower","mobility","full"], c:"Talons au sol, coudes poussent les genoux vers l'extérieur."},
  triceps: {n:"Étirement des triceps", z:["upper"], side:true, c:"Main dans le dos derrière la tête, tire le coude avec l'autre main."},
};

const WORKOUT_ZONES = {
  full: "Tout le corps", upper: "Haut du corps", lower: "Bas du corps", core: "Abdos & gainage",
  cardio: "Cardio / HIIT", mobility: "Mobilité & étirements", run: "Course à pied",
};
const WORKOUT_LEVELS = {1: "Débutant", 2: "Intermédiaire", 3: "Confirmé"};
const WORKOUT_EQUIP = {none: "Sans matériel", db: "Haltères (maison)", gym: "Salle de sport"};
const EQ_RANK = {none: 0, db: 1, gym: 2};

// Movement order per zone: compound movements first, then accessories, core last.
const ZONE_PATTERNS = {
  full: ["squat", "push_h", "hinge", "pull_h", "lunge", "push_v", "pull_v", "core", "core_flex"],
  upper: ["push_h", "pull_h", "push_v", "pull_v", "shoulders", "biceps", "triceps", "core"],
  lower: ["squat", "hinge", "lunge", "glute", "calf", "core", "hinge", "lunge"],
  core: ["core", "core_flex", "hinge", "core", "core_flex", "glute", "core"],
  cardio: ["cardio", "cardio", "cardio", "cardio", "cardio", "cardio"],
};

function guessWorkoutZone(title){
  const t = (title || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  if(/course|running|footing|jogging|run\b|trail|fractionne/.test(t)) return "run";
  if(/yoga|etirement|stretch|mobilite|souplesse|pilates/.test(t)) return "mobility";
  if(/abdo|gainage|core|sangle/.test(t)) return "core";
  if(/hiit|cardio|tabata|circuit|crossfit|corde|boxe/.test(t)) return "cardio";
  if(/jambe|bas du corps|fessier|squat|cuisse|leg/.test(t)) return "lower";
  if(/haut du corps|pec|dos|bras|epaule|biceps|triceps|push|pull|upper/.test(t)) return "upper";
  return "full";
}

function pickRandom(list){ return list[Math.floor(Math.random() * list.length)]; }
function shuffled(list){ const a = list.slice(); for(let i = a.length - 1; i > 0; i--){ const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function fmtSec(s){ return s >= 60 ? `${Math.floor(s/60)} min${s % 60 ? ' ' + (s % 60) + ' s' : ''}` : `${s} s`; }

// Best exercise for a movement pattern: fits the level, uses the equipment when available.
const exFamily = n=> n.split(/[ (]/)[0].toLowerCase();
function pickExercise(pattern, level, equip, used){
  const families = new Set([...used].map(exFamily));
  const ok = EXERCISES.filter(e=> e.p === pattern && EQ_RANK[e.eq] <= EQ_RANK[equip] && level >= e.lv[0] && level <= e.lv[1]
    && !used.has(e.n) && (pattern !== "cardio" || !families.has(exFamily(e.n))));
  if(!ok.length) return null;
  // prefer loaded variants when the person has equipment (bodyweight stays as a fallback)
  const best = Math.max(...ok.map(e=> EQ_RANK[e.eq]));
  const preferred = ok.filter(e=> EQ_RANK[e.eq] === best);
  return pickRandom(Math.random() < 0.8 ? preferred : ok);
}

function strengthDose(ex, level){
  const sets = [0, 2, 3, 4][level];
  const compound = ["squat", "hinge", "push_h", "push_v", "pull_h", "pull_v", "lunge"].includes(ex.p);
  let reps;
  // hard bodyweight moves (pike push-up, inverted row...) can't take 15-20 clean reps
  const hardBw = ex.bw && ["push_v", "pull_v", "pull_h"].includes(ex.p);
  if(ex.time) reps = `${[0, 25, 35, 45][level]} s`;
  else if(hardBw) reps = ["", "6-10", "8-12", "10-15"][level];
  else if(ex.bw) reps = ["", "8-12", "12-15", "15-20"][level];
  else if(compound) reps = ["", "10-12", "8-12", "6-10"][level];
  else reps = ["", "12-15", "10-15", "10-12"][level];
  if(ex.side) reps += " par côté";
  const rest = compound && !ex.bw ? [0, 75, 75, 105][level] : [0, 60, 60, 60][level];
  return {sets, reps, rest};
}

function warmupFor(zone, minutes, level){
  const items = [
    zone === "run"
      ? {n: "Marche rapide puis trot très lent", d: `${minutes} min`, c: "Monte progressivement en température, tu dois pouvoir parler sans effort."}
      : zone === "mobility"
        ? {n: "Marche sur place en respirant amplement", d: "1 min", c: "Relâche les épaules et la mâchoire."}
        : {n: "Jumping jacks ou marche rapide sur place", d: "2 min", c: "Monte progressivement en température, tu dois pouvoir parler."},
  ];
  if(zone === "run"){
    if(minutes >= 8 && level >= 2) items.push({n:"Gammes : talons-fesses, montées de genoux, pas chassés", d:"2 × 20 m chacun", c:"Léger et dynamique, sans forcer."});
    return items;
  }
  items.push({n:"Cercles d'épaules et de hanches", d:"1 min", c:"Grands cercles lents dans les deux sens."});
  if(zone === "upper") items.push({n:"Pompes inclinées faciles", d:"2 × 8", c:"Pour réveiller les épaules et les pectoraux."});
  else if(zone === "lower") items.push({n:"Squats lents + fentes arrière", d:"10 + 5 par côté", c:"Amplitude progressive."});
  else if(zone === "core") items.push({n:"Chat-vache + bird dog", d:"8 + 5 par côté", c:"Mobilise le dos avant le gainage."});
  else if(zone === "mobility") items.push({n:"Respiration ventrale", d:"1 min", c:"Inspire par le nez 4 s, expire 6 s."});
  else items.push({n:"Squats lents + pompes inclinées", d:"10 + 8", c:"Prépare tout le corps."});
  if(zone === "cardio" && minutes >= 5) items.push({n:"Montées de genoux progressives", d:"1 min", c:"Accélère sur les 20 dernières secondes."});
  return items;
}

function cooldownFor(zone, minutes){
  const pool = Object.values(MOBILITY).filter(m=> m.z.includes(zone === "cardio" ? "full" : zone));
  const hold = minutes >= 5 ? 40 : 30;
  const out = [];
  let left = minutes * 60;
  for(const m of shuffled(pool)){
    const cost = (hold + 10) * (m.side ? 2 : 1);
    if(out.length >= 2 && cost > left) continue;
    out.push({n: m.n, d: `${hold} s${m.side ? " par côté" : ""}`, c: m.c});
    left -= cost;
    if(left <= 0 || out.length >= 5) break;
  }
  return out;
}

// Builds a full session. opts: {minutes, zone, level (1-3), equip ('none'|'db'|'gym')}
function generateWorkout(opts){
  const minutes = Math.max(10, Math.min(120, Math.round(opts.minutes || 45)));
  const zone = WORKOUT_ZONES[opts.zone] ? opts.zone : "full";
  const level = [1, 2, 3].includes(opts.level) ? opts.level : 1;
  const equip = WORKOUT_EQUIP[opts.equip] ? opts.equip : "none";
  const warmMin = zone === "mobility" ? Math.max(2, Math.round(minutes * 0.1)) : Math.max(3, Math.min(12, Math.round(minutes * 0.15)));
  const coolMin = minutes >= 30 ? 5 : 3;
  const mainMin = minutes - warmMin - coolMin;
  const blocks = [{name: "Échauffement", min: warmMin, items: warmupFor(zone, warmMin, level)}];
  const tips = [];
  let format;

  if(zone === "run"){
    format = "Course";
    const items = [];
    if(level === 1){
      const reps = Math.max(2, Math.floor(mainMin / 3));
      items.push({n:"Alternance course lente / marche", d:`${reps} × (2 min course + 1 min marche)`, c:"Course à une allure où tu peux parler en phrases. Le but : courir plus longtemps sans t'épuiser."});
      tips.push("Débutant : augmente le temps de course de 30 s par semaine, pas plus.");
    } else if(level === 2){
      if(mainMin >= 25){
        items.push({n:"Footing en endurance fondamentale", d:`${mainMin - 8} min`, c:"Allure confortable (environ 70 % de ta fréquence cardiaque max)."});
        items.push({n:"Accélérations progressives", d:"6 × 20 s, 1 min de marche entre", c:"Monte jusqu'à 85-90 % de ta vitesse max, en restant relâché."});
      } else {
        items.push({n:"Fractionné 30/30", d:`2 séries de ${Math.max(4, Math.floor((mainMin - 3) / 2))} × (30 s rapide / 30 s trot)`, c:"Rapide mais tenable sur toute la série ; 3 min de trot entre les séries."});
      }
      tips.push("80 % de tes sorties doivent rester faciles : c'est ce qui fait progresser sans se blesser.");
    } else {
      if(mainMin >= 40){
        items.push({n:"Blocs au seuil", d:"3 × 8 min, 2 min de trot entre", c:"Allure « confortablement difficile », que tu pourrais tenir environ 1 h en course."});
        items.push({n:"Footing de fin", d:`${Math.max(5, mainMin - 30)} min`, c:"Retour à une allure facile."});
      } else {
        items.push({n:"Fractionné court", d:`2 séries de 8 × (30 s vite / 30 s trot), 3 min entre`, c:"Vite = allure 5 km ou plus rapide, foulée relâchée."});
        if(mainMin > 20) items.push({n:"Footing de fin", d:`${mainMin - 20} min`, c:"Allure facile."});
      }
      tips.push("Garde au moins 48 h entre deux séances intenses.");
    }
    blocks.push({name:"Corps de séance", min: mainMin, items});
  } else if(zone === "mobility"){
    format = "Mobilité";
    const hold = level === 1 ? 30 : 45;
    const moves = shuffled(Object.values(MOBILITY).filter(m=> m.z.includes("mobility")));
    const costOf = m=> (hold + 10) * (m.side ? 2 : 1);
    // pick enough postures for one pass to last ~8-12 min, then repeat it
    const pass = [];
    let passSec = 0;
    for(const m of moves){ if(passSec >= Math.min(mainMin * 60, 600)) break; pass.push(m); passSec += costOf(m); }
    const passes = Math.max(1, Math.round(mainMin * 60 / passSec));
    blocks.push({name:`Enchaînement${passes > 1 ? ` : ${passes} passages` : ""}`, min: mainMin,
      note: passes > 1 ? "Va un peu plus loin dans chaque position au passage suivant." : "",
      items: pass.map(m=> ({n: m.n, d: `${hold} s${m.side ? " par côté" : ""}`, c: m.c}))});
    tips.push("Respire lentement et relâche un peu plus à chaque expiration : on ne force jamais dans la douleur.");
  } else {
    const useCircuit = zone === "cardio" || zone === "core" || minutes < 25;
    const used = new Set();
    if(useCircuit){
      format = zone === "cardio" ? "HIIT" : "Circuit";
      const [work, rest] = [[0, 0], [30, 30], [40, 20], [45, 15]][level];
      const patterns = ZONE_PATTERNS[zone === "cardio" ? "cardio" : zone];
      const n = Math.max(4, Math.min(6, Math.round(mainMin / 3)));
      const items = [];
      for(let i = 0; i < patterns.length && items.length < n; i++){
        const ex = pickExercise(patterns[i], level, equip, used);
        if(!ex) continue;
        used.add(ex.n);
        items.push({n: ex.n, d: `${work} s d'effort${ex.side ? " (alterne les côtés)" : ""}`, c: ex.c});
      }
      const roundSec = items.length * (work + rest);
      const rounds = Math.max(2, Math.floor((mainMin * 60 + 60) / (roundSec + 60)));
      blocks.push({name: `${format} : ${rounds} tours`, min: mainMin, note: `${work} s d'effort / ${rest} s de récupération, 1 min de pause entre les tours.`, items});
      tips.push(zone === "cardio" ? "Bonne intensité : tu peux dire quelques mots, pas des phrases." : "Garde une technique propre : ralentis plutôt que de bâcler les répétitions.");
    } else {
      format = "Renforcement";
      // Supersets (A1 then A2, rest after the pair) fit more work in a long session
      // and pair opposite movements so one muscle group rests while the other works.
      const superset = level >= 2 && minutes >= 40 && zone !== "core";
      const finisher = minutes >= 30 && zone !== "core";
      const patterns = ZONE_PATTERNS[zone].filter(pt=> !finisher || !pt.startsWith("core"));
      const items = [];
      let budget = mainMin * 60 - (finisher ? 240 : 0);
      if(superset){
        let pairNo = 0;
        for(let i = 0; budget > 180 && i + 1 < patterns.length * 2; i += 2){
          const a = pickExercise(patterns[i % patterns.length], level, equip, used);
          if(a) used.add(a.n);
          const b = pickExercise(patterns[(i + 1) % patterns.length], level, equip, used);
          if(!a || !b){ if(a) used.delete(a.n); continue; }
          const da = strengthDose(a, level), db = strengthDose(b, level);
          const rest = Math.max(da.rest, db.rest);
          const cost = da.sets * (45 + 20 + 45 + rest) + 40;
          if(cost > budget + 60){ used.delete(a.n); break; }
          used.add(b.n);
          budget -= cost;
          const L = "ABCDEF"[pairNo++];
          items.push({n: `${L}1 · ${a.n}`, d: `${da.sets} × ${da.reps}, puis enchaîne ${L}2`, c: a.c});
          items.push({n: `${L}2 · ${b.n}`, d: `${db.sets} × ${db.reps} · repos ${fmtSec(rest)} après la paire`, c: b.c});
        }
      } else {
        for(let i = 0; budget > 120 && i < patterns.length * 2; i++){
          const ex = pickExercise(patterns[i % patterns.length], level, equip, used);
          if(!ex) continue;
          const dose = strengthDose(ex, level);
          const cost = dose.sets * (45 + dose.rest) + 30;
          if(cost > budget + 60) break;
          used.add(ex.n);
          budget -= cost;
          items.push({n: ex.n, d: `${dose.sets} × ${dose.reps} · repos ${fmtSec(dose.rest)}`, c: ex.c});
        }
      }
      if(finisher){
        const c1 = pickExercise("core", level, equip, used); if(c1) used.add(c1.n);
        const c2 = pickExercise("core_flex", level, equip, used) || pickExercise("core", level, equip, used);
        const t = [0, 25, 35, 45][level];
        [c1, c2].filter(Boolean).forEach(ex=> items.push({n: `Finisher gainage · ${ex.n}`, d: `${level + 1} tours de ${t} s${ex.side ? " par côté" : ""}, 15 s de pause`, c: ex.c}));
      }
      blocks.push({name: superset ? "Corps de séance (en supersets)" : "Corps de séance", min: mainMin,
        note: superset ? "Enchaîne A1 puis A2 sans pause, repose-toi après la paire, puis recommence." : "", items});
      tips.push("Garde 1 à 2 répétitions en réserve : la dernière doit être dure mais propre.");
      tips.push(equip === "none" ? "Progression : quand tu fais le haut de la fourchette partout, passe à une variante plus dure." : "Progression : quand tu fais le haut de la fourchette sur toutes les séries, ajoute 1 à 2 kg.");
      if(level === 1) tips.push("Contrôle la descente sur 2 à 3 secondes : c'est plus efficace et plus sûr.");
    }
  }
  blocks.push({name:"Retour au calme", min: coolMin, items: cooldownFor(zone, coolMin)});
  tips.push("Douleur articulaire vive : on arrête l'exercice. Brûlure musculaire : c'est normal.");
  if(level === 1 && zone !== "mobility") tips.push("2 à 3 séances par semaine suffisent pour progresser, avec un jour de repos entre deux séances intenses.");
  else tips.push("Bois de l'eau pendant la séance et mange une source de protéines dans les heures qui suivent.");
  return {
    minutes, zone, level, equip, format,
    title: `${WORKOUT_ZONES[zone]} · ${minutes} min`,
    meta: [WORKOUT_LEVELS[level], zone === "run" || zone === "mobility" ? "" : WORKOUT_EQUIP[equip], format].filter(Boolean).join(" · "),
    blocks, tips,
  };
}

// Compact text version for the task note (max ~2000 characters).
function workoutAsNote(w){
  const lines = [`🏋️ ${w.title} · ${w.meta}`];
  w.blocks.forEach(b=>{
    lines.push(`\n${b.name} (${b.min} min)${b.note ? " — " + b.note : ""}`);
    b.items.forEach(it=> lines.push(`• ${it.n}${it.d ? " : " + it.d : ""}`));
  });
  lines.push(`\n💡 ${w.tips[0]}`);
  return lines.join("\n").slice(0, 2000);
}
