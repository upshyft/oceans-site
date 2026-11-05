#!/usr/bin/env python3
"""Local preview of Render's clean URLs.

Each page is one .html file. /contact, /contact.html, and /contact/ all
serve that file with status 200. This server does not deploy or submit forms.

Usage: python3 scripts/preview.py [port]
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        translated = super().translate_path(path)
        if translated.endswith(("/", os.sep)):
            stripped = translated.rstrip("/\\")
            if os.path.isdir(stripped):
                return translated
            html = stripped + ".html"
            if os.path.isfile(html):
                return html
            return translated
        if os.path.exists(translated):
            return translated
        html = translated + ".html"
        if os.path.isfile(html):
            return html
        return translated


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Preview at http://127.0.0.1:{port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
