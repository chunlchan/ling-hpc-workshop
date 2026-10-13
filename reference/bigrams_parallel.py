#!/usr/bin/env python3

from collections import Counter
from pathlib import Path
from multiprocessing import Pool
import os
import time


# Read-only corpus location (set CORPUS_DIR to override)
CORPUS_DIR = os.environ.get("CORPUS_DIR", "corpus")

# Where results are written (set OUTPUT_DIR to override)
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")


def count_bigrams(filename):
    """Count bigrams in one corpus file. Each line is a separate document."""
    counts = Counter()

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            words = line.split()
            for word1, word2 in zip(words, words[1:]):
                counts[(word1, word2)] += 1

    return counts


def count_bigrams_in_files(filenames):
    """Count bigrams across a batch of files (the work done by one worker)."""
    counts = Counter()

    for filename in filenames:
        counts.update(count_bigrams(filename))

    return counts


def split_into_chunks(items, num_chunks):
    """Split a list into num_chunks contiguous, nearly equal pieces."""
    size, extra = divmod(len(items), num_chunks)
    chunks = []
    start = 0

    for i in range(num_chunks):
        end = start + size + (1 if i < extra else 0)
        chunks.append(items[start:end])
        start = end

    return chunks


def main():
    files = sorted(Path(CORPUS_DIR).glob("*.txt"))

    if not files:
        raise SystemExit(
            f"ERROR: no .txt documents found in '{CORPUS_DIR}'. "
            "Check that CORPUS_DIR is set to the folder containing the documents."
        )

    # Get the number of CPUs allocated by SLURM.
    # Fall back to 1 if the script is run outside SLURM.
    num_processes = int(
        os.environ.get("SLURM_CPUS_PER_TASK", 1)
    )

    print(f"Found {len(files)} files.")
    print(f"Running parallel bigram analysis with {num_processes} processes...")

    start = time.perf_counter()

    total_counts = Counter()

    # Give each worker one contiguous block of documents. Each worker
    # returns a single combined count, so little data is sent back.
    chunks = split_into_chunks(files, num_processes)

    with Pool(processes=num_processes) as pool:
        results = pool.map(count_bigrams_in_files, chunks)

    # Combine the results from all workers
    for counts in results:
        total_counts.update(counts)

    elapsed = time.perf_counter() - start

    print(f"\nFinished in {elapsed:.2f} seconds")
    print("\nTop 20 bigrams:")

    for (word1, word2), count in total_counts.most_common(20):
        print(f"{word1} {word2}: {count}")

    # Summary numbers students can compare between serial and parallel runs
    print(f"\nTotal bigrams:    {sum(total_counts.values()):,}")
    print(f"Distinct bigrams: {len(total_counts):,}")

    # Save the top bigrams to the output directory
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "bigram_counts_parallel.tsv"
    with open(out_file, "w", encoding="utf-8") as f:
        for (word1, word2), count in total_counts.most_common(1000):
            f.write(f"{word1}\t{word2}\t{count}\n")
    print(f"Results saved to {out_file}")


if __name__ == "__main__":
    main()
