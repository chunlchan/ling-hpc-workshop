# Instructor Guide: Bigram Counting Activity

Two parts: an **answer sheet** (what a correct run looks like) and a **troubleshooting sheet**
(what goes wrong and how to fix it). Both come from our own test runs on Quartz.

---

# Part 1: Answer sheet

## Settings students fill into the prompt

| Setting | Value |
|---|---|
| Corpus folder | `<CORPUS_DIR>`, the folder containing `corpus_001.txt` to `corpus_040.txt` |
| Partition | `general` (or `debug` as the fallback) |
| Account | `<ACCOUNT>` (the workshop account, or the student's own) |

## What a correct result looks like

Whatever code the agent writes, these numbers must match:

| Quantity | Expected value |
|---|---|
| Files | **40** |
| Documents (one per line) | **3,999** |
| Total bigrams | **19,500,939** |
| Distinct bigrams | **5,306,726** |
| Most frequent bigram | **of the**, 177,785 |

Top 20 bigrams, in order:

| # | Bigram | Count | # | Bigram | Count |
|---|---|---|---|---|---|
| 1 | of the | 177,785 | 11 | it is | 27,128 |
| 2 | in the | 94,561 | 12 | from the | 26,321 |
| 3 | to the | 67,397 | 13 | by the | 26,195 |
| 4 | and the | 46,749 | 14 | with the | 26,166 |
| 5 | on the | 42,309 | 15 | in a | 25,576 |
| 6 | to be | 34,255 | 16 | he was | 23,422 |
| 7 | it was | 30,524 | 17 | of his | 22,414 |
| 8 | of a | 29,675 | 18 | that the | 21,762 |
| 9 | at the | 29,121 | 19 | he had | 20,834 |
| 10 | for the | 27,339 | 20 | with a | 19,690 |

**Formatting varies between agents and between runs.** Some print `19500939`, others
`19,500,939`; some print a table, others a tab-separated list. Tell students to compare the
numbers and not the layout. The `.tsv` results file has `word1<TAB>word2<TAB>count` on each line.

## Expected runtime

- The counting itself takes **about 30 seconds** (29.0 s and 30.4 s in two runs of the same job
  on Quartz). The whole job takes about 15–20 seconds longer than the number the program prints.
- **Some variation is normal** on a shared cluster, so don't worry if two students see somewhat
  different times.
- **Why 40 large files?** Reading thousands of small files from a Lustre filesystem is slow and
  erratic, because every file open has a fixed cost that depends on cluster load. The same
  corpus stored as 3,999 small files took anywhere from about 1 minute to over 8 minutes,
  depending on the day. As 40 large files (one document per line) it takes about 30 seconds,
  with identical results.
- Peak memory is **under 1 GB**. The prompt requests 4 GB and 10 minutes, which is comfortable.

## What a student should see, step by step

| Step | Command | What they see |
|---|---|---|
| Submit | `sbatch run_bigrams.slurm` | `Submitted batch job <number>` |
| Watch | `squeue --me` | state `PD` (pending) then `R` (running); the job disappears when finished |
| Finish | `ls /N/scratch/$USER` | `bigrams_<number>.out`, `bigrams_<number>.err`, `bigram_counts.tsv` |
| Read | `cat /N/scratch/$USER/bigrams_<number>.out` | the numbers above |

The `.err` file is normally empty. Running the job twice overwrites `bigram_counts.tsv` (the
log files have the job number in their names and stay separate).

## Useful reference commands

| Task | Command |
|---|---|
| See your jobs | `squeue --me` |
| Cancel a job | `scancel <jobid>` |
| See how a finished job ended | `sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS,ExitCode` |
| See available Python modules | `module spider python` |

Meaning of the `ST` column in `squeue`: `PD` pending, `R` running, `CG` completing.
In `sacct`, `COMPLETED` is success, `TIMEOUT` is out of time, `OUT_OF_ME...` is out of memory,
`FAILED` is a non-zero exit, and `CANCELLED` was stopped by the user or an admin.

## Fallback: the reference scripts

If a student's agent produces something that won't work, give them our tested files:
`reference/bigrams_serial.py` and `reference/run_serial.slurm`. Fill in the `--account`,
`--partition`, `module load` and `CORPUS_DIR` placeholders in `run_serial.slurm` first. These write `bigram_counts_serial.tsv` and
`serial_<jobid>.out` to `/N/scratch/$USER/` (different file names from the agent's version).

## Checklist before the workshop

- [ ] Run the prompt in the agent students will use, at least 3 times, from empty folders. Check
      the generated `.slurm` and `.py` files each time.
- [ ] In that agent, confirm `module spider python` works (the `module` command is a shell
      function, and some agent tools don't have it set up).
- [ ] Confirm the account works on both `general` and `debug`.
- [ ] Confirm the corpus folder is readable by a participant (not just you).
- [ ] Confirm `/N/scratch/$USER` exists for participants.
- [ ] Run a small simultaneous test with several people submitting at once.
- [ ] Check the queue on the day (`squeue | wc -l`, `sinfo -s`). On a busy Friday, every `general`
      node was allocated and jobs queued. Consider asking UITS for a **reservation**; otherwise
      `debug` is the fallback (below).

---

# Part 2: Troubleshooting sheet

## Problems at submission

| Symptom | Likely cause | Fix |
|---|---|---|
| `sbatch: error: Invalid account or account/partition combination` | Wrong account, or the account isn't allowed on that partition | Check the account spelling in `#SBATCH --account=`; try the other partition |
| `sbatch: error: Unable to open file run_bigrams.slurm` | Student is in the wrong folder, or the agent saved the file elsewhere | `ls` to find it, then `cd` there |
| `sbatch` accepted but job vanishes and **no `.out` or `.err` file appears** | SLURM couldn't write the log: the log folder doesn't exist or the path is wrong | Check the `--output` / `--error` lines point to `/N/scratch/%u/...` and that `/N/scratch/$USER` exists |
| Line `#SBATCH` ignored (job gets default settings) | A `#SBATCH` line placed *after* a command in the script | Move all `#SBATCH` lines above the first command |

## Problems in the queue

| Symptom | Likely cause | Fix |
|---|---|---|
| Job stays `PD` for a long time | The cluster is busy. The reason is in the last column of `squeue --me` (`Priority` and `Resources` mean it is waiting its turn) | Wait, or resubmit to `debug` (below) |
| Everyone's jobs pending at once | `general` full | Use `debug`, or request a reservation |

**Switching to `debug`:** no need to edit the file.
```
sbatch --partition=debug run_bigrams.slurm
```
`debug` has only a few nodes and a 1-hour limit, so it only helps a handful of jobs at a time.
If the earlier job is still pending, cancel it first (`scancel <jobid>`).

## Problems when the job runs

Look at the **`.err` file first**, then the `.out` file:
```
cat /N/scratch/$USER/bigrams_<jobid>.err
```

| Symptom / message | Likely cause | Fix |
|---|---|---|
| `python: command not found` or `python3: command not found` | Python module not loaded | Make sure the script has a `module load python/<version>` line before the Python command; find versions with `module spider python` |
| `module: command not found`, or `Lmod has detected the following error: ... unknown` | Wrong or invented module version | Run `module spider python`, copy a real version exactly |
| `module load python` stops working, or the module system seems broken | The agent ran `module purge`, which removes the cluster's default setup | Remove any `module purge` line. In an affected shell, start a new login session (or try `module reset`) |
| `unbound variable` near the `module load` line | The script has `set -u` and the module system uses unset variables | Change `set -euo pipefail` to `set -eo pipefail`, or remove the `set` line |
| `python3: can't open file '.../bigrams_serial.py'` | `sbatch` was run from a different folder than the one containing the `.py` file | `cd` to the folder with both files, or add `cd "$SLURM_SUBMIT_DIR"` to the script |
| `ERROR: CORPUS_DIR environment variable is not set` | The `export CORPUS_DIR=...` line is missing or misspelled | Add `export CORPUS_DIR=<CORPUS_DIR>` (your corpus folder) |
| `ERROR: no .txt files found` or `Found 0 documents` | `CORPUS_DIR` points to the wrong folder (typo, or a parent folder) | `ls <CORPUS_DIR> \| head` should list `corpus_001.txt` and so on |
| `Permission denied` on the corpus | Folder isn't readable by that student | Instructor check of folder permissions |
| `FileNotFoundError` / `Permission denied` when writing results | `OUTPUT_DIR` is not `/N/scratch/$USER`, or the folder isn't writable | Make sure `export OUTPUT_DIR=/N/scratch/$USER` is in the script |

## Problems with how the job ends

Run `sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS,ExitCode`.

| `State` | Meaning | Fix |
|---|---|---|
| `TIMEOUT` | Job exceeded `--time` | Raise `--time` (for example to `00:20:00`). Slow storage can stretch run time |
| `OUT_OF_ME...` | Job exceeded `--mem` | Raise `--mem` (our reference job needed under 1 GB; agent code that holds all the data in memory could need more) |
| `FAILED` | The program exited with an error | Read the `.err` file |
| `COMPLETED`, but numbers are wrong | The program has a logic error | See the next table |

## Problems with the numbers

| Symptom | Likely cause | Fix |
|---|---|---|
| Total bigrams too high by about 4,000 (for example 19,504,898 or 19,504,937) | The agent treated each file (or all the files together) as one text, so words were paired across line (document) boundaries | Bigrams must be counted **within each line** only. Total should be 19,500,939 |
| Total is far too low | Only some files were read (wrong glob pattern, wrong folder) | Files must be 40 and documents (lines) 3,999 |
| Different top bigrams | The agent changed the text (for example stripped punctuation, or lowercased) | The corpus is already lowercase plain text; split on whitespace only |
| Runtime much slower than expected (over 2–3 minutes) | The shared filesystem is busy | Normal variation; wait and re-run, nothing is wrong |

## Problems with the agent

| Symptom | Fix |
|---|---|
| The agent ran `sbatch` or the Python script itself | Not harmful, but tell the student to re-run with the rule restated; check no duplicate jobs with `squeue --me` and `scancel` extras |
| The agent made a parallel (multiprocessing) version | Ask it to redo it as a single-process program, or use the reference `bigrams_serial.py` |
| The agent invented a module version or paths | Remind it to run `module spider python`, or use the reference scripts |
| The agent finished without printing the commands | Ask it to print the commands to type, step by step |
| The student pasted the prompt without replacing `<PATH>`, `<PARTITION>` or `<ACCOUNT>` | Re-paste with the three values filled in |

## When nothing else works

Use the reference scripts (`reference/bigrams_serial.py` and `reference/run_serial.slurm`), after
editing the account and partition lines. They are tested and give the expected numbers.
