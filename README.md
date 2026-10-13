# Linguistics HPC Workshop: Your First Cluster Job

A short, hands-on activity that introduces linguistics faculty and students to high-performance
computing. Participants use an AI agent on the cluster to write a small Python program and a
SLURM batch script that counts **bigrams** (pairs of consecutive words) in a corpus of about
4,000 short Project Gutenberg passages (19.5 million words). They then submit the job themselves,
watch it run, and read the results.

The aim is for students to experience the real workflow of submitting and monitoring a job. The
linguistic analysis is deliberately simple.

Developed for Indiana University's Quartz cluster, but nothing about the method is specific to IU.
Cluster-specific values (account, partition, module version, corpus path) are placeholders.

## What's in this repository

| Path | What it is |
|---|---|
| [`AGENT_PROMPT.md`](AGENT_PROMPT.md) | The prompt students paste into the agent. They fill in three values: corpus path, partition, account |
| [`INSTRUCTOR_GUIDE.md`](INSTRUCTOR_GUIDE.md) | Answer sheet (expected numbers) and troubleshooting for common failures |
| [`reference/`](reference/) | Tested serial script and SLURM script, to use as a fallback if a student's agent-written version fails. Also a parallel (multiprocessing) version for future use, with a student README |
| [`corpus_prep/`](corpus_prep/) | Scripts and the book list used to build the corpus |
| [`docs/`](docs/) | The workshop slide deck: a single HTML page, published with GitHub Pages at <https://chunlchan.github.io/ling-hpc-workshop/> (short link: <https://go.iu.edu/yPx3ED>) |
| [`archive/PLAN.md`](archive/PLAN.md) | The original design notes, kept for reference (partly out of date) |

## Instructor quick start

1. **Get the corpus onto the cluster** (see below) in a folder that all participants can read.
2. **Fill in your values:** the corpus path, the partition (`general` or `debug`), and the account
   participants should use. Participants enter these into the prompt.
3. **Test the prompt** in the agent your participants will use, several times, from empty
   folders. The checklist is in the instructor guide.
4. **Run the activity** from the slide deck (above). Participants save the prompt as `prompt.txt`,
   edit the three values, and give it to the agent. Expected results for a correct run: 3,999 documents, 19,500,939 total
   bigrams, 5,306,726 distinct bigrams, "of the" as the most frequent bigram (177,785).

## The corpus

The corpus is 40 plain-text files (`corpus_001.txt` to `corpus_040.txt`, about 2.8 MB each).
Together they hold 3,999 documents of about 5,000 words of lowercase text from Project Gutenberg
books, with **one document per line**. It is **not stored in the repository** (110 MB
uncompressed).

**Why 40 large files and not thousands of small ones?** On parallel filesystems such as Lustre,
every file open has a fixed cost that depends on cluster load. The same text stored as 3,999
small files took from about 1 minute to over 8 minutes to process, depending on the day. As 40
large files it takes about 30 seconds, consistently. One document per line keeps the document
boundaries, so a program that counts bigrams line by line gets exactly the same counts either
way (19,500,939 bigrams, 5,306,726 distinct).

**Download the prebuilt corpus** (about 40 MB) from the Releases page of this repository:

```
wget https://github.com/chunlchan/ling-hpc-workshop/releases/download/2026-10-12_01/prepared_4k_concat.zip
unzip prepared_4k_concat.zip
```

Then use the unpacked `prepared_4k_concat/` folder as the corpus path. If your cluster's shared
project space is slow, each participant can instead unpack a copy in their home directory. That is
not best practice for large data, but it works for a mini workshop of this size.

**Rebuild it from scratch**, using the book list in `corpus_prep/book_ids.txt`:

```
cd corpus_prep
python3 fetch_gutenberg.py --ids book_ids.txt --output gutenberg_books
python3 prepare_corpus.py --input gutenberg_books --output prepared --books 500 --words-per-file 5000
mkdir prepared_4k && cp prepared/document_00[0-3]*.txt prepared_4k/
python3 concat_corpus.py --input prepared_4k --output prepared_4k_concat --files 40
```

The first two steps produce about 9,900 small documents. The workshop uses the first 3,999 of
them (the `cp` step), merged into 40 files (the last step). The download step waits between
requests to respect Project Gutenberg's
[robot access policy](https://www.gutenberg.org/policy/robot_access.html). The books were chosen
from Gutenberg's catalog with a fixed random seed (42), and `book_ids.txt` records the 500 books,
so the corpus can be rebuilt closely (Project Gutenberg occasionally updates a text, so a
rebuild may differ slightly from the prebuilt download).

### Source and terms of use of the texts

All text in the corpus comes from [Project Gutenberg](https://www.gutenberg.org). The books are in
the **public domain in the United States**. Their copyright status in other countries can differ,
so check it if you are outside the US.

`prepare_corpus.py` removes the standard Project Gutenberg header and license text from each book,
but the removal is not perfect. A small number of documents still mention "Project Gutenberg" in
other places: 59 of the 3,999 documents (70 mentions in total) contain it, for example in older
"End of Project Gutenberg's ..." footers that don't use the standard end marker, in volunteer
production credits, and in transcriber's notes. If you redistribute the corpus, read Project
Gutenberg's [terms of use](https://www.gutenberg.org/policy/license.html).

## Notes on timing

On the 40-file corpus, the serial bigram count took about 30 seconds on Quartz (29.0 s and 30.4 s
for the reference script, and about 32.7 s for two agent-written scripts). Runtimes on a shared
cluster can vary with load.

## Scope and possible next steps

The current activity is deliberately small: each participant has an agent write one **serial**
program and batch script, submits the job, and reads the results. That is enough to experience the
real workflow of running a job on a cluster within a short workshop.

Natural extensions, not yet part of the workshop:

- **Serial versus parallel.** A follow-up prompt that asks the agent for a `multiprocessing`
  version, so participants can compare runtimes. A tested parallel script and SLURM file are in
  [`reference/`](reference/). They give the same counts as the serial script on this corpus, but
  have not been timed on the final 40-file layout. Earlier timings on a different file layout
  suggested a clear speedup at 8 cores and little at 4, so measure before promising a result.
- **Many participants at once.** A test with several people submitting at the same time, to see
  how the shared storage and queue behave.
- **A reservation** for the workshop time slot, if the cluster is busy.

## License

The code and documentation in this repository are released under the [MIT License](LICENSE). The
corpus text is from Project Gutenberg and is not covered by this license; see
[Source and terms of use of the texts](#source-and-terms-of-use-of-the-texts) above.
