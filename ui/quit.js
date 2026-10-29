// Sidequest « Arrêter » : tabac, alcool ou autre habitude (fonction bonus).
// Contenu (types, jalons, phrases, boîte à outils) + calculs purs.
// Les jalons santé du tabac reprennent les étapes publiées par l'OMS et
// Tabac Info Service ; ceux de l'alcool restent volontairement prudents.

const QUIT_KINDS = {
  tabac: {label: "Tabac", icon: "🚭", unit: "cigarette", units: "cigarettes", verb: "sans fumer",
          perDayLabel: "Cigarettes par jour (avant)", perDay: 10, unitCost: 0.65,
          costLabel: "Prix d'une cigarette (€) — un paquet de 20 à 13 € = 0,65 €"},
  alcool: {label: "Alcool", icon: "🍷", unit: "verre", units: "verres", verb: "sans alcool",
           perDayLabel: "Verres par jour en moyenne (avant)", perDay: 2, unitCost: 3,
           costLabel: "Prix moyen d'un verre (€)"},
  autre: {label: "Autre habitude", icon: "🎯", unit: "fois", units: "fois", verb: "",
          perDayLabel: "Combien de fois par jour (avant)", perDay: 1, unitCost: 0,
          costLabel: "Ce que ça te coûte à chaque fois (€, facultatif)"},
};

// h = heures depuis l'arrêt
const QUIT_MILESTONES = {
  tabac: [
    {h: 0.34, t: "20 minutes", d: "Ton rythme cardiaque et ta tension artérielle commencent déjà à redescendre."},
    {h: 12, t: "12 heures", d: "Le monoxyde de carbone dans ton sang revient à un niveau normal : ton sang transporte mieux l'oxygène."},
    {h: 48, t: "48 heures", d: "Le goût et l'odorat commencent à s'améliorer."},
    {h: 72, t: "72 heures", d: "La nicotine a quitté ton corps et respirer devient plus facile. C'est souvent le pic du manque : chaque heure tenue compte double."},
    {h: 24 * 14, t: "2 semaines", d: "Ta circulation sanguine et ta fonction pulmonaire s'améliorent (jusqu'à 3 mois)."},
    {h: 24 * 30, t: "1 mois", d: "Toux, fatigue et essoufflement commencent à diminuer, et ça continue pendant les mois suivants."},
    {h: 24 * 90, t: "3 mois", d: "Ta capacité respiratoire a nettement progressé : l'effort physique devient plus facile."},
    {h: 24 * 365, t: "1 an", d: "Ton risque de maladie coronarienne est environ deux fois plus faible que celui d'un fumeur."},
    {h: 24 * 365 * 5, t: "5 ans", d: "Le risque de cancers de la bouche, de la gorge et de l'œsophage est réduit de moitié."},
    {h: 24 * 365 * 10, t: "10 ans", d: "Le risque de cancer du poumon est environ moitié moindre que celui d'un fumeur."},
    {h: 24 * 365 * 15, t: "15 ans", d: "Ton risque de maladie coronarienne rejoint celui d'une personne qui n'a jamais fumé."},
  ],
  alcool: [
    {h: 24, t: "1 jour", d: "Premier jour : bois beaucoup d'eau, ton corps commence à se réhydrater."},
    {h: 72, t: "3 jours", d: "Les premiers jours peuvent être difficiles (sommeil agité, irritabilité) : c'est fréquent et ça passe. Tremblements, sueurs ou confusion : consulte un médecin rapidement."},
    {h: 24 * 7, t: "1 semaine", d: "Le sommeil devient souvent plus réparateur, et l'humeur plus stable."},
    {h: 24 * 14, t: "2 semaines", d: "Chez beaucoup de personnes : moins de reflux et d'irritation de l'estomac, et souvent quelques kilos en moins."},
    {h: 24 * 30, t: "1 mois", d: "Le foie a commencé à éliminer la graisse accumulée ; énergie, concentration et peau s'améliorent souvent."},
    {h: 24 * 90, t: "3 mois", d: "La tension artérielle s'améliore souvent et tu as reconstruit de nouvelles habitudes."},
    {h: 24 * 180, t: "6 mois", d: "Ton corps et ton budget ont profondément changé : regarde le chemin parcouru."},
    {h: 24 * 365, t: "1 an", d: "Une année entière : les risques liés à l'alcool ont nettement baissé et tu as repris le contrôle."},
  ],
  autre: [
    {h: 24, t: "1 jour", d: "Le premier jour est fait : c'est toujours le plus symbolique."},
    {h: 72, t: "3 jours", d: "Les premiers jours sont souvent les plus durs. Tu les as passés."},
    {h: 24 * 7, t: "1 semaine", d: "Une semaine complète : la nouvelle habitude commence à s'installer."},
    {h: 24 * 21, t: "3 semaines", d: "Trois semaines : les automatismes commencent vraiment à changer."},
    {h: 24 * 30, t: "1 mois", d: "Un mois : ce n'est plus un effort ponctuel, c'est un nouveau mode de vie."},
    {h: 24 * 90, t: "3 mois", d: "Trois mois : la plupart des envies sont devenues rares."},
    {h: 24 * 365, t: "1 an", d: "Un an. Prends le temps d'être fier de toi."},
  ],
};

