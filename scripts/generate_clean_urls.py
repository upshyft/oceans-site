#!/usr/bin/env python3
"""Regenerate extensionless pages from the .html sources.

The .html files are the only editable page sources. The extensionless files
are committed generated copies so the current Render publish (repository
root, no build command) keeps serving /contact and the other canonical
paths while stale redirect rules remain.

  python3 scripts/generate_clean_urls.py
  python3 scripts/generate_clean_urls.py --check
  python3 scripts/generate_clean_urls.py --self-test
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clean_urls import SOURCES, drift_errors, generate

ROOT = Path(__file__).resolve().parents[1]


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sample = b"<!doctype html><title>Contact</title>\n"
        (root / "contact.html").write_bytes(sample)
        # Only the contact pair is exercised; point the other sources at it
        # by writing every source the generator knows about.
        for source_name in SOURCES:
            (root / source_name).write_bytes(sample + source_name.encode())
        written = generate(root)
        if set(written) != set(SOURCES.values()):
            raise SystemExit(f"self-test did not write every copy: {written}")
        if drift_errors(root):
            raise SystemExit(f"self-test found drift after generate: {drift_errors(root)}")
        generated = root / "contact"
        generated.write_bytes(b"edited by hand")
        errors = drift_errors(root)
        if not any("contact drifted" in error for error in errors):
            raise SystemExit(f"self-test did not catch an edited copy: {errors}")
        generate(root)
        if drift_errors(root):
            raise SystemExit("self-test still drifting after regenerate")
        if generated.read_bytes() != (root / "contact.html").read_bytes():
            raise SystemExit("self-test regenerate was not byte-for-byte")
    print("self-test OK")


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    if "--check" in argv:
        errors = drift_errors(ROOT)
        if errors:
            print("FAILED")
            for error in errors:
                print("-", error)
            return 1
        print(f"OK generated copies match {len(SOURCES)} html sources")
        return 0
    written = generate(ROOT)
    if written:
        print("updated", ", ".join(written))
    else:
        print("already in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
