"""Builds ui/recipes_world.js: world-cuisine recipes that complete ui/recipes.js
(hand-written) up to 1000 recipes, ~10 % of them cheat meals.

How it works: each "base dish" below is a real recipe with its own sauce,
spices and steps; it is declined with ingredients that make sense for it
(proteins, vegetables, fruits...). Steps are built from each ingredient's own
cooking instructions, so a tofu curry and a shrimp curry are both correct.

Run:  python scripts/build_recipes.py   (deterministic: same output each time)
"""
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ui", "recipes_world.js")
TARGET_TOTAL = 1000
rng = random.Random(1000)

# ---------------------------------------------------------------- ingredients
# a: "au poulet" form for titles · ing: ingredient line (1 person)
# cook: how to cook it in a pan/wok · t: minutes · prot/vege flags
P = {
    "poulet": dict(n="poulet", a="au poulet", ing="150 g de blanc de poulet", cook="Coupe le poulet en morceaux et fais-le dorer 6 à 7 min à feu moyen-vif", t=8, prot=True, vege=False, fish=False),
    "dinde": dict(n="dinde", a="à la dinde", ing="150 g d'escalope de dinde", cook="Coupe la dinde en lanières et saisis-la 5 à 6 min", t=6, prot=True, vege=False, fish=False),
    "boeuf": dict(n="bœuf", a="au bœuf", ing="130 g de bœuf maigre (rumsteck)", cook="Coupe le bœuf en fines lanières et saisis-le 2 à 3 min à feu vif", t=4, prot=True, vege=False, fish=False),
    "porc": dict(n="porc", a="au porc", ing="130 g de filet mignon de porc", cook="Coupe le porc en fines tranches et fais-le cuire 4 à 5 min", t=5, prot=True, vege=False, fish=False),
    "saumon": dict(n="saumon", a="au saumon", ing="1 pavé de saumon (130 g)", cook="Coupe le saumon en cubes et fais-le cuire 4 min sans trop remuer", t=5, prot=True, vege=False, fish=True),
    "cabillaud": dict(n="cabillaud", a="au cabillaud", ing="150 g de dos de cabillaud", cook="Ajoute le cabillaud en gros morceaux et laisse cuire 5 min sans remuer", t=6, prot=True, vege=False, fish=True),
    "crevettes": dict(n="crevettes", a="aux crevettes", ing="150 g de crevettes décortiquées", cook="Saisis les crevettes 2 à 3 min, jusqu'à ce qu'elles deviennent roses", t=3, prot=True, vege=False, fish=True),
    "tofu": dict(n="tofu", a="au tofu", ing="150 g de tofu ferme", cook="Coupe le tofu en dés, sèche-le dans un torchon et fais-le dorer 6 à 8 min", t=8, prot=True, vege=True, fish=False),
    "tempeh": dict(n="tempeh", a="au tempeh", ing="120 g de tempeh", cook="Coupe le tempeh en tranches et dore-le 3 min par face", t=6, prot=True, vege=True, fish=False),
    "poischiches": dict(n="pois chiches", a="aux pois chiches", ing="150 g de pois chiches cuits", cook="Rince les pois chiches et fais-les revenir 4 min pour les colorer", t=4, prot=True, vege=True, fish=False),
    "lentilles": dict(n="lentilles", a="aux lentilles", ing="150 g de lentilles cuites", cook="Ajoute les lentilles et réchauffe-les 3 min", t=3, prot=True, vege=True, fish=False),
    "haricotsrouges": dict(n="haricots rouges", a="aux haricots rouges", ing="150 g de haricots rouges cuits", cook="Rince les haricots rouges et réchauffe-les 3 min", t=3, prot=True, vege=True, fish=False),
    "halloumi": dict(n="halloumi", a="à l'halloumi", ing="80 g d'halloumi", cook="Coupe l'halloumi en tranches et grille-le 2 min par face", t=4, prot=True, vege=True, fish=False),
    "oeuf": dict(n="œuf", a="à l'œuf", ing="2 œufs", cook="Fais cuire les œufs mollets : 6 min dans l'eau bouillante, puis eau froide", t=7, prot=True, vege=True, fish=False),
    "thon": dict(n="thon", a="au thon", ing="1 boîte de thon au naturel", cook="Égoutte et émiette le thon", t=0, prot=True, vege=False, fish=True),
}
# the: with article, for steps · prep: how to cut it
V = {
    "courgette": dict(n="courgette", the="la courgette", ing="1 courgette", prep="Coupe la courgette en demi-rondelles"),
    "brocoli": dict(n="brocoli", the="le brocoli", ing="150 g de brocoli", prep="Détaille le brocoli en petites fleurettes"),
    "poivron": dict(n="poivron", the="le poivron", ing="1 poivron", prep="Coupe le poivron en lanières"),
    "epinards": dict(n="épinards", the="les épinards", ing="2 poignées d'épinards", prep="Lave les épinards", late=True),
    "champignons": dict(n="champignons", the="les champignons", ing="150 g de champignons", prep="Émince les champignons"),
    "haricotsverts": dict(n="haricots verts", the="les haricots verts", ing="150 g de haricots verts", prep="Coupe les haricots verts en tronçons"),
    "choufleur": dict(n="chou-fleur", the="le chou-fleur", ing="1/4 de chou-fleur", prep="Détaille le chou-fleur en petites fleurettes"),
    "carotte": dict(n="carotte", the="les carottes", ing="2 carottes", prep="Coupe les carottes en fins bâtonnets"),
    "aubergine": dict(n="aubergine", the="l'aubergine", ing="1/2 aubergine", prep="Coupe l'aubergine en dés"),
    "poisgourmands": dict(n="pois gourmands", the="les pois gourmands", ing="1 poignée de pois gourmands", prep="Équeute les pois gourmands"),
    "chou": dict(n="chou kale", the="le chou kale", ing="2 poignées de chou kale", prep="Retire les côtes du kale et cisèle les feuilles", late=True),
    "petitspois": dict(n="petits pois", the="les petits pois", ing="100 g de petits pois", prep="Sors les petits pois du congélateur", late=True),
    "butternut": dict(n="butternut", the="la butternut", ing="200 g de butternut", prep="Coupe la butternut en petits dés"),
    "poireau": dict(n="poireau", the="le poireau", ing="1 poireau", prep="Émince finement le poireau"),
    "asperges": dict(n="asperges", the="les asperges", ing="6 asperges vertes", prep="Coupe les asperges en tronçons"),
    "pakchoi": dict(n="pak-choï", the="le pak-choï", ing="1 pak-choï", prep="Coupe le pak-choï en quatre dans la longueur"),
    "patatedouce": dict(n="patate douce", the="la patate douce", ing="1 petite patate douce", prep="Coupe la patate douce en petits cubes"),
    "fenouil": dict(n="fenouil", the="le fenouil", ing="1/2 bulbe de fenouil", prep="Émince finement le fenouil"),
}
BASE = {
    "riz": dict(n="riz basmati", ing="60 g de riz basmati", step="Fais cuire le riz (environ 12 min)", t=12),
    "rizjasmin": dict(n="riz jasmin", ing="60 g de riz jasmin", step="Fais cuire le riz jasmin (environ 12 min)", t=12),
    "rizcomplet": dict(n="riz complet", ing="60 g de riz complet", step="Fais cuire le riz complet (environ 20 min)", t=20),
    "quinoa": dict(n="quinoa", ing="60 g de quinoa", step="Rince le quinoa et fais-le cuire 12 min", t=12),
    "nouillesriz": dict(n="nouilles de riz", ing="70 g de nouilles de riz", step="Fais tremper les nouilles de riz selon le paquet", t=8),
    "soba": dict(n="nouilles soba", ing="70 g de nouilles soba", step="Fais cuire les nouilles soba 4 min et rince-les à l'eau froide", t=5),
    "boulgour": dict(n="boulgour", ing="60 g de boulgour", step="Couvre le boulgour d'eau bouillante et laisse gonfler 10 min", t=10),
    "semoule": dict(n="semoule complète", ing="60 g de semoule complète", step="Verse le même volume d'eau bouillante sur la semoule et couvre 5 min", t=5),
    "pates": dict(n="pâtes complètes", ing="80 g de pâtes complètes", step="Fais cuire les pâtes al dente", t=10),
}