// Phrases originales (pas de fausses citations attribuées à des célébrités).
const QUIT_PHRASES = [
  "Chaque envie à laquelle tu ne cèdes pas affaiblit la suivante.",
  "Tu n'as pas besoin d'arrêter pour toujours aujourd'hui. Juste pour aujourd'hui.",
  "Une envie, c'est une vague : elle monte, elle culmine, et elle redescend toujours.",
  "Tu ne te prives de rien : tu reprends ce qui t'appartient.",
  "Le plus dur n'est pas devant toi, il est déjà derrière.",
  "Ton corps te remercie déjà, même si tu ne le sens pas encore.",
  "Un écart n'efface pas tes progrès. Abandonner, si.",
  "Tu es plus fort qu'une habitude.",
  "Chaque jour tenu est une preuve que tu peux en tenir un autre.",
  "La version de toi dans un an te dit merci pour aujourd'hui.",
  "Ce n'est pas de la volonté qu'il faut, c'est de la constance. Et tu en as.",
  "Tu ne perds rien. Tu gagnes du souffle, de l'argent et du temps.",
  "Respire. Cette envie ne commande rien.",
  "Les premiers jours sont un passage, pas une destination.",
  "Tu as déjà fait le plus difficile : décider.",
  "Remplace le « je ne peux pas » par « je ne veux plus ».",
  "Ton argent économisé a un nom : choisis ce que tu vas t'offrir.",
  "Ce que tu construis aujourd'hui vaut plus que ce que l'envie te promet.",
  "Personne ne regrette d'avoir tenu bon.",
  "Tu n'es pas en manque de quelque chose : tu es en train de guérir.",
  "Une petite victoire par jour, c'est une grande victoire par an.",
  "L'envie passe. Ta fierté reste.",
  "Tu te libères d'une dépendance, pas d'un plaisir.",
  "Chaque matin sans, c'est un matin un peu plus libre.",
  "Le doute est normal. Il ne décide pas pour toi.",
  "Tu mérites de te sentir bien sans rien.",
  "Ta remontada, c'est maintenant.",
  "Regarde ton compteur : chaque minute est à toi.",
  "Tu ne recommences pas de zéro après un écart : tu repars de l'expérience.",
  "La fatigue, le stress, l'ennui : ce sont des déclencheurs, pas des ordres.",
  "Dans dix minutes, cette envie ne sera plus qu'un souvenir.",
  "Tu peux avoir envie et dire non. Les deux en même temps.",
  "Sois aussi patient avec toi que tu le serais avec un ami.",
  "Chaque refus est un vote pour la personne que tu veux devenir.",
  "Tu n'as rien à prouver aux autres, seulement à tenir ta promesse à toi-même.",
  "Le confort de l'habitude est un mirage ; la liberté est réelle.",
  "Aujourd'hui compte. Et demain comptera encore plus.",
  "Garde le cap : les bénéfices arrivent même quand on ne les voit pas.",
  "Tu as survécu à 100 % de tes envies jusqu'ici.",
  "Fais-le pour ton souffle, ton sommeil, ton portefeuille et tes proches.",
  "Le meilleur moment pour arrêter, c'était hier. Le deuxième meilleur, c'est maintenant.",
  "Un pas à la fois. Une heure à la fois s'il le faut.",
  "Tu n'es pas seul : des milliers de personnes ont réussi exactement ce que tu fais.",
  "L'envie te parle fort, mais elle ment.",
  "Ce soir, tu pourras te dire : j'ai tenu.",
  "Prends soin de toi comme de quelqu'un que tu aimes.",
  "Ta santé ne se négocie pas avec une envie de cinq minutes.",
  "La liberté, c'est de ne plus avoir à y penser. Tu t'en approches chaque jour.",
  "Tu as choisi la difficulté de l'arrêt plutôt que celle de la dépendance. Bon choix.",
  "Continue. Tu es exactement là où tu dois être.",
];

