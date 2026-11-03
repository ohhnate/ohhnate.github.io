"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver, Yep) that the site's pages changed.

Usage: python tools/indexnow.py   (after the changes are deployed)

Submits every URL in sitemap.xml. The engines confirm ownership by fetching the key file
at the site root (a 32-character hex name ending in .txt, containing the same key), so
that file must stay in the repo and be live before submitting.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "ohhnate.dev"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_FILE = re.compile(r"^[0-9a-f]{32}\.txt$")
RESPONSES = {
    200: "submitted",
    202: "accepted; the key is still being validated",
    400: "bad request",
    403: "key not valid (is the key file live?)",
    422: "URLs don't belong to the host or don't match the key",
    429: "too many requests; try again later",
}


def find_key() -> str:
    keys = [p for p in ROOT.iterdir() if KEY_FILE.match(p.name)]
    if len(keys) != 1:
        sys.exit(f"Expected exactly one IndexNow key file at the repo root, found {len(keys)}")
    return keys[0].stem


def main() -> None:
    key = find_key()
    urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}).encode()
    request = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code
    print(f"IndexNow: HTTP {status} ({RESPONSES.get(status, 'unexpected response')}) for {len(urls)} URLs")
    if status not in (200, 202):
        sys.exit(1)


if __name__ == "__main__":
    main()
