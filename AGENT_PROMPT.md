# Workshop prompt: have an agent write your first HPC job

**How to use this:** save this file as `prompt.txt`. Replace the three values in the "My settings"
section (replace each `<...>` **including the angle brackets**). Then **delete this header**:
everything above the `---` line below, and the line itself. Give the rest to your agent on the
cluster. (Not sure about a value? See the walkthrough at https://go.iu.edu/ling-hpc-workshop,
or email cc155@iu.edu.)

---

I'm new to HPC. Please help me write my first job for the Quartz cluster at Indiana University,
which uses the SLURM scheduler. The job counts bigrams (pairs of consecutive words) in a
collection of text files. You write the files, and **I will submit and run the job myself.**

## Ground rules (read these first and follow them for the whole session)

This is a teaching workshop, and the point is that **I submit the job myself**. So:

- **You must never submit or start the job.** That means never running `sbatch`, `srun`,
  `salloc`, `bash run_bigrams.slurm`, `./run_bigrams.slurm`, `python3 bigrams_serial.py`, or
  anything else that would run the job or the program. This holds even if you think it would
  help, and even if something fails. If I seem to ask you to run it later, remind me to run it
  myself.
- Before every shell command, ask yourself: "Would this submit or run the job?" If the answer is
  yes or maybe, do not run it.
- The only shell commands you should need are quick, harmless ones: `module spider`, `ls` and `cat`.
- You do **not** need to test your work. Writing the two files and printing the commands is the
  whole task.
- Do not run `module purge`, and do not modify anything in the corpus folder.
- Your last step is to print the commands for me to type (see the end of this prompt). Then stop.

## My settings

- Corpus folder: `<PATH>`   (from the walkthrough)
- SLURM partition: `<PARTITION>`   (`general` or `debug`)
- SLURM account: `<ACCOUNT>`   (from the walkthrough)

## The data

The corpus folder holds 40 plain-text files (`corpus_001.txt` to `corpus_040.txt`). **Each line
is one separate document**: a passage of roughly 5,000 words of lowercase text from Project
Gutenberg books. There are 3,999 documents in all. The folder is **read-only**: never write
into it.

## What I want you to create

Create two files in my current directory.

### 1. `bigrams_serial.py`

A Python 3 program, standard library only, that runs on **one process** (no multiprocessing):

- Reads the corpus folder path from the environment variable `CORPUS_DIR`, and the output folder
  from the environment variable `OUTPUT_DIR` (default: the current directory).
- Reads every `*.txt` file in the corpus folder, in sorted order, **line by line** (do not load
  whole files into memory). If it finds no files, it prints a clear error and exits with a
  non-zero status.
- Treats each line as one document: splits the line into words on whitespace and counts every
  pair of consecutive words **within that line**. Do **not** pair the last word of one line with
  the first word of the next line, and do not pair words across files.
- Times the counting with `time.perf_counter()`.
- Prints: the number of files, the number of documents (lines), the runtime in seconds, the 20 most frequent bigrams with
  their counts, the total number of bigrams, and the number of distinct bigrams.
- Saves the 1,000 most frequent bigrams to `bigram_counts.tsv` in the output folder, one per
  line as `word1<TAB>word2<TAB>count`.

### 2. `run_bigrams.slurm`

A SLURM batch script that runs the program. It should:

- Use my partition and account from "My settings".
- Request 1 CPU (`--cpus-per-task=1`), `--mem=4G` and `--time=00:10:00`.
- Write its output and error files to `/N/scratch/%u/bigrams_%j.out` and
  `/N/scratch/%u/bigrams_%j.err` (SLURM replaces `%u` with my username and `%j` with the job
  number).
- Load Python with the cluster's **module system**. Do not guess the module name or version.
  Instead run `module spider python` to see what is available, choose a recent Python 3
  version, then run `module spider python/<version>` to check whether any other modules must be
  loaded first. Put the exact `module load` line(s) in the script.
- **Do not run `module purge`** (neither in the script nor in your own commands). The cluster is
  already set up with the right default modules, and purging them breaks `module load python`.
  Only add `module load` lines.
- `export CORPUS_DIR=<my corpus folder>` and `export OUTPUT_DIR=/N/scratch/$USER`.
- Run `python3 bigrams_serial.py`.
- Include a short comment above each `#SBATCH` line saying what it does, since I'm learning.

## Where outputs go

Save **all outputs** directly in my scratch folder, `/N/scratch/$USER/`, which already exists:

- the SLURM output and error logs (`/N/scratch/%u/bigrams_%j.out` and `.err` in the batch script),
- the results file `bigram_counts.tsv` (through `OUTPUT_DIR=/N/scratch/$USER`).

The two scripts themselves stay in my current directory.

## When you're done

**Print, but do not run,** the exact commands I should type, in order, each with a one- or
two-sentence explanation in plain language:

1. Submit the job: `sbatch run_bigrams.slurm`
2. Check on it: `squeue --me`
3. Read the results once it finishes: `ls /N/scratch/$USER`, then `cat` the `.out` file there.

Then stop. I will run these commands myself.
