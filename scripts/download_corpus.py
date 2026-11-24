"""Recreate data/raw from data/corpus.csv. Usage: python scripts/download_corpus.py"""
import csv
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]
raw = ROOT / "data" / "raw"
raw.mkdir(parents=True, exist_ok=True)
with open(ROOT / "data" / "corpus.csv", newline="") as f:
    for row in csv.DictReader(f):
        if not row.get("url") or not row.get("filename"):
            continue
        dest = raw / row["filename"]
        if dest.exists():
            print("skip", dest.name)
            continue
        print("get ", row["url"])
        r = httpx.get(row["url"], follow_redirects=True, timeout=120,
                      headers={"User-Agent": "docagent-corpus-fetch"})
        r.raise_for_status()
        dest.write_bytes(r.content)
