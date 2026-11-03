#!/usr/bin/env python3
"""Localize the public Guide snapshot without translating its markup or URLs.

Build and validation are offline. Only the explicit `translate` command sends
deduplicated, already-public English prose to Google's translation endpoint.
Reviewed translations live in data/translations and can be edited directly.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import html
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
LOCALES = {
    "en": {"name": "English", "dir": "en", "readme": "README.md"},
    "zh-CN": {"name": "简体中文", "dir": "zh", "readme": "README.zh-CN.md"},
    "pt-BR": {"name": "Português (Brasil)", "dir": "pt-BR", "readme": "README.pt-BR.md"},
    "es": {"name": "Español", "dir": "es", "readme": "README.es.md"},
    "fr": {"name": "Français", "dir": "fr", "readme": "README.fr.md"},
    "de": {"name": "Deutsch", "dir": "de", "readme": "README.de.md"},
    "ar": {"name": "العربية", "dir": "ar", "readme": "README.ar.md"},
    "ru": {"name": "Русский", "dir": "ru", "readme": "README.ru.md"},
    "ja": {"name": "日本語", "dir": "ja", "readme": "README.ja.md"},
    "hi": {"name": "हिन्दी", "dir": "hi", "readme": "README.hi.md"},
}
NEW_LOCALES = tuple(k for k in LOCALES if k not in ("en", "zh-CN"))
CATALOG_DIR = ROOT / "data/translations"
NAV_START, NAV_END = "<!-- LANGUAGES:START -->", "<!-- LANGUAGES:END -->"
OLD_README_NAV = '<p align="center"><strong>English</strong> · <a href="README.zh-CN.md">简体中文</a></p>'
OLD_ZH_NAV = '<p align="center"><a href="README.md">English</a> · <strong>简体中文</strong></p>'
OLD_INDEX_NAV = "[English](../en/INDEX.md) · [简体中文](../zh/INDEX.md)"

# Opaque syntax is copied byte-for-byte, while alt/title attributes are localized.
# Link destinations can contain balanced parentheses (e.g. image filenames).
TOKENS = re.compile(
    r'<!--.*?-->|<[^>]+>|\]\((?:[^()\n]|\([^()\n]*\))*\)'
    r'|https?://[^\s<>\)"\']+|\*\*|[\[\]|`]',
    re.DOTALL,
)
PREFIX = re.compile(r"^(\s*(?:#{1,6}\s+|(?:[-+*]|\d+\.)\s+|>\s*)?)(.*?)(\s*)$", re.DOTALL)
ATTR = re.compile(r'\b(alt|title)="([^"]*)"')
WORDS = re.compile(r"[A-Za-z]{2}")
FENCE = re.compile(r"^\s*```")
PROTECTED = ("ETERNAL BLOOM", "Photo to Art", "PodPlo", "Skills", "Skill", "Recreate", "Remix", "POD")
PROTECT_PATTERN = re.compile(r"\b(?:" + "|".join(map(re.escape, PROTECTED)) + r")\b")
NOTES = {
    "pt-BR": "Os capítulos desta edição estão em português do Brasil. Os links para o site PodPlo podem abrir páginas em inglês. Os textos nas imagens originais são mantidos.",
    "es": "Los capítulos de esta edición están en español. Los enlaces al sitio de PodPlo pueden abrir páginas en inglés. Se conserva el texto de las imágenes originales.",
    "fr": "Les chapitres de cette édition sont en français. Les liens vers le site PodPlo peuvent ouvrir des pages en anglais. Le texte des images originales est conservé.",
    "de": "Die Kapitel dieser Ausgabe sind auf Deutsch. Links zur PodPlo-Website können englische Seiten öffnen. Texte in den Originalbildern bleiben unverändert.",
    "ar": "فصول هذا الإصدار مترجمة إلى العربية. قد تفتح روابط موقع PodPlo صفحات باللغة الإنجليزية. تظل النصوص داخل الصور الأصلية كما هي.",
    "ru": "Главы этого издания переведены на русский язык. Ссылки на сайт PodPlo могут открывать страницы на английском. Надписи на исходных изображениях сохранены.",
    "ja": "この版の各章は日本語です。PodPlo サイトへのリンク先は英語で表示される場合があります。元の画像内の文字はそのまま残しています。",
    "hi": "इस संस्करण के अध्याय हिन्दी में हैं। PodPlo वेबसाइट के लिंक अंग्रेज़ी पृष्ठ खोल सकते हैं। मूल चित्रों में मौजूद पाठ को यथावत रखा गया है।",
}
FULL_GUIDE = {
    "pt-BR": "Guia completo em português do Brasil", "es": "Guía completa en español",
    "fr": "Guide complet en français", "de": "Vollständiger Leitfaden auf Deutsch",
    "ar": "الدليل الكامل بالعربية", "ru": "Полное руководство на русском",
    "ja": "日本語ガイドの全目次", "hi": "हिन्दी में पूरी मार्गदर्शिका",
}
BY = {"pt-BR": "Por", "es": "Por", "fr": "Par", "de": "Von", "ar": "إعداد",
      "ru": "Автор", "ja": "制作：", "hi": "प्रस्तुतकर्ता:"}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def read_catalog(locale):
    p = CATALOG_DIR / f"{locale}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def polished_catalog(locale):
    catalog = read_catalog(locale)
    terminology = json.loads((ROOT / "data/terminology.json").read_text())[locale]
    catalog.update(terminology)
    editorial = json.loads((ROOT / "data/editorial.json").read_text())
    catalog.update({source: values[locale] for source, values in editorial.items() if locale in values})
    creative_direction = {
        "pt-BR": "DIREÇÃO CRIATIVA", "es": "DIRECCIÓN CREATIVA", "fr": "ORIENTATION CRÉATIVE",
        "de": "GESTALTUNGSRICHTUNG", "ar": "اتجاه إبداعي", "ru": "ТВОРЧЕСКОЕ НАПРАВЛЕНИЕ",
        "ja": "制作の方向性", "hi": "रचनात्मक दिशा",
    }
    for source, translated in list(catalog.items()):
        if locale == "ar":
            if re.search(r"\btreatments?\b", source, re.I):
                translated = (translated.replace("العلاجات", "المعالجات").replace("علاجات", "معالجات")
                              .replace("العلاج", "المعالجة").replace("علاج", "معالجة"))
            if re.search(r"\bpalette\b", source, re.I):
                translated = translated.replace("اللوحة", "لوحة الألوان")
            if re.search(r"\bsubjects?\b", source, re.I) and not re.search(r"\btheme\b", source, re.I):
                translated = (translated.replace("الموضوعات", "العناصر").replace("موضوعات", "عناصر")
                              .replace("مواضيع", "عناصر").replace("الموضوع", "العنصر").replace("موضوع", "عنصر"))
        elif locale == "hi" and re.search(r"\btreatments?\b", source, re.I):
            translated = translated.replace("उपचारों", "दृश्य शैलियों").replace("उपचार", "दृश्य शैली")
        elif locale == "ja" and re.search(r"\bsubjects?\b", source, re.I) and not re.search(r"\btheme\b", source, re.I):
            translated = translated.replace("主題", "主役")
        catalog[source] = translated
    for source in list(catalog):
        if " → " in source and ": " not in source:
            parts = source.split(" → ")
            if all(part in catalog for part in parts):
                catalog[source] = " → ".join(catalog[part] for part in parts)
        if source.endswith(" / CREATIVE DIRECTION"):
            category = source.removesuffix(" / CREATIVE DIRECTION")
            if category in catalog:
                catalog[source] = catalog[category] + " / " + creative_direction[locale]
    # Russian machine translations sometimes interpret a model "prompt" as an
    # invitation. Restrict this correction to source strings about AI prompts.
    if locale == "ru":
        forms = {"приглашение": "промпт", "приглашения": "промпта", "приглашений": "промптов",
                 "приглашению": "промпту", "приглашением": "промптом", "приглашениях": "промптах"}
        for source, value in list(catalog.items()):
            if re.search(r"\bprompts?\b", source, re.I):
                def replace(match):
                    result = forms[match[0].lower()]
                    return result.capitalize() if match[0][0].isupper() else result
                catalog[source] = re.sub(r"\b(?:" + "|".join(forms) + r")\b", replace, value, flags=re.I)
    fields = ("Target direction", "Input and output", "Target structure", "Background",
              "Wording", "Preserve and adapt", "Scope and boundaries", "Output check")
    for source, translated in list(catalog.items()):
        numbered = re.fullmatch(r"(\d+\s+)(.+)", source)
        if numbered and numbered[2] in terminology:
            catalog[source] = numbered[1] + terminology[numbered[2]]
            continue
        for field in fields:
            if not source.startswith(field + ": "):
                continue
            if field == "Target direction":
                parts = source[len(field) + 2:].split(" → ")
                if all(p in catalog for p in parts):
                    catalog[source] = terminology[field] + ": " + " → ".join(catalog[p] for p in parts)
                    break
            body = source[len(field) + 2:]
            if body in catalog:
                catalog[source] = terminology[field] + ": " + catalog[body]
                break
            prefix = re.match(r"^[^:：]+[:：]\s*", translated)
            if not prefix:
                raise ValueError(f"{locale}: missing instruction label for {source[:70]}")
            catalog[source] = terminology[field] + ": " + translated[prefix.end():]
            break
    return catalog


def map_plain(value, lookup):
    leading = value[:len(value) - len(value.lstrip())]
    trailing = value[len(value.rstrip()):]
    core = value.strip()
    if not WORDS.search(core):
        return value
    # Formatting symbols belong to Markdown, not the prose sent for translation.
    left = re.match(r"^[*_~]+", core)
    right = re.search(r"[*_~]+$", core)
    a = left.group() if left else ""
    b = right.group() if right else ""
    text = core[len(a):len(core) - len(b) if b else None]
    if not WORDS.search(text):
        return value
    return leading + a + lookup(text) + b + trailing


def map_inline(line, lookup):
    output, offset = [], 0
    for match in TOKENS.finditer(line):
        output.append(map_plain(line[offset:match.start()], lookup))
        token = match.group()
        if token.startswith("<") and not token.startswith("<!--"):
            token = ATTR.sub(lambda m: m[1] + '="' + html.escape(
                map_plain(html.unescape(m[2]), lookup), quote=True
            ) + '"', token)
        output.append(token)
        offset = match.end()
    output.append(map_plain(line[offset:], lookup))
    return "".join(output)


def strip_navigation(text):
    text = re.sub(re.escape(NAV_START) + r".*?" + re.escape(NAV_END) + r"\n*", "", text, flags=re.DOTALL)
    return text.replace(OLD_README_NAV, "").replace(OLD_ZH_NAV, "").replace(OLD_INDEX_NAV, "")


def map_document(text, lookup):
    output = []
    for line in strip_navigation(text).splitlines(keepends=True):
        if FENCE.match(line):
            output.append(line)
            continue
        match = PREFIX.match(line)
        output.append(match[1] + map_inline(match[2], lookup) + match[3])
    return "".join(output)


def source_documents():
    return [ROOT / "README.md", *sorted((ROOT / "en").rglob("*.md"))]


def source_strings():
    strings = set()
    def collect(s):
        strings.add(s)
        return s
    for path in source_documents():
        map_document(path.read_text(), collect)
    return sorted(strings)


def protect(text):
    terms = []
    def replace(match):
        terms.append(match.group())
        return f"__ZXQ{len(terms) - 1:03d}XQZ__"
    return PROTECT_PATTERN.sub(replace, text), terms


def restore(text, terms):
    for i, term in enumerate(terms):
        token = f"ZXQ{i:03d}XQZ"
        if text.count(token) != 1:
            raise ValueError(f"Protected term was changed: {term}")
        text = re.sub(r"_*" + token + r"_*", lambda _: term, text)
    if re.search(r"ZXQ\d+XQZ|\[\d{6}\]", text):
        raise ValueError("Unresolved translation marker")
    return text.strip()


def request_translation(locale, batch):
    protected = [protect(s) for s in batch]
    query = "\n\n".join(f"[{i:06d}]\n{pair[0]}" for i, pair in enumerate(protected))
    url = "https://translate.googleapis.com/translate_a/single?" + urlencode({
        "client": "gtx", "sl": "en", "tl": locale, "dt": "t", "q": query,
    })
    with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=45) as response:
        data = json.load(response)
    result = "".join(part[0] for part in data[0] if part[0])
    markers = list(re.finditer(r"\[(\d{6})\]", result))
    if [int(m[1]) for m in markers] != list(range(len(batch))):
        raise ValueError("Translation batch markers were changed")
    values = []
    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(result)
        value = restore(result[marker.end():end], protected[i][1])
        if not value or "\n" in value:
            raise ValueError("Translation has missing prose or unexpected line breaks")
        values.append(value)
    return dict(zip(batch, values))


def translate_batch(locale, batch, attempts=4):
    error = None
    for attempt in range(attempts):
        try:
            return request_translation(locale, batch)
        except ValueError as exc:
            # Marker/format errors are deterministic; split promptly instead of
            # retrying an identical malformed response several times.
            error = exc
            break
        except Exception as exc:
            error = exc
            time.sleep(min(2 ** attempt, 8))
    if len(batch) > 1:
        midpoint = len(batch) // 2
        return {**translate_batch(locale, batch[:midpoint]), **translate_batch(locale, batch[midpoint:])}
    raise RuntimeError(f"{locale}: translation failed for {batch[0][:70]!r}: {error}")


def batches(strings, maximum=3400):
    batch, size = [], 0
    for string in strings:
        weight = len(string) + 14
        if batch and size + weight > maximum:
            yield batch
            batch, size = [], 0
        batch.append(string)
        size += weight
    if batch:
        yield batch


def translate_all(locales, workers):
    strings = source_strings()
    catalogs = {code: read_catalog(code) for code in locales}
    pending = []
    progress, totals = {}, {}
    for locale in locales:
        missing = [s for s in strings if s not in catalogs[locale]]
        jobs = list(batches(missing))
        progress[locale], totals[locale] = 0, len(jobs)
        pending.extend((locale, batch) for batch in jobs)
        print(f"{locale}: {len(catalogs[locale])} cached, {len(missing)} missing, {len(jobs)} batches", flush=True)
    failures = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(translate_batch, locale, batch): locale for locale, batch in pending}
        for job in as_completed(jobs):
            locale = jobs[job]
            try:
                catalogs[locale].update(job.result())
                write_json(CATALOG_DIR / f"{locale}.json", dict(sorted(catalogs[locale].items())))
                progress[locale] += 1
                if progress[locale] % 10 == 0 or progress[locale] == totals[locale]:
                    print(f"{locale}: {progress[locale]}/{totals[locale]} batches, "
                          f"{len(catalogs[locale])} translations", flush=True)
            except Exception as exc:
                failures.append(str(exc))
    if failures:
        raise RuntimeError("\n".join(failures))


def navigation(locale, current_path, article=None):
    """Link to the equivalent document, not just each locale's homepage."""
    links = []
    for code, data in LOCALES.items():
        target = Path(data["dir"]) / article if article else Path(data["readme"])
        relative = os.path.relpath(ROOT / target, (ROOT / current_path).parent)
        label = data["name"]
        links.append(f"**{label}**" if code == locale else f"[{label}]({relative})")
    # Isolate the selector from Arabic prose to retain consistent language order.
    return NAV_START + '\n<div dir="ltr">\n\n' + " · ".join(links) + "\n\n</div>\n" + NAV_END


