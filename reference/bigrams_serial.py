#!/usr/bin/env python3

"""
Serial bigram counter for the concatenated corpus.

Each line of each file is one document, so bigrams are counted line by line
and never pair the last word of one document with the first word of the next.
"""

from collections import Counter
from pathlib import Path
import os
import time


# Read-only corpus location (set CORPUS_DIR to override)
CORPUS_DIR = os.environ.get("CORPUS_DIR", "corpus")

# Where results are written (set OUTPUT_DIR to override)
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")


def main():
    files = sorted(Path(CORPUS_DIR).glob("*.txt"))

    if not files:
        raise SystemExit(
            f"ERROR: no .txt files found in '{CORPUS_DIR}'. "
            "Check that CORPUS_DIR is set to the folder containing the corpus files."
        )

    print(f"Found {len(files)} files.")
    print("Running serial bigram analysis...")

    start = time.perf_counter()

    total_counts = Counter()
    num_documents = 0

    for filename in files:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                words = line.split()
                if not words:
                    continue
                num_documents += 1
                for word1, word2 in zip(words, words[1:]):
                    total_counts[(word1, word2)] += 1

    elapsed = time.perf_counter() - start

    print(f"\nDocuments (lines): {num_documents:,}")
    print(f"Finished in {elapsed:.2f} seconds")
    print("\nTop 20 bigrams:")

    for (word1, word2), count in total_counts.most_common(20):
        print(f"{word1} {word2}: {count}")

    print(f"\nTotal bigrams:    {sum(total_counts.values()):,}")
    print(f"Distinct bigrams: {len(total_counts):,}")

    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "bigram_counts_serial.tsv"
    with open(out_file, "w", encoding="utf-8") as f:
        for (word1, word2), count in total_counts.most_common(1000):
            f.write(f"{word1}\t{word2}\t{count}\n")
    print(f"Results saved to {out_file}")


if __name__ == "__main__":
    main()