# ---------------------------------------------------------------- base dishes
# Each dish: name pattern, cuisine, emoji, meals, which proteins/veg/bases fit,
# fixed ingredients, steps (with {p}, {v}, {b} hooks), light flag, how many to keep.
DISHES = [
    dict(t="Curry vert thaï {pa} et {vn}", c="Thaïlandaise", e="🍛", m=["dej", "din"], P=["poulet", "crevettes", "tofu", "cabillaud", "dinde"], V=["courgette", "poivron", "brocoli", "aubergine", "poisgourmands", "haricotsverts"], B=["rizjasmin"],
         fix=["1 c. à soupe de pâte de curry vert", "150 ml de lait de coco léger", "1 c. à café de sauce nuoc-mâm (ou soja)", "Quelques feuilles de basilic thaï ou coriandre"],
         steps=["{b}.", "{vp}.", "{p}, puis réserve.", "Dans la même poêle, fais revenir la pâte de curry 1 min, ajoute le lait de coco et {vthe}, laisse mijoter 8 min.", "Remets la protéine 2 min, assaisonne au nuoc-mâm et parsème de basilic. Sers avec le riz."], tm=8, n=30),
    dict(t="Curry rouge {pa} et {vn}", c="Thaïlandaise", e="🌶️", m=["din"], P=["poulet", "crevettes", "tofu", "boeuf"], V=["butternut", "poivron", "aubergine", "haricotsverts", "patatedouce"], B=["rizjasmin"],
         fix=["1 c. à soupe de pâte de curry rouge", "150 ml de lait de coco léger", "1/2 citron vert", "Coriandre"],
         steps=["{b}.", "{vp}.", "Fais revenir la pâte de curry 1 min, ajoute le lait de coco et {vthe}, laisse cuire 8 min.", "{p}, puis ajoute la protéine à la sauce.", "Finis avec le citron vert et la coriandre."], tm=10, n=20),
    dict(t="Curry indien {pa} et {vn}", c="Indienne", e="🍛", m=["dej", "din"], P=["poulet", "poischiches", "lentilles", "tofu", "crevettes"], V=["epinards", "choufleur", "petitspois", "patatedouce", "aubergine"], B=["riz"],
         fix=["1/2 oignon", "1 gousse d'ail", "1 c. à café de garam masala", "1/2 c. à café de curcuma", "150 g de tomates concassées", "2 c. à soupe de yaourt nature"],
         steps=["{b}.", "Fais revenir l'oignon et l'ail émincés avec les épices 2 min.", "{vp}, puis ajoute {vthe} et les tomates, laisse mijoter 10 min.", "{p}, puis ajoute la protéine à la sauce.", "Hors du feu, ajoute le yaourt et sers avec le riz."], tm=15, n=25),
    dict(t="Tikka masala léger {pa}", c="Indienne", e="🧡", m=["din"], P=["poulet", "tofu", "poischiches", "crevettes", "dinde"], V=["epinards"], B=["riz"],
         fix=["3 c. à soupe de yaourt nature", "1 c. à café d'épices tikka masala", "150 g de coulis de tomate", "1/2 oignon", "Coriandre"],
         steps=["{b}.", "Mélange la protéine avec 1 c. à soupe de yaourt et les épices, laisse mariner 10 min.", "{p}.", "Ajoute l'oignon émincé et le coulis, laisse mijoter 8 min.", "Ajoute le reste du yaourt et la coriandre hors du feu."], tm=20, n=5),
    dict(t="Wok de {bn} {pa}, {vn} et soja-gingembre", c="Chinoise", e="🥢", m=["dej", "din"], P=["poulet", "boeuf", "crevettes", "tofu", "porc", "tempeh"], V=["brocoli", "poivron", "poisgourmands", "pakchoi", "carotte", "champignons"], B=["nouillesriz", "riz", "soba"],
         fix=["1 c. à soupe de sauce soja", "1 c. à café de gingembre râpé", "1 gousse d'ail", "1 c. à café d'huile de sésame", "1 oignon nouveau"],
         steps=["{b}.", "{vp}.", "{p} dans le wok bien chaud, puis réserve.", "Saute {vthe} 4 min à feu vif avec l'ail et le gingembre.", "Remets la protéine, ajoute la base, le soja et l'huile de sésame, mélange 1 min. Parsème d'oignon nouveau."], tm=6, n=60),
    dict(t="Bowl teriyaki {pa}, {vn} et {bn}", c="Japonaise", e="🍱", m=["dej", "din"], P=["poulet", "saumon", "tofu", "boeuf"], V=["brocoli", "carotte", "poisgourmands", "courgette", "pakchoi"], B=["riz", "rizcomplet"],
         fix=["1 c. à soupe de sauce soja", "1 c. à café de miel", "1 c. à café de vinaigre de riz", "1 c. à café de graines de sésame"],
         steps=["{b}.", "{vp}, puis fais cuire {vthe} 4 min à la vapeur ou à la poêle.", "{p}.", "Ajoute soja, miel et vinaigre, laisse caraméliser 1 min en enrobant bien.", "Dresse sur la base avec les légumes et parsème de sésame."], tm=6, n=40),
    dict(t="Poke bowl {pa}", c="Hawaïenne", e="🍣", m=["dej"], P=["saumon", "thon", "tofu", "crevettes"], V=["carotte"], B=["riz", "quinoa"],
         fix=["1/2 avocat", "1/4 de concombre", "1 poignée d'edamame", "1 c. à soupe de sauce soja", "1 c. à café de sésame", "1 c. à café de vinaigre de riz"],
         steps=["{b}, puis assaisonne-le avec le vinaigre.", "Coupe l'avocat et le concombre en dés, râpe la carotte.", "Prépare la protéine : cubes crus pour un saumon qualité sashimi, sinon {plower}.", "Dispose tout sur la base, arrose de soja et parsème de sésame."], tm=5, light=False, n=8),
    dict(t="Buddha bowl {bn} {pa}, {vn} et tahini", c="Végétale du monde", e="🥗", m=["dej"], P=["poischiches", "tofu", "lentilles", "oeuf", "tempeh", "halloumi"], V=["patatedouce", "brocoli", "chou", "carotte", "butternut"], B=["quinoa", "boulgour", "riz"],
         fix=["1/2 avocat", "1 poignée de jeunes pousses", "1 c. à soupe de tahini", "Jus d'1/2 citron", "1 c. à soupe de graines (courge ou tournesol)"],
         steps=["{b}.", "{vp}, puis fais rôtir {vthe} 15 min à 200 °C (ou 6 min à la poêle).", "{p}.", "Délaye le tahini avec le citron et un peu d'eau.", "Assemble le bol et arrose de sauce tahini."], tm=15, n=55),
    dict(t="Tacos {pa}, {vn} et salsa", c="Mexicaine", e="🌮", m=["din"], P=["poulet", "boeuf", "crevettes", "haricotsrouges", "dinde", "cabillaud", "tofu"], V=["poivron", "courgette", "champignons"], B=[],
         fix=["2 petites tortillas de maïs", "1 tomate", "1/4 d'oignon rouge", "1/2 citron vert", "Coriandre", "1/2 c. à café de paprika fumé"],
         steps=["{vp}.", "{p} avec le paprika et {vthe}.", "Coupe la tomate et l'oignon en petits dés, ajoute citron vert et coriandre pour la salsa.", "Chauffe les tortillas 30 s par face et garnis-les."], tm=8, n=21),
    dict(t="Burrito bowl {pa} et {bn}", c="Mexicaine", e="🌯", m=["dej", "din"], P=["poulet", "boeuf", "haricotsrouges", "crevettes", "tofu"], V=["poivron"], B=["rizcomplet", "riz"],
         fix=["50 g de maïs", "1/2 avocat", "1 tomate", "2 c. à soupe de yaourt grec", "1/2 citron vert", "1/2 c. à café de cumin"],
         steps=["{b}.", "{p} avec le cumin et le poivron en lanières.", "Écrase l'avocat avec le citron vert, coupe la tomate en dés.", "Assemble le bol : riz, protéine, maïs, tomate, avocat et yaourt."], tm=8, n=10),
    dict(t="Fajitas {pa} et {vn}", c="Tex-Mex", e="🫑", m=["din"], P=["poulet", "boeuf", "crevettes", "tofu", "dinde"], V=["poivron", "courgette", "champignons"], B=[],
         fix=["2 tortillas de blé complètes", "1/2 oignon", "1/2 c. à café d'épices mexicaines", "2 c. à soupe de yaourt grec", "1/2 citron vert"],
         steps=["{vp}, émince l'oignon.", "{p} avec les épices.", "Ajoute l'oignon et {vthe}, saute 5 min à feu vif.", "Chauffe les tortillas, garnis-les et ajoute le yaourt citronné."], tm=8, n=15),
    dict(t="Salade grecque {pa}", c="Grecque", e="🫒", m=["dej"], P=["poulet", "poischiches", "crevettes", "halloumi", "thon"], V=["poivron"], B=[],
         fix=["1 tomate", "1/2 concombre", "1/4 d'oignon rouge", "40 g de feta", "Quelques olives noires", "Origan", "1 c. à soupe d'huile d'olive"],
         steps=["{p}.", "Coupe tomate, concombre et poivron en gros dés, l'oignon en lamelles.", "Ajoute olives, feta et origan.", "Assaisonne d'huile d'olive et dépose la protéine dessus."], tm=5, light=True, n=6),
    dict(t="Salade de {bn} {pa} et {vn}", c="Méditerranéenne", e="🥙", m=["dej"], P=["poulet", "poischiches", "thon", "oeuf", "halloumi", "crevettes", "lentilles"], V=["courgette", "poivron", "aubergine", "asperges", "fenouil", "champignons"], B=["quinoa", "boulgour", "pates"],
         fix=["8 tomates cerises", "Persil ou basilic", "Jus d'1/2 citron", "1 c. à soupe d'huile d'olive"],
         steps=["{b}, puis laisse refroidir.", "{vp}, puis fais griller {vthe} 5 min à la poêle.", "{p}.", "Mélange tout avec les tomates cerises coupées, les herbes, le citron et l'huile."], tm=5, light=True, n=60),
    dict(t="Pâtes complètes {pa}, {vn} et tomate", c="Italienne", e="🍝", m=["dej", "din"], P=["poulet", "crevettes", "lentilles", "dinde", "halloumi", "poischiches"], V=["courgette", "epinards", "aubergine", "champignons", "poivron", "brocoli"], B=["pates"],
         fix=["150 g de sauce tomate", "1 gousse d'ail", "Basilic", "15 g de parmesan"],
         steps=["{b}.", "{vp}.", "{p}, puis ajoute l'ail et {vthe} 4 min.", "Verse la sauce tomate, laisse mijoter 5 min, mélange avec les pâtes. Ajoute basilic et parmesan."], tm=8, n=36),
    dict(t="Risotto d'orge {pa} et {vn}", c="Italienne", e="🍚", m=["din"], P=["poulet", "crevettes", "halloumi", "saumon"], V=["champignons", "asperges", "petitspois", "butternut", "poireau"], B=[],
         fix=["70 g d'orge perlé", "1 échalote", "500 ml de bouillon de légumes", "15 g de parmesan"],
         steps=["{vp}, émince l'échalote.", "Fais revenir l'échalote et l'orge 2 min, puis ajoute le bouillon louche par louche pendant 25 min.", "Ajoute {vthe} 8 min avant la fin.", "Dans une autre poêle : {plower}. Dépose la protéine sur le risotto avec le parmesan."], tm=30, n=20),
    dict(t="Tajine {pa}, {vn} et citron confit", c="Marocaine", e="🫕", m=["din"], P=["poulet", "poischiches", "dinde"], V=["carotte", "courgette", "butternut", "patatedouce", "fenouil"], B=["semoule"],
         fix=["1/2 oignon", "1 c. à café de ras-el-hanout", "1/4 de citron confit", "Quelques olives vertes", "200 ml de bouillon", "Coriandre"],
         steps=["{vp}, émince l'oignon.", "{p} avec l'oignon et les épices.", "Ajoute {vthe}, le citron confit, les olives et le bouillon. Couvre et laisse mijoter 25 min.", "{b} et sers avec la coriandre."], tm=30, n=15),
    dict(t="Couscous express {pa}", c="Maghrébine", e="🥘", m=["dej", "din"], P=["poulet", "poischiches", "dinde"], V=["courgette", "carotte"], B=["semoule"],
         fix=["1 navet", "100 g de pois chiches cuits", "1 c. à café d'épices à couscous", "300 ml de bouillon"],
         steps=["{vp}, coupe le navet en morceaux.", "{p}.", "Ajoute les légumes, les pois chiches, les épices et le bouillon, laisse cuire 20 min.", "{b} et sers avec le bouillon."], tm=25, n=6),
    dict(t="Bibimbap {pa} et {vn}", c="Coréenne", e="🍚", m=["din"], P=["boeuf", "tofu", "poulet", "porc"], V=["epinards", "carotte", "champignons", "courgette"], B=["riz"],
         fix=["1 œuf", "1 c. à café de gochujang (ou sriracha)", "1 c. à café d'huile de sésame", "1 c. à café de sésame"],
         steps=["{b}.", "{vp}, puis fais sauter {vthe} 3 min avec un peu d'huile de sésame.", "{p}.", "Fais cuire l'œuf au plat.", "Dispose tout sur le riz, ajoute le gochujang et le sésame. Mélange au moment de manger."], tm=6, n=16),
    dict(t="Ramen léger {pa} et {vn}", c="Japonaise", e="🍜", m=["din"], P=["poulet", "tofu", "porc", "crevettes", "oeuf"], V=["pakchoi", "champignons", "epinards", "poireau"], B=["soba"],
         fix=["500 ml de bouillon de volaille ou de légumes", "1 c. à soupe de sauce soja", "1 c. à café de pâte miso", "1 morceau de gingembre", "1 oignon nouveau"],
         steps=["Fais chauffer le bouillon avec le gingembre en lamelles, le soja et le miso délayé.", "{vp}, puis ajoute {vthe} au bouillon 3 min.", "{p}.", "{b}, mets-les dans un bol, verse le bouillon et ajoute la garniture."], tm=8, light=True, n=20),
    dict(t="Pho {pa}", c="Vietnamienne", e="🍜", m=["dej", "din"], P=["boeuf", "poulet", "tofu", "crevettes"], V=["pakchoi"], B=["nouillesriz"],
         fix=["500 ml de bouillon de bœuf ou de légumes", "1 étoile de badiane et 1 bâton de cannelle", "1 morceau de gingembre", "1 poignée de pousses de soja", "Menthe, coriandre et basilic thaï", "1/2 citron vert"],
         steps=["Fais infuser le bouillon 15 min avec la badiane, la cannelle et le gingembre.", "{b}.", "{p} (pour le bœuf : tranches très fines, le bouillon chaud suffit à les cuire).", "Verse le bouillon filtré sur les nouilles, ajoute pousses de soja, herbes et citron vert."], tm=15, light=True, n=6),
    dict(t="Pad thaï {pa}", c="Thaïlandaise", e="🥜", m=["din"], P=["crevettes", "poulet", "tofu"], V=["carotte"], B=["nouillesriz"],
         fix=["1 œuf", "1 poignée de pousses de soja", "1 c. à soupe de sauce soja", "1 c. à café de sucre de coco (ou miel)", "1 c. à soupe de cacahuètes", "1/2 citron vert"],
         steps=["{b}.", "{p}, puis pousse sur le côté et brouille l'œuf.", "Ajoute les nouilles, la carotte en julienne, le soja et le sucre, saute 2 min.", "Ajoute les pousses de soja, les cacahuètes concassées et le citron vert."], tm=5, n=4),
    dict(t="Dahl de lentilles corail et {vn}", c="Indienne", e="🟠", m=["dej", "din"], P=["lentilles"], V=["epinards", "patatedouce", "butternut", "choufleur", "carotte"], B=["riz"],
         fix=["80 g de lentilles corail", "150 ml de lait de coco léger", "1/2 oignon", "1 c. à café de curry", "1/2 c. à café de cumin", "Coriandre"],
         steps=["{b}.", "{vp}.", "Fais revenir l'oignon avec les épices 2 min.", "Ajoute les lentilles corail, {vthe}, le lait de coco et 200 ml d'eau, laisse cuire 15 min.", "Parsème de coriandre."], tm=20, own=True, n=5),
    dict(t="Chili {pa}", c="Tex-Mex", e="🌶️", m=["dej", "din"], P=["boeuf", "dinde", "haricotsrouges", "lentilles"], V=["poivron", "courgette"], B=["riz"],
         fix=["150 g de haricots rouges cuits", "200 g de tomates concassées", "1/2 oignon", "1 c. à café de cumin", "1/2 c. à café de piment doux", "2 c. à soupe de yaourt grec"],
         steps=["{b}.", "{vp}, émince l'oignon et fais-les revenir 5 min.", "{p}.", "Ajoute tomates, haricots et épices, laisse mijoter 15 min. Sers avec le riz et le yaourt."], tm=20, n=6),
    dict(t="Paella express {pa}", c="Espagnole", e="🥘", m=["din"], P=["crevettes", "poulet", "cabillaud"], V=["poivron", "petitspois", "haricotsverts"], B=[],
         fix=["60 g de riz rond", "1/2 oignon", "1 pincée de safran (ou curcuma)", "1/2 c. à café de paprika", "250 ml de bouillon", "1/4 de citron"],
         steps=["{vp}, émince l'oignon.", "Fais revenir l'oignon et {vthe}, ajoute le riz, le safran et le paprika.", "Verse le bouillon et laisse cuire 15 min sans remuer.", "{p}, puis dépose la protéine sur le riz et finis avec le citron."], tm=22, n=6),
    dict(t="Papillote de {pn}, {vn} et citron", c="Française", e="🐟", m=["din"], P=["saumon", "cabillaud", "crevettes", "poulet"], V=["courgette", "fenouil", "poireau", "carotte", "asperges", "haricotsverts"], B=[],
         fix=["1/2 citron", "Aneth ou thym", "1 c. à café d'huile d'olive", "1 petite pomme de terre (ou 60 g de riz)"],
         steps=["Préchauffe le four à 200 °C.", "{vp} en fines lamelles.", "Dépose les légumes et la protéine sur une feuille de cuisson avec le citron, les herbes et l'huile.", "Ferme la papillote et enfourne 15 à 18 min. Sers avec la pomme de terre vapeur ou le riz."], tm=20, light=True, own=True, n=24),
    dict(t="Brochettes {pa} et {vn}, {bn} et sauce yaourt", c="Turque", e="🍢", m=["din"], P=["poulet", "dinde", "halloumi", "crevettes", "boeuf"], V=["poivron", "courgette", "champignons"], B=["boulgour", "semoule"],
         fix=["3 c. à soupe de yaourt grec", "1/2 gousse d'ail", "Menthe", "1 c. à café de paprika", "1 c. à café d'huile d'olive"],
         steps=["{b}.", "Coupe la protéine et les légumes en cubes, mélange avec le paprika et l'huile.", "Monte les brochettes et fais-les griller 10 min en les retournant.", "Mélange le yaourt avec l'ail râpé et la menthe, sers avec la base."], tm=12, own=True, n=30),
    dict(t="Wrap {pa}, {vn} et houmous", c="Libanaise", e="🌯", m=["dej"], P=["poulet", "falafel", "poischiches", "dinde", "halloumi", "thon"], V=["poivron", "carotte", "epinards"], B=[],
         fix=["1 grande tortilla complète", "2 c. à soupe d'houmous", "1/4 de concombre", "Quelques feuilles de salade"],
         steps=["{p}.", "{vp}.", "Étale l'houmous sur la tortilla, ajoute salade, concombre et légumes.", "Ajoute la protéine, roule bien serré et coupe en deux."], tm=5, n=18),
    dict(t="Shakshuka {vn}", c="Moyen-Orient", e="🍳", m=["pd", "din"], P=["oeuf"], V=["poivron", "epinards", "courgette", "aubergine"], B=[],
         fix=["2 œufs", "200 g de tomates concassées", "1/2 oignon", "1/2 c. à café de cumin", "1/2 c. à café de paprika", "Coriandre ou persil", "1 tranche de pain complet"],
         steps=["{vp}, émince l'oignon et fais-les revenir 5 min.", "Ajoute les tomates et les épices, laisse mijoter 8 min.", "Creuse deux puits, casse les œufs dedans, couvre et cuis 5 à 6 min.", "Parsème d'herbes et sers avec le pain."], tm=20, own=True, n=4),
    dict(t="Frittata {vn} et feta", c="Italienne", e="🥚", m=["pd", "dej", "din"], P=["oeuf"], V=["courgette", "epinards", "poivron", "champignons", "asperges", "poireau"], B=[],
         fix=["3 œufs", "30 g de feta", "Herbes fraîches", "1 c. à café d'huile d'olive", "Salade verte"],
         steps=["{vp}, puis fais revenir {vthe} 5 min.", "Bats les œufs avec les herbes, verse sur les légumes et émiette la feta.", "Cuis 5 min à couvert à feu doux (ou finis 5 min au four).", "Sers avec la salade."], tm=15, own=True, light=True, n=6),
    dict(t="Velouté de {vn} et {pn}", c="Française", e="🥣", m=["din"], P=["poischiches", "oeuf"], V=["butternut", "carotte", "brocoli", "choufleur", "poireau", "courgette", "champignons", "patatedouce"], B=[],
         fix=["1/2 oignon", "1 petite pomme de terre", "500 ml de bouillon de légumes", "1 c. à soupe de crème légère", "1 tranche de pain complet"],
         steps=["{vp}, coupe l'oignon et la pomme de terre.", "Fais cuire les légumes 20 min dans le bouillon.", "Mixe avec la crème.", "Pour la garniture protéinée : {plower}. Dépose-la sur le velouté et sers avec le pain."], tm=25, light=True, n=16),
    dict(t="Soupe miso {pa} et {vn}", c="Japonaise", e="🍵", m=["din"], P=["tofu", "crevettes", "saumon", "oeuf"], V=["pakchoi", "champignons", "epinards", "poireau"], B=["soba"],
         fix=["1 c. à soupe de pâte miso", "400 ml d'eau", "1 feuille d'algue nori (facultatif)", "1 oignon nouveau"],
         steps=["{b}.", "Chauffe l'eau sans la faire bouillir et délaye le miso.", "{vp}, puis ajoute {vthe} 3 min.", "{p}, puis ajoute la protéine avec les nouilles et l'oignon nouveau."], tm=6, light=True, n=16),
    dict(t="Gnocchis poêlés {pa} et {vn}", c="Italienne", e="🥟", m=["din"], P=["poulet", "halloumi", "crevettes", "poischiches"], V=["epinards", "courgette", "champignons", "asperges"], B=[],
         fix=["200 g de gnocchis", "8 tomates cerises", "1 gousse d'ail", "15 g de parmesan"],
         steps=["Dore les gnocchis 5 min à la poêle sans les faire bouillir.", "{vp}.", "{p}, puis ajoute l'ail, les tomates et {vthe} 3 min.", "Mélange avec les gnocchis et parsème de parmesan."], tm=8, n=16),
    dict(t="Kebab bowl {pa} et {bn}", c="Turque", e="🥙", m=["dej", "din"], P=["poulet", "dinde", "boeuf", "falafel", "halloumi"], V=["poivron"], B=["boulgour", "semoule", "riz"],
         fix=["1 tomate", "1/4 d'oignon rouge", "1/4 de concombre", "3 c. à soupe de yaourt grec", "1 c. à café d'épices kebab (cumin, paprika, ail)"],
         steps=["{b}.", "{p} avec les épices.", "Coupe tomate, concombre et oignon.", "Assemble le bol et ajoute le yaourt à l'ail."], tm=8, n=15),
    dict(t="Banh mi bowl {pa} et {bn}", c="Vietnamienne", e="🥖", m=["dej"], P=["porc", "poulet", "tofu", "crevettes"], V=["carotte"], B=["riz", "nouillesriz"],
         fix=["1/4 de concombre", "1 radis", "1 c. à soupe de vinaigre de riz", "1 c. à café de sucre", "Coriandre", "1 c. à café de sriracha"],
         steps=["{b}.", "Fais mariner la carotte et le radis en julienne 10 min dans le vinaigre sucré (pickles express).", "{p}.", "Assemble avec le concombre, la coriandre et la sriracha."], tm=10, n=8),
    dict(t="{pn} à la plancha, {vn} et {bn}", c="Nordique", e="🐟", m=["din"], P=["saumon", "cabillaud", "poulet", "dinde"], V=["asperges", "haricotsverts", "brocoli", "fenouil", "epinards"], B=["quinoa", "rizcomplet", "riz"],
         fix=["1/2 citron", "1 c. à café d'huile d'olive", "Aneth ou persil"],
         steps=["{b}.", "{vp}, puis cuis {vthe} 5 à 8 min à la vapeur.", "Assaisonne la protéine et grille-la à la poêle (4 min par face pour le poisson, 6 pour la volaille).", "Sers avec le citron et les herbes."], tm=10, light=True, own=True, n=40),
    dict(t="Plaque au four : {pn}, {vn} et citron", c="Française", e="🍋", m=["din"], P=["poulet", "dinde", "tofu", "poischiches", "cabillaud"], V=["courgette", "poivron", "butternut", "patatedouce", "carotte", "fenouil"], B=[],
         fix=["1/2 citron", "1 c. à soupe d'huile d'olive", "Thym ou romarin", "1/2 oignon rouge"],
         steps=["Préchauffe le four à 200 °C.", "{vp} et coupe l'oignon en quartiers.", "Mélange les légumes avec l'huile et les herbes, dépose la protéine dessus avec le citron en tranches.", "Enfourne 25 min (15 min pour le poisson)."], tm=25, own=True, n=30),
    dict(t="Bowl coréen {pa}, {vn} et kimchi", c="Coréenne", e="🥬", m=["dej", "din"], P=["tofu", "porc", "poulet", "boeuf"], V=["courgette", "epinards", "carotte"], B=["riz"],
         fix=["50 g de kimchi", "1 c. à café de gochujang", "1 c. à café de sauce soja", "1 c. à café de sésame", "1 oignon nouveau"],
         steps=["{b}.", "{p}, puis ajoute le gochujang et le soja pour l'enrober.", "{vp}, puis fais sauter {vthe} 3 min.", "Assemble avec le kimchi, le sésame et l'oignon nouveau."], tm=6, n=12),
    dict(t="Ceviche {pa}", c="Péruvienne", e="🍋", m=["dej"], P=["cabillaud", "crevettes", "saumon"], V=["poivron"], B=[],
         fix=["2 citrons verts", "1/4 d'oignon rouge", "1/2 avocat", "Coriandre", "1 pincée de piment", "50 g de maïs ou de patate douce cuite"],
         steps=["Coupe un poisson ultra-frais (qualité sashimi) ou des crevettes cuites en petits dés.", "Couvre de jus de citron vert et laisse « cuire » 15 min au frais.", "Ajoute l'oignon émincé, le poivron, l'avocat, la coriandre et le piment.", "Sers bien frais avec le maïs ou la patate douce."], tm=20, light=True, own=True, n=3),
    dict(t="Lentilles du Puy, {vn} et {pn}", c="Française", e="🟤", m=["dej", "din"], P=["oeuf", "saumon", "poulet", "halloumi"], V=["carotte", "poireau", "epinards", "fenouil"], B=[],
         fix=["70 g de lentilles vertes du Puy", "1 échalote", "1 feuille de laurier", "1 c. à café de moutarde", "1 c. à soupe de vinaigrette"],
         steps=["Fais cuire les lentilles 25 min avec le laurier.", "{vp}, puis ajoute {vthe} aux lentilles 10 min avant la fin.", "{p}.", "Égoutte, assaisonne avec l'échalote, la moutarde et la vinaigrette."], tm=25, n=16),
    dict(t="Stir-fry {pa}, {vn} et cacahuètes ({bn})", c="Asiatique", e="🥜", m=["dej", "din"], P=["poulet", "tofu", "crevettes", "tempeh"], V=["brocoli", "poivron", "poisgourmands", "pakchoi"], B=["riz", "soba"],
         fix=["1 c. à soupe de beurre de cacahuète", "1 c. à soupe de sauce soja", "1/2 citron vert", "1 c. à café de sriracha", "1 c. à soupe de cacahuètes"],
         steps=["{b}.", "{vp}.", "{p}, puis ajoute {vthe} 4 min à feu vif.", "Délaye le beurre de cacahuète avec soja, citron vert, sriracha et 2 c. à soupe d'eau, verse et mélange. Parsème de cacahuètes."], tm=6, n=32),
]
DISHES += [
    dict(t="Salade César {pa}", c="Américaine", e="🥗", m=["dej"], P=["poulet", "crevettes", "tofu", "oeuf", "saumon"], V=[], B=[],
         fix=["1 cœur de romaine", "1 tranche de pain complet en croûtons", "15 g de parmesan", "2 c. à soupe de yaourt", "1 c. à café de moutarde", "Jus de citron"],
         steps=["{p}.", "Fais griller les croûtons à sec 3 min.", "Mélange yaourt, moutarde, citron et un peu de parmesan pour la sauce.", "Assemble romaine, protéine, croûtons, sauce et copeaux de parmesan."], tm=8, light=True, n=5),
    dict(t="Bò bún {pa}", c="Vietnamienne", e="🍜", m=["dej", "din"], P=["boeuf", "poulet", "crevettes", "tofu"], V=["carotte"], B=["nouillesriz"],
         fix=["1/4 de concombre", "1 poignée de pousses de soja", "Menthe, coriandre", "1 c. à soupe de cacahuètes", "Sauce : 1 c. à soupe de nuoc-mâm, jus d'1/2 citron vert, 1 c. à café de sucre, eau"],
         steps=["{b}, rince à l'eau froide.", "{p} avec un peu de citronnelle si tu en as.", "Râpe la carotte, coupe le concombre en bâtonnets.", "Dispose les nouilles, les crudités, la protéine et les herbes, arrose de sauce et parsème de cacahuètes."], tm=8, light=True, n=4),
    dict(t="Nasi goreng {pa} et {vn}", c="Indonésienne", e="🍳", m=["din"], P=["poulet", "crevettes", "tofu", "tempeh"], V=["carotte", "poivron", "petitspois", "pakchoi"], B=["riz"],
         fix=["1 œuf", "1 échalote", "1 gousse d'ail", "1 c. à soupe de kecap manis (ou soja + miel)", "1 c. à café de sambal (ou sriracha)"],
         steps=["{b} (idéalement la veille : un riz froid saute mieux).", "{vp}.", "{p}, puis ajoute l'échalote, l'ail et {vthe} 3 min.", "Ajoute le riz, le kecap manis et le sambal, saute 3 min à feu vif.", "Sers avec l'œuf au plat dessus."], tm=10, n=14),
    dict(t="Riz sauté {pa} et {vn}", c="Chinoise", e="🍚", m=["dej", "din"], P=["poulet", "crevettes", "porc", "tofu", "oeuf"], V=["petitspois", "carotte", "poivron", "champignons", "brocoli"], B=["riz", "rizcomplet"],
         fix=["1 œuf", "1 oignon nouveau", "1 c. à soupe de sauce soja", "1 c. à café d'huile de sésame"],
         steps=["{b} (la veille de préférence).", "{vp}.", "{p}, puis ajoute {vthe} 3 min.", "Ajoute le riz et l'œuf battu, saute 3 min, assaisonne de soja et d'huile de sésame.", "Parsème d'oignon nouveau."], tm=8, n=24),
    dict(t="Yakisoba {pa} et {vn}", c="Japonaise", e="🍜", m=["din"], P=["porc", "poulet", "crevettes", "tofu"], V=["chou", "carotte", "poivron", "champignons"], B=["soba"],
         fix=["1 c. à soupe de sauce yakisoba (ou Worcestershire + soja + ketchup)", "1/2 oignon", "1 c. à café de graines de sésame"],
         steps=["{b}.", "{vp}, émince l'oignon.", "{p}, puis ajoute l'oignon et {vthe} 4 min.", "Ajoute les nouilles et la sauce, saute 2 min. Parsème de sésame."], tm=6, n=14),
    dict(t="Donburi {pa} et {vn}", c="Japonaise", e="🍱", m=["dej", "din"], P=["poulet", "boeuf", "saumon", "tofu"], V=["epinards", "champignons", "poireau", "brocoli"], B=["riz"],
         fix=["1 œuf", "1 c. à soupe de sauce soja", "1 c. à café de mirin (ou miel)", "100 ml de bouillon dashi (ou de légumes)", "1 oignon nouveau"],
         steps=["{b}.", "{vp}.", "{p}, ajoute {vthe}, le bouillon, le soja et le mirin, laisse frémir 3 min.", "Verse l'œuf battu dessus, couvre 1 min (il doit rester crémeux).", "Fais glisser sur le riz et parsème d'oignon nouveau."], tm=8, n=14),
    dict(t="Biryani express {pa} et {vn}", c="Indienne", e="🍛", m=["din"], P=["poulet", "poischiches", "dinde", "tofu"], V=["petitspois", "carotte", "choufleur", "haricotsverts"], B=[],
         fix=["70 g de riz basmati", "1/2 oignon", "1 c. à café de garam masala", "1 pincée de curcuma", "2 c. à soupe de yaourt", "Menthe, coriandre", "1 c. à soupe d'amandes effilées"],
         steps=["{vp}, émince l'oignon.", "{p} avec l'oignon et les épices.", "Ajoute le riz rincé, {vthe} et 150 ml d'eau, couvre et cuis 12 min à feu doux.", "Laisse reposer 5 min, ajoute les herbes, les amandes et le yaourt."], tm=20, n=14),
    dict(t="Basquaise {pa}", c="Française", e="🫑", m=["din"], P=["poulet", "dinde", "tofu", "cabillaud", "poischiches"], V=["poivron"], B=["riz", "rizcomplet", "quinoa"],
         fix=["1 poivron rouge supplémentaire", "1/2 oignon", "1 gousse d'ail", "200 g de tomates concassées", "1/2 c. à café de piment d'Espelette"],
         steps=["{b}.", "{vp} avec le second poivron, émince l'oignon et l'ail.", "Fais revenir oignon, ail et poivrons 8 min, ajoute les tomates et le piment, laisse mijoter 10 min.", "{p}, puis ajoute la protéine à la sauce 3 min."], tm=20, n=10),
    dict(t="Tom kha {pa}", c="Thaïlandaise", e="🥥", m=["din"], P=["poulet", "crevettes", "tofu", "cabillaud"], V=["champignons", "pakchoi", "poivron"], B=[],
         fix=["200 ml de lait de coco léger", "200 ml de bouillon", "1 tige de citronnelle", "3 tranches de galanga ou de gingembre", "1 c. à café de nuoc-mâm", "1/2 citron vert", "Coriandre"],
         steps=["Fais infuser le bouillon et le lait de coco 10 min avec la citronnelle écrasée et le galanga.", "{vp}.", "{p}, ajoute la protéine et {vthe} dans la soupe 4 min.", "Assaisonne au nuoc-mâm et au citron vert, parsème de coriandre."], tm=15, light=True, n=12),
    dict(t="Larb {pa}", c="Laotienne", e="🌿", m=["dej"], P=["poulet", "porc", "tofu", "dinde"], V=[], B=["rizjasmin"],
         fix=["1 échalote", "Menthe, coriandre", "Jus d'1 citron vert", "1 c. à café de nuoc-mâm", "1 c. à soupe de riz grillé moulu (facultatif)", "Feuilles de salade pour servir"],
         steps=["{b}.", "Hache finement la protéine et fais-la cuire 5 min sans matière grasse.", "Hors du feu, ajoute l'échalote émincée, le citron vert, le nuoc-mâm et beaucoup d'herbes.", "Sers dans les feuilles de salade avec le riz."], tm=8, light=True, n=4),
    dict(t="Gado-gado {pa}", c="Indonésienne", e="🥜", m=["dej"], P=["tofu", "tempeh", "oeuf", "poulet"], V=["haricotsverts", "chou", "carotte"], B=[],
         fix=["1 petite pomme de terre", "1 poignée de pousses de soja", "1/4 de concombre", "Sauce : 1 c. à soupe de beurre de cacahuète, 1 c. à café de soja, citron vert, eau"],
         steps=["Fais cuire la pomme de terre 15 min et {vthe} 5 min à l'eau.", "{p}.", "Délaye la sauce cacahuète jusqu'à ce qu'elle soit nappante.", "Dispose légumes, protéine et concombre, nappe de sauce."], tm=15, n=12),
    dict(t="Souvlaki {pa}, {bn} et tzatziki", c="Grecque", e="🍢", m=["din"], P=["poulet", "porc", "halloumi", "dinde"], V=[], B=["riz", "boulgour"],
         fix=["1/2 citron", "1 c. à café d'origan", "1 c. à café d'huile d'olive", "3 c. à soupe de yaourt grec", "1/4 de concombre", "1 tomate"],
         steps=["{b}.", "Coupe la protéine en cubes, fais-la mariner 10 min avec citron, origan et huile.", "Grille les brochettes 8 à 10 min en les retournant.", "Mélange yaourt et concombre râpé pour le tzatziki, sers avec la tomate."], tm=15, n=8),
    dict(t="Zoodles {pa} au pesto", c="Italienne", e="🥒", m=["dej", "din"], P=["poulet", "crevettes", "saumon", "tofu", "halloumi"], V=[], B=[],
         fix=["2 courgettes en spaghetti", "1 c. à soupe de pesto", "8 tomates cerises", "15 g de parmesan", "1 c. à soupe de pignons"],
         steps=["Taille les courgettes en spaghetti (ou en fines lanières à l'économe).", "{p}.", "Saute les zoodles 2 min seulement, ajoute le pesto et les tomates.", "Ajoute la protéine, le parmesan et les pignons."], tm=8, light=True, n=5),
    dict(t="Lettuce wraps {pa}", c="Asiatique", e="🥬", m=["dej"], P=["poulet", "porc", "tofu", "crevettes", "dinde"], V=["champignons", "carotte"], B=[],
         fix=["6 feuilles de laitue iceberg ou de sucrine", "1 c. à soupe de sauce hoisin", "1 c. à café de sauce soja", "1 oignon nouveau", "1 c. à soupe de cacahuètes"],
         steps=["{vp} en petits dés.", "{p} (haché fin c'est encore mieux), ajoute {vthe} 3 min.", "Ajoute hoisin et soja.", "Garnis les feuilles de salade et parsème d'oignon nouveau et de cacahuètes."], tm=8, light=True, n=10),
    dict(t="Harira {pa}", c="Marocaine", e="🍲", m=["din"], P=["lentilles", "poischiches", "poulet"], V=["carotte"], B=[],
         fix=["40 g de lentilles vertes", "50 g de pois chiches cuits", "200 g de tomates concassées", "1/2 oignon", "1 c. à café de ras-el-hanout", "Coriandre, persil", "1/2 citron"],
         steps=["Fais revenir l'oignon avec les épices 2 min.", "{vp}, ajoute-les avec les tomates, les lentilles et 500 ml d'eau, laisse cuire 25 min.", "{p}, puis ajoute la protéine et les pois chiches 5 min.", "Sers avec beaucoup d'herbes et un filet de citron."], tm=30, light=True, n=3),
    dict(t="Minestrone et {pn}", c="Italienne", e="🥣", m=["din"], P=["poischiches", "haricotsrouges", "poulet", "oeuf"], V=["courgette", "poireau", "haricotsverts"], B=[],
         fix=["1 carotte", "1 branche de céleri", "200 g de tomates concassées", "40 g de petites pâtes", "500 ml de bouillon", "Basilic, parmesan"],
         steps=["{vp}, coupe la carotte et le céleri en dés.", "Cuis les légumes 15 min dans le bouillon avec les tomates.", "Ajoute les pâtes 8 min.", "{p}, puis ajoute la protéine. Sers avec basilic et parmesan."], tm=25, light=True, n=12),
    dict(t="Enchiladas légères {pa}", c="Mexicaine", e="🌯", m=["din"], P=["poulet", "haricotsrouges", "dinde", "poischiches"], V=["poivron", "courgette", "epinards"], B=[],
         fix=["2 tortillas de maïs", "150 g de sauce tomate épicée", "30 g de cheddar ou de mozzarella", "2 c. à soupe de yaourt grec", "Coriandre"],
         steps=["Préchauffe le four à 200 °C.", "{vp}.", "{p}, ajoute {vthe} 4 min.", "Garnis et roule les tortillas, nappe de sauce, parsème de fromage et gratine 12 min. Sers avec le yaourt et la coriandre."], tm=20, n=12),
    dict(t="Okonomiyaki léger {pa}", c="Japonaise", e="🥞", m=["din"], P=["crevettes", "porc", "tofu", "poulet"], V=["chou"], B=[],
         fix=["150 g de chou blanc émincé", "2 œufs", "40 g de farine", "1 oignon nouveau", "1 c. à soupe de sauce okonomi (ou soja + ketchup)", "1 c. à café de mayonnaise légère"],
         steps=["Mélange le chou émincé, les œufs, la farine et l'oignon.", "{p} en petits morceaux et ajoute à la pâte.", "Cuis la galette 5 min par face à feu moyen.", "Nappe de sauce et d'un trait de mayonnaise."], tm=15, n=4),
    dict(t="Laksa {pa}", c="Malaisienne", e="🍜", m=["din"], P=["crevettes", "poulet", "tofu"], V=["pakchoi", "poivron"], B=["nouillesriz"],
         fix=["1 c. à soupe de pâte de laksa (ou de curry rouge)", "200 ml de lait de coco léger", "200 ml de bouillon", "1 poignée de pousses de soja", "1/2 citron vert", "Coriandre"],
         steps=["{b}.", "Fais revenir la pâte de laksa 1 min, ajoute lait de coco et bouillon, laisse frémir 5 min.", "{vp}.", "{p}, puis ajoute la protéine et {vthe} dans la soupe 3 min.", "Verse sur les nouilles avec pousses de soja, citron vert et coriandre."], tm=12, n=6),
    dict(t="Jambalaya léger {pa}", c="Cajun", e="🍤", m=["din"], P=["crevettes", "poulet", "dinde"], V=["poivron"], B=[],
         fix=["60 g de riz long", "1/2 oignon", "1 branche de céleri", "200 g de tomates concassées", "1 c. à café d'épices cajun", "250 ml de bouillon"],
         steps=["{vp}, coupe l'oignon et le céleri.", "{p} avec les épices cajun, puis réserve.", "Fais revenir les légumes 5 min, ajoute le riz, les tomates et le bouillon, cuis 15 min à couvert.", "Remets la protéine 2 min avant de servir."], tm=22, n=3),
    dict(t="Mezzé bowl {pa}", c="Libanaise", e="🥙", m=["dej"], P=["falafel", "poulet", "halloumi", "poischiches"], V=["aubergine", "poivron"], B=["boulgour", "quinoa"],
         fix=["2 c. à soupe d'houmous", "1 c. à soupe de taboulé ou de persil", "1/4 de concombre", "Quelques olives", "1 c. à soupe de yaourt"],
         steps=["{b}.", "{vp}, puis fais griller {vthe} 6 min.", "{p}.", "Assemble le bol avec l'houmous, le concombre, les olives et le yaourt."], tm=10, n=14),
    dict(t="Gratin léger de {vn} et {pn}", c="Française", e="🧀", m=["din"], P=["poulet", "cabillaud", "poischiches", "dinde"], V=["courgette", "brocoli", "choufleur", "poireau", "butternut", "epinards"], B=[],
         fix=["1 œuf", "100 ml de lait", "20 g de gruyère râpé", "Muscade, sel, poivre"],
         steps=["Préchauffe le four à 190 °C.", "{vp} et fais précuire 5 min à la vapeur.", "{p}.", "Mets légumes et protéine dans un plat, verse l'œuf battu avec le lait et la muscade, parsème de gruyère. Enfourne 20 min."], tm=30, n=22),
    dict(t="Quiche sans pâte {vn} et {pn}", c="Française", e="🥧", m=["dej", "din"], P=["saumon", "poulet", "thon", "halloumi"], V=["poireau", "epinards", "courgette", "brocoli", "champignons"], B=[],
         fix=["2 œufs", "100 ml de lait", "30 g de comté râpé", "Salade verte"],
         steps=["Préchauffe le four à 180 °C.", "{vp}, puis fais revenir {vthe} 5 min.", "{p}.", "Mélange œufs, lait et comté, ajoute légumes et protéine, verse dans un plat et cuis 25 min. Sers avec la salade."], tm=35, n=20),
    dict(t="Ratatouille et {pn}", c="Provençale", e="🍆", m=["din"], P=["oeuf", "poulet", "cabillaud", "poischiches", "halloumi"], V=["aubergine"], B=["quinoa", "riz", "boulgour"],
         fix=["1 courgette", "1 poivron", "1 tomate", "1/2 oignon", "Thym, laurier", "1 c. à soupe d'huile d'olive"],
         steps=["Coupe tous les légumes en dés.", "Fais-les mijoter 25 min à couvert avec l'oignon, l'huile et les herbes.", "{b}.", "{p}, puis sers la protéine sur la ratatouille."], tm=30, light=True, n=15),
    dict(t="Quesadillas légères {pa} et {vn}", c="Mexicaine", e="🧀", m=["dej", "din"], P=["poulet", "haricotsrouges", "dinde", "champignon"] if False else ["poulet", "haricotsrouges", "dinde", "tofu"], V=["poivron", "epinards", "courgette", "champignons"], B=[],
         fix=["2 tortillas complètes", "30 g de cheddar ou de mozzarella", "2 c. à soupe de salsa", "2 c. à soupe de yaourt grec", "Salade verte"],
         steps=["{vp}.", "{p}, ajoute {vthe} 3 min.", "Garnis une tortilla, ajoute le fromage et couvre de la seconde.", "Dore 2 min par face, coupe en quarts, sers avec salsa, yaourt et salade."], tm=10, n=16),
]