def with_navigation(body, locale, path, article=None):
    body = strip_navigation(body).strip()
    nav = navigation(locale, path, article)
    if locale == "ar":
        return nav + '\n\n<div dir="rtl" lang="ar">\n\n' + body + "\n\n</div>\n"
    return nav + "\n\n" + body + "\n"


def rewrite_locale_links(text, locale):
    directory = LOCALES[locale]["dir"]
    # Relative links within en/ already point to the corresponding local file.
    text = re.sub(r'(?<=[("\'])en/', directory + "/", text)
    text = text.replace("utm_content=en_", f"utm_content={locale}_")
    return text


def heading(text, fallback):
    match = re.search(r"^# (.+)$", text, re.MULTILINE)
    return match[1] if match else fallback


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(locales):
    if set(locales) != set(NEW_LOCALES):
        raise ValueError("Build is atomic at the edition level: all eight new locales are required. "
                         "Use --locales only with translate to resume selected translations.")
    # Do not read application files, private configuration, or live site data.
    source = {p.relative_to(ROOT / "en"): p.read_text() for p in sorted((ROOT / "en").rglob("*.md"))}
    readme_source = (ROOT / "README.md").read_text()
    required = set(source_strings())
    original = json.loads((ROOT / "data/manifest.json").read_text())
    articles = {Path(p["path"]).relative_to("en") for p in original["pages"] if p["locale"] == "en"}
    if set(source) != articles | {Path("INDEX.md"), Path("ai-directions.md")}:
        raise ValueError("English source file tree disagrees with the edition manifest")
    catalogs = {}
    for locale in locales:
        catalog = polished_catalog(locale)
        missing = required - catalog.keys()
        if missing:
            raise ValueError(f"{locale}: {len(missing)} missing translations; run translate first")
        catalogs[locale] = catalog
    for locale in locales:
        catalog = catalogs[locale]
        directory = LOCALES[locale]["dir"]
        for article, body in source.items():
            target = Path(directory) / article
            translated = rewrite_locale_links(map_document(body, catalog.__getitem__), locale)
            if article == Path("INDEX.md"):
                translated = re.sub(r"^(# .+)$", r"\1\n\n> " + NOTES[locale], translated, count=1, flags=re.MULTILINE)
            path = ROOT / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(with_navigation(translated, locale, target, article))
        translated = rewrite_locale_links(map_document(readme_source, catalog.__getitem__), locale)
        publisher = (f"https://podplo.app/?utm_source=github&utm_medium=readme"
                     f"&utm_campaign=print-on-demand-design-guide&utm_content={locale}_publisher")
        author = f"{BY[locale]} [PodPlo]({publisher}) · [{FULL_GUIDE[locale]}]({directory}/INDEX.md)"
        translated = re.sub(r"^.*utm_content=" + re.escape(locale) + r"_publisher.*$", author,
                            translated, flags=re.MULTILINE)
        translated = re.sub(r"^\*\*.*INDEX\.md.*INDEX\.md.*\*\*$",
                            f"**[{FULL_GUIDE[locale]}]({directory}/INDEX.md)**", translated, flags=re.MULTILINE)
        translated = re.sub(r"^(<h1[^>]*>.*?</h1>)$", r"\1\n\n> " + NOTES[locale], translated,
                            count=1, flags=re.MULTILINE)
        readme_path = Path(LOCALES[locale]["readme"])
        (ROOT / readme_path).write_text(with_navigation(translated, locale, readme_path))
        print(f"Built {locale}: {len(source)} documents and {readme_path}", flush=True)
    # Original English and Chinese content is preserved; only navigation changes.
    for locale in ("en", "zh-CN"):
        data = LOCALES[locale]
        for path in sorted((ROOT / data["dir"]).rglob("*.md")):
            relative = path.relative_to(ROOT)
            article = path.relative_to(ROOT / data["dir"])
            path.write_text(with_navigation(path.read_text(), locale, relative, article))
        path = ROOT / data["readme"]
        path.write_text(with_navigation(path.read_text(), locale, path.relative_to(ROOT)))
    build_manifest()


