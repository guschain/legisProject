#!/usr/bin/env python3
"""
Download the JSON datasets published on the Portuguese Parliament “Dados Abertos”
portal, convert each to CSV and save (or update) in the repo’s `data/` folder.
A file is only rewritten when its content changes.
"""

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

THEME_URLS = [
    "https://www.parlamento.pt/Cidadania/Paginas/DAIniciativas.aspx",
    "https://www.parlamento.pt/Cidadania/Paginas/DAatividades.aspx",
    "https://www.parlamento.pt/Cidadania/Paginas/DAInformacaoBase.aspx",
]

DATA_DIR = Path("data")          # <repo-root>/data
DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def safe_filename(s: str) -> str:
    """Turn the link’s title string into a safe filename."""
    # keep letters, numbers, dash & underscore; replace others with _
    return re.sub(r"[^\w\-]", "_", s).strip("_")


def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def fetch_text(url: str) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def fetch_json(url: str):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# scraping logic
# ---------------------------------------------------------------------------

def get_legislature_page_links(theme_html: str, base_url: str) -> list[str]:
    """Return the URLs for each legislature page underneath a top-level theme."""
    soup = BeautifulSoup(theme_html, "html.parser")
    links = []
    for div in soup.find_all("div", class_="archive-item"):
        a = div.find("a", href=True)
        if a:
            links.append(urljoin(base_url, a["href"]))
    return links


def get_json_link_from_legislature_page(page_html: str, base_url: str) -> tuple[str, str] | None:
    """
    Return (url, title) for the JSON file advertised on a legislature page.
    Returns None if not found (shouldn’t happen but keeps things safe).
    """
    soup = BeautifulSoup(page_html, "html.parser")
    a = soup.select_one('div.archive-item a[title*="json"][href]')
    if not a:
        return None
    return urljoin(base_url, a["href"]), a["title"]


def download_and_write_if_changed(json_url: str, title: str) -> bool:
    """
    Download JSON, convert to CSV and write to data/<title>.csv.
    Returns True if FILE CONTENT changed (written or updated), False otherwise.
    """
    # 1) Fetch and normalise JSON → DataFrame
    df = pd.json_normalize(fetch_json(json_url))
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    # 2) Determine output path & compare hash
    filename = safe_filename(title) + ".csv"
    out_path = DATA_DIR / filename
    new_hash = sha256_bytes(csv_bytes)

    if out_path.exists():
        with out_path.open("rb") as f:
            old_hash = sha256_bytes(f.read())
        if new_hash == old_hash:
            print(f"✓ {filename}: unchanged")
            return False  # no change

    # 3) Write/overwrite
    with out_path.open("wb") as f:
        f.write(csv_bytes)
    print(f"↻ {filename}: written ({len(csv_bytes):,} bytes)")
    return True


def run_for_theme(theme_url: str) -> int:
    """Process one of the three main theme pages. Returns #files that changed."""
    print(f"\n=== {theme_url} ===")
    theme_html = fetch_text(theme_url)
    base_url = f"{urlparse(theme_url).scheme}://{urlparse(theme_url).netloc}"

    changed = 0
    for leg_url in get_legislature_page_links(theme_html, base_url):
        leg_html = fetch_text(leg_url)
        result = get_json_link_from_legislature_page(leg_html, base_url)
        if result:
            json_url, title = result
            if download_and_write_if_changed(json_url, title):
                changed += 1
    return changed


def main():
    total_changes = sum(run_for_theme(url) for url in THEME_URLS)
    print(f"\nDone – {total_changes} file(s) updated.")
    # exit code 0 regardless; git diff decide commit


if __name__ == "__main__":
    main()