# falafel used in wraps/kebab: pseudo-protein
P["falafel"] = dict(n="falafels", a="aux falafels", ing="4 falafels (maison ou du commerce)", cook="Réchauffe les falafels 8 min au four", t=8, prot=True, vege=True, fish=False)

# ---------------------------------------------------------------- breakfasts / snacks
FRUITS = [("banane", "1 banane"), ("pomme et cannelle", "1 pomme + 1 pincée de cannelle"), ("poire", "1 poire"), ("fruits rouges", "100 g de fruits rouges"),
          ("mangue", "1/2 mangue"), ("myrtilles", "100 g de myrtilles"), ("abricots", "3 abricots (ou 4 secs)"), ("kiwi", "2 kiwis"), ("figues", "2 figues"), ("framboises", "100 g de framboises")]
TOPS = [("amandes", "1 poignée d'amandes"), ("noix", "1 poignée de noix"), ("noisettes", "1 poignée de noisettes"), ("graines de chia", "1 c. à soupe de graines de chia"),
        ("beurre de cacahuète", "1 c. à soupe de beurre de cacahuète"), ("coco", "1 c. à soupe de noix de coco râpée"), ("granola", "30 g de granola peu sucré"), ("graines de courge", "1 c. à soupe de graines de courge")]


def breakfasts():
    out = []
    combos = [(f, t) for f in FRUITS for t in TOPS]
    rng.shuffle(combos)
    for f, t in combos[:18]:
        out.append(dict(n=f"Porridge {f[0]} et {t[0]}", e="🥣", m=["pd"], t=10, tags=["vege", "rapide"], c="Écossaise",
                        i=["50 g de flocons d'avoine", "200 ml de lait (ou boisson végétale)", f[1], t[1]],
                        s=["Fais cuire l'avoine dans le lait 4 à 5 min en remuant.", f"Ajoute {f[0]} coupé(es) en morceaux.", f"Sers avec {t[0]} sur le dessus."]))
    rng.shuffle(combos)
    for f, t in combos[:14]:
        out.append(dict(n=f"Overnight oats {f[0]} et {t[0]}", e="🫙", m=["pd"], t=5, tags=["vege", "rapide"], c="Américaine",
                        i=["50 g de flocons d'avoine", "150 ml de lait", "1 yaourt nature", f[1], t[1]],
                        s=["La veille, mélange l'avoine, le lait et le yaourt dans un bocal.", "Laisse toute la nuit au frigo.", f"Le matin, ajoute {f[0]} et {t[0]}."]))
    rng.shuffle(combos)
    for f, t in combos[:16]:
        out.append(dict(n=f"Bol skyr, {f[0]} et {t[0]}", e="🥛", m=["pd", "col"], t=5, tags=["proteine", "vege", "rapide"], c="Islandaise",
                        i=["200 g de skyr nature", f[1], t[1], "1 c. à café de miel"],
                        s=["Verse le skyr dans un bol.", f"Ajoute {f[0]} et {t[0]}.", "Termine par un filet de miel."]))
    smoothies = [("mangue-passion", ["1/2 mangue", "1 fruit de la passion"]), ("fraise-banane", ["100 g de fraises", "1/2 banane"]), ("myrtille-avoine", ["100 g de myrtilles", "2 c. à soupe d'avoine"]),
                 ("vert épinards-pomme", ["1 poignée d'épinards", "1 pomme", "1/2 banane"]), ("açaï", ["100 g de purée d'açaï surgelée", "1/2 banane"]), ("pitaya", ["100 g de pitaya surgelée", "1/2 banane"]),
                 ("cacao-banane", ["1 banane", "1 c. à soupe de cacao"]), ("ananas-coco", ["150 g d'ananas", "100 ml de lait de coco léger"])]
    for name, ings in smoothies:
        out.append(dict(n=f"Smoothie bowl {name}", e="🍓", m=["pd", "col"], t=8, tags=["vege", "leger", "rapide"], c="Brésilienne" if name in ("açaï",) else "Californienne",
                        i=ings + ["100 ml de lait ou yaourt", "1 c. à soupe de granola", "1 c. à café de graines de chia"],
                        s=["Mixe les fruits (bien froids) avec le lait jusqu'à une texture épaisse.", "Verse dans un bol.", "Ajoute le granola et les graines."]))
    veg_eggs = ["epinards", "champignons", "poivron", "courgette", "asperges", "poireau"]
    cheeses = [("feta", "30 g de feta"), ("chèvre", "30 g de chèvre frais"), ("parmesan", "15 g de parmesan"), ("comté", "20 g de comté râpé")]
    k = 0
    for v in veg_eggs:
        for ch in cheeses:
            if (k := k + 1) % 2:
                continue
            vv = V[v]
            out.append(dict(n=f"Omelette {vv['n']} et {ch[0]}", e="🍳", m=["pd", "din"], t=10, tags=["proteine", "vege", "rapide"], c="Française",
                            i=["3 œufs", vv["ing"], ch[1], "1 c. à café d'huile d'olive", "Poivre, herbes"],
                            s=[f"{vv['prep']}, puis fais revenir {vv['the']} 3 min.", "Verse les œufs battus avec les herbes.", f"Ajoute le {ch[0]}, cuis 3 min et plie l'omelette."]))
    for fl, ing in [("banane", "1 banane mûre"), ("myrtilles", "80 g de myrtilles"), ("cacao", "1 c. à soupe de cacao"), ("pomme-cannelle", "1/2 pomme râpée + cannelle"), ("citron-pavot", "1/2 citron (zeste) + 1 c. à café de pavot"), ("matcha", "1 c. à café de matcha")]:
        out.append(dict(n=f"Pancakes protéinés {fl}", e="🥞", m=["pd"], t=15, tags=["proteine", "vege", "rapide"], c="Américaine",
                        i=["2 œufs", "40 g de flocons d'avoine", "100 g de fromage blanc", ing, "1/2 c. à café de levure"],
                        s=["Mixe tous les ingrédients.", "Cuis de petites louches 2 min par face dans une poêle légèrement huilée.", "Sers avec des fruits frais."]))
    for f in FRUITS[:8]:
        out.append(dict(n=f"Chia pudding {f[0]}", e="🍮", m=["pd", "col"], t=5, tags=["vege", "leger", "rapide"], c="Mexicaine",
                        i=["3 c. à soupe de graines de chia", "200 ml de lait d'amande", f[1], "Quelques gouttes de vanille"],
                        s=["Mélange chia, lait et vanille, attends 5 min et remélange.", "Laisse au frigo au moins 2 h (ou la nuit).", f"Sers avec {f[0]}."]))
    world = [
        ("Congee au poulet et gingembre", "🍚", "Chinoise", ["40 g de riz", "500 ml de bouillon de volaille", "100 g de poulet cuit", "1 morceau de gingembre", "1 oignon nouveau", "1 c. à café de sauce soja"], ["Fais cuire le riz 30 min dans le bouillon avec le gingembre, en remuant de temps en temps.", "Ajoute le poulet effiloché.", "Sers avec l'oignon nouveau et le soja."], 35, ["proteine"]),
        ("Huevos rancheros", "🌶️", "Mexicaine", ["2 œufs", "1 tortilla de maïs", "100 g de haricots noirs", "100 g de salsa tomate", "1/4 d'avocat", "Coriandre"], ["Chauffe la tortilla et les haricots.", "Fais cuire les œufs au plat.", "Dépose les œufs sur la tortilla avec les haricots, la salsa, l'avocat et la coriandre."], 15, ["proteine", "vege", "rapide"]),
        ("Menemen (œufs à la turque)", "🍅", "Turque", ["2 œufs", "1 tomate", "1/2 poivron vert", "1/4 d'oignon", "1 pincée de piment d'Alep", "1 tranche de pain complet"], ["Fais revenir l'oignon et le poivron 4 min.", "Ajoute la tomate en dés et laisse compoter 4 min.", "Ajoute les œufs battus et remue doucement jusqu'à ce qu'ils soient crémeux. Sers avec le pain."], 15, ["proteine", "vege", "rapide"]),
        ("Ful medames", "🫘", "Égyptienne", ["150 g de fèves cuites", "1/2 gousse d'ail", "1/2 citron", "1 c. à café de cumin", "1 c. à soupe d'huile d'olive", "1 pain pita complet"], ["Réchauffe les fèves avec un peu d'eau.", "Écrase-les grossièrement avec l'ail, le citron et le cumin.", "Arrose d'huile d'olive et sers avec le pain."], 10, ["proteine", "vege", "rapide"]),
        ("Tamagoyaki et soupe miso", "🥚", "Japonaise", ["3 œufs", "1 c. à café de sauce soja", "1 c. à café de mirin (facultatif)", "1 c. à café de pâte miso", "300 ml d'eau"], ["Bats les œufs avec le soja et le mirin.", "Cuis en fines couches roulées les unes sur les autres dans une petite poêle.", "Délaye le miso dans l'eau chaude (sans bouillir) et sers avec l'omelette."], 15, ["proteine", "vege", "rapide"]),
        ("Açaí bowl", "🫐", "Brésilienne", ["100 g de purée d'açaí surgelée", "1 banane", "50 ml de lait", "2 c. à soupe de granola", "Quelques fruits frais"], ["Mixe l'açaí avec la moitié de la banane et le lait.", "Verse dans un bol.", "Ajoute granola, rondelles de banane et fruits."], 8, ["vege", "leger", "rapide"]),
        ("Shakshuka verte", "🥬", "Israélienne", ["2 œufs", "2 poignées d'épinards", "1/2 courgette", "1 poireau", "30 g de feta", "Herbes fraîches"], ["Fais fondre le poireau et la courgette 6 min.", "Ajoute les épinards jusqu'à ce qu'ils tombent.", "Casse les œufs dessus, couvre 5 min, ajoute la feta et les herbes."], 20, ["proteine", "vege"]),
        ("Chilaquiles légers", "🌽", "Mexicaine", ["1 tortilla de maïs", "150 g de salsa verde ou tomate", "1 œuf", "2 c. à soupe de yaourt grec", "1/4 d'oignon rouge", "Coriandre"], ["Coupe la tortilla en triangles et dore-les au four 8 min.", "Chauffe la salsa et enrobe les chips.", "Ajoute l'œuf au plat, le yaourt, l'oignon et la coriandre."], 15, ["vege", "rapide"]),
        ("Idli-sambar express", "🍘", "Indienne", ["3 idlis (prêts à cuire ou maison)", "80 g de lentilles corail", "1/2 tomate", "1 c. à café de poudre sambar (ou curry)", "Coriandre"], ["Fais cuire les lentilles 15 min avec la tomate et les épices.", "Réchauffe les idlis à la vapeur.", "Sers les idlis avec le sambar."], 20, ["vege"]),
        ("Tartine nordique saumon-concombre", "🐟", "Nordique", ["2 tranches de pain de seigle", "2 c. à soupe de fromage frais", "2 tranches de saumon fumé", "1/4 de concombre", "Aneth"], ["Tartine le pain de fromage frais.", "Ajoute le concombre en fines tranches et le saumon.", "Parsème d'aneth."], 5, ["proteine", "rapide"]),
    ]
    for n, e, c, i, s, t, tags in world:
        out.append(dict(n=n, e=e, m=["pd"], t=t, tags=tags, c=c, i=i, s=s))
    return out


