#!/usr/bin/env python3
"""Offline validation of the complete ten-language public Guide edition."""
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

from localize import (ROOT, LOCALES, NEW_LOCALES, NAV_START, NAV_END, NOTES,
                      source_strings, polished_catalog, strip_navigation)

ERRORS = []
COUNTS = Counter()
MD_DEST = re.compile(r'\]\(((?:[^()\n]|\([^()\n]*\))*)\)')
HTML_URL = re.compile(r'\b(?:href|src)=["\']([^"\']+)["\']')
ANCHORS = re.compile(r'<a\s+id=["\']([^"\']+)["\']')
FENCES = re.compile(r'^```(.*)$', re.MULTILINE)
CODE_BLOCKS = re.compile(r'^```text\n(.*?)\n```', re.MULTILINE | re.DOTALL)
HTML_TAGS = re.compile(r'<[^>]+>')


def check(condition, message):
    COUNTS["assertions"] += 1
    if not condition:
        ERRORS.append(message)


def clean_body(text, locale):
    body = strip_navigation(text).strip()
    if locale == "ar":
        check(body.startswith('<div dir="rtl" lang="ar">') and body.endswith("</div>"),
              "Arabic document lacks RTL wrapper")
        body = body.removeprefix('<div dir="rtl" lang="ar">').removesuffix("</div>").strip()
    if locale in NOTES:
        body = body.replace("> " + NOTES[locale] + "\n", "")
    return body


def destinations(text):
    return [html.unescape(m[1]) for m in MD_DEST.finditer(text)] + [
        html.unescape(m[1]) for m in HTML_URL.finditer(text)]


def image_urls(text):
    # Every picture in this edition is remote; links to external actions are not.
    return re.findall(r'https://[^\s<>"\')]+?\.(?:png|webp|jpe?g|svg)(?:\?[^\s<>"\')]*)?', text)


def heading_ids(text):
    """GitHub-style heading slugs, including Unicode and duplicate suffixes."""
    identifiers, seen = set(), Counter()
    inside_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            inside_fence = not inside_fence
        if inside_fence or not re.match(r"^#{1,6}\s", line):
            continue
        heading = re.sub(r"^#{1,6}\s+", "", line).strip().lower()
        heading = re.sub(r"!?(?:\[([^]]+)\])\([^)]*\)", r"\1", heading)
        heading = html.unescape(re.sub(r"<[^>]*>|[`*_~]", "", heading))
        slug = "".join(c for c in heading if c in "-_ " or unicodedata.category(c)[0] in "LMN")
        slug = slug.replace(" ", "-")
        count = seen[slug]
        seen[slug] += 1
        identifiers.add(slug + (f"-{count}" if count else ""))
    return identifiers


def tag_skeleton(text):
    # Alt/title are translated, while every other structural attribute is fixed.
    return [re.sub(r'\b(?:alt|title)="[^"]*"', 'alt="TEXT"', tag)
            for tag in HTML_TAGS.findall(text)]


def validate_links(path, text):
    for dest in destinations(text):
        COUNTS["links"] += 1
        if urlsplit(dest).scheme:
            check(urlsplit(dest).scheme in ("https", "mailto"), f"Unsafe URL in {path}: {dest}")
            continue
        parts = urlsplit(unquote(dest))
        target = ((ROOT / path).parent / parts.path).resolve() if parts.path else ROOT / path
        check(target.is_relative_to(ROOT), f"Link escapes repository: {path}: {dest}")
        check(target.is_file(), f"Missing link target: {path}: {dest}")
        if target.is_file() and parts.fragment and target.suffix == ".md":
            content = target.read_text()
            ids = set(ANCHORS.findall(content)) | heading_ids(content)
            check(parts.fragment in ids, f"Missing anchor: {path}: {dest}")


def validate_navigation(path, locale, article=None):
    text = (ROOT / path).read_text()
    check(text.count(NAV_START) == text.count(NAV_END) == 1, f"Missing/duplicate language nav: {path}")
    nav = text.split(NAV_START)[-1].split(NAV_END)[0]
    for code, data in LOCALES.items():
        check(data["name"] in nav, f"Missing {code} label in {path}")
        if code == locale:
            check(f'**{data["name"]}**' in nav, f"Active language missing: {path}")
        else:
            target = (ROOT / (Path(data["dir"]) / article if article else Path(data["readme"]))).resolve()
            links = [(ROOT / path).parent / urlsplit(d).path for d in destinations(nav)]
            check(any(p.resolve() == target for p in links), f"Wrong {code} counterpart: {path}")
    validate_links(path, text)
    check(not re.search(r"ZXQ\d+XQZ|\[\d{6}\]", text), f"Unresolved translation marker: {path}")
    check(len(FENCES.findall(text)) % 2 == 0, f"Unbalanced code fence: {path}")
    for alt in re.findall(r'\balt="([^"]*)"', text):
        check(bool(alt.strip()), f"Empty image alt: {path}")
    return clean_body(text, locale)


