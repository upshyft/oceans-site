#!/usr/bin/env python3
"""Check that each HTML file is served at its clean URL, .html URL, and slash URL.

Uses the local preview server, which maps those paths the way Render serves
a static .html file. Does not request production or submit a form.
"""
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preview import Handler

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "index.html": "/",
    "contact.html": "/contact",
    "valuation.html": "/valuation",
    "investor.html": "/investor",
    "loan-signing.html": "/loan-signing",
    "rate.html": "/rate",
    "next-home.html": "/next-home",
    "move-plan.html": "/move-plan",
    "investment-plan.html": "/investment-plan",
    "how-we-sell.html": "/how-we-sell",
    "seller-prep.html": "/seller-prep",
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(opener, url):
    request = Request(url)
    try:
        with opener.open(request, timeout=10) as response:
            return response.status, response.read(), response.headers.get("Content-Type")
    except HTTPError as error:
        return error.code, error.read(), error.headers.get("Content-Type")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    opener = build_opener(NoRedirect)
    errors = []
    try:
        for name, path in PAGES.items():
            source = (ROOT / name).read_bytes()
            variants = [path, "/" + name]
            if path != "/":
                variants.append(path + "/")
            for variant in variants:
                status, body, content_type = fetch(opener, f"http://127.0.0.1:{port}{variant}")
                if status != 200:
                    errors.append(f"{variant} returned {status}")
                elif body != source:
                    errors.append(f"{variant} body differs from {name}")
                elif not content_type or "text/html" not in content_type:
                    errors.append(f"{variant} content type is {content_type}")
        status, _, _ = fetch(opener, f"http://127.0.0.1:{port}/does-not-exist")
        if status != 404:
            errors.append(f"/does-not-exist returned {status}")
    finally:
        server.shutdown()
    if errors:
        print("FAILED")
        for error in errors:
            print("-", error)
        return 1
    print(f"OK clean urls for {len(PAGES)} html sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