def snacks():
    out = []
    for name, extra in [("classique", "1 c. à café de cumin"), ("betterave", "1 petite betterave cuite"), ("poivron grillé", "1/2 poivron rouge grillé"), ("avocat", "1/2 avocat"), ("patate douce", "100 g de patate douce cuite")]:
        out.append(dict(n=f"Houmous {name} et crudités", e="🥕", m=["col"], t=8, tags=["vege", "leger", "rapide"], c="Libanaise",
                        i=["100 g de pois chiches cuits", "1 c. à soupe de tahini", "1/2 citron", extra, "Carottes, concombre et radis en bâtonnets"],
                        s=["Mixe pois chiches, tahini, citron et la garniture avec 2 c. à soupe d'eau.", "Coupe les crudités en bâtonnets.", "Sers l'houmous avec les crudités."]))
    for name, extra in [("cacao-noisette", "1 c. à soupe de cacao + 30 g de noisettes"), ("coco-citron", "2 c. à soupe de coco râpée + zeste de citron"), ("cacahuète", "1 c. à soupe de beurre de cacahuète"), ("matcha", "1 c. à café de matcha + 30 g de noix de cajou"), ("abricot-amande", "4 abricots secs + 30 g d'amandes"), ("figue-noix", "3 figues sèches + 30 g de noix")]:
        out.append(dict(n=f"Energy balls {name}", e="⚡", m=["col"], t=15, tags=["vege", "rapide"], c="Maison",
                        i=["6 dattes dénoyautées", "2 c. à soupe de flocons d'avoine", extra],
                        s=["Mixe tous les ingrédients en pâte.", "Forme 6 petites boules.", "Garde-les au frigo (une semaine)."]))
    for f, nb in [("Pomme", "beurre d'amande"), ("Banane", "beurre de cacahuète"), ("Poire", "purée de noisette"), ("Dattes", "amandes"), ("Clémentines", "noix de cajou")]:
        out.append(dict(n=f"{f} et {nb}", e="🍎", m=["col"], t=2, tags=["vege", "rapide"], c="Maison",
                        i=[f"1 portion de {f.lower()}", f"1 c. à soupe de {nb}"], s=["Coupe le fruit si besoin.", f"Accompagne-le de {nb}."]))
    for name, ings in [("vert protéiné", ["1 poignée d'épinards", "1/2 banane", "150 g de skyr", "200 ml de lait"]), ("café protéiné", ["1 expresso refroidi", "1 banane", "150 g de skyr", "150 ml de lait"]), ("fraise-avoine", ["100 g de fraises", "2 c. à soupe d'avoine", "150 ml de lait", "1 yaourt"]),
                       ("mangue-lassi", ["1/2 mangue", "150 g de yaourt nature", "1 pincée de cardamome", "100 ml de lait"]), ("myrtille-amande", ["100 g de myrtilles", "200 ml de lait d'amande", "1 c. à soupe de purée d'amande"])]:
        tags = ["vege", "rapide"] + (["proteine"] if "skyr" in " ".join(ings) else [])
        out.append(dict(n=f"Smoothie {name}", e="🥤", m=["col", "pd"], t=5, tags=tags, c="Maison", i=ings, s=["Mets tout dans le blender.", "Mixe 30 secondes et bois aussitôt."]))
    for sp in ["paprika fumé", "curry", "za'atar", "cumin et citron"]:
        out.append(dict(n=f"Pois chiches grillés {sp}", e="🌶️", m=["col"], t=25, tags=["vege", "proteine"], c="Maison",
                        i=["150 g de pois chiches cuits", "1 c. à café d'huile d'olive", f"1 c. à café de {sp}", "1 pincée de sel"],
                        s=["Sèche bien les pois chiches et enrobe-les d'huile et d'épices.", "Enfourne 20 à 25 min à 200 °C en remuant à mi-cuisson.", "Laisse refroidir pour qu'ils croustillent."]))
    for dip, ings, c in [("Guacamole", ["1 avocat", "1/2 citron vert", "1/4 d'oignon rouge", "Coriandre", "Crudités ou 2 galettes de maïs"], "Mexicaine"),
                         ("Tzatziki", ["150 g de yaourt grec", "1/4 de concombre", "1/2 gousse d'ail", "Menthe ou aneth", "Crudités"], "Grecque"),
                         ("Baba ganoush", ["1 aubergine", "1 c. à soupe de tahini", "1/2 citron", "1/2 gousse d'ail", "Crudités"], "Libanaise"),
                         ("Edamame sel et piment", ["150 g d'edamame", "Fleur de sel", "1 pincée de piment"], "Japonaise"),
                         ("Pop-corn maison au paprika", ["40 g de maïs à pop-corn", "1 c. à café d'huile", "1/2 c. à café de paprika"], "Maison"),
                         ("Yaourt grec, miel et noix", ["170 g de yaourt grec", "1 c. à café de miel", "1 poignée de noix"], "Grecque"),
                         ("Rouleaux de printemps express", ["2 galettes de riz", "1/4 de concombre", "1 carotte", "Menthe", "50 g de crevettes ou de tofu", "Sauce soja"], "Vietnamienne"),
                         ("Muhammara et crudités", ["1 poivron rouge grillé", "30 g de noix", "1 c. à café de mélasse de grenade (ou miel)", "1/2 c. à café de cumin", "Crudités"], "Syrienne")]:
        tags = ["vege", "rapide", "leger"] if dip not in ("Rouleaux de printemps express",) else ["leger", "rapide"]
        if dip == "Baba ganoush":
            tags = ["vege", "leger"]
        out.append(dict(n=dip, e="🥄", m=["col"], t=30 if dip == "Baba ganoush" else 10, tags=tags, c=c, i=ings,
                        s=["Prépare et coupe les ingrédients.", "Mixe ou mélange selon la recette (l'aubergine du baba ganoush se rôtit 25 min à 220 °C avant).", "Sers frais."]))
    return out


