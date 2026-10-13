#!/usr/bin/env python3

"""
Prepare a workshop corpus from Project Gutenberg texts.

Example:

    python prepare_corpus.py \
        --input gutenberg_books \
        --output corpus \
        --books 50 \
        --words-per-file 5000

This takes up to 50 Gutenberg books and divides them into
5,000-word text files.
"""

import argparse
import re
from pathlib import Path


START_RE = re.compile(r"\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
END_RE = re.compile(r"\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK", re.I)


def strip_gutenberg_boilerplate(text):
    """Keep only the text between the Gutenberg START and END markers."""
    start = START_RE.search(text)
    if start:
        text = text[start.end():]
    end = END_RE.search(text)
    if end:
        text = text[:end.start()]
    return text


def clean_text(text):
    """Basic text cleaning for the workshop."""

    text = strip_gutenberg_boilerplate(text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Lowercase
    text = text.lower()

    return text.strip()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing Gutenberg .txt files"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Directory where workshop corpus will be created"
    )

    parser.add_argument(
        "--books",
        type=int,
        default=50,
        help="Number of source books to use"
    )

    parser.add_argument(
        "--words-per-file",
        type=int,
        default=5000,
        help="Approximate number of words per output document"
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    output_dir.mkdir(parents=True, exist_ok=True)

    books = sorted(input_dir.glob("*.txt"))

    if not books:
        raise RuntimeError(
            f"No .txt files found in {input_dir}"
        )

    books = books[:args.books]

    print(f"Using {len(books)} Gutenberg books")
    print(f"Target words per file: {args.words_per_file}")
    print(f"Output directory: {output_dir}")

    document_number = 1
    total_words = 0

    for book in books:

        print(f"Processing {book.name}")

        text = book.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        text = clean_text(text)

        words = text.split()

        # Divide this book into chunks
        for start in range(
            0,
            len(words),
            args.words_per_file
        ):

            chunk = words[
                start:start + args.words_per_file
            ]

            if len(chunk) < 100:
                continue

            output_file = (
                output_dir /
                f"document_{document_number:06d}.txt"
            )

            output_file.write_text(
                " ".join(chunk),
                encoding="utf-8"
            )

            document_number += 1
            total_words += len(chunk)

    total_documents = document_number - 1

    print()
    print("Corpus created")
    print("----------------------------")
    print(f"Documents: {total_documents}")
    print(f"Words:     {total_words:,}")
    print(f"Location:  {output_dir}")

if __name__ == "__main__":
    main()
