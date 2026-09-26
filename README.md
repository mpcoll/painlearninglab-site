# Laboratoire apprentissage et douleur / Pain and Learning Lab: website

A static site (plain HTML, CSS and JS, with no build step required) that can be uploaded to any web server.

## Structure

```
index.html            Sends visitors to /fr/ (or /en/ if they previously chose English)
404.html              Bilingual "page not found"
.htaccess             Apache only: redirects the old Google Sites URLs to the new pages
fr/                   index.html, recherche.html, equipe.html, nous-joindre.html
en/                   index.html, research.html, team.html, contact.html
assets/css/style.css  All styles (colours are variables at the top)
assets/js/main.js     Language memory, mobile menu, animated EEG header
assets/img/           Photos and logos (see below)
_build/build.py       Optional generator; all FR/EN content lives here side by side
```

## Language switching

Every page has a FR | EN switch in the header. It goes to the same page in the other
language, keeps the section you were reading (e.g. `#projects`), and remembers the choice.
French is the default.

## Images

Already in place: the lab logo (header and favicon), the Université Laval and Cirris logos (footer), the six funder
logos, the three equipment photos, and portraits of Michel-Pierre Coll, Alyson Champagne, Mégane Lacombe-Thibault, Shima Hassanpour, Joshua Duquette, Antoine Cyr-Bouchard and Pouya Rabiei.

Still missing (a styled placeholder shows until the file exists). Save them with these exact names:

- `assets/img/team/`: leane-beaulieu-laliberte.jpg, nicolas-roy.jpg, sanoussy-diallo.jpg,
  audrey-lalancette.jpg, lorie-eve-barrette.jpg,
  laurie-caumartin.jpg, alysun-paradis.jpg
  (square or portrait works, at least 600 px wide; faces are framed slightly above centre)

Funder logos live in `assets/img/funders/` (svg, png or jpg). A language-specific file (e.g. `cihr-fr.png`)
takes priority over a shared one (e.g. `cihr.png`); the funder's name is shown as text if no logo exists.
Logo changes require running `python3 _build/build.py`.

## Editing content

The simplest option is to edit the HTML files directly, but remember to update both the `fr/` and the `en/` version.
Alternatively, edit `_build/build.py` (the FR and EN text sit next to each other) and run
`python3 _build/build.py` to regenerate all pages. Don't mix the two methods: running the
script overwrites manual HTML edits.

## Deploying

Upload everything (including the hidden `.htaccess`) to the web root. The `_build/` folder is optional.
On a non-Apache server, recreate the redirects in `.htaccess` in that server's config.
The domain currently points to Google Sites, so its DNS will need to point to the new server.