# ---------------------------------------------------------------- cheat meals (~10 %)
def cheat_meals():
    out = []
    pizzas = [("Margherita", ["100 g de sauce tomate", "1 boule de mozzarella", "Basilic frais"]), ("Reine", ["100 g de sauce tomate", "1 tranche de jambon", "4 champignons", "1/2 mozzarella"]),
              ("Quatre fromages", ["50 g de mozzarella", "30 g de gorgonzola", "20 g de parmesan", "30 g de chèvre"]), ("Pepperoni", ["100 g de sauce tomate", "12 tranches de pepperoni", "1/2 mozzarella"]),
              ("Chèvre-miel", ["2 c. à soupe de crème fraîche", "60 g de chèvre", "1 c. à soupe de miel", "Quelques noix"]), ("Calzone jambon-œuf", ["100 g de sauce tomate", "1 tranche de jambon", "1 œuf", "1/2 mozzarella"]),
              ("Diavola", ["100 g de sauce tomate", "Chorizo piquant", "1/2 mozzarella", "Piment"]), ("Burrata et jambon cru", ["100 g de sauce tomate", "1 burrata", "2 tranches de jambon cru", "Roquette"]),
              ("Barbecue poulet", ["2 c. à soupe de sauce barbecue", "100 g de poulet cuit", "1/4 d'oignon rouge", "1/2 mozzarella"]), ("Végétarienne gourmande", ["100 g de sauce tomate", "Poivron, champignons, olives", "1/2 mozzarella", "Origan"])]
    for name, ings in pizzas:
        out.append(dict(n=f"Pizza {name.lower() if name[0].islower() else name}", e="🍕", m=["din"], t=25, tags=["cheat"], c="Italienne",
                        i=["1 pâte à pizza"] + ings,
                        s=["Préchauffe le four à 250 °C (le plus chaud possible).", "Étale la pâte et garnis-la.", "Enfourne 10 à 12 min jusqu'à ce que les bords soient dorés.", "Savoure, c'est le cheat meal de la semaine !"]))
    burgers = [("classique", ["1 steak haché 15 %", "1 tranche de cheddar", "Salade, tomate, oignon", "Ketchup et moutarde"]), ("bacon cheddar", ["1 steak haché", "2 tranches de bacon", "2 tranches de cheddar", "Oignons caramélisés"]),
               ("double smash", ["2 steaks hachés fins de 80 g", "2 tranches de cheddar", "Cornichons", "Sauce burger"]), ("chicken crispy", ["1 filet de poulet pané", "Salade, tomate", "Mayonnaise épicée"]),
               ("raclette", ["1 steak haché", "2 tranches de raclette", "1 tranche de jambon cru", "Oignons"]), ("barbecue", ["1 steak haché", "Sauce barbecue", "Rondelles d'oignon frites", "Cheddar"]),
               ("végé halloumi", ["2 tranches d'halloumi grillées", "Poivron grillé", "Roquette", "Sauce yaourt-harissa"]), ("fish burger", ["1 filet de poisson pané", "Sauce tartare", "Salade"])]
    for name, ings in burgers:
        out.append(dict(n=f"Burger {name} et frites", e="🍔", m=["din"], t=30, tags=["cheat"], c="Américaine",
                        i=["1 pain à burger brioché"] + ings + ["150 g de frites"],
                        s=["Enfourne les frites selon le paquet (ou à l'air fryer).", "Cuis la viande (ou le poisson, le poulet, l'halloumi) à la poêle bien chaude.", "Toaste le pain et monte le burger.", "Sers avec les frites."]))
    simple = [
        ("Tacos frites-cordon bleu (tacos lyonnais)", "🌯", "Française", ["1 grande tortilla", "1 cordon bleu", "100 g de frites", "Sauce fromagère", "Cheddar"]),
        ("Fish and chips", "🐟", "Britannique", ["150 g de cabillaud", "Pâte à beignet (farine + bière ou eau gazeuse)", "200 g de frites", "Sauce tartare", "Petits pois"]),
        ("Poulet frit croustillant (style Korean fried chicken)", "🍗", "Coréenne", ["300 g de pilons ou hauts de cuisse", "Fécule de maïs", "Sauce gochujang-miel", "Sésame"]),
        ("Tenders de poulet et sauce miel-moutarde", "🍗", "Américaine", ["200 g de filets de poulet", "Chapelure panko", "1 œuf", "Sauce miel-moutarde", "Frites"]),
        ("Ramen tonkotsu", "🍜", "Japonaise", ["Bouillon de porc riche", "Nouilles ramen", "Tranches de poitrine de porc chashu", "1 œuf mariné", "Oignon nouveau, nori"]),
        ("Pad see ew au bœuf", "🥡", "Thaïlandaise", ["Larges nouilles de riz", "130 g de bœuf", "Brocoli chinois", "Sauce soja sucrée", "1 œuf"]),
        ("Mac and cheese gratiné", "🧀", "Américaine", ["100 g de macaronis", "100 g de cheddar", "200 ml de lait", "1 c. à soupe de beurre", "1 c. à soupe de farine", "Chapelure"]),
        ("Lasagnes bolognaise", "🍝", "Italienne", ["Feuilles de lasagne", "150 g de bœuf haché", "Sauce tomate", "Béchamel", "Parmesan"]),
        ("Carbonara (la vraie)", "🍝", "Italienne", ["100 g de spaghetti", "60 g de guanciale ou lardons", "2 jaunes d'œufs", "30 g de pecorino", "Poivre noir"]),
        ("Tartiflette", "🧀", "Française", ["300 g de pommes de terre", "100 g de lardons", "1/2 reblochon", "1 oignon", "Crème fraîche"]),
        ("Raclette maison", "🧀", "Suisse", ["300 g de pommes de terre", "150 g de fromage à raclette", "Charcuterie", "Cornichons"]),
        ("Poutine", "🍟", "Québécoise", ["200 g de frites", "80 g de fromage en grains (ou mozzarella)", "Sauce brune (gravy)"]),
        ("Hot-dog new-yorkais", "🌭", "Américaine", ["1 pain à hot-dog", "1 saucisse de Francfort", "Oignons frits", "Moutarde, ketchup", "Cornichons"]),
        ("Croque-monsieur à la béchamel", "🥪", "Française", ["2 tranches de pain de mie", "1 tranche de jambon", "Béchamel", "50 g d'emmental"]),
        ("Kebab assiette frites", "🥙", "Turque", ["150 g de viande kebab", "Frites", "Salade, tomate, oignon", "Sauce blanche"]),
        ("Quesadillas au fromage et chorizo", "🧀", "Mexicaine", ["2 tortillas", "80 g de cheddar ou mozzarella", "Quelques tranches de chorizo", "Crème aigre"]),
        ("Nachos gratinés", "🌮", "Tex-Mex", ["100 g de chips de maïs", "80 g de cheddar", "Haricots rouges", "Guacamole", "Crème aigre", "Jalapeños"]),
        ("Gyoza frits et riz cantonais", "🥟", "Japonaise", ["10 gyoza", "Riz cantonais", "Sauce soja-vinaigre"]),
        ("Pâtes à la crème, lardons et champignons", "🍝", "Française", ["100 g de pâtes", "80 g de lardons", "100 g de champignons", "10 cl de crème fraîche", "Parmesan"]),
        ("Aligot-saucisse", "🧀", "Française", ["300 g de pommes de terre", "100 g de tomme fraîche", "1 saucisse de Toulouse", "Crème, ail"]),
        ("Chicken tikka et naan au fromage", "🫓", "Indienne", ["150 g de poulet", "Sauce tikka masala crémeuse", "1 naan au fromage", "Riz basmati"]),
        ("Club sandwich et chips", "🥪", "Américaine", ["3 tranches de pain de mie", "Poulet, bacon, œuf", "Salade, tomate, mayonnaise", "Chips"]),
        ("Bao au porc caramélisé", "🥟", "Taïwanaise", ["2 pains bao", "150 g de poitrine de porc", "Sauce hoisin", "Concombre, cacahuètes, coriandre"]),
        ("Pizza tacos (crunchwrap)", "🌮", "Tex-Mex", ["1 grande tortilla", "Bœuf haché épicé", "Cheddar", "1 tostada", "Crème aigre, salade"]),
        ("Gratin dauphinois et côte de porc", "🥔", "Française", ["300 g de pommes de terre", "20 cl de crème", "1 gousse d'ail", "1 côte de porc"]),
        ("Fondue savoyarde", "🫕", "Française", ["200 g de mélange de fromages (comté, beaufort, emmental)", "100 ml de vin blanc (ou bouillon)", "1 gousse d'ail", "Pain de campagne en cubes", "Charcuterie"]),
        ("Choucroute garnie", "🥬", "Alsacienne", ["250 g de choucroute cuite", "1 saucisse de Strasbourg", "1 tranche de lard", "2 pommes de terre", "Moutarde"]),
        ("Chicken wings buffalo et frites", "🍗", "Américaine", ["8 ailes de poulet", "Sauce buffalo (piquante)", "Sauce blue cheese", "Frites", "Bâtonnets de céleri"]),
        ("Poulet katsu curry", "🍛", "Japonaise", ["1 escalope de poulet panée au panko", "Sauce curry japonaise", "Riz japonais", "Pickles"]),
        ("Pad krapow et œuf frit", "🌶️", "Thaïlandaise", ["150 g de porc ou poulet haché", "Basilic sacré", "Piment, ail", "Sauce d'huître", "1 œuf frit", "Riz jasmin"]),
        ("Calamars frits et sauce aïoli", "🦑", "Espagnole", ["200 g d'anneaux de calamar", "Farine", "Huile de friture", "Aïoli", "Citron"]),
        ("Nems et samoussas (assiette de 8)", "🥟", "Vietnamienne", ["4 nems", "4 samoussas", "Salade, menthe", "Sauce nuoc-mâm sucrée"]),
        ("Tempura de crevettes et légumes", "🍤", "Japonaise", ["8 crevettes", "Légumes en bâtonnets", "Pâte à tempura glacée", "Sauce tentsuyu"]),
        ("Philly cheesesteak", "🥖", "Américaine", ["1 pain sub", "150 g de bœuf en fines lamelles", "Oignons et poivrons grillés", "Provolone ou cheddar fondu"]),
        ("Bagel pastrami-cheddar", "🥯", "New-yorkaise", ["1 bagel", "80 g de pastrami", "Cheddar", "Cornichons", "Moutarde au miel"]),
        ("Panini trois fromages", "🥪", "Italienne", ["1 pain panini", "Mozzarella, gorgonzola, parmesan", "Jambon cru", "Pesto"]),
        ("Croque-madame et frites", "🍳", "Française", ["2 tranches de pain de mie", "Jambon, béchamel, emmental", "1 œuf au plat", "Frites"]),
        ("Gyros pita frites", "🥙", "Grecque", ["1 pain pita", "150 g de porc gyros", "Frites dans le sandwich", "Tzatziki", "Tomate, oignon"]),
        ("Pâtes quatre fromages", "🧀", "Italienne", ["100 g de penne", "Gorgonzola, parmesan, mozzarella, emmental", "10 cl de crème"]),
        ("Burger chèvre-miel et frites de patate douce", "🍔", "Française", ["1 pain brioché", "1 steak haché", "Chèvre, miel, roquette", "Frites de patate douce"]),
        ("Tacos al pastor", "🌮", "Mexicaine", ["3 tortillas de maïs", "150 g de porc mariné aux piments et à l'ananas", "Ananas grillé", "Oignon, coriandre, citron vert"]),
        ("Pizza calzone quatre saisons", "🍕", "Italienne", ["1 pâte à pizza", "Sauce tomate", "Jambon, champignons, artichauts, olives", "Mozzarella"]),
        ("Katsu sando", "🥪", "Japonaise", ["2 tranches de pain de mie moelleux", "1 escalope de porc panée", "Chou blanc émincé", "Sauce tonkatsu"]),
    ]
    for n, e, c, i in simple:
        t, steps = CHEAT_STEPS[n]
        out.append(dict(n=n, e=e, m=["din"], t=t, tags=["cheat"], c=c, i=i, s=steps))
    desserts = [
        ("Tiramisu", "☕", "Italienne", ["2 œufs", "125 g de mascarpone", "40 g de sucre", "8 biscuits cuillère", "1 grand café froid", "Cacao"], 20),
        ("Brownie fondant", "🍫", "Américaine", ["100 g de chocolat noir", "60 g de beurre", "1 œuf", "50 g de sucre", "30 g de farine", "Noix de pécan"], 35),
        ("Cookies géants aux pépites", "🍪", "Américaine", ["60 g de beurre mou", "50 g de sucre roux", "1 œuf", "120 g de farine", "80 g de pépites de chocolat"], 25),
        ("Crêpes au Nutella", "🥞", "Française", ["125 g de farine", "2 œufs", "250 ml de lait", "Pâte à tartiner", "Banane (facultatif)"], 30),
        ("Gaufres chantilly", "🧇", "Belge", ["125 g de farine", "1 œuf", "200 ml de lait", "30 g de beurre fondu", "Chantilly"], 25),
        ("Churros et chocolat chaud", "🍩", "Espagnole", ["125 g de farine", "250 ml d'eau", "Sucre, cannelle", "Huile de friture", "Chocolat chaud épais"], 30),
        ("Cheesecake New York (part)", "🍰", "Américaine", ["Biscuits émiettés + beurre", "200 g de cream cheese", "1 œuf", "50 g de sucre", "Coulis de fruits rouges"], 60),
        ("Fondant au chocolat cœur coulant", "🍫", "Française", ["50 g de chocolat noir", "40 g de beurre", "1 œuf", "30 g de sucre", "15 g de farine"], 20),
        ("Banana split", "🍌", "Américaine", ["1 banane", "3 boules de glace (vanille, chocolat, fraise)", "Chantilly", "Sauce chocolat", "Amandes grillées"], 10),
        ("Pancakes sirop d'érable et bacon", "🥞", "Canadienne", ["Pâte à pancakes", "Sirop d'érable", "2 tranches de bacon", "Beurre"], 25),
        ("Crème brûlée", "🍮", "Française", ["2 jaunes d'œufs", "20 cl de crème", "30 g de sucre", "Vanille", "Cassonade"], 50),
        ("Mochis glacés", "🍡", "Japonaise", ["3 mochis glacés du commerce (mangue, matcha, chocolat)"], 2),
        ("Tarte tatin et crème fraîche", "🍎", "Française", ["1 pâte feuilletée", "3 pommes", "60 g de sucre", "30 g de beurre", "Crème fraîche"], 50),
        ("Donuts glacés", "🍩", "Américaine", ["Pâte levée (farine, levure, lait, beurre)", "Huile de friture", "Glaçage sucre glace"], 90),
        ("Sundae caramel beurre salé", "🍨", "Française", ["3 boules de glace vanille", "Caramel au beurre salé", "Chantilly", "Éclats de cookies"], 5),
        ("Pain perdu brioché", "🍞", "Française", ["2 tranches de brioche", "1 œuf", "100 ml de lait", "Sucre, cannelle", "Beurre"], 15),
        ("Milkshake Oreo", "🥤", "Américaine", ["3 boules de glace vanille", "150 ml de lait", "4 biscuits Oreo", "Chantilly"], 5),
        ("Profiteroles", "🍫", "Française", ["6 choux", "Glace vanille", "Sauce chocolat chaude", "Amandes effilées"], 15),
        ("Baklava (3 pièces)", "🍯", "Turque", ["3 baklavas", "Thé à la menthe"], 2),
        ("Crumble pomme-fruits rouges et glace", "🍏", "Britannique", ["2 pommes", "100 g de fruits rouges", "40 g de farine", "30 g de beurre", "30 g de sucre", "Glace vanille"], 40),
        ("Tarte au citron meringuée (part)", "🍋", "Française", ["1 part de tarte au citron meringuée (pâtisserie ou maison)"], 5),
        ("Éclair au chocolat", "🍫", "Française", ["1 éclair au chocolat de ta pâtisserie préférée"], 2),
        ("Paris-Brest (part)", "🥐", "Française", ["1 part de Paris-Brest", "Un bon café"], 2),
        ("Fondue au chocolat et fruits", "🍓", "Suisse", ["100 g de chocolat noir", "50 ml de crème", "Fraises, banane, ananas", "Guimauves"], 15),
        ("Cinnamon rolls", "🌀", "Suédoise", ["Pâte briochée", "Beurre, cassonade, cannelle", "Glaçage au fromage frais"], 90),
        ("Muffins aux myrtilles", "🧁", "Américaine", ["150 g de farine", "1 œuf", "80 g de sucre", "80 ml de lait", "50 g de beurre fondu", "100 g de myrtilles"], 35),
        ("Panna cotta coulis de fruits rouges", "🍮", "Italienne", ["20 cl de crème", "25 g de sucre", "1 feuille de gélatine", "Vanille", "Coulis de fruits rouges"], 15),
        ("Riz au lait et caramel", "🍚", "Française", ["50 g de riz rond", "400 ml de lait", "30 g de sucre", "Vanille", "Caramel"], 45),
        ("Clafoutis aux cerises", "🍒", "Française", ["200 g de cerises", "2 œufs", "40 g de farine", "40 g de sucre", "150 ml de lait"], 45),
        ("Crêpes Suzette", "🍊", "Française", ["3 crêpes", "Beurre, sucre", "Jus et zeste d'orange", "Grand Marnier (facultatif)"], 20),
        ("Kouign-amann (part)", "🧈", "Bretonne", ["1 part de kouign-amann", "Une tasse de cidre ou de thé"], 2),
        ("Tarte au chocolat et caramel", "🍫", "Française", ["1 fond de tarte sablé", "100 g de chocolat noir", "10 cl de crème", "Caramel au beurre salé"], 30),
        ("Gâteau basque (part)", "🥮", "Basque", ["1 part de gâteau basque à la crème ou à la cerise"], 2),
        ("Affogato et cookie", "☕", "Italienne", ["1 boule de glace vanille", "1 expresso bien chaud", "1 cookie"], 5),
    ]
    for n, e, c, i, t in desserts:
        out.append(dict(n=n, e=e, m=["col"], t=t, tags=["cheat"], c=c, i=i, s=DESSERT_STEPS[n]))
    return out