// Idées pour traverser une envie (on en tire 3 au hasard)
const QUIT_DISTRACTIONS = [
  "Bois un grand verre d'eau fraîche, lentement.",
  "Sors marcher 5 minutes, même juste devant chez toi.",
  "Mâche un chewing-gum sans sucre ou croque une pomme.",
  "Envoie un message à quelqu'un que tu aimes bien.",
  "Fais 15 squats ou 10 pompes : l'effort coupe l'envie net.",
  "Brosse-toi les dents : le goût frais aide à tenir.",
  "Lance une chanson que tu adores et écoute-la en entier.",
  "Range un tiroir ou une étagère pendant 5 minutes.",
  "Prends une douche ou passe-toi de l'eau froide sur le visage.",
  "Change de pièce : l'envie est souvent liée à un endroit.",
  "Écris ce que tu ressens en une phrase : nommer l'envie la rend plus petite.",
  "Joue à un petit jeu sur ton téléphone pendant 3 minutes.",
  "Prépare-toi une boisson chaude (thé, tisane) et bois-la doucement.",
  "Relis tes raisons d'arrêter, une par une.",
  "Calcule ce que tu vas t'offrir avec l'argent économisé ce mois-ci.",
  "Fais un mot croisé, un sudoku ou un puzzle rapide.",
  "Étire-toi : bras au-dessus de la tête, puis penche-toi doucement en avant.",
  "Occupe tes mains : stylo, balle anti-stress, élastique.",
];

