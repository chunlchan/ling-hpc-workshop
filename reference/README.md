# Linguistics HPC Workshop: Counting Bigrams in Parallel

In this activity you will count **bigrams** (pairs of consecutive words, such as
"of the" or "it was") across a corpus of about 4,000 short passages (stored in 40 files) from Project
Gutenberg, about 19.5 million words in all. You will run the same analysis
twice:

1. **Serial:** one core processes the files one after another.
2. **Parallel:** eight cores each process part of the corpus, then the results are combined.

The linguistic analysis is the same in both. Only the way the work is scheduled changes.

## Before you start

You need to be logged in to the Quartz cluster (for example through the Research Desktop).
Your instructor will tell you:

- which **account** to use (the `--account` line in the two `.slurm` files), and
- where to find the workshop files.

Make a working folder and copy the files into it:

```
mkdir ~/bigrams && cd ~/bigrams
cp <WORKSHOP_FILES>/* .
```

Check that your scratch folder exists. Your results are saved there:

```
ls -d /N/scratch/$USER
```

## Step 1: Run the serial job

```
sbatch run_serial.slurm
```

`sbatch` prints a job number, for example `Submitted batch job 12345678`.
Check on your job with:

```
squeue --me
```

When your job no longer appears in the list, it has finished.

## Step 2: Run the parallel job

```
sbatch run_parallel.slurm
```

Wait for it to finish in the same way.

## Step 3: Read your results

The output files are in your scratch folder:

```
ls /N/scratch/$USER
cat /N/scratch/$USER/serial_<jobnumber>.out
cat /N/scratch/$USER/parallel_<jobnumber>.out
```

Replace `<jobnumber>` with your job's number. In each file, find:

- `Found ... files` and `Documents (lines)`: the number of files and documents read.
- `Finished in ... seconds`: the **runtime**.
- The **top 20 bigrams**.
- `Total bigrams` and `Distinct bigrams`.

The top 1,000 bigrams are also saved as tab-separated files that you can open in a spreadsheet:

- `/N/scratch/$USER/bigram_counts_serial.tsv`
- `/N/scratch/$USER/bigram_counts_parallel.tsv`

## Step 4: Compare

Fill in your own numbers:

| Cores | Runtime (seconds) | Speedup |
|-------|-------------------|---------|
| 1 (serial) | | 1.0× |
| 8 (parallel) | | |

**Speedup = serial runtime ÷ parallel runtime.**

Questions to think about:

1. Are the bigram counts identical in the serial and parallel runs? Should they be?
2. Is the speedup 8×? Why might it be less?
3. What are the most frequent bigrams? What kinds of words do they contain?

## Notes

- **Runtimes vary.** The cluster is shared, so the same job can take noticeably longer or shorter
  from one run to the next. If your results look odd, run the job again.
- **What "cores" means.** A core is one processing unit. The parallel job asks SLURM for 8 cores on
  one machine, and the program starts 8 worker processes, one per core.
- **Optional:** try a different number of cores without editing the script:
  ```
  sbatch --cpus-per-task=4 run_parallel.slurm
  ```
  More cores do not always give a proportionally faster run, because starting the workers and
  combining their results takes time too. Compare your own timings.
- If a job fails, look at the matching `.err` file in `/N/scratch/$USER` and ask an instructor for help.
