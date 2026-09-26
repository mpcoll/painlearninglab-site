#!/usr/bin/env python3
"""
Generates the static site (fr/ and en/ pages) from the content below.

Usage (optional):  python3 _build/build.py
You can also edit the generated HTML files directly; but if you do,
don't run this script afterwards or it will overwrite your edits.
"""
import hashlib
import os
import re
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://www.painlearninglab.ca"
YEAR = 2026

# ------------------------------------------------------------------
# Shared data
# ------------------------------------------------------------------

LAB = {"fr": "Laboratoire apprentissage et douleur", "en": "Pain and Learning Lab"}

PAGES = [  # key, (fr label, fr file), (en label, en file)
    ("home", ("Accueil", "index.html"), ("Home", "index.html")),
    ("research", ("Recherche", "recherche.html"), ("Research", "research.html")),
    ("team", ("Équipe", "equipe.html"), ("Team", "team.html")),
    ("contact", ("Nous joindre", "nous-joindre.html"), ("Contact", "contact.html")),
]

EMAIL_LAB = "lab.apprentissage.douleur@cirris.ulaval.ca"
EMAIL_PI = "michel-pierre.coll@psy.ulaval.ca"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd-2gCxTfhbgU2y4AOynGTvvAzUvyY0UEmAVgegLsdk5m-oJQ/viewform"

PLACES = [
    {
        "id": "cirris",
        "name": {"fr": "Cirris", "en": "Cirris"},
        "addr": "525, boul. Wilfrid-Hamel, aile H<br>Québec (Québec) G1M 2S8",
        "q": "46.821213,-71.245554",
    },
    {
        "id": "ulaval",
        "name": {"fr": "Université Laval", "en": "Université Laval"},
        "addr": "Pavillon Félix-Antoine-Savard<br>2325, rue des Bibliothèques<br>Québec (Québec) G1V 0A6",
        "q": "46.781028,-71.272699",
    },
]

