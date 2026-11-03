# Maintaining this edition

This repository is a public content snapshot, separate from the PodPlo
application. Do not copy application configuration, credentials, private Skill
rules, hidden references, or user assets here.

## Languages and source

English articles in `en/` are the source for the eight added languages. Existing
Simplified Chinese articles remain in `zh/`. Locale folders and their README
filenames are defined in `scripts/localize.py`; Brazilian Portuguese is `pt-BR`
and Simplified Chinese is identified as `zh-CN` in metadata.

Each language has the same 165 exported articles, `INDEX.md`, and
`ai-directions.md`. The latter contains 123 natural-language instructions inside
copyable `text` code fences. Translate the instructions; preserve the fences,
article slugs, explicit anchor IDs, image URLs, and file hierarchy.

`ai-directions/INDEX.md` and `part-1.md` / `part-2.md` are generated reading views,
bringing the total to 170 Markdown files per language. Each part is smaller than
390 KB for reliable GitHub previews. The index links to the complete original
collection as a raw download. These three generated files are excluded from
translation source extraction; their instruction text comes from the complete
collection. Never remove a direction to satisfy a preview limit.

## Offline build and validation

Python 3.10 or newer is sufficient; no third-party Python packages are required.
Run these commands from this repository:

```sh
python3 scripts/localize.py inventory
python3 scripts/localize.py build
python3 scripts/validate.py
git diff --check
```

Build is a complete-edition operation: all eight added translation catalogs must
be available before any documents are written. It rebuilds every added locale,
updates all ten language selectors, and refreshes the manifest. It does not
contact a translation provider or publish to GitHub. Repeated builds produce the
same files.

Edit `data/translations/<locale>.json` for prose corrections and
`data/terminology.json` for preferred titles and labels. Terminology overrides
take precedence during builds. `data/editorial.json` contains reviewed shared
instruction paragraphs and contextual corrections. Those paragraphs are reused
in both article prose and collected prompt blocks to keep their meaning aligned.
The catalogs map exact public English source
strings to their translations; missing translations cause the build to fail
instead of silently inserting English. Context-sensitive corrections may also
require adjusting how the source paragraph is segmented.

## Updating translations

After an explicitly authorized content update, these commands submit only
missing, deduplicated public English prose to Google Translate:

```sh
python3 scripts/localize.py translate --workers 4
# Resume only selected languages if necessary:
python3 scripts/localize.py translate --locales ja ar --workers 2
```

This command uses a public translation endpoint, with retries and checkpointed
catalogs. Service availability and translation quality are not guaranteed.
Review new prose and terminology, then run the offline build and validation.
Do not add private content to the translation source.

The manifest's `pages` list preserves the original 165-article edition contract
per language; `documents` additionally lists every contents and collected
directions page. `readmes` lists the ten root READMEs. New source articles require
an intentional update to that edition contract and validation counts.

## Review and publish

Check representative long catalog pages, a direction page, a product page, and
each root README in GitHub-flavored Markdown. Check Arabic on desktop and narrow
screens, including the first heading, code blocks, and language selector. Keep
original image wording and existing English website destinations explicit in
edition notes. Structural validation does not certify translation fluency or
that every original public direction produces the expected image.

Before publishing, verify the authenticated GitHub account and the exact remote
repository, inspect the full diff, and confirm that only public content is staged.
