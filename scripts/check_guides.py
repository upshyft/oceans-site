#!/usr/bin/env python3
"""Checks for the situation guides and the no-JavaScript market figures.

Does not request production or submit a form.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def fail(msg):
    errors.append(msg)


def read(name):
    return (ROOT / name).read_text()


def format_stat(open_tag):
    def attr(name):
        found = re.search(rf'{name}="([^"]*)"', open_tag)
        return found.group(1) if found else ""

    target = float(attr("data-target") or 0)
    prefix = attr("data-prefix")
    suffix = attr("data-suffix")
    decimals = int(attr("data-decimals") or 0)
    if 'data-format="compact"' in open_tag:
        return f"{prefix}{target / 1000000:.1f}M{suffix}"
    return f"{prefix}{target:.{decimals}f}{suffix}"


index = read("index.html")
stats = re.findall(r'(<b class="stat-count"[^>]*>)([^<]*)(</b>)', index)
if len(stats) < 21:
    fail(f"expected community and summary counters, found {len(stats)}")
for open_tag, text, _close in stats:
    expected = format_stat(open_tag)
    if text != expected:
        fail(f"counter shows {text!r}, published value is {expected!r}")
    if text in {"0", "$0", "$0M", "0%"}:
        fail(f"counter still renders a zero placeholder: {text}")
if "stat-fallback" not in index or "$1.3M" not in index:
    fail("homepage is missing the no-JavaScript market-figure fallback")
for href in ("/next-home", "/move-plan", "/investment-plan", "/how-we-sell", "/seller-prep"):
    if f'href="{href}"' not in index:
        fail(f"homepage does not link to {href}")
if 'href="/first-home"' in index or "My first coastal home" in index:
    fail("homepage still promotes the first-home path")

how = read("how-we-sell.html")
for phrase in ("Illustrative sample", "not a current listing", "not a client", "not a sale result"):
    if phrase not in how:
        fail(f"how-we-sell.html missing sample label: {phrase}")
for banned in ("testimonial", "guaranteed sale", "sold in", "days on market was"):
    if banned.lower() in how.lower():
        fail(f"how-we-sell.html includes unsupported claim language: {banned}")

move = read("move-plan.html")
if "does not guarantee" not in move or "does not provide lending, legal, or tax advice" not in move:
    fail("move-plan.html missing the disclaimer")
if "Help me compare my options" not in move:
    fail("move-plan.html missing the comparison call to action")
for ident in ("path-buy", "path-sell", "path-both", "buy-first", "sell-first", "coordinated"):
    if ident not in move:
        fail(f"move-plan.html missing {ident}")

prep = read("seller-prep.html")
if "Content reviewed" not in prep or "November 6, 2026" not in prep:
    fail("seller-prep.html missing the review date")
if "are not sent to Oceans" not in prep:
    fail("seller-prep.html does not say ticks stay on the device")
if "<form" in prep.lower():
    fail("seller-prep.html must not wrap the checklist in a form")
if "localStorage" not in prep:
    fail("seller-prep.html does not keep ticks locally")
prep_script = prep.split('var KEY = "oceans-seller-prep-v1"', 1)[-1]
if "fetch(" in prep_script or "XMLHttpRequest" in prep_script or "sendBeacon" in prep_script:
    fail("seller prep script must not transmit checklist data")
boxes = re.findall(r'data-prep="([^"]+)"', prep)
if len(boxes) < 12:
    fail(f"seller prep board is missing items ({len(boxes)})")
if "Ask before spending" not in prep:
    fail("seller prep board is missing ask-before-spending decisions")

contact = read("contact.html")
valuation = read("valuation.html")
investor = read("investor.html")
for page_name, page, key in (
    ("next-home.html", contact, "next-home"),
    ("move-plan.html", contact, "move-compare"),
    ("investment-plan.html", investor, "investment"),
    ("how-we-sell.html", valuation, "sell-launch"),
    ("seller-prep.html", valuation, "seller-prep"),
):
    guide = read(page_name)
    if f"starter={key}" not in guide:
        fail(f"{page_name} does not link to starter={key}")
    quoted = re.search(r"<blockquote class=\"starter\"><b>Conversation starter</b>(.*?)</blockquote>", guide, re.S)
    if not quoted:
        fail(f"{page_name} missing conversation starter")
        continue
    if quoted.group(1) not in page:
        fail(f"{key} starter is not the prefilled text on the existing form page")

buyer = read("next-home.html").lower()
for banned in ("first home", "first-time", "first time", "my first coastal"):
    if banned in buyer:
        fail(f"next-home.html still uses first-time framing: {banned}")
for phrase in ("How it works", "Decisions to make", 'href="/contact?starter=next-home"'):
    if phrase.lower() not in buyer and phrase not in read("next-home.html"):
        fail(f"next-home.html missing {phrase}")

redirect = read("first-home.html")
for needle in (
    'http-equiv="refresh" content="0; url=/next-home"',
    'href="/next-home"',
    'rel="canonical" href="https://www.theoceans.com/next-home"',
    'content="noindex"',
):
    if needle not in redirect:
        fail(f"first-home redirect missing {needle}")
if "My first coastal home" in redirect or "first-home plan" in redirect.lower():
    fail("first-home.html still contains the old guide")
if re.search(r"(?m)^\s*routes\s*:", (ROOT / "render.yaml").read_text()):
    fail("render.yaml must not add a routes block for this redirect")

if errors:
    print("FAILED")
    for err in errors:
        print("-", err)
    sys.exit(1)
print(f"OK guides counters={len(stats)} prep_items={len(boxes)}")