// Boîte à outils : sections affichées en accordéon (k = types concernés)
const QUIT_TOOLBOX = [
  {title: "🗓️ Bien préparer l'arrêt", k: ["tabac", "alcool", "autre"], items: [
    "Choisis une date dans les 2 semaines, idéalement une période calme (pas la veille d'un examen ou d'une grosse échéance).",
    "Écris tes raisons d'arrêter, avec tes mots. Relis-les souvent : c'est ton meilleur carburant.",
    "Repère tes déclencheurs : café, pause, apéro, stress, ennui, fin de repas, certaines personnes ou certains lieux.",
    "Prépare une réponse pour chaque déclencheur (voir « Remplacer les rituels »).",
    "Préviens deux ou trois proches : leur soutien aide vraiment, et ça t'engage.",
    "Fais le vide : cigarettes, briquets, cendriers, bouteilles. Ce qui n'est pas à portée de main ne tente pas.",
  ]},
  {title: "🌊 Gérer une envie (la méthode des 4 R)", k: ["tabac", "alcool", "autre"], items: [
    "Retarder : dis-toi « j'attends 10 minutes ». Une envie dure rarement plus de quelques minutes.",
    "Respirer : inspire 5 secondes, expire 5 secondes, pendant 2 minutes (le bouton « J'ai une envie » te guide).",
    "Réhydrater : un grand verre d'eau, lentement.",
    "Remplacer : bouge, occupe tes mains, change de pièce, appelle quelqu'un.",
    "Note chaque envie surmontée dans l'app : tu verras qu'elles deviennent plus rares et moins fortes.",
  ]},
  {title: "🔁 Remplacer les rituels", k: ["tabac", "alcool", "autre"], items: [
    "Café + cigarette : change de tasse, de lieu ou passe au thé pendant quelques semaines.",
    "Pause au travail : marche 5 minutes ou fais la pause avec un collègue non-fumeur.",
    "Fin de repas : lève-toi tout de suite, brosse-toi les dents ou mange un fruit.",
    "Apéro : prépare une boisson « à toi » (eau pétillante citron-menthe, kombucha, bière sans alcool, mocktail).",
    "Le soir pour décompresser : une douche chaude, une série, une balade, du sport léger.",
    "Garde tes mains occupées : stylo, balle anti-stress, élastique, jeu sur téléphone.",
  ]},
  {title: "⚠️ Situations à risque", k: ["tabac", "alcool", "autre"], items: [
    "Soirées : arrive avec ta propre boisson, garde un verre plein en main, prévois une heure de départ.",
    "Stress : prends 2 minutes de respiration avant de réagir. L'envie promet un soulagement qu'elle ne tient pas.",
    "Fatigue et faim augmentent les envies : dors, mange à heures régulières.",
    "Entourage qui consomme : dis simplement « j'ai arrêté », pas besoin de te justifier.",
    "Une phrase prête à l'emploi : « Non merci, je suis en pleine remontada. »",
  ]},
  {title: "🤝 Après un écart", k: ["tabac", "alcool", "autre"], items: [
    "Un écart n'est pas un échec. Ce qui compte, c'est de reprendre tout de suite.",
    "Note-le dans l'app sans culpabiliser : tes jours et tes économies ne disparaissent pas.",
    "Demande-toi ce qui s'est passé (lieu, émotion, personne) et prépare une parade pour la prochaine fois.",
    "Évite le « foutu pour foutu » : une cigarette ou un verre ne doit pas devenir une journée entière.",
    "La plupart des personnes qui réussissent ont fait plusieurs tentatives. Chacune t'apprend quelque chose.",
  ]},
  {title: "🚭 Spécial tabac", k: ["tabac"], items: [
    "Les substituts nicotiniques (patchs, gommes, pastilles) augmentent nettement les chances de réussite, surtout bien dosés. Ils sont remboursés sur prescription : parles-en à ton médecin, ou demande conseil à ton pharmacien.",
    "Le manque de nicotine culmine en général entre le 2e et le 4e jour, puis diminue nettement.",
    "Les envies liées aux habitudes (café, pause) durent plus longtemps que le manque physique : c'est là que les rituels de remplacement font la différence.",
    "Tabac Info Service : 39 89 (appel gratuit + coaching) et l'appli Tabac Info Service.",
  ]},
  {title: "🍷 Spécial alcool", k: ["alcool"], items: [
    "Si tu bois beaucoup chaque jour, n'arrête pas d'un coup sans avis médical : un sevrage brutal peut être dangereux (tremblements, sueurs, convulsions). Ton médecin peut t'accompagner.",
    "Tu peux aussi commencer par réduire : repères de santé publique, pas plus de 10 verres par semaine, pas plus de 2 par jour, et des jours sans alcool chaque semaine.",
    "Alcool Info Service : 0 980 980 930 (appel anonyme et non surtaxé, 7 j/7) et alcool-info-service.fr.",
    "Les associations d'entraide (Alcooliques Anonymes, Vie Libre, Croix Bleue…) proposent des groupes de parole, souvent près de chez toi.",
  ]},
  {title: "🩺 Signes à surveiller (alcool)", k: ["alcool"], items: [
    "Signes de dépendance physique, à repérer AVANT d'arrêter : mains qui tremblent le matin, sueurs, nausées au réveil, besoin de boire le matin pour aller mieux, anxiété ou cœur qui s'emballe après quelques heures sans boire. Si c'est ton cas : vois un médecin avant d'arrêter.",
    "De 6 à 24 h après l'arrêt : tremblements, sueurs, anxiété, insomnie, nausées, cœur rapide. C'est le sevrage, il demande un avis médical.",
    "Entre 12 et 48 h : risque de convulsions.",
    "Entre 48 et 72 h : risque de delirium tremens (confusion, hallucinations, fièvre, agitation intense). C'est une urgence vitale.",
    "Appelle le 15 ou le 112 immédiatement en cas de convulsion, d'hallucinations, de confusion, de forte fièvre ou de tremblements violents.",
    "Un sevrage accompagné médicalement (parfois sans hospitalisation) est sûr et efficace : il ne faut pas hésiter à le demander.",
  ]},
  {title: "🩺 Signes à surveiller (tabac)", k: ["tabac"], items: [
    "Arrêter brutalement le tabac n'est pas dangereux physiquement : irritabilité, anxiété, difficultés de concentration, appétit en hausse, sommeil perturbé, parfois une toux passagère.",
    "Ces symptômes culminent entre le 2e et le 4e jour, puis s'estompent en 2 à 4 semaines.",
    "Si tu prends un traitement au long cours, préviens ton médecin : arrêter de fumer modifie le taux sanguin de certains médicaments (certains antipsychotiques comme la clozapine ou l'olanzapine, la théophylline…).",
    "Si un moral bas s'installe ou s'aggrave pendant plusieurs semaines, parles-en à un professionnel.",
  ]},
  {title: "🆘 Aide et urgences", k: ["tabac", "alcool", "autre"], items: [
    "Ton médecin traitant est le meilleur point de départ pour un accompagnement adapté.",
    "Tabac Info Service : 39 89 · Alcool Info Service : 0 980 980 930 · Drogues Info Service : 0 800 23 13 13 (gratuit).",
    "En cas de malaise, de confusion ou de signes inquiétants : appelle le 15 (SAMU) ou le 112.",
    "Si tu te sens au bout du rouleau : 3114 (prévention du suicide, gratuit, 24 h/24).",
  ]},
];

