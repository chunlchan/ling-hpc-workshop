#!/usr/bin/env python3

"""
Combine many small corpus documents into a few large files.

Reading thousands of small files is slow on parallel filesystems such as Lustre,
because every file open has a fixed cost. A few large files read much faster.

Each input document becomes ONE LINE of an output file, so document boundaries
are preserved: a program that counts bigrams line by line gets exactly the same
counts as one that counts file by file.

Example:

    python concat_corpus.py \
        --input prepared_4k \
        --output prepared_4k_concat \
        --files 40

This turns 3,999 documents into 40 files of about 100 documents each
(corpus_001.txt ... corpus_040.txt).
"""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Folder of small document_*.txt files")
    parser.add_argument("--output", required=True,
                        help="Folder to create for the combined files")
    parser.add_argument("--files", type=int, default=40,
                        help="Number of output files")
    args = parser.parse_args()

    documents = sorted(Path(args.input).glob("*.txt"))
    if not documents:
        raise SystemExit(f"No .txt files found in {args.input}")
    if args.files < 1 or args.files > len(documents):
        raise SystemExit(f"--files must be between 1 and {len(documents)}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Split the sorted documents into contiguous, nearly equal groups
    size, extra = divmod(len(documents), args.files)
    start = 0
    total_words = 0

    for i in range(args.files):
        end = start + size + (1 if i < extra else 0)
        lines = []

        for document in documents[start:end]:
            text = document.read_text(encoding="utf-8")
            # One document per line: collapse any internal line breaks
            words = text.split()
            total_words += len(words)
            lines.append(" ".join(words))

        out_file = output_dir / f"corpus_{i + 1:03d}.txt"
        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        start = end

    print(f"Documents: {len(documents):,}")
    print(f"Words:     {total_words:,}")
    print(f"Files:     {args.files}  ({size}-{size + (1 if extra else 0)} documents each)")
    print(f"Location:  {output_dir}")


if __name__ == "__main__":
    main()
