#!/usr/bin/env python3
"""Local preview that mirrors the live extensionless URLs.

Render already serves /contact from contact.html. This server does the same
so nav links can be clicked locally. It does not deploy or submit forms.

Usage: python3 scripts/preview.py [port]
"""
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path != "/" and path.endswith("/"):
            target = path.rstrip("/") or "/"
            if parsed.query:
                target += "?" + parsed.query
            self.send_response(301)
            self.send_header("Location", target)
            self.end_headers()
            return
        super().do_GET()

    def translate_path(self, path):
        translated = super().translate_path(path)
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