# real steps for every cheat meal: (minutes, steps)
CHEAT_STEPS = {
    "Tacos frites-cordon bleu (tacos lyonnais)": (30, ["Fais cuire les frites et le cordon bleu au four (ou à l'air fryer).", "Coupe le cordon bleu en lanières.", "Garnis la tortilla : frites, cordon bleu, sauce fromagère, cheddar, et plie-la en rectangle.", "Dore-la 2 min par face dans une poêle bien chaude."]),
    "Fish and chips": (35, ["Fais cuire les frites.", "Mélange farine et bière (ou eau gazeuse) en pâte épaisse.", "Trempe le cabillaud dans la pâte et fais-le frire 5 à 6 min à 180 °C.", "Sers avec la sauce tartare et les petits pois."]),
    "Poulet frit croustillant (style Korean fried chicken)": (45, ["Enrobe le poulet de fécule.", "Fais-le frire 8 min à 170 °C, laisse reposer 5 min, puis refais frire 3 min à 190 °C : c'est le secret du croustillant.", "Fais chauffer la sauce gochujang-miel 1 min.", "Enrobe le poulet de sauce et parsème de sésame."]),
    "Tenders de poulet et sauce miel-moutarde": (30, ["Coupe le poulet en lanières.", "Passe-les dans l'œuf battu puis dans le panko.", "Fais-les cuire 15 min à 200 °C (ou frire 4 min).", "Mélange miel et moutarde pour la sauce et sers avec les frites."]),
    "Ramen tonkotsu": (30, ["Fais chauffer le bouillon de porc (du commerce ou maison).", "Fais cuire les nouilles selon le paquet.", "Fais dorer les tranches de chashu à la poêle.", "Monte le bol : nouilles, bouillon brûlant, chashu, œuf mariné coupé en deux, oignon nouveau et nori."]),
    "Pad see ew au bœuf": (20, ["Saisis le bœuf en lanières 2 min à feu vif.", "Ajoute le brocoli chinois 2 min.", "Ajoute les nouilles et la sauce soja sucrée, pousse sur le côté et brouille l'œuf.", "Mélange le tout jusqu'à ce que les nouilles caramélisent légèrement."]),
    "Mac and cheese gratiné": (30, ["Fais cuire les macaronis al dente.", "Fais un roux avec le beurre et la farine, ajoute le lait et laisse épaissir.", "Ajoute le cheddar hors du feu, puis les pâtes.", "Verse dans un plat, couvre de chapelure et gratine 10 min à 200 °C."]),
    "Lasagnes bolognaise": (60, ["Fais revenir le bœuf, ajoute la sauce tomate et laisse mijoter 15 min.", "Alterne dans un plat : feuilles de lasagne, bolognaise, béchamel.", "Termine par la béchamel et le parmesan.", "Enfourne 35 min à 180 °C et laisse reposer 5 min."]),
    "Carbonara (la vraie)": (15, ["Fais cuire les spaghetti al dente.", "Fais dorer le guanciale à sec.", "Mélange les jaunes d'œufs avec le pecorino et beaucoup de poivre.", "Hors du feu, mélange les pâtes avec le guanciale puis la crème d'œufs et un peu d'eau de cuisson : pas de crème fraîche !"]),
    "Tartiflette": (50, ["Fais cuire les pommes de terre 15 min à l'eau et coupe-les en rondelles.", "Fais revenir les lardons et l'oignon.", "Mélange avec les pommes de terre et la crème dans un plat, pose le reblochon coupé en deux dessus.", "Enfourne 20 min à 200 °C."]),
    "Raclette maison": (30, ["Fais cuire les pommes de terre en robe des champs.", "Fais fondre le fromage à raclette dans les poêlons (ou au four).", "Nappe les pommes de terre de fromage fondu.", "Sers avec la charcuterie et les cornichons."]),
    "Poutine": (25, ["Fais cuire les frites bien croustillantes.", "Fais chauffer la sauce brune.", "Dispose le fromage en grains sur les frites brûlantes.", "Nappe de sauce bien chaude pour qu'il fonde."]),
    "Hot-dog new-yorkais": (10, ["Fais chauffer la saucisse 5 min dans l'eau frémissante.", "Toaste légèrement le pain.", "Glisse la saucisse dans le pain.", "Ajoute moutarde, ketchup, oignons frits et cornichons."]),
    "Croque-monsieur à la béchamel": (20, ["Tartine les tranches de pain de béchamel.", "Ajoute le jambon et la moitié de l'emmental, referme.", "Nappe le dessus de béchamel et du reste d'emmental.", "Enfourne 10 min à 200 °C jusqu'à ce que ce soit doré."]),
    "Kebab assiette frites": (25, ["Fais cuire les frites.", "Fais griller la viande kebab à la poêle bien chaude 4 min.", "Coupe la salade, la tomate et l'oignon.", "Dresse l'assiette et ajoute la sauce blanche."]),
    "Quesadillas au fromage et chorizo": (15, ["Garnis une tortilla de fromage et de chorizo.", "Couvre de la seconde tortilla.", "Dore 2 à 3 min par face à feu moyen.", "Coupe en quarts et sers avec la crème aigre."]),
    "Nachos gratinés": (15, ["Étale les chips de maïs sur une plaque.", "Ajoute les haricots rouges et le cheddar.", "Gratine 6 à 8 min à 200 °C.", "Ajoute guacamole, crème aigre et jalapeños."]),
    "Gyoza frits et riz cantonais": (20, ["Fais dorer les gyoza 2 min à la poêle huilée.", "Ajoute un fond d'eau, couvre et laisse cuire 5 min à la vapeur.", "Réchauffe le riz cantonais.", "Sers avec la sauce soja-vinaigre."]),
    "Pâtes à la crème, lardons et champignons": (20, ["Fais cuire les pâtes.", "Fais dorer les lardons, puis les champignons émincés.", "Ajoute la crème et laisse réduire 2 min.", "Mélange avec les pâtes et le parmesan."]),
    "Aligot-saucisse": (40, ["Fais cuire les pommes de terre et écrase-les en purée avec la crème et l'ail.", "Ajoute la tomme fraîche en lamelles et mélange énergiquement jusqu'à ce que ça file.", "Fais griller la saucisse 15 min.", "Sers l'aligot bien chaud avec la saucisse."]),
    "Chicken tikka et naan au fromage": (30, ["Lance le riz.", "Fais dorer le poulet en morceaux.", "Ajoute la sauce tikka masala et laisse mijoter 10 min.", "Réchauffe le naan au four et sers le tout."]),
    "Club sandwich et chips": (20, ["Fais griller le poulet, le bacon et cuis l'œuf au plat.", "Toaste les 3 tranches de pain.", "Monte en deux étages : mayonnaise, salade, tomate, poulet, bacon, œuf.", "Coupe en triangles, pique avec des cure-dents et sers avec les chips."]),
    "Bao au porc caramélisé": (45, ["Fais cuire la poitrine de porc en tranches 10 min, puis laque-la à la sauce hoisin.", "Réchauffe les pains bao 5 min à la vapeur.", "Garnis avec le porc, le concombre en fines tranches.", "Ajoute cacahuètes concassées et coriandre."]),
    "Pizza tacos (crunchwrap)": (25, ["Fais revenir le bœuf haché avec les épices.", "Au centre de la grande tortilla : bœuf, cheddar, la tostada, crème aigre et salade.", "Replie les bords en plis vers le centre pour fermer.", "Dore 3 min par face côté pliures d'abord."]),
    "Gratin dauphinois et côte de porc": (75, ["Coupe les pommes de terre en fines rondelles.", "Range-les dans un plat frotté à l'ail, couvre de crème salée-poivrée.", "Enfourne 1 h à 170 °C.", "Poêle la côte de porc 5 min par face et sers avec le gratin."]),
    "Fondue savoyarde": (25, ["Frotte le caquelon avec l'ail et fais chauffer le vin.", "Ajoute les fromages râpés petit à petit en remuant en huit.", "Garde sur le réchaud à feu doux.", "Trempe les cubes de pain et sers avec la charcuterie."]),
    "Choucroute garnie": (40, ["Réchauffe la choucroute 20 min à couvert avec un fond d'eau.", "Ajoute le lard et la saucisse 10 min.", "Fais cuire les pommes de terre à la vapeur.", "Sers avec la moutarde."]),
    "Chicken wings buffalo et frites": (45, ["Fais cuire les ailes 35 min à 220 °C en les retournant à mi-cuisson.", "Lance les frites.", "Enrobe les ailes de sauce buffalo chaude.", "Sers avec la sauce blue cheese et les bâtonnets de céleri."]),
    "Poulet katsu curry": (35, ["Fais cuire le riz.", "Fais frire (ou cuire au four 20 min) l'escalope panée au panko.", "Fais chauffer la sauce curry japonaise.", "Coupe le poulet en tranches, sers sur le riz nappé de sauce, avec les pickles."]),
    "Pad krapow et œuf frit": (15, ["Fais revenir l'ail et le piment 30 s.", "Ajoute la viande hachée et saisis 4 min à feu vif.", "Ajoute la sauce d'huître et le basilic hors du feu.", "Sers sur le riz avec un œuf frit bien croustillant."]),
    "Calamars frits et sauce aïoli": (20, ["Sèche bien les anneaux de calamar et passe-les dans la farine.", "Fais-les frire 2 min à 180 °C (pas plus, sinon ils durcissent).", "Égoutte sur du papier absorbant et sale.", "Sers avec l'aïoli et le citron."]),
    "Nems et samoussas (assiette de 8)": (20, ["Fais cuire nems et samoussas au four 15 min à 200 °C (ou frits 4 min).", "Prépare les feuilles de salade et de menthe.", "Enroule chaque nem dans une feuille de salade avec de la menthe.", "Trempe dans la sauce nuoc-mâm sucrée."]),
    "Tempura de crevettes et légumes": (25, ["Prépare une pâte à tempura avec de l'eau glacée, sans trop mélanger.", "Trempe crevettes et légumes dans la pâte.", "Fais-les frire 2 à 3 min à 180 °C.", "Sers aussitôt avec la sauce tentsuyu."]),
    "Philly cheesesteak": (20, ["Fais revenir oignons et poivrons 6 min.", "Saisis le bœuf en fines lamelles 2 min à feu vif.", "Couvre de fromage pour qu'il fonde.", "Garnis le pain sub grillé."]),
    "Bagel pastrami-cheddar": (10, ["Coupe et toaste le bagel.", "Tartine de moutarde au miel.", "Garnis de pastrami, cheddar et cornichons.", "Passe 2 min au four pour faire fondre le fromage."]),
    "Panini trois fromages": (10, ["Tartine le pain de pesto.", "Garnis des trois fromages et du jambon cru.", "Presse-le dans un appareil à panini (ou dans une poêle avec un poids) 4 min.", "Coupe en deux et sers bien chaud."]),
    "Croque-madame et frites": (25, ["Prépare le croque-monsieur à la béchamel et enfourne 10 min à 200 °C.", "Lance les frites.", "Fais cuire un œuf au plat.", "Pose l'œuf sur le croque et sers avec les frites."]),
    "Gyros pita frites": (20, ["Fais griller la viande gyros à la poêle.", "Réchauffe la pita.", "Garnis : tzatziki, viande, tomate, oignon et quelques frites.", "Roule dans du papier et déguste."]),
    "Pâtes quatre fromages": (15, ["Fais cuire les penne.", "Fais fondre les fromages dans la crème à feu doux.", "Mélange avec les pâtes.", "Poivre généreusement."]),
    "Burger chèvre-miel et frites de patate douce": (35, ["Enfourne les frites de patate douce 25 min à 210 °C.", "Poêle le steak.", "Pose le chèvre sur le steak en fin de cuisson et arrose de miel.", "Monte le burger avec la roquette."]),
    "Tacos al pastor": (30, ["Fais mariner le porc en lamelles avec les piments et l'ananas.", "Saisis-le à feu vif 5 min.", "Grille quelques morceaux d'ananas.", "Garnis les tortillas chaudes : porc, ananas, oignon, coriandre, citron vert."]),
    "Pizza calzone quatre saisons": (25, ["Préchauffe le four à 250 °C.", "Étale la pâte et garnis une moitié.", "Replie et soude bien les bords.", "Enfourne 12 à 14 min."]),
    "Katsu sando": (25, ["Fais cuire l'escalope panée (four 20 min ou friture 4 min).", "Tartine le pain de sauce tonkatsu.", "Ajoute le chou émincé et le porc.", "Presse légèrement, coupe les croûtes et tranche en deux."]),
}
DESSERT_STEPS = {
    "Tiramisu": ["Sépare les blancs des jaunes. Fouette les jaunes avec le sucre, ajoute le mascarpone.", "Monte les blancs en neige et incorpore-les délicatement.", "Trempe rapidement les biscuits dans le café et alterne couches de biscuits et de crème.", "Laisse au frais au moins 4 h et saupoudre de cacao."],
    "Brownie fondant": ["Fais fondre le chocolat avec le beurre.", "Ajoute l'œuf, le sucre, puis la farine et les noix.", "Verse dans un petit moule.", "Enfourne 20 min à 180 °C : le centre doit rester fondant."],
    "Cookies géants aux pépites": ["Mélange le beurre mou et le sucre roux, ajoute l'œuf.", "Ajoute la farine puis les pépites.", "Forme 4 grosses boules sur une plaque.", "Enfourne 11 min à 180 °C : ils durcissent en refroidissant."],
    "Crêpes au Nutella": ["Mélange farine, œufs et lait jusqu'à une pâte lisse, laisse reposer 30 min.", "Fais cuire de fines crêpes dans une poêle beurrée.", "Tartine de pâte à tartiner.", "Ajoute quelques rondelles de banane et plie en quatre."],
    "Gaufres chantilly": ["Mélange farine, œuf, lait et beurre fondu.", "Fais chauffer le gaufrier.", "Cuis les gaufres 3 à 4 min.", "Sers avec la chantilly."],
    "Churros et chocolat chaud": ["Porte l'eau à ébullition, verse la farine d'un coup et mélange jusqu'à une boule.", "Mets la pâte dans une poche à douille cannelée et forme des bâtons dans l'huile chaude.", "Fais frire 2 à 3 min, égoutte et roule dans le sucre-cannelle.", "Trempe dans le chocolat chaud épais."],
    "Cheesecake New York (part)": ["Tasse les biscuits émiettés au beurre dans un petit moule.", "Mélange cream cheese, œuf et sucre et verse sur le fond.", "Enfourne 40 min à 160 °C, puis laisse refroidir dans le four entrouvert.", "Une nuit au frais, puis nappe de coulis."],
    "Fondant au chocolat cœur coulant": ["Fais fondre le chocolat et le beurre.", "Ajoute l'œuf, le sucre puis la farine.", "Verse dans un ramequin beurré.", "Enfourne 9 à 10 min à 200 °C : le cœur doit couler."],
    "Banana split": ["Coupe la banane en deux dans la longueur.", "Dispose les trois boules de glace entre les deux moitiés.", "Ajoute chantilly et sauce chocolat.", "Parsème d'amandes grillées."],
    "Pancakes sirop d'érable et bacon": ["Prépare la pâte à pancakes.", "Fais cuire les pancakes 2 min par face.", "Fais griller le bacon.", "Empile, ajoute une noisette de beurre et arrose de sirop d'érable."],
    "Crème brûlée": ["Fais chauffer la crème avec la vanille.", "Fouette les jaunes et le sucre, verse la crème chaude dessus.", "Cuis au bain-marie 40 min à 100 °C, puis laisse refroidir au frais.", "Saupoudre de cassonade et caramélise au chalumeau ou sous le gril."],
    "Mochis glacés": ["Sors les mochis du congélateur 5 min avant.", "Savoure-les tranquillement."],
    "Tarte tatin et crème fraîche": ["Fais un caramel avec le sucre et le beurre dans un moule allant au four.", "Dispose les pommes en quartiers serrés.", "Couvre de pâte feuilletée en rentrant les bords et enfourne 30 min à 200 °C.", "Retourne tiède et sers avec la crème fraîche."],
    "Donuts glacés": ["Prépare la pâte levée et laisse-la doubler de volume (1 h).", "Étale-la et découpe des anneaux.", "Fais-les frire 1 min par face à 170 °C.", "Trempe-les dans le glaçage."],
    "Sundae caramel beurre salé": ["Dispose les boules de glace dans une coupe.", "Nappe de caramel au beurre salé tiède.", "Ajoute la chantilly.", "Parsème d'éclats de cookies."],
    "Pain perdu brioché": ["Bats l'œuf avec le lait, le sucre et la cannelle.", "Trempe les tranches de brioche.", "Dore-les 2 min par face au beurre.", "Saupoudre d'un peu de sucre."],
    "Milkshake Oreo": ["Mets la glace, le lait et les biscuits dans le blender.", "Mixe 20 secondes.", "Verse dans un grand verre.", "Ajoute la chantilly et un biscuit émietté."],
    "Profiteroles": ["Coupe les choux en deux.", "Garnis-les de glace vanille.", "Nappe de sauce chocolat bien chaude.", "Parsème d'amandes effilées."],
    "Baklava (3 pièces)": ["Sers les baklavas à température ambiante.", "Accompagne-les d'un thé à la menthe peu sucré."],
    "Crumble pomme-fruits rouges et glace": ["Coupe les pommes en dés et mélange avec les fruits rouges dans un plat.", "Sable du bout des doigts la farine, le beurre et le sucre.", "Recouvre les fruits et enfourne 30 min à 180 °C.", "Sers tiède avec une boule de glace."],
    "Tarte au citron meringuée (part)": ["Choisis une belle part chez ton pâtissier (ou ta recette maison).", "Sors-la du frigo 10 min avant pour qu'elle soit à bonne température."],
    "Éclair au chocolat": ["Prends-le chez ton pâtissier préféré.", "Savoure-le avec un café."],
    "Paris-Brest (part)": ["Choisis une part chez ton pâtissier.", "Accompagne-la d'un bon café."],
    "Fondue au chocolat et fruits": ["Fais fondre le chocolat avec la crème à feu doux.", "Coupe les fruits en morceaux.", "Garde le chocolat au chaud (caquelon ou bain-marie).", "Trempe fruits et guimauves."],
    "Cinnamon rolls": ["Prépare la pâte briochée et laisse-la lever 1 h.", "Étale-la, tartine de beurre, cassonade et cannelle, puis roule-la.", "Coupe en tranches, laisse lever 30 min et enfourne 20 min à 180 °C.", "Nappe de glaçage au fromage frais encore tiède."],
    "Muffins aux myrtilles": ["Mélange les ingrédients secs d'un côté, les liquides de l'autre.", "Réunis-les sans trop mélanger, ajoute les myrtilles.", "Remplis les moules aux 3/4.", "Enfourne 20 min à 190 °C."],
    "Panna cotta coulis de fruits rouges": ["Fais ramollir la gélatine dans l'eau froide.", "Fais chauffer la crème avec le sucre et la vanille, ajoute la gélatine essorée.", "Verse dans une verrine et laisse prendre 4 h au frais.", "Nappe de coulis au moment de servir."],
    "Riz au lait et caramel": ["Fais cuire le riz 40 min à feu très doux dans le lait vanillé, en remuant souvent.", "Ajoute le sucre en fin de cuisson.", "Laisse tiédir.", "Nappe de caramel."],
    "Clafoutis aux cerises": ["Dispose les cerises dans un plat beurré.", "Mélange œufs, sucre, farine puis lait.", "Verse sur les cerises.", "Enfourne 35 min à 180 °C."],
    "Crêpes Suzette": ["Fais fondre le beurre et le sucre dans une poêle.", "Ajoute le jus et le zeste d'orange, laisse réduire.", "Plie les crêpes en quatre et réchauffe-les dans la sauce.", "Flambe au Grand Marnier si tu veux."],
    "Kouign-amann (part)": ["Réchauffe-le 3 min au four pour qu'il redevienne croustillant.", "Savoure avec un cidre ou un thé."],
    "Tarte au chocolat et caramel": ["Coule un fond de caramel au beurre salé dans le fond de tarte.", "Fais chauffer la crème et verse-la sur le chocolat haché, mélange en ganache.", "Verse la ganache sur le caramel.", "Laisse prendre 2 h au frais."],
    "Gâteau basque (part)": ["Choisis une part à la crème ou à la cerise.", "Sers à température ambiante."],
    "Affogato et cookie": ["Mets la boule de glace dans une tasse.", "Verse l'expresso brûlant dessus.", "Déguste aussitôt avec le cookie."],
}