def validate_equivalence(article, locale):
    source = clean_body((ROOT / "en" / article).read_text(), "en")
    path = Path(LOCALES[locale]["dir"]) / article
    target = validate_navigation(path, locale, article)
    check(ANCHORS.findall(source) == ANCHORS.findall(target), f"Anchor IDs/order changed: {path}")
    check(Counter(image_urls(source)) == Counter(image_urls(target)), f"Image URLs changed: {path}")
    check(FENCES.findall(source) == FENCES.findall(target), f"Code fence types changed: {path}")
    check(re.findall(r"^#{1,6} ", source, re.M) == re.findall(r"^#{1,6} ", target, re.M),
          f"Heading levels/order changed: {path}")
    check(tag_skeleton(source) == tag_skeleton(target), f"HTML structure changed: {path}")
    expected = [d.replace("utm_content=en_", f"utm_content={locale}_") for d in destinations(source)]
    check(expected == destinations(target), f"Article link destinations/order changed: {path}")
    # Each code paragraph is a separate instruction. Counts detect truncated
    # translations even when both code fences survive.
    source_blocks, target_blocks = CODE_BLOCKS.findall(source), CODE_BLOCKS.findall(target)
    check(len(source_blocks) == len(target_blocks), f"Prompt block count changed: {path}")
    for i, (a, b) in enumerate(zip(source_blocks, target_blocks)):
        check(len(a.split("\n\n")) == len(b.split("\n\n")), f"Instruction paragraphs lost: {path} #{i}")
        check(len(a.splitlines()) == len(b.splitlines()), f"Instruction lines lost: {path} #{i}")
    COUNTS["documents"] += 1
    COUNTS["codeBlocks"] += len(target_blocks)
    COUNTS["images"] += len(image_urls(target))


def validate_manifest():
    manifest = json.loads((ROOT / "data/manifest.json").read_text())
    check(manifest["languages"] == list(LOCALES), "Manifest language list mismatch")
    check(manifest["guidePages"] == len(manifest["pages"]) == 1650, "Expected 1,650 exported articles")
    check(manifest["totalGuideDocuments"] == len(manifest["documents"]) == 1670, "Expected 1,670 guide documents")
    check(len(manifest["readmes"]) == 10, "Expected ten root READMEs")
    check(manifest["visualForms"] == 1388 and manifest["visualGroups"] == 128, "Catalog scope changed")
    check(manifest["publicDirectionsPerLanguage"] == 123, "Public direction count changed")
    for record in manifest["pages"] + manifest["documents"] + manifest["readmes"]:
        path = ROOT / record["path"]
        check(path.is_file(), f"Missing manifest file: {record['path']}")
        if path.is_file():
            check(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                  f"Stale manifest hash: {record['path']}")
    for locale, data in LOCALES.items():
        listed = {p["path"] for p in manifest["documents"] if p["locale"] == locale}
        actual = {str(p.relative_to(ROOT)) for p in (ROOT / data["dir"]).rglob("*.md")}
        check(listed == actual, f"Manifest tree mismatch: {locale}")
        articles = [p for p in manifest["pages"] if p["locale"] == locale]
        check(len(articles) == 165, f"Manifest article count mismatch: {locale}")
        if locale in NEW_LOCALES:
            check(all(p.get("webLocale") == "en" for p in articles), f"Incorrect website locale: {locale}")
            check(all(p["webUrl"].startswith("https://podplo.app/pod-guide") for p in articles),
                  f"Invented localized website routes: {locale}")
    return manifest


def main():
    source_tree = {p.relative_to(ROOT / "en") for p in (ROOT / "en").rglob("*.md")}
    check(len(source_tree) == 167, "Expected 167 English source documents")
    required = set(source_strings())
    for locale in NEW_LOCALES:
        catalog = polished_catalog(locale)
        check(required <= catalog.keys(), f"Missing catalog strings: {locale}")
        for source in required:
            value = catalog.get(source, "")
            check(bool(value.strip()), f"Empty translation: {locale}: {source[:60]}")
            check(not re.search(r"ZXQ\d+XQZ|\[\d{6}\]", value), f"Marker in catalog: {locale}")
            if len(source) > 80:
                check(source != value, f"Untranslated paragraph: {locale}: {source[:60]}")
        tree = {p.relative_to(ROOT / LOCALES[locale]["dir"]) for p in (ROOT / LOCALES[locale]["dir"]).rglob("*.md")}
        check(tree == source_tree, f"Incomplete document tree: {locale}")
        if tree == source_tree:
            for article in sorted(source_tree):
                validate_equivalence(article, locale)
        body = validate_navigation(Path(LOCALES[locale]["readme"]), locale)
        en_body = clean_body((ROOT / "README.md").read_text(), "en")
        check(ANCHORS.findall(en_body) == ANCHORS.findall(body), f"README anchors changed: {locale}")
        check(Counter(image_urls(en_body)) == Counter(image_urls(body)), f"README images changed: {locale}")
        check(FENCES.findall(en_body) == FENCES.findall(body), f"README fences changed: {locale}")
        for d in destinations(body):
            if not urlsplit(d).scheme:
                check(not d.startswith(("en/", "zh/")), f"README cross-language leak: {locale}: {d}")
    # Existing languages also receive the complete counterpart navigation.
    for locale in ("en", "zh-CN"):
        directory = ROOT / LOCALES[locale]["dir"]
        for path in sorted(directory.rglob("*.md")):
            article = path.relative_to(directory)
            validate_navigation(path.relative_to(ROOT), locale, article)
            COUNTS["documents"] += 1
        validate_navigation(Path(LOCALES[locale]["readme"]), locale)
    for locale, data in LOCALES.items():
        blocks = CODE_BLOCKS.findall((ROOT / data["dir"] / "ai-directions.md").read_text())
        check(len(blocks) == 123, f"Expected 123 copyable public directions: {locale}")
    manifest = validate_manifest()
    print(json.dumps({"status": "PASS" if not ERRORS else "FAIL", "languages": manifest["languages"],
                      "counts": dict(COUNTS), "errorCount": len(ERRORS), "errors": ERRORS[:80]},
                     ensure_ascii=False, indent=2))
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
