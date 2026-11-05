#!/usr/bin/env python3
"""Check search-visibility basics without sending leads or hitting production.

Run from the repo root: python3 scripts/check_seo.py
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = "https://www.theoceans.com"
PAGES = {
    "index.html": "/",
    "contact.html": "/contact",
    "valuation.html": "/valuation",
    "investor.html": "/investor",
    "loan-signing.html": "/loan-signing",
    "rate.html": "/rate",
}
FORBIDDEN_TYPES = {"VacationRental", "LodgingBusiness", "Review", "AggregateRating"}
FORM_ENDPOINT = "https://formsubmit.app/f/q8vhg24vbb"
errors = []


def fail(msg):
    errors.append(msg)


def load(name):
    return (ROOT / name).read_text()


titles = {}
descriptions = {}
canonicals = {}

for name, path in PAGES.items():
    html = load(name)
    title = re.search(r"<title>(.*?)</title>", html)
    desc = re.search(r'<meta name="description" content="(.*?)">', html)
    canon = re.search(r'<link rel="canonical" href="(.*?)">', html)
    if not title or not title.group(1).strip():
        fail(f"{name} missing title")
    else:
        titles[name] = title.group(1)
    if not desc or not desc.group(1).strip():
        fail(f"{name} missing description")
    else:
        descriptions[name] = desc.group(1)
        if not 50 <= len(desc.group(1)) <= 180:
            fail(f"{name} description length {len(desc.group(1))}")
    expected = HOST + path
    if not canon or canon.group(1) != expected:
        fail(f"{name} canonical {canon.group(1) if canon else None} != {expected}")
    else:
        canonicals[name] = canon.group(1)
    if "theoceans.com/rate" in html and "www.theoceans.com/rate" not in html and name == "rate.html":
        fail("rate page still canonicalizes to the apex host")
    if html.count('id="main"') != 1:
        fail(f"{name} has {html.count('id=\"main\"')} #main ids")
    if "data:image/png;base64" in html or "data:image/jpeg;base64" in html:
        fail(f"{name} still inlines a photo or logo")
    if FORM_ENDPOINT not in html:
        fail(f"{name} lost the FormSubmit endpoint")
    blocks = re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S
    )
    if len(blocks) != 1:
        fail(f"{name} expected 1 JSON-LD block, found {len(blocks)}")
        continue
    try:
        data = json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        fail(f"{name} invalid JSON-LD: {exc}")
        continue
    types = []

    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            if isinstance(t, str):
                types.append(t)
            elif isinstance(t, list):
                types.extend(t)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)
    banned = FORBIDDEN_TYPES.intersection(types)
    if banned:
        fail(f"{name} schema uses {sorted(banned)}")
    if "RealEstateAgent" not in types or "WebPage" not in types:
        fail(f"{name} schema missing RealEstateAgent or WebPage")
    blob = json.dumps(data)
    for needle in ("02167533", "02087436", "info@theoceans.com", "Keston Abe", "Tracey Takeshita"):
        if needle not in blob:
            fail(f"{name} schema missing verified fact {needle}")

if len(set(titles.values())) != len(titles):
    fail(f"duplicate titles: {titles}")
if len(set(descriptions.values())) != len(descriptions):
    fail(f"duplicate descriptions: {descriptions}")

index = load("index.html")
for needle in (
    "https://www.redfin.com/neighborhood/547182/CA/Rancho-Palos-Verdes/South-Bay/housing-market",
    "updated November 2026",
    'data-target="3285935"',
    'data-target="1.3"',
    'data-lead-form="contact"' if False else "FORM_SUBJECTS",
):
    if needle not in index:
        fail(f"index lost {needle}")
for form_name in ("contact", "valuation", "investor", "loan-signing", "rate"):
    page = "index.html" if form_name == "contact" else f"{form_name}.html"
    # contact/valuation/investor/loan-signing/rate pages own the forms; index only has the shared script.
    pass
for name, attr in (
    ("contact.html", 'data-lead-form="contact"'),
    ("valuation.html", 'data-lead-form="valuation"'),
    ("investor.html", 'data-lead-form="investor"'),
    ("loan-signing.html", 'data-lead-form="loan-signing"'),
    ("rate.html", 'data-lead-form="rate"'),
):
    if attr not in load(name):
        fail(f"{name} lost {attr}")

robots = (ROOT / "robots.txt").read_text()
if "Sitemap: https://www.theoceans.com/sitemap.xml" not in robots:
    fail("robots.txt missing sitemap")
if "Disallow: /" in robots:
    fail("robots.txt disallows the site")

ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [el.text for el in ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", ns)]
expected_locs = [HOST + path for path in PAGES.values()]
if locs != expected_locs:
    fail(f"sitemap locs {locs} != {expected_locs}")

# Internal links should resolve to a page, hash, or existing file.
link_re = re.compile(r'href="([^"]+)"')
known = set(PAGES.values()) | {"/", "/#areas", "/#about"}
for name in PAGES:
    for href in link_re.findall(load(name)):
        if href.startswith(("mailto:", "tel:", "http://", "https://", "#")):
            continue
        path = href.split("#", 1)[0] or "/"
        if path in known or path in PAGES.values():
            continue
        candidate = ROOT / path.lstrip("/")
        if candidate.is_file() or (ROOT / (path.lstrip("/") + ".html")).is_file():
            continue
        fail(f"{name} broken internal link {href}")

for name, path in PAGES.items():
    if path == "/":
        continue
    twin = ROOT / path.lstrip("/")
    if not twin.is_file():
        fail(f"missing extensionless copy for {path}")
    elif twin.read_text() != load(name):
        fail(f"{twin.name} is out of date with {name}")

for rel in (
    "images/brand-logo.png",
    "images/keston-abe.jpg",
    "images/tracey-takeshita.jpg",
    "images/hero-manhattan-pier-mobile.jpg",
    "images/hero-manhattan-pier-desktop.jpg",
    "images/hero-beach-golden-hour.jpg",
    "robots.txt",
    "sitemap.xml",
):
    if not (ROOT / rel).is_file():
        fail(f"missing {rel}")

mobile = (ROOT / "images/hero-manhattan-pier-mobile.jpg").stat().st_size
if mobile >= 834041:
    fail(f"mobile hero was not reduced ({mobile})")

if errors:
    print("FAILED")
    for err in errors:
        print("-", err)
    sys.exit(1)
print("OK")
print(f"pages={len(PAGES)} unique_titles={len(set(titles.values()))} mobile_hero_bytes={mobile}")
for name, title in titles.items():
    print(f"  {name}: {title} | {len(descriptions[name])} chars | {canonicals[name]}")