// ---------- calculs ----------
const QUIT_DAY_MS = 86400000;

// q : {kind, start (ISO), perDay, unitCost, lapses: [{at ISO, note}], cravings: n}
function quitStats(q, now){
  now = now || Date.now();
  const start = new Date(q.start).getTime();
  const elapsedMs = Math.max(0, now - start);
  const lapses = (q.lapses || []).map(l=> new Date(l.at).getTime()).filter(t=> t >= start && t <= now).sort((a,b)=> a - b);
  const streakStart = lapses.length ? lapses[lapses.length - 1] : start;
  const streakMs = Math.max(0, now - streakStart);
  const perDay = Math.max(0, Number(q.perDay) || 0);
  const unitCost = Math.max(0, Number(q.unitCost) || 0);
  // each lapse counts as one "lost" day of avoided units (simple and honest)
  const effectiveDays = Math.max(0, elapsedMs / QUIT_DAY_MS - lapses.length);
  const avoided = Math.floor(effectiveDays * perDay);
  return {
    elapsedMs, streakMs, lapses: lapses.length,
    days: Math.floor(elapsedMs / QUIT_DAY_MS),
    streakDays: Math.floor(streakMs / QUIT_DAY_MS),
    avoided,
    saved: Math.round(effectiveDays * perDay * unitCost * 100) / 100,
    cravings: Number(q.cravings) || 0,
    hours: elapsedMs / 3600000,
    streakHours: streakMs / 3600000,
  };
}

// Milestones based on the current streak: reached ones + the next with its progress
function quitMilestones(q, now){
  const s = quitStats(q, now);
  const list = QUIT_MILESTONES[q.kind] || QUIT_MILESTONES.autre;
  const reached = list.filter(m=> s.streakHours >= m.h);
  const next = list.find(m=> s.streakHours < m.h) || null;
  const prevH = reached.length ? reached[reached.length - 1].h : 0;
  const progress = next ? Math.min(1, (s.streakHours - prevH) / (next.h - prevH)) : 1;
  return {list, reached, next, progress};
}

function fmtQuitDuration(ms){
  const min = Math.floor(ms / 60000);
  const d = Math.floor(min / 1440), h = Math.floor((min % 1440) / 60), m = min % 60;
  if(d >= 1) return `${d} j ${h} h`;
  if(h >= 1) return `${h} h ${String(m).padStart(2, "0")} min`;
  return `${m} min`;
}

function quitPhraseOfDay(dateKey, offset){
  let hash = 0;
  for(const ch of String(dateKey) + (offset || "")) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return QUIT_PHRASES[hash % QUIT_PHRASES.length];
}

