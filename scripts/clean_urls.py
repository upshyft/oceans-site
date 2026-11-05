"""Map editable HTML pages to the extensionless files Render is serving.

Edit the .html files only. scripts/generate_clean_urls.py rewrites the
extensionless copies. Those copies stay in git because the live service
publishes the repository root and still has redirect rules that would loop
if the copies disappeared.
"""
from pathlib import Path

# Editable source -> generated path relative to the repo root.
SOURCES = {
    "contact.html": "contact",
    "valuation.html": "valuation",
    "investor.html": "investor",
    "loan-signing.html": "loan-signing",
    "rate.html": "rate",
}


def drift_errors(root: Path):
    errors = []
    for source_name, generated_name in SOURCES.items():
        source = root / source_name
        generated = root / generated_name
        if not source.is_file():
            errors.append(f"missing editable source {source_name}")
            continue
        if not generated.is_file():
            errors.append(
                f"missing generated {generated_name}; run python3 scripts/generate_clean_urls.py"
            )
            continue
        if generated.read_bytes() != source.read_bytes():
            errors.append(
                f"{generated_name} drifted from {source_name}; run python3 scripts/generate_clean_urls.py"
            )
    return errors


def generate(root: Path):
    written = []
    for source_name, generated_name in SOURCES.items():
        source = root / source_name
        data = source.read_bytes()
        target = root / generated_name
        if not target.is_file() or target.read_bytes() != data:
            target.write_bytes(data)
            written.append(generated_name)
    return written