def build_manifest():
    manifest_path = ROOT / "data/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    # The original manifest identifies the 165 exported articles per locale.
    source_records = [p for p in manifest["pages"] if p["locale"] == "en"]
    pages, documents, readmes = [], [], []
    for locale, data in LOCALES.items():
        for original in source_records:
            article = Path(original["path"]).relative_to("en")
            relative = Path(data["dir"]) / article
            path = ROOT / relative
            if not path.exists():
                raise ValueError(f"Missing document: {relative}")
            web = original["webUrl"]
            if locale == "zh-CN":
                web = web.replace("https://podplo.app/pod-guide", "https://podplo.app/zh/pod-guide")
            record = {"path": str(relative), "title": heading(path.read_text(), original["title"]),
                      "locale": locale, "webUrl": web, "sha256": sha256(path)}
            if locale in NEW_LOCALES:
                record.update({"sourcePath": original["path"], "webLocale": "en"})
            pages.append(record)
        for path in sorted((ROOT / data["dir"]).rglob("*.md")):
            documents.append({"path": str(path.relative_to(ROOT)), "locale": locale,
                              "sha256": sha256(path)})
        path = ROOT / data["readme"]
        readmes.append({"path": data["readme"], "locale": locale, "sha256": sha256(path)})
    manifest.update({
        "sourceEdition": manifest.get("sourceEdition", manifest["edition"]),
        "edition": "2026-11-03", "languages": list(LOCALES), "guidePages": len(pages),
        "totalGuideDocuments": len(documents), "pages": pages,
        "documents": documents, "readmes": readmes,
        "localeDirectories": {k: v["dir"] for k, v in LOCALES.items()},
        "translation": {"sourceLocale": "en", "addedLocales": list(NEW_LOCALES),
                        "method": "Machine translation with terminology and structural checks",
                        "provider": "Google Translate", "nativeSpeakerReviewed": False,
                        "websiteLinks": "New locales retain existing English website destinations",
                        "originalImageText": "Preserved"},
    })
    write_json(manifest_path, manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inventory", "translate", "build"))
    parser.add_argument("--locales", nargs="+", choices=NEW_LOCALES, default=list(NEW_LOCALES))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.command == "inventory":
        strings = source_strings()
        print(json.dumps({"sourceFiles": len(source_documents()), "uniqueStrings": len(strings),
                          "sourceCharacters": sum(map(len, strings)),
                          "catalogs": {k: len(read_catalog(k)) for k in NEW_LOCALES}}, indent=2))
    elif args.command == "translate":
        translate_all(args.locales, args.workers)
    else:
        build(args.locales)


if __name__ == "__main__":
    main()