// ---------- plan in the planning: supportive routines ----------
// at: "risk" = relative to the risky time (offset in minutes), or a fixed "HH:MM"
// days: "risk" = the risky days chosen by the user, "all", or a list (0 = Sunday)
const QUIT_PLAN = {
  alcool: [
    {id:"drink", on:true, at:"risk", offset:-15, dur:15, days:"risk", title:"🍹 Moment à risque : ta boisson sans alcool",
     notes:"Prépare-la AVANT que l'envie arrive : eau pétillante citron-menthe, kombucha, bière ou vin sans alcool, mocktail. Garde ton verre plein en main, ça coupe court aux « tu bois quoi ? »."},
    {id:"move", on:true, at:"risk", offset:0, dur:15, days:"risk", title:"🚶 Casser le rituel : sortir 10 min ou bouger",
     notes:"Marche, douche, sport léger, appel à un ami : change de pièce et d'activité au moment où l'apéro commençait. Envie trop forte ? Ouvre « J'ai une envie » (menu ⋯ ou Ctrl+K)."},
    {id:"review", on:true, at:"21:30", dur:10, days:"all", title:"🌙 Bilan du soir sans alcool",
     notes:"Clôture ta journée : coche « sans alcool » ou note l'écart, et écris ce qui t'a aidé. 5 minutes qui renforcent tout le reste."},
    {id:"sport", on:true, at:"risk", offset:-75, dur:45, days:[1, 3, 5], title:"🏃 Sport doux",
     notes:"Le sport fait baisser le stress, réduit les envies et améliore le sommeil, souvent perturbé les premières semaines sans alcool."},
    {id:"shop", on:true, at:"11:00", dur:30, days:[6], title:"🛒 Courses sans alcool",
     notes:"Liste : eaux pétillantes, sirops, citrons, menthe, bières et vins sans alcool. N'achète pas d'alcool « pour les invités » : ce qui n'est pas à la maison ne tente pas."},
    {id:"call", on:false, at:"18:00", dur:20, days:[0], title:"📞 Appeler un proche ou un groupe de soutien",
     notes:"Raconte où tu en es à quelqu'un qui te soutient. Besoin d'aide ? Alcool Info Service : 0 980 980 930 (anonyme, 7 j/7)."},
    {id:"reward", on:false, at:"16:00", dur:30, days:[0], title:"🎁 Me faire plaisir avec l'argent économisé",
     notes:"Regarde ton compteur d'économies et offre-toi quelque chose : c'est ta récompense, tu l'as méritée."},
  ],
  tabac: [
    {id:"coffee", on:true, at:"08:30", dur:10, days:"all", title:"☕ Café sans cigarette (change de place)",
     notes:"Change de tasse ou de pièce, ou passe au thé quelques semaines : le café-cigarette est un des rituels les plus tenaces."},
    {id:"walk", on:true, at:"13:15", dur:10, days:"all", title:"🚶 Après le repas : 10 min de marche",
     notes:"La fin du repas est un gros déclencheur. Lève-toi tout de suite, marche ou brosse-toi les dents."},
    {id:"risk", on:true, at:"risk", offset:0, dur:5, days:"risk", title:"💨 Moment à risque : respiration + grand verre d'eau",
     notes:"Ouvre « J'ai une envie » (menu ⋯ ou Ctrl+K) : 3 minutes de respiration guidée et l'envie redescend."},
    {id:"review", on:true, at:"21:30", dur:10, days:"all", title:"🌙 Bilan du soir sans tabac",
     notes:"Clôture ta journée et note tes envies surmontées. Chaque soir tenu compte."},
    {id:"sport", on:false, at:"18:00", dur:40, days:[1, 3, 5], title:"🏃 Sport doux",
     notes:"Le souffle revient vite après l'arrêt : le sport le rend visible, et il aide à gérer le stress et l'appétit."},
    {id:"reward", on:false, at:"16:00", dur:30, days:[0], title:"🎁 Me faire plaisir avec l'argent économisé",
     notes:"Regarde ton compteur d'économies et offre-toi quelque chose : c'est ta récompense."},
  ],
  autre: [
    {id:"risk", on:true, at:"risk", offset:-10, dur:15, days:"risk", title:"🎯 Moment à risque : activité de remplacement",
     notes:"Prévois une activité à la place de l'habitude : marche, appel, lecture, rangement. Envie trop forte ? Ouvre « J'ai une envie »."},
    {id:"review", on:true, at:"21:30", dur:10, days:"all", title:"🌙 Bilan du soir",
     notes:"Clôture ta journée et note si tu as tenu. Ce qui a aidé, ce qui a été dur."},
    {id:"reward", on:false, at:"16:00", dur:30, days:[0], title:"🎁 Une récompense pour la semaine tenue",
     notes:"Fais-toi plaisir : chaque semaine tenue mérite d'être fêtée."},
  ],
};
const QUIT_RISK_DEFAULT = {alcool: {time: "18:30", days: [5, 6]}, tabac: {time: "10:30", days: [0, 1, 2, 3, 4, 5, 6]}, autre: {time: "20:00", days: [0, 1, 2, 3, 4, 5, 6]}};

// Resolve a plan item into a routine definition {title, start, duration, days, notes}
function quitPlanRoutine(item, riskTime, riskDays){
  const [h, m] = riskTime.split(":").map(Number);
  let start = item.at === "risk" ? h * 60 + m + (item.offset || 0) : Number(item.at.slice(0, 2)) * 60 + Number(item.at.slice(3));
  start = Math.max(6 * 60, Math.min(23 * 60 + 45 - item.dur, start));
  const days = item.days === "risk" ? riskDays.slice() : item.days === "all" ? [0, 1, 2, 3, 4, 5, 6] : item.days.slice();
  const p2 = n=> String(n).padStart(2, "0");
  return {title: item.title, start: `${p2(Math.floor(start / 60))}:${p2(start % 60)}`, duration: item.dur, days, notes: item.notes};
}