MARK_SVG = (
    '<svg viewBox="0 0 36 36" aria-hidden="true" focusable="false">'
    '<rect x="1" y="1" width="34" height="34" rx="9" fill="none" stroke="#5FE3D2" stroke-width="1.5" opacity=".5"/>'
    '<path d="M5 19.5h5.5l2.2-2.6 2.3 2.6 2.4-10.5 3.4 16.5 2.4-7.5 1.6 1.5H31" fill="none" stroke="#5FE3D2" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

THEME_SVG = ('<svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z" '
             'fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
             '<svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2" fill="none" '
             'stroke="currentColor" stroke-width="2"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8'
             'M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round"/></svg>')

MENU_SVG = ('<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')

T = {  # UI strings
    "skip": {"fr": "Passer au contenu", "en": "Skip to content"},
    "nav": {"fr": "Navigation principale", "en": "Main navigation"},
    "menu": {"fr": "Menu", "en": "Menu"},
    "theme": {"fr": "Mode sombre", "en": "Dark mode"},
    "lang_group": {"fr": "Langue / Language", "en": "Language / Langue"},
    "other_title": {"fr": "English version", "en": "Version française"},
    "brand_small": {"fr": "Laboratoire", "en": "Université Laval"},
    "brand_name": {"fr": "Apprentissage et douleur", "en": "Pain and Learning Lab"},
    "email": {"fr": "Courriel", "en": "Email"},
    "map": {"fr": "Voir sur la carte", "en": "View on map"},
    "open_map": {"fr": "Ouvrir dans Google Maps", "en": "Open in Google Maps"},
    "footer_aff": {
        "fr": "École de psychologie, Université Laval<br>Centre interdisciplinaire de recherche en réadaptation et intégration sociale (Cirris)",
        "en": "School of Psychology, Université Laval<br>Centre for Interdisciplinary Research in Rehabilitation and Social Integration (Cirris)",
    },
}



def asset_version(path):
    """Short content hash appended to CSS/JS links so browsers fetch new versions right after an update."""
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

def other(lang):
    return "en" if lang == "fr" else "fr"


def file_for(key, lang):
    for k, fr, en in PAGES:
        if k == key:
            return (fr if lang == "fr" else en)[1]


def maps_link(q):
    return f"https://www.google.com/maps?q={q}"


def img_slot(src, alt, placeholder, cls="media"):
    """Image with a styled placeholder behind it. If the file is missing, the placeholder shows."""
    return (f'<div class="{cls}"><span class="ph" aria-hidden="true">{placeholder}</span>'
            f'<img src="{src}" alt="{escape(alt)}" loading="lazy" onerror="this.remove()"></div>')


def initials(name):
    parts = name.replace("-", " ").split()
    return (parts[0][0] + parts[-1][0]).upper()


# ------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------

def header(lang, key):
    o = other(lang)
    items = []
    for k, fr, en in PAGES:
        label, f = fr if lang == "fr" else en
        cur = ' aria-current="page"' if k == key else ""
        items.append(f'<li><a href="{f}"{cur}>{label}</a></li>')
    return f'''<a class="skip" href="#main">{T["skip"][lang]}</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html">
      <img src="../assets/img/logo.png" alt="" width="36" height="36">
      <span class="brand-text"><span class="brand-small">{T["brand_small"][lang]}</span><span class="brand-name">{T["brand_name"][lang]}</span></span>
    </a>
    <div class="partners">
      <a href="https://www.ulaval.ca/"><img src="../assets/img/logos/ulaval-reversed.png" alt="Université Laval" width="70" height="29"></a>
      <a href="https://www.cirris.ulaval.ca/"><img src="../assets/img/logos/cirris.png" alt="Cirris" width="127" height="29"></a>
    </div>
    <nav class="nav" id="nav" aria-label="{T["nav"][lang]}"><ul>{"".join(items)}</ul></nav>
    <div class="lang" role="group" aria-label="{T["lang_group"][lang]}">
      <span class="lang-opt is-current" lang="{lang}">{lang.upper()}</span>
      <a class="lang-opt" href="../{o}/{file_for(key, o)}" hreflang="{o}" lang="{o}" data-lang="{o}" title="{T["other_title"][lang]}">{o.upper()}</a>
    </div>
    <button class="theme-btn" type="button" aria-pressed="false" aria-label="{T["theme"][lang]}" title="{T["theme"][lang]}">{THEME_SVG}</button>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="{T["menu"][lang]}">{MENU_SVG}<span>{T["menu"][lang]}</span></button>
  </div>
</header>'''


def footer(lang):
    places = "".join(
        f'<div><h2>{p["name"][lang]}</h2><address>{p["addr"]}</address>'
        f'<p><a href="{maps_link(p["q"])}">{T["map"][lang]}</a></p></div>'
        for p in PLACES
    )
    return f'''<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="footer-name">{LAB["fr"]}<br>{LAB["en"]}</p>
      <p>{T["footer_aff"][lang]}</p>
      <div class="footer-logos">
        <a href="https://www.ulaval.ca/"><img src="../assets/img/logos/ulaval-reversed.png" alt="Université Laval" height="44" loading="lazy"></a>
        <a href="https://www.cirris.ulaval.ca/"><img src="../assets/img/logos/cirris.png" alt="Cirris" height="38" loading="lazy"></a>
      </div>
    </div>
    {places}
    <div><h2>{T["email"][lang]}</h2><p><a href="mailto:{EMAIL_LAB}">{EMAIL_LAB.replace("@", "@<wbr>")}</a></p></div>
  </div>
  <div class="wrap footer-base">© {YEAR} {LAB["fr"]} / {LAB["en"]}, Université Laval</div>
</footer>'''


def page(lang, key, title, desc, body):
    o = other(lang)
    f_self, f_other = file_for(key, lang), file_for(key, o)
    full_title = LAB[lang] if key == "home" else f"{title} | {LAB[lang]}"
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{SITE_URL}/{lang}/{f_self}">
<link rel="alternate" hreflang="{lang}" href="{SITE_URL}/{lang}/{f_self}">
<link rel="alternate" hreflang="{o}" href="{SITE_URL}/{o}/{f_other}">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/fr/{file_for(key, "fr")}">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{"fr_CA" if lang == "fr" else "en_CA"}">
<meta property="og:url" content="{SITE_URL}/{lang}/{f_self}">
<meta property="og:site_name" content="{LAB[lang]}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-{lang}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{LAB[lang]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#071E33">
<meta name="color-scheme" content="light dark">
<script>try{{var t=localStorage.getItem('pll-theme');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<link rel="icon" href="../assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="../assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&amp;display=swap">
<link rel="stylesheet" href="../assets/css/style.css?v={asset_version("assets/css/style.css")}">
<script defer src="../assets/js/main.js?v={asset_version("assets/js/main.js")}"></script>
</head>
<body>
{header(lang, key)}
<main id="main">
{body}
</main>
{footer(lang)}
</body>
</html>
'''


def page_head(title, intro, jumps=None, labels="Fz Cz Pz C4", seed=11, kind="eeg"):
    j = ""
    if jumps:
        j = '<ul class="jump">' + "".join(f'<li><a href="#{i}">{l}</a></li>' for i, l in jumps) + "</ul>"
    return f'''<section class="page-head">
  {f'<canvas class="fmri" data-src="../assets/img/mri-slices.png" data-seed="{seed}" aria-hidden="true"></canvas>' if kind == "fmri" else f'<canvas class="eeg" data-static data-labels="{labels}" data-seed="{seed}" aria-hidden="true"></canvas>'}
  <div class="wrap">
    <h1>{title}</h1>
    <p>{intro}</p>
    {j}
  </div>
</section>'''


# ------------------------------------------------------------------
# Content
# ------------------------------------------------------------------

AXES = [
    {
        "id": "axis-1",
        "label": {"fr": "Axe 1", "en": "Axis 1"},
        "title": {"fr": "Modèles computationnels de l'apprentissage et de la décision liés à la douleur",
                  "en": "Computational models of pain learning and decision-making"},
        "text": {
            "fr": "Cet axe de recherche théorique vise à identifier des architectures computationnelles et neuronales cohérentes capables d'expliquer et de prédire la perception de la douleur et l'évitement de la douleur.",
            "en": "This theoretical research axis aims to identify coherent computational and neural architectures that can explain and predict pain perception and pain avoidance.",
        },
        "pubs": [
            ("2025", "Expectations and uncertainty shape pain perception during learning",
             "Lacombe-Thibault, M., &amp; Coll, M.-P.", "<i>The Journal of Pain</i>, 37, 105569",
             "10.1016/j.jpain.2025.105569"),
            ("2024", "Pain reflects the informational value of nociceptive inputs",
             "Coll, M.-P. et al.", "<i>Pain</i>, 165(10), e115–e125", "10.1097/j.pain.0000000000003254"),
            ("2022", "The neural signature of the decision value of future pain",
             "Coll, M.-P. et al.", "<i>PNAS</i>, 119(23), e2119931119", "10.1073/pnas.2119931119"),
        ],
    },
    {
        "id": "axis-2",
        "label": {"fr": "Axe 2", "en": "Axis 2"},
        "title": {"fr": "Oscillations neuronales et biomarqueurs de la douleur", "en": "Neural oscillations and biomarkers of pain"},
        "text": {
            "fr": "Cet axe de recherche basé sur les données étudie les oscillations cérébrales et les signaux physiologiques associés à la douleur, et les utilise pour développer des biomarqueurs généralisables entre les individus et les modalités de douleur.",
            "en": "This data-driven research axis investigates the brain oscillations and physiological signals that accompany pain, and uses them to build biomarkers that generalize across individuals and pain modalities.",
        },
        "pubs": [
            ("2026", "No effect of rhythmic visual stimulation on experimental pain perception",
             "Roy, N., Deslauriers, C., Côté-Cazes, T., Etcheverry, A., &amp; Coll, M.-P.", "<i>Pain</i>, 167(9), e441–e452",
             "10.1097/j.pain.0000000000004044"),
            ("2025", "Towards Generalizable Learning Models for EEG-Based Identification of Pain Perception",
             "Rezzouk, M., Gagnon, F., Champagne, A., Roy, M., Albouy, P., Coll, M.-P., &amp; Subakan, C.",
             "<i>2025 IEEE 35th International Workshop on Machine Learning for Signal Processing (MLSP)</i>, 1–6",
             "10.1109/MLSP62443.2025.11204206", "https://arxiv.org/abs/2508.11691"),
        ],
        "upcoming": [  # (year, title, authors, note or None); listed before published work
            ("2026", "A comprehensive physiological dataset of pain and aversive modalities for pain biomarkers research",
             "Champagne, A., Barrette, L.-E., Cyr-Bouchard, A., Roy, M., &amp; Coll, M.-P.", None),
            ("2026", "Distinct EEG microstate signatures across different pain types",
             "Rabiei, P., Champagne, A., Barrette, L.-È., Fakhry, N., Massé-Alarie, H., &amp; Coll, M.-P.", None),
        ],
    },
]

PI = {
    "name": "Michel-Pierre Coll",
    "slug": "michel-pierre-coll",
    "roles": [
        ({"fr": "Professeur agrégé", "en": "Associate Professor"},
         {"fr": "École de psychologie, Université Laval", "en": "School of Psychology, Université Laval"}),
        ({"fr": "Chercheur", "en": "Researcher"},
         {"fr": "Centre interdisciplinaire de recherche en réadaptation et intégration sociale (Cirris)",
          "en": "Centre for Interdisciplinary Research in Rehabilitation and Social Integration (Cirris)"}),
    ],
    "timeline": [
        ("2019–2021", {"fr": "Stagiaire postdoctoral, Université McGill",
                       "en": "Postdoctoral Fellow, McGill University"}),
        ("2016–2019", {"fr": "Stagiaire postdoctoral, Université d'Oxford",
                       "en": "Postdoctoral Fellow, University of Oxford"}),
        ("2009–2016", {"fr": "Ph. D. Neuropsychologie clinique, Université Laval",
                       "en": "Ph.D. Clinical Neuropsychology, Université Laval"}),
    ],
    "links": [
        ({"fr": "Profil Université Laval", "en": "Université Laval profile"},
         "https://www.fss.ulaval.ca/notre-faculte/repertoire-du-personnel/michel-pierre-coll"),
        ({"fr": "Google Scholar", "en": "Google Scholar"},
         "https://scholar.google.com/citations?hl=en&amp;user=EHQepC0AAAAJ&amp;view_op=list_works&amp;sortby=pubdate"),
        ({"fr": "ORCID", "en": "ORCID"}, "https://orcid.org/0000-0002-1475-5522"),
        ({"fr": "GitHub", "en": "GitHub"}, "https://github.com/mpcoll"),
    ],
}

STUDENTS = [
    ("shima-hassanpour", "Shima Hassanpour",
     {"fr": "Stagiaire postdoctorale 2026–", "en": "Postdoctoral Fellow 2026–"},
     {"fr": "Réseaux corticaux de la douleur", "en": "Cortical Networks of Pain"}),
    ("laurie-caumartin", "Laurie Caumartin",
     {"fr": "M. Sc. Neurosciences 2026–", "en": "M.Sc. Neuroscience 2026–"},
     {"fr": "Dissocier le rôle de l'attention et des attentes dans la perception de la douleur",
      "en": "Disentangling Attention and Expectation in Pain Perception"}),
    ("leane-beaulieu-laliberte", "Léane Beaulieu-Laliberté",
     {"fr": "M.A. Psychologie 2022–2024<br>D.Psy. 2024–", "en": "M.A. Psychology 2022–2024<br>D.Psy. 2024–"},
     {"fr": "Discrimination de la douleur lors de la modulation endogène",
      "en": "Influence of Endogenous Modulation by Offset Analgesia on Pain Discrimination"}),
    ("alyson-champagne", "Alyson Champagne",
     {"fr": "Ph. D. Psychologie clinique 2022–", "en": "Ph.D. Clinical Psychology 2022–"},
     {"fr": "Décodage de l'intensité subjective de la douleur à partir de l'activité cérébrale",
      "en": "Decoding Subjective Pain Intensity from Brain Activity"}),
    ("megane-lacombe-thibault", "Mégane Lacombe-Thibault",
     {"fr": "Ph. D. Psychologie clinique 2022–", "en": "Ph.D. Clinical Psychology 2022–"},
     {"fr": "Vers une compréhension computationnelle de la douleur chronique",
      "en": "Toward a Computational Understanding of Chronic Pain"}),
    ("nicolas-roy", "Nicolas Roy",
     {"fr": "Professionnel de recherche 2023–2024<br>Ph. D. Psychologie clinique 2024–",
      "en": "Research Professional 2023–2024<br>Ph.D. Clinical Psychology 2024–"},
     {"fr": "Modélisation computationnelle du traitement cérébral de la douleur dans le contexte du dilemme d'exploration et d'exploitation",
      "en": "Neural Bases of Pain Modulation During Exploration"}),
    ("sanoussy-diallo", "Sanoussy Diallo",
     {"fr": "D.Psy. 2024–", "en": "D.Psy. 2024–"},
     {"fr": "Modélisation bayésienne de l'inférence sensorielle de la douleur en contexte d'incertitude",
      "en": "Bayesian Modelling of Pain Sensory Inference in the Context of Uncertainty"}),
    ("joshua-duquette", "Joshua Duquette",
     {"fr": "Auxiliaire de recherche 2025<br>Ph. D. Psychologie clinique 2025–",
      "en": "Research Assistant 2025<br>Ph.D. Clinical Psychology 2025–"},
     {"fr": "Prédiction des signatures neuronales de la douleur à partir des oscillations EEG",
      "en": "Predicting Neural Signatures of Pain Using EEG Oscillations"}),
    ("pouya-rabiei", "Pouya Rabiei",
     {"fr": "Ph. D. Sciences biomédicales<br>Codirection : Hugo Massé-Alarie",
      "en": "Ph.D. Biomedical Sciences<br>Co-supervision: Hugo Massé-Alarie"},
     {"fr": "Prédiction de la transition vers la douleur chronique : étude des variables comportementales et neuronales",
      "en": "Predicting the Transition to Chronic Pain: A Study of Behavioral and Neural Variables"}),
    ("audrey-lalancette", "Audrey Lalancette",
     {"fr": "Ph. D. Sciences de la réadaptation<br>Codirection : Maximiliano Wilson",
      "en": "Ph.D. Rehabilitation Sciences<br>Co-supervision: Maximiliano Wilson"},
     {"fr": "Traitement phonologique au cours du vieillissement : données issues de l'EEG",
      "en": "Phonological Processing in Older Age: Evidence From EEG Data"}),
]

STAFF = [
    ("antoine-cyr-bouchard", "Antoine Cyr-Bouchard",
     {"fr": "Professionnel de recherche 2026–<br>Auxiliaire de recherche 2023–2025<br>Ph. D. Psychologie clinique A2025",
      "en": "Research Professional 2026–<br>Research Assistant 2023–2025<br>Ph.D. Clinical Psychology A2025"}),
    ("lorie-eve-barrette", "Lorie-Ève Barrette",
     {"fr": "Auxiliaire de recherche 2025–<br>Baccalauréat en psychologie 2024–",
      "en": "Research Assistant 2025–<br>Undergraduate in Psychology 2024–"}),
    ("alysun-paradis", "Alysun Paradis",
     {"fr": "Auxiliaire de recherche 2026–<br>Baccalauréat en psychologie 2025–",
      "en": "Research Assistant 2026–<br>Undergraduate in Psychology 2025–"}),
]

ALUMNI = [  # (names fr, names en, what fr, what en) - most recent first
    ("Marie-Hélène Tessier", None, "Professionnelle de recherche 2026", "Research Professional 2026"),
    ("Samuel Lépine, Marie-Joëlle Tremblay et Jérôme Verret", "Samuel Lépine, Marie-Joëlle Tremblay and Jérôme Verret",
     "RD 2025–2026 ; Différences individuelles et perception de la douleur", "RD 2025–2026; Individual differences and pain perception"),
    ("Mathis Rezzouk", None, "M. Sc. Informatique (codirection Cem Subakan) 2024–2026 ; Apprentissage profond et EEG",
     "M.Sc. Computer Science (co-supervision Cem Subakan) 2024–2026; Deep learning and EEG"),
    ("Amandine Daigney", None, "Professionnelle de recherche 2025–2026", "Research Professional 2025–2026"),
    ("Pénélope Alain-Thériault et Aurélie Tremblay", "Pénélope Alain-Thériault and Aurélie Tremblay",
     "RD 2024–2025 ; Influence de la fatigue mentale sur l'apprentissage et la perception de la douleur",
     "RD 2024–2025; Influence of mental fatigue on learning and pain perception"),
    ("Veronika Wendler", None, "Stagiaire MITACS (Université d'Aberdeen, Royaume-Uni) 2024",
     "MITACS Intern (University of Aberdeen, United Kingdom) 2024"),
    ("Jacob Schink, Laurence Lagadec-Gaulin et Mégane Déry", "Jacob Schink, Laurence Lagadec-Gaulin and Mégane Déry",
     "RD 2023–2024 ; Placebo et discrimination", "RD 2023–2024; Placebo and discrimination"),
    ("Rachel Fortin", None, "Auxiliaire de recherche 2023–2024", "Research Assistant 2023–2024"),
    ("Mathilda Buschmann", None, "Stagiaire d'été en visite (Université d'Osnabrück, Allemagne) 2023 ; EEG et apprentissage profond",
     "Visiting Summer Intern (Osnabrück University, Germany) 2023; EEG and deep learning"),
    ("Mélanie Lachance", None, "Auxiliaire de recherche 2022–2023", "Research Assistant 2022–2023"),
    ("Audrey Etcheverry, Thaliane Côté-Cazes et Coralie Deslauriers", "Audrey Etcheverry, Thaliane Côté-Cazes and Coralie Deslauriers",
     "RD 2022–2023 ; Effet d'une stimulation rythmique visuelle sur la perception de la douleur",
     "RD 2022–2023; Effect of rhythmic visual stimulation on pain perception"),
]

FUNDERS = [
    ("cihr", {"fr": ("IRSC", "Instituts de recherche en santé du Canada"), "en": ("CIHR", "Canadian Institutes of Health Research")},
     {"fr": "https://cihr-irsc.gc.ca/f/193.html", "en": "https://cihr-irsc.gc.ca/e/193.html"}),
    ("nserc", {"fr": ("CRSNG", "Conseil de recherches en sciences naturelles et en génie"), "en": ("NSERC", "Natural Sciences and Engineering Research Council")},
     {"fr": "https://nserc-crsng.canada.ca/fr", "en": "https://nserc-crsng.canada.ca/en"}),
    ("frq", {"fr": ("FRQ", "Fonds de recherche du Québec"), "en": ("FRQ", "Fonds de recherche du Québec")},
     {"fr": "https://frq.gouv.qc.ca/", "en": "https://frq.gouv.qc.ca/en/"}),
    ("qprn", {"fr": ("RQRD", "Réseau québécois de recherche sur la douleur"), "en": ("QPRN", "Quebec Pain Research Network")},
     {"fr": "https://qprn.ca/fr/", "en": "https://qprn.ca/en/"}),
    ("cfi", {"fr": ("FCI", "Fondation canadienne pour l'innovation"), "en": ("CFI", "Canada Foundation for Innovation")},
     {"fr": "https://www.innovation.ca/fr", "en": "https://www.innovation.ca/"}),
    ("braincanada", {"fr": ("Brain Canada", "Fondation Brain Canada"), "en": ("Brain Canada", "Brain Canada Foundation")},
     {"fr": "https://braincanada.ca/fr/", "en": "https://braincanada.ca/"}),
]


# Figures shown in the carousel under each research axis (file in assets/img/figures/).
# (file, figure number, paper key); licences: J Pain = CC BY 4.0, PNAS = CC BY-NC-ND 4.0 (shown unaltered),
# Pain 2024 = figures from the bioRxiv preprint (doi:10.1101/2023.07.14.549006); Pain 2026 = CC BY-NC-ND 4.0;
# MLSP 2025 = figures cropped from the arXiv version. The doi slot may also hold a full URL.
FIG_PAPERS = {
    "jpain2025": ("Expectations and uncertainty shape pain perception during learning", "<i>The Journal of Pain</i>, 2025",
                  "10.1016/j.jpain.2025.105569", "CC BY 4.0"),
    "pain2024": ("Pain reflects the informational value of nociceptive inputs", "<i>Pain</i>, 2024 (bioRxiv preprint)",
                 "10.1101/2023.07.14.549006", None),
    "pnas2022": ("The neural signature of the decision value of future pain", "<i>PNAS</i>, 2022",
                 "10.1073/pnas.2119931119", "CC BY-NC-ND 4.0"),
    "pain2026": ("No effect of rhythmic visual stimulation on experimental pain perception", "<i>Pain</i>, 2026",
                 "10.1097/j.pain.0000000000004044", "CC BY-NC-ND 4.0"),
    "mlsp2025": ("Towards Generalizable Learning Models for EEG-Based Identification of Pain Perception",
                 "IEEE MLSP, 2025 (arXiv preprint)", "https://arxiv.org/abs/2508.11691", None),
}
FIGURES = {
    "axis-1": [
        ("jpain2025-fig2.jpg", 2, "jpain2025"), ("jpain2025-fig3.jpg", 3, "jpain2025"),
        ("pain2024-fig3.jpg", 3, "pain2024"), ("pain2024-fig4.jpg", 4, "pain2024"),
        ("pnas2022-fig1.jpg", 1, "pnas2022"), ("pnas2022-fig2.jpg", 2, "pnas2022"), ("pnas2022-fig7.jpg", 7, "pnas2022"),
    ],
    "axis-2": [
        ("pain2026-fig1.jpg", 1, "pain2026"), ("pain2026-fig2.jpg", 2, "pain2026"), ("pain2026-fig4.jpg", 4, "pain2026"),
        ("mlsp2025-fig1.jpg", 1, "mlsp2025"), ("mlsp2025-fig2.jpg", 2, "mlsp2025"),
    ],
}


def carousel(axis_id, lang):
    slides = FIGURES.get(axis_id)
    if not slides:
        return ""
    t = {"fr": ("Figures tirées de nos publications", "Figure", "Figure précédente", "Figure suivante", "Aller à la figure", "Licence"),
         "en": ("Figures from our publications", "Figure", "Previous figure", "Next figure", "Go to figure", "Licence")}[lang]
    items, dots = [], []
    for i, (f, n, key) in enumerate(slides):
        title, venue, doi, lic = FIG_PAPERS[key]
        credit = f' · {t[5]} {lic}' if lic else ""
        items.append(f'''<figure class="slide"{"" if i == 0 else " hidden"} aria-roledescription="slide" aria-label="{i + 1} / {len(slides)}">
          <div class="slide-img"><img src="../assets/img/figures/{f}" alt="{t[1]} {n}, {escape(title)}" loading="lazy"></div>
          <figcaption><strong>{t[1]} {n}</strong> · <a href="{doi if doi.startswith("http") else "https://doi.org/" + doi}">{title}</a>. {venue}{credit}</figcaption>
        </figure>''')
        cur = ' aria-current="true"' if i == 0 else ""
        dots.append(f'<button type="button" class="dot"{cur} aria-label="{t[4]} {i + 1}"></button>')
    return f'''<div class="carousel" aria-roledescription="carousel" aria-label="{t[0]}">
      <div class="slides" aria-live="off">{"".join(items)}</div>
      <div class="carousel-nav"><button type="button" class="prev" aria-label="{t[2]}">‹</button>
        <div class="dots">{"".join(dots)}</div><button type="button" class="next" aria-label="{t[3]}">›</button></div>
    </div>'''


def funder_logo(slug, lang):
    """Logo file for a funder: a language-specific one (slug-fr.png) wins over a shared one (slug.png)."""
    folder = os.path.join(ROOT, "assets", "img", "funders")
    for name in (f"{slug}-{lang}", slug):
        for ext in ("svg", "png", "jpg"):
            if os.path.exists(os.path.join(folder, f"{name}.{ext}")):
                return f"../assets/img/funders/{name}.{ext}"
    return None


def funders_list(lang):
    items = []
    for slug, names, url in FUNDERS:
        logo = funder_logo(slug, lang)
        img = f'\n        <img src="{logo}" alt="{names[lang][1]}" loading="lazy">' if logo else ""
        cls = "funder has-img" if logo else "funder"
        items.append(f'''<li><a class="{cls}" href="{url[lang]}">{img}
        <span class="funder-text"><span class="funder-name">{names[lang][0]}</span><span class="funder-full">{names[lang][1]}</span></span></a></li>''')
    return "".join(items)


def participate_band(lang, with_id=False):
    t = {
        "fr": ("Participer à une étude",
               "Nous recrutons des volontaires pour nos études sur la perception de la douleur, en laboratoire ou à distance. Les stimulations utilisées sont sécuritaires, contrôlées et toujours conformes aux normes éthiques en vigueur.",
               "Manifester mon intérêt", "Écrire à l'équipe",
               "Le formulaire s'ouvre dans Google Forms."),
        "en": ("Take part in a study",
               "We recruit volunteers for our studies on pain perception, in the lab or remotely. The stimulations we use are safe, well controlled, and always comply with current ethical standards.",
               "Express your interest", "Email the team",
               "The form opens in Google Forms."),
    }[lang]
    idattr = ' id="participate"' if with_id else ""
    return f'''<section class="participate"{idattr}>
  <div class="wrap participate-inner">
    <div>
      <h2>{t[0]}</h2>
      <p>{t[1]}</p>
    </div>
    <div>
      <div class="actions">
        <a class="btn btn-primary" href="{FORM_URL}">{t[2]}</a>
        <a class="btn btn-ghost" href="mailto:{EMAIL_LAB}">{t[3]}</a>
      </div>
      <p class="note">{t[4]}</p>
    </div>
  </div>
</section>'''


# ---------------- Approach diagram ----------------

APPROACH = {
    "fr": {"h": "Notre approche", "human": ["Apprentissage", "humain"], "machine": ["Apprentissage", "automatique"],
           "goal_wide": ["Comprendre et prédire la perception", "de la douleur aiguë et clinique"],
           "goal_narrow": ["Comprendre et prédire", "la perception de la douleur", "aiguë et clinique"],
           "desc": "L'apprentissage humain et l'apprentissage automatique s'éclairent mutuellement pour comprendre et prédire la perception de la douleur aiguë et clinique."},
    "en": {"h": "Our approach", "human": ["Human", "learning"], "machine": ["Machine", "learning"],
           "goal_wide": ["Understand and predict", "acute and clinical pain perception"],
           "goal_narrow": ["Understand and predict", "acute and clinical", "pain perception"],
           "desc": "Human learning and machine learning inform each other to understand and predict acute and clinical pain perception."},
}


def _network(x, y, k=1.0):
    """Small neural-network glyph (2 inputs, 5 hidden, 1 output) centred on x, y."""
    ins = [(x - 24 * k, y + d * k) for d in (-12, 12)]
    hid = [(x, y + d * k) for d in (-24, -12, 0, 12, 24)]
    out = [(x + 24 * k, y)]
    lines = "".join(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}"/>'
                    for (a, b) in ins for (c, d) in hid)
    lines += "".join(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}"/>'
                     for (a, b) in hid for (c, d) in out)
    r = 3.4 * k
    nodes = "".join(f'<circle class="n-in" cx="{a:.1f}" cy="{b:.1f}" r="{r:.1f}"/>' for a, b in ins + out)
    nodes += "".join(f'<circle class="n-hid" cx="{a:.1f}" cy="{b:.1f}" r="{r:.1f}"/>' for a, b in hid)
    return f'<g class="net">{lines}{nodes}</g>'


def _head(cx, cy, k=1.0):
    """Head in profile (facing right) with a network inside; box ~110x110 centred on cx, cy."""
    path = ("M32,108 L32,90 C15,82 6,64 8,45 C10,20 30,3 55,3 C80,3 96,20 96,42 "
            "L96,50 L105,64 L96,68 L97,74 L94,77 L96,82 C96,90 89,93 80,92 L72,91 L72,108")
    return (f'<g transform="translate({cx - 55 * k:.1f},{cy - 55 * k:.1f}) scale({k})">'
            f'<path class="icon-line" d="{path}"/>{_network(52, 44)}</g>')


def _monitor(cx, cy, k=1.0):
    return (f'<g transform="translate({cx - 62 * k:.1f},{cy - 50 * k:.1f}) scale({k})">'
            '<rect class="icon-fill" x="0" y="0" width="124" height="80" rx="7"/>'
            '<rect class="screen" x="7" y="7" width="110" height="60" rx="2"/>'
            '<path class="icon-fill" d="M50,80 L74,80 L78,96 L46,96 Z"/>'
            '<rect class="icon-fill" x="36" y="95" width="52" height="5" rx="2.5"/>'
            f'{_network(62, 37)}</g>')


def _lines(x, y, lines, gap):
    y0 = y - gap * (len(lines) - 1) / 2
    return "".join(f'<tspan x="{x}" y="{y0 + i * gap:.1f}">{l}</tspan>' for i, l in enumerate(lines))


def approach_svg(lang, narrow):
    t = APPROACH[lang]
    uid = f"ap-{lang}-{'n' if narrow else 'w'}"
    defs = (f'<defs><marker id="{uid}-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="11" markerHeight="11" '
            f'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" class="arrowhead"/></marker></defs>')
    m = f'marker-end="url(#{uid}-arr)"'
    ms = f'marker-start="url(#{uid}-arr)" {m}'
    if not narrow:
        vb, fs, gfs = "0 0 960 470", 23, 22
        body = (
            _head(200, 68) + _monitor(760, 72) +
            '<rect class="card human" x="30" y="140" width="340" height="92" rx="10"/>'
            f'<text class="lbl" x="200" y="188" font-size="{fs}">{" ".join(t["human"])}</text>'
            '<rect class="card machine" x="590" y="140" width="340" height="92" rx="10"/>'
            f'<text class="lbl" x="760" y="188" font-size="{fs}">{" ".join(t["machine"])}</text>'
            f'<line class="link" x1="378" y1="186" x2="582" y2="186" {ms}/>'
            f'<path class="link" d="M200,240 C200,330 215,392 250,392" {m}/>'
            f'<path class="link" d="M760,240 C760,330 745,392 710,392" {m}/>'
            '<rect class="card goal" x="260" y="338" width="440" height="108" rx="10"/>'
            f'<text class="lbl lbl-goal" font-size="{gfs}">{_lines(480, 392, t["goal_wide"], 30)}</text>'
        )
    else:
        vb, fs, gfs = "0 0 360 470", 17, 17
        body = (
            _head(82, 50, .62) + _monitor(278, 52, .62) +
            '<rect class="card human" x="6" y="104" width="152" height="78" rx="9"/>'
            f'<text class="lbl" font-size="{fs}">{_lines(82, 143, t["human"], 21)}</text>'
            '<rect class="card machine" x="202" y="104" width="152" height="78" rx="9"/>'
            f'<text class="lbl" font-size="{fs}">{_lines(278, 143, t["machine"], 21)}</text>'
            f'<line class="link" x1="163" y1="143" x2="197" y2="143" {ms}/>'
            f'<path class="link" d="M82,188 C82,250 150,250 150,300" {m}/>'
            f'<path class="link" d="M278,188 C278,250 210,250 210,300" {m}/>'
            '<rect class="card goal" x="30" y="306" width="300" height="118" rx="10"/>'
            f'<text class="lbl lbl-goal" font-size="{gfs}">{_lines(180, 365, t["goal_narrow"], 25)}</text>'
        )
    cls = "approach-narrow" if narrow else "approach-wide"
    return (f'<svg class="approach-svg {cls}" viewBox="{vb}" role="img" aria-labelledby="{uid}-t">'
            f'<title id="{uid}-t">{t["desc"]}</title>{defs}{body}</svg>')


def approach_section(lang):
    t = APPROACH[lang]
    return f'''<section class="section section-mist approach">
  <div class="wrap">
    <h2>{t["h"]}</h2>
    <figure class="approach-fig">{approach_svg(lang, False)}{approach_svg(lang, True)}</figure>
  </div>
</section>'''


# ---------------- Home ----------------

def home(lang):
    o = other(lang)
    t = {
        "fr": {
            "lead": "Le programme de recherche du laboratoire tire parti de l'imagerie cérébrale humaine et des avancées récentes en modélisation computationnelle et en intelligence artificielle pour comprendre la perception et la modulation de la douleur normale et pathologique.",
            "b1": "Découvrir nos recherches", "b2": "Participer à une étude",
            "why_h": "La douleur, un défi scientifique et de santé publique",
            "why_k": "Pourquoi certaines personnes développent-elles une douleur chronique et d'autres non?",
            "p1": "La douleur est une expérience humaine universelle et un moteur fondamental du comportement. Cependant, sa perception est subjective et fortement influencée par de multiples facteurs tels que l'expérience, l'humeur et les émotions. Bien que de nombreuses études aient révélé un réseau complexe de régions cérébrales impliquées dans l'expérience de la douleur et sa modulation, notre compréhension des mécanismes précis qui génèrent et régulent la perception de la douleur au sein de ce système reste limitée. De plus, la nature subjective de la douleur rend sa mesure difficile dans les recherches et les contextes cliniques, puisqu'elle repose principalement sur des échelles d'évaluation et des questionnaires fortement influencés par de multiples facteurs et seulement modérément fiables.",
            "p2": "Comprendre la douleur n'est pas seulement un défi scientifique, mais aussi une question de santé publique urgente. La douleur chronique est la principale raison pour laquelle les gens recherchent des soins de santé, la première cause d'utilisation des ressources de santé et la source la plus importante d'invalidité parmi les adultes actifs au Canada. Malgré les impacts importants de cette condition, les causes de la douleur chronique restent nébuleuses et son traitement continue de représenter un défi pour les cliniciens. Étant donné notre connaissance limitée des mécanismes fondamentaux sous-jacents à la perception et à la modulation de la douleur, nous avons une compréhension limitée de pourquoi la douleur chronique se développe et persiste chez certains individus et non chez d'autres.",
            "axes_h": "Deux axes de recherche", "axes_more": "Voir les projets et publications",
            "fund_h": "Financement", "fund_more": "En savoir plus",
        },
        "en": {
            "lead": "The laboratory's research program combines human brain imaging with computational modelling and artificial intelligence to better understand how pain is perceived and modulated under both normal and pathological conditions.",
            "b1": "Explore our research", "b2": "Take part in a study",
            "why_h": "Pain: a scientific and public health challenge",
            "why_k": "Why does chronic pain develop and persist in some people but not in others?",
            "p1": "Pain is a universal human experience and a fundamental driver of behavior. However, its perception is subjective and strongly influenced by multiple factors such as experience, mood, and emotions. Although numerous studies have revealed a complex network of brain regions involved in the experience of pain and its modulation, our understanding of the specific mechanisms that generate and regulate pain perception within this network remains limited. Furthermore, the subjective nature of pain makes it difficult to measure in research and clinical settings, as it relies primarily on rating scales and questionnaires that are heavily influenced by multiple factors and only moderately reliable.",
            "p2": "Understanding pain is not only a scientific challenge but also an urgent public health issue. Chronic pain is the leading reason people seek health care, the primary cause of health resource use, and the most significant source of disability among working-age adults in Canada. Despite the significant impacts of this condition, the causes of chronic pain remain unclear, and its treatment continues to pose a challenge for clinicians. Given our limited knowledge of the fundamental mechanisms underlying pain perception and modulation, we have a poor understanding of why chronic pain develops and persists in some individuals but not in others.",
            "axes_h": "Two research axes", "axes_more": "See projects and publications",
            "fund_h": "Funding", "fund_more": "Learn more",
        },
    }[lang]
    rfile = file_for("research", lang)

    axes = "".join(
        f'''<article class="axis">
      <span class="axis-num" aria-hidden="true">{i + 1}</span>
      <h3><a href="{rfile}#{a["id"]}">{a["label"][lang]} : {a["title"][lang]}</a></h3>
      <p>{a["text"][lang]}</p>
    </article>'''.replace(" : ", " : " if lang == "fr" else ": ")
        for i, a in enumerate(AXES)
    )

    body = f'''<section class="hero">
  <canvas class="eeg" aria-hidden="true"></canvas>
  <div class="wrap hero-inner">
    <h1>{LAB[lang]}</h1>
    <p class="hero-alt" lang="{o}">{LAB[o]}</p>
    <p class="hero-lead">{t["lead"]}</p>
    <div class="actions">
      <a class="btn btn-primary" href="{rfile}">{t["b1"]}</a>
      <a class="btn btn-ghost" href="{rfile}#participate">{t["b2"]}</a>
    </div>
    <p class="hero-aff">{T["footer_aff"][lang].replace("<br>", ", ")}</p>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div>
      <h2>{t["why_h"]}</h2>
      <p class="kicker lede">{t["why_k"]}</p>
    </div>
    <div>
      <p>{t["p1"]}</p>
      <p>{t["p2"]}</p>
    </div>
  </div>
</section>

{approach_section(lang)}

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>{t["axes_h"]}</h2>
      <a class="more" href="{rfile}">{t["axes_more"]}</a>
    </div>
    <div class="axes">{axes}</div>
  </div>
</section>

<section class="section section-mist">
  <div class="wrap">
    <div class="section-head">
      <h2>{t["fund_h"]}</h2>
      <a class="more" href="{rfile}#funding">{t["fund_more"]}</a>
    </div>
    <ul class="funders">{funders_list(lang)}</ul>
  </div>
</section>

{participate_band(lang)}'''
    desc = t["lead"]
    return page(lang, "home", LAB[lang], desc, body)


# ---------------- Research ----------------

def research(lang):
    t = {
        "fr": {
            "title": "Recherche",
            "intro": "Nous combinons l'imagerie cérébrale, la modélisation computationnelle et l'intelligence artificielle pour comprendre comment la douleur est perçue et modulée.",
            "jumps": [("axis-1", "Axe 1"), ("axis-2", "Axe 2"), ("projects", "Projets en cours"), ("participate", "Participer"), ("funding", "Financement")],
            "related": "Travaux associés",
            "proj_h": "Projets de recherche en cours",
            "proj_p1": "Nous menons une variété de projets de recherche portant sur la perception de la douleur chez l'humain. Dans le cadre de ces études, des personnes participantes sont invitées à réaliser différentes tâches sur ordinateur et à répondre à des questionnaires, en laboratoire (Cirris, Université Laval ou Unité de neuroimagerie du CERVO) ou à distance.",
            "proj_p2": "Certains projets peuvent inclure l'exposition à des stimulations faiblement à modérément douloureuses ou désagréables, qui sont sécuritaires, contrôlées et toujours dans le respect des normes éthiques en vigueur. Dans certaines études, l'activité cérébrale ainsi que divers signaux physiologiques peuvent également être enregistrés à l'aide de méthodes non invasives.",
            "proj_list_h": "Quelques exemples de projets en cours",
            "projects": [
                "Étude visant à créer et à interpréter des modèles prédictifs de la douleur à l'aide de l'électroencéphalographie (EEG)",
                "Étude visant à comprendre comment la perception de la douleur est influencée par l'apprentissage",
                "Étude d'imagerie par résonance magnétique (IRM) sur l'interaction entre l'exploration et l'apprentissage sur la perception de la douleur",
                "Étude combinant deux méthodes de neuroimagerie (IRM et EEG) afin de mieux comprendre comment le cerveau traite la douleur",
            ],
            "eq_h": "Exemples du matériel utilisé",
            "eq": [
                ("thermode", "Thermode", "Stimulation douloureuse par la chaleur", ""),
                ("eeg", "Électroencéphalographie (EEG)", "Activité du cerveau",
                 'Crédit image : <a href="https://commons.wikimedia.org/wiki/File:Treinamento_de_EEG-20.jpeg">RIDC NeuroMat</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0">CC BY-SA 4.0</a>, via Wikimedia Commons'),
                ("irm", "Imagerie par résonance magnétique (IRM)", "Activité du cerveau",
                 'Crédit image : <a href="https://cervo.ulaval.ca/plateformes-et-initiatives-cervo/plateforme-irm/">UNiC, Unité de neuroimagerie du CERVO</a>'),
            ],
            "fund_h": "Financement",
            "fund_p": "Ces projets sont rendus possibles grâce au soutien de ces organismes subventionnaires.",
        },
        "en": {
            "title": "Research",
            "intro": "We combine brain imaging, computational modelling and artificial intelligence to understand how pain is perceived and modulated.",
            "jumps": [("axis-1", "Axis 1"), ("axis-2", "Axis 2"), ("projects", "Current projects"), ("participate", "Participate"), ("funding", "Funding")],
            "related": "Related work",
            "proj_h": "Current research projects",
            "proj_p1": "We conduct a wide range of research projects examining pain perception in humans. As part of these studies, participants are invited to complete various computer-based tasks and questionnaires, either in laboratory settings (Cirris, Université Laval, or the CERVO Neuroimaging Unit) or remotely.",
            "proj_p2": "Some projects may involve exposure to mild to moderately painful or unpleasant stimuli that are safe, well controlled, and always administered in compliance with current ethical standards. In certain studies, brain activity as well as various physiological signals may also be recorded using non-invasive methods.",
            "proj_list_h": "Examples of ongoing projects",
            "projects": [
                "A study aimed at developing and interpreting predictive models of pain using electroencephalography (EEG)",
                "A study investigating how pain perception is influenced by learning",
                "A magnetic resonance imaging (MRI) study examining the interaction between exploration and learning in pain perception",
                "A study combining two neuroimaging methods (MRI and EEG) to better understand how the brain processes pain",
            ],
            "eq_h": "Examples of the equipment used",
            "eq": [
                ("thermode", "Thermode", "Painful heat stimulation", ""),
                ("eeg", "Electroencephalography (EEG)", "Brain activity",
                 'Image credit: <a href="https://commons.wikimedia.org/wiki/File:Treinamento_de_EEG-20.jpeg">RIDC NeuroMat</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0">CC BY-SA 4.0</a>, via Wikimedia Commons'),
                ("irm", "Magnetic resonance imaging (MRI)", "Brain activity",
                 'Image credit: <a href="https://cervo.ulaval.ca/plateformes-et-initiatives-cervo/plateforme-irm/">UNiC, CERVO Neuroimaging Unit</a>'),
            ],
            "fund_h": "Funding",
            "fund_p": "These projects are made possible thanks to the support of the following funding agencies.",
        },
    }[lang]

    blocks = []
    for a in AXES:
        badge = "À venir" if lang == "fr" else "Upcoming"
        pubs = "".join(
            f'''<li class="pub"><span class="pub-year">{y}</span><div>
          <span class="pub-title">{title} <span class="badge">{badge}</span></span>
          <span class="pub-meta">{authors}{" " + note[lang] if note else ""}</span></div></li>'''
            for y, title, authors, note in a.get("upcoming", [])
        )
        pubs += "".join(
            f'''<li class="pub"><span class="pub-year">{y}</span><div>
          <a class="pub-title" href="{link[0] if link else "https://doi.org/" + doi}">{title}</a>
          <span class="pub-meta">{authors} {src}. doi:{doi}</span></div></li>'''
            for y, title, authors, src, doi, *link in a["pubs"]  # optional 6th item: link overriding the DOI
        )
        blocks.append(f'''<div class="axis-block split" id="{a["id"]}">
    <div>
      <span class="axis-label">{a["label"][lang]}</span>
      <h2>{a["title"][lang]}</h2>
      {carousel(a["id"], lang)}
    </div>
    <div>
      <p class="lede">{a["text"][lang]}</p>
      <h3 class="pubs-title">{t["related"]}</h3>
      <ul class="pubs">{pubs}</ul>
    </div>
  </div>''')

    projects = "".join(f"<li>{p}</li>" for p in t["projects"])
    figs = "".join(
        f'''<figure>{img_slot(f"../assets/img/research/{slug}.jpg", name, name.split(" (")[0] if "(" not in name else name[name.find("(")+1:name.find(")")], "media media-contain" if slug == "thermode" else "media")}
      <figcaption><strong>{name}</strong>{desc}{f'<span class="credit">{credit}</span>' if credit else ""}</figcaption></figure>'''
        for slug, name, desc, credit in t["eq"]
    )
    funders = funders_list(lang)

    body = f'''{page_head(t["title"], t["intro"], t["jumps"], "Fz Cz CPz Pz C4", 11, "fmri")}

<section class="section">
  <div class="wrap">
  {"".join(blocks)}
  </div>
</section>

<section class="section section-mist" id="projects">
  <div class="wrap split">
    <div><h2>{t["proj_h"]}</h2></div>
    <div>
      <p class="lede">{t["proj_p1"]}</p>
      <p>{t["proj_p2"]}</p>
      <h3 class="pubs-title">{t["proj_list_h"]}</h3>
      <ul class="ticks">{projects}</ul>
    </div>
  </div>
  <div class="wrap" style="margin-top:clamp(3rem,6vw,4.5rem)">
    <h3>{t["eq_h"]}</h3>
    <div class="figures">{figs}</div>
  </div>
</section>

{participate_band(lang, with_id=True)}

<section class="section" id="funding">
  <div class="wrap">
    <h2>{t["fund_h"]}</h2>
    <p>{t["fund_p"]}</p>
    <ul class="funders">{funders}</ul>
  </div>
</section>'''
    return page(lang, "research", t["title"], t["intro"], body)


# ---------------- Team ----------------

def start_year(member):
    """Earliest year in a member's role; members without a year go last."""
    years = re.findall(r"\b(?:19|20)\d\d\b", member[2]["en"])
    return min(map(int, years)) if years else 9999


def team(lang):
    t = {
        "fr": {"title": "Équipe", "intro": "Des étudiant·e·s, des stagiaires et du personnel de recherche en psychologie, en neurosciences et en informatique.",
               "jumps": [("director", "Direction"), ("students", "Étudiant·e·s"), ("staff", "Personnel de recherche"), ("alumni", "Anciens membres")],
               "dir": "Direction", "career": "Expérience professionnelle et formation",
               "students": "Étudiant·e·s et stagiaires postdoctoraux·ales", "staff": "Personnel de recherche",
               "alumni": "Anciens membres du laboratoire", "show": f"Afficher les {len(ALUMNI)} entrées",
               "photo": "Photo de"},
        "en": {"title": "Team", "intro": "Students, trainees and research staff from psychology, neuroscience and computer science.",
               "jumps": [("director", "Director"), ("students", "Students"), ("staff", "Research staff"), ("alumni", "Lab alumni")],
               "dir": "Director", "career": "Professional experience and education",
               "students": "Students and postdoctoral fellows", "staff": "Research staff",
               "alumni": "Lab alumni", "show": f"Show all {len(ALUMNI)} entries",
               "photo": "Photo of"},
    }[lang]

    roles = "".join(f"<p><strong>{r[lang]}</strong>{w[lang]}</p>" for r, w in PI["roles"])
    tl = "".join(f'<li><span class="yrs">{y}</span><span>{d[lang]}</span></li>' for y, d in PI["timeline"])
    links = "".join(f'<a class="btn btn-outline btn-sm" href="{u}">{l[lang]}</a>' for l, u in PI["links"])

    def person(slug, name, role, topic=None):
        tp = f'<p class="topic">{topic[lang]}</p>' if topic else ""
        return f'''<li class="person">{img_slot(f"../assets/img/team/{slug}.jpg", f"{t['photo']} {name}", initials(name))}
        <h3>{name}</h3><p class="role">{role[lang]}</p>{tp}</li>'''

    students = "".join(person(s, n, r, tp) for s, n, r, tp in sorted(STUDENTS, key=start_year))
    staff = "".join(person(s, n, r) for s, n, r in sorted(STAFF, key=start_year))
    alumni = "".join(
        f'<li><span class="who">{(ne or nf) if lang == "en" else nf}</span><span class="what">{wf if lang == "fr" else we}</span></li>'
        for nf, ne, wf, we in ALUMNI
    )

    body = f'''{page_head(t["title"], t["intro"], t["jumps"], "C3 Cz C4", 23, "fmri")}

<section class="section" id="director">
  <div class="wrap pi">
    {img_slot(f"../assets/img/team/{PI['slug']}.jpg", f"{t['photo']} {PI['name']}", initials(PI["name"]))}
    <div>
      <span class="axis-label">{t["dir"]}</span>
      <h2>{PI["name"]}</h2>
      <div class="pi-roles">{roles}</div>
      <h3>{t["career"]}</h3>
      <ul class="timeline">{tl}</ul>
      <div class="links">{links}</div>
    </div>
  </div>
</section>

<section class="section section-mist" id="students">
  <div class="wrap">
    <h2>{t["students"]}</h2>
    <ul class="people">{students}</ul>
  </div>
</section>

<section class="section" id="staff">
  <div class="wrap">
    <h2>{t["staff"]}</h2>
    <ul class="people">{staff}</ul>
  </div>
</section>

<section class="section" id="alumni">
  <div class="wrap">
    <h2>{t["alumni"]}</h2>
    <details class="alumni"><summary>{t["show"]}</summary><ul>{alumni}</ul></details>
  </div>
</section>'''
    return page(lang, "team", t["title"], t["intro"], body)


# ---------------- Contact ----------------

def contact(lang):
    t = {
        "fr": {
            "title": "Nous joindre",
            "intro": "Vous souhaitez vous joindre au laboratoire ou participer à une étude? Voici à qui écrire.",
            "join_h": "Faire partie du laboratoire",
            "join_p": "Vous souhaitez rejoindre le laboratoire à titre d'étudiant·e (maîtrise ou doctorat), de stagiaire postdoctoral·e ou comme membre du personnel de recherche (auxiliaire ou professionnel·le de recherche)? Écrivez au Pr Michel-Pierre Coll en joignant votre CV et une brève lettre de motivation.",
            "join_b": "Écrire au Pr Coll",
            "part_h": "Participer à une étude",
            "part_p": "Vous aimeriez participer à l'un de nos projets de recherche à titre de volontaire? Pour en savoir plus ou pour manifester votre intérêt, écrivez à notre équipe ou remplissez le formulaire.",
            "part_b1": "Manifester mon intérêt", "part_b2": "Écrire à l'équipe",
            "where": "Où nous trouver",
            "map_title": "Carte :",
        },
        "en": {
            "title": "Contact",
            "intro": "Want to join the lab or take part in a study? Here's who to write to.",
            "join_h": "Join the lab",
            "join_p": "Interested in joining the lab as a graduate student (master's or PhD), a postdoctoral fellow, or a member of the research staff (research assistant or research professional)? Write to Prof. Michel-Pierre Coll and include your CV and a short cover letter.",
            "join_b": "Email Prof. Coll",
            "part_h": "Take part in a study",
            "part_p": "Would you like to volunteer for one of our research projects? To learn more or express your interest, email our team or fill out the form.",
            "part_b1": "Express your interest", "part_b2": "Email the team",
            "where": "Where to find us",
            "map_title": "Map:",
        },
    }[lang]

    places = "".join(
        f'''<div class="place" id="{p["id"]}">
      <h3>{p["name"][lang]}</h3>
      <address>{p["addr"]}</address>
      <iframe src="https://maps.google.com/maps?q={p["q"]}&amp;z=16&amp;output=embed&amp;hl={lang}" title="{t["map_title"]} {p["name"][lang]}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      <a class="maplink" href="{maps_link(p["q"])}">{T["open_map"][lang]}</a>
    </div>'''
        for p in PLACES
    )

    body = f'''{page_head(t["title"], t["intro"], None, "Fz Cz Pz", 5)}

<section class="section section-mist">
  <div class="wrap paths">
    <div class="path" id="join">
      <h2>{t["join_h"]}</h2>
      <p>{t["join_p"]}</p>
      <a class="email" href="mailto:{EMAIL_PI}">{EMAIL_PI}</a>
      <div class="actions"><a class="btn btn-dark" href="mailto:{EMAIL_PI}">{t["join_b"]}</a></div>
    </div>
    <div class="path" id="participate">
      <h2>{t["part_h"]}</h2>
      <p>{t["part_p"]}</p>
      <a class="email" href="mailto:{EMAIL_LAB}">{EMAIL_LAB}</a>
      <div class="actions">
        <a class="btn btn-dark" href="{FORM_URL}">{t["part_b1"]}</a>
        <a class="btn btn-outline" href="mailto:{EMAIL_LAB}">{t["part_b2"]}</a>
      </div>
    </div>
  </div>
</section>

<section class="section" id="locations">
  <div class="wrap">
    <h2>{t["where"]}</h2>
    <div class="places">{places}</div>
  </div>
</section>'''
    return page(lang, "contact", t["title"], t["intro"], body)


# ------------------------------------------------------------------
# Root files
# ------------------------------------------------------------------

ROOT_INDEX = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Laboratoire apprentissage et douleur / Pain and Learning Lab</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="alternate" hreflang="fr" href="https://www.painlearninglab.ca/fr/index.html">
<link rel="alternate" hreflang="en" href="https://www.painlearninglab.ca/en/index.html">
<meta name="description" content="Laboratoire apprentissage et douleur / Pain and Learning Lab, Université Laval et Cirris.">
<meta property="og:title" content="Laboratoire apprentissage et douleur / Pain and Learning Lab">
<meta property="og:description" content="Imagerie cérébrale, modélisation computationnelle et IA pour comprendre la douleur. Human brain imaging, computational modelling and AI to understand pain.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.painlearninglab.ca/">
<meta property="og:image" content="https://www.painlearninglab.ca/assets/img/og-fr.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script>
  var l = 'fr';
  try { if (localStorage.getItem('pll-lang') === 'en') l = 'en'; } catch (e) {}
  location.replace(l + '/index.html');
</script>
<noscript><meta http-equiv="refresh" content="0; url=fr/index.html"></noscript>
</head>
<body>
<p><a href="fr/index.html">Français</a> | <a href="en/index.html">English</a></p>
</body>
</html>
'''

NOT_FOUND = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable / Page not found</title>
<link rel="icon" href="/assets/img/favicon.png" type="image/png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&amp;display=swap">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body style="background:var(--abyss);color:#fff;min-height:100vh;display:grid;place-items:center">
<main class="wrap" style="padding:4rem 0">
  <h1>Page introuvable</h1>
  <p style="color:var(--on-dark)">Cette page n'existe pas ou a été déplacée.</p>
  <p><a class="btn btn-primary" href="/fr/index.html">Retour à l'accueil</a></p>
  <h2 lang="en" style="margin-top:3rem">Page not found</h2>
  <p lang="en" style="color:var(--on-dark)">This page doesn't exist or has moved.</p>
  <p lang="en"><a class="btn btn-ghost" href="/en/index.html">Back to home</a></p>
</main>
</body>
</html>
'''

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><rect width="36" height="36" rx="9" fill="#071E33"/><path d="M5 19.5h5.5l2.2-2.6 2.3 2.6 2.4-10.5 3.4 16.5 2.4-7.5 1.6 1.5H31" fill="none" stroke="#5FE3D2" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
'''


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    for lang in ("fr", "en"):
        write(f"{lang}/{file_for('home', lang)}", home(lang))
        write(f"{lang}/{file_for('research', lang)}", research(lang))
        write(f"{lang}/{file_for('team', lang)}", team(lang))
        write(f"{lang}/{file_for('contact', lang)}", contact(lang))
    write("index.html", ROOT_INDEX)
    write("404.html", NOT_FOUND)
    print("Site generated in", ROOT)


if __name__ == "__main__":
    main()
