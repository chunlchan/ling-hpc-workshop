#!/usr/bin/env python3

"""
Download a reproducible sample of English Project Gutenberg books.

Example:

    python fetch_gutenberg.py --count 50 --seed 42 --output gutenberg_books

Steps:
  1. Download Gutenberg's catalog (pg_catalog.csv) and keep English text entries.
  2. Shuffle them with a fixed seed.
  3. Download books in that order, skipping any shorter than --min-words,
     until --count books have been kept.
  4. Write the kept IDs and titles to book_ids.txt so the corpus can be
     rebuilt exactly (python fetch_gutenberg.py --ids book_ids.txt).

Please keep --delay at 1 second or more. See
https://www.gutenberg.org/policy/robot_access.html
"""

import argparse
import csv
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

CATALOG_URL = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
BOOK_URL = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
USER_AGENT = "ling-hpc-workshop/1.0 (educational; small sample download)"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def load_catalog(cache_path):
    """Return {id: title} for English text entries."""
    if not cache_path.exists():
        print(f"Downloading catalog to {cache_path}")
        cache_path.write_bytes(fetch(CATALOG_URL))

    books = {}
    with open(cache_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["Type"] == "Text" and row["Language"] == "en":
                title = " ".join(row["Title"].split())
                books[int(row["Text#"])] = (title, row["Authors"])
    return books


def read_ids_file(path):
    ids = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*(\d+)", line)
        if match:
            ids.append(int(match.group(1)))
    return ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="gutenberg_books",
                        help="Directory for downloaded .txt files")
    parser.add_argument("--count", type=int, default=50,
                        help="Number of books to keep")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for the sample")
    parser.add_argument("--min-words", type=int, default=50000,
                        help="Discard books shorter than this")
    parser.add_argument("--max-words", type=int, default=500000,
                        help="Discard books longer than this (dictionaries, "
                        "collected speeches, etc.)")
    parser.add_argument("--exclude", type=int, nargs="*", default=[],
                        help="Gutenberg IDs to skip")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Seconds to wait between downloads")
    parser.add_argument("--ids", help="Rebuild from an existing book_ids.txt "
                        "instead of sampling")
    parser.add_argument("--id-list-out", default="book_ids.txt",
                        help="Where to write the kept IDs")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    catalog = load_catalog(output_dir / "pg_catalog.csv")
    print(f"Catalog: {len(catalog):,} English text entries")

    if args.ids:
        candidates = read_ids_file(args.ids)
    else:
        candidates = sorted(catalog)
        random.Random(args.seed).shuffle(candidates)

    kept = []

    for book_id in candidates:
        if len(kept) >= args.count and not args.ids:
            break

        if book_id in args.exclude:
            continue

        title, authors = catalog.get(book_id, ("(unknown)", ""))
        path = output_dir / f"pg{book_id}.txt"

        if not path.exists():
            try:
                data = fetch(BOOK_URL.format(id=book_id))
            except urllib.error.URLError as error:
                print(f"  skip {book_id}: {error}")
                time.sleep(args.delay)
                continue
            path.write_bytes(data)
            time.sleep(args.delay)

        words = len(path.read_text(encoding="utf-8", errors="ignore").split())

        if words > args.max_words:
            print(f"  drop {book_id}: {words:,} words, too long  ({title[:50]})")
            path.unlink()
            continue

        if words < args.min_words:
            print(f"  drop {book_id}: only {words:,} words  ({title[:50]})")
            path.unlink()
            continue

        kept.append((book_id, title, authors, words))
        print(f"[{len(kept):3d}] {book_id}: {words:>9,} words  {title[:60]}")

    with open(args.id_list_out, "w", encoding="utf-8") as f:
        for book_id, title, authors, words in kept:
            f.write(f"{book_id}\t{words}\t{title}\t{authors}\n")

    total = sum(book[3] for book in kept)
    print()
    print(f"Kept {len(kept)} books, {total:,} words")
    print(f"ID list written to {args.id_list_out}")
    print("Review the titles, delete unsuitable files, and re-run with --ids "
          "if you want to rebuild.")


if __name__ == "__main__":
    sys.exit(main())