# ---------------------------------------------------------------- generation
def make_dish(d, pk, vk, bk):
    p = P[pk]
    v = V.get(vk)
    b = BASE.get(bk) if bk else None
    title = d["t"].format(pa=p["a"], pn=p["n"], vn=v["n"] if v else "", bn=b["n"] if b else "").replace(" et ,", ",").replace("  ", " ").strip()
    if title.endswith(" et"):
        title = title[:-3]
    ings = []
    if not d.get("own") or pk not in ("lentilles", "oeuf"):  # dahl / shakshuka / frittata list them already
        ings.append(p["ing"])
    if v:
        ings.append(v["ing"])
    if b:
        ings.append(b["ing"])
    ings += d["fix"]
    # dedupe (e.g. a dish whose fixed list already has eggs)
    seen, uniq = set(), []
    for x in ings:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    steps = []
    for s in d["steps"]:
        if "{b}" in s and not b:
            continue
        if ("{vp}" in s or "{vthe}" in s) and not v:
            continue
        s = s.replace("{b}", b["step"] if b else "")
        s = s.replace("{vp}", v["prep"] if v else "")
        s = s.replace("{vthe}", v["the"] if v else "les légumes")
        s = s.replace("{plower}", p["cook"][0].lower() + p["cook"][1:])
        s = s.replace("{p}", p["cook"])
        steps.append(s.replace("..", ".").strip())
    t = d["tm"] + max(p["t"], (b["t"] if b else 0))
    t = int(round(t / 5.0) * 5) or 5
    tags = []
    if p["prot"]:
        tags.append("proteine")
    if p["vege"]:
        tags.append("vege")
    if d.get("light"):
        tags.append("leger")
    if t <= 15:
        tags.append("rapide")
    return dict(n=title[0].upper() + title[1:], e=d["e"], m=d["m"], t=t, tags=tags, c=d["c"], i=uniq, s=steps)


