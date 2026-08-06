"""Fetch and cache a curated set of Handbook pages as markdown for QAEngine.

Run manually (not part of the live demo) to (re)generate the `handbook-*.md`
files under src/furhat_demos/opendemo/data/. Requires network access to
handbook.unimelb.edu.au. The live demo never calls the Handbook site itself —
it only reads the cached output of this script.

Usage: python scripts/ingest_handbook.py
"""

from __future__ import annotations

import re
from pathlib import Path

from furhat_demos.opendemo.handbook import RequestsHttpClient, fetch_detail_text

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "src" / "furhat_demos" / "opendemo" / "data"

# A small, representative set of CIS courses/subjects for the first pass.
# Expand this list to broaden coverage in a follow-up.
PAGES = [
    "https://handbook.unimelb.edu.au/courses/d-comp",
    "https://handbook.unimelb.edu.au/subjects/comp10001",
    "https://handbook.unimelb.edu.au/subjects/comp20003",
]


def _slugify(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", url.rsplit("/", 1)[-1].lower()).strip("-")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = RequestsHttpClient()
    for url in PAGES:
        text = fetch_detail_text(client, url)
        if not text:
            print(f"WARNING: no content extracted from {url}")
            continue
        out_path = OUTPUT_DIR / f"handbook-{_slugify(url)}.md"
        out_path.write_text(f"<!-- Source: {url} -->\n\n{text}\n")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