def mains():
    out = []
    for d in DISHES:
        combos = []
        for pk in d["P"]:
            for vk in d["V"] or [None]:
                for bk in d["B"] or [None]:
                    combos.append((pk, vk, bk))
        rng.shuffle(combos)
        # spread proteins evenly: round-robin over proteins
        by_p = {}
        for c in combos:
            by_p.setdefault(c[0], []).append(c)
        ordered = []
        while any(by_p.values()):
            for pk in d["P"]:
                if by_p.get(pk):
                    ordered.append(by_p[pk].pop())
        names = set()
        for pk, vk, bk in ordered:
            r = make_dish(d, pk, vk, bk)
            if r["n"] in names:
                continue
            names.add(r["n"])
            out.append(r)
            if len(names) >= d["n"]:
                break
    return out


def hand_written_names():
    path = os.path.join(ROOT, "ui", "recipes.js")
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    import re
    return re.findall(r'\{n:"([^"]+)"', txt)


def main():
    existing = hand_written_names()
    have = set(existing)
    cheat = cheat_meals()
    healthy = breakfasts() + snacks() + mains()
    out, names = [], set(have)
    for r in cheat + healthy:
        if r["n"] in names:
            continue
        names.add(r["n"])
        out.append(r)
    need = TARGET_TOTAL - len(existing)
    n_cheat = len(cheat)
    if len(out) < need:
        raise SystemExit(f"Pas assez de recettes générées : {len(out)} pour {need} demandées")
    # keep every cheat meal, trim healthy ones (evenly) to hit exactly the target
    healthy_out = [r for r in out if "cheat" not in r["tags"]]
    keep_h = need - n_cheat
    step = len(healthy_out) / keep_h
    healthy_kept = [healthy_out[int(i * step)] for i in range(keep_h)]
    final = [r for r in out if "cheat" in r["tags"]] + healthy_kept
    header = (
        "// GÉNÉRÉ par scripts/build_recipes.py — ne pas modifier à la main (relance le script).\n"
        f"// {len(final)} recettes du monde, dont {n_cheat} cheat meals, qui complètent ui/recipes.js.\n"
        "// Champs : n nom · e emoji · m moments (pd/dej/din/col) · t minutes · tags · c cuisine · i ingrédients · s étapes\n"
        "RECIPES.push(...[\n"
    )
    body = ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in final)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(header + body + "\n]);\n")
    cuisines = sorted({r["c"] for r in final})
    print(f"{len(existing)} écrites à la main + {len(final)} générées = {len(existing) + len(final)} recettes")
    print(f"cheat meals : {n_cheat} ({n_cheat / (len(existing) + len(final)):.1%}) · cuisines : {len(cuisines)}")


if __name__ == "__main__":
    main()
