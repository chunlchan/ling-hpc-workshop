> **Historical note.** This is the original design plan, kept for reference. The workshop has
> changed since it was written:
>
> - Students now have an AI agent write a serial bigram-counting script and a SLURM script from a
>   prompt ([`AGENT_PROMPT.md`](../AGENT_PROMPT.md)), instead of running provided scripts. The tested
>   serial and parallel scripts are kept in [`reference/`](../reference/) as a fallback. The
>   parallel exercise is on hold.
> - The corpus is 3,999 documents (19.5M words) stored as **40 large files, one document per
>   line**, not about 10,000 small files. Reading thousands of small files from the cluster's
>   shared filesystem was slow and erratic.
> - The reference parallel script uses 8 cores, not 4, because 8 gave a clearer speedup in testing.
> - Resource requests, paths and timings in this plan are placeholders or early estimates. See the
>   [README](../README.md) and [`INSTRUCTOR_GUIDE.md`](../INSTRUCTOR_GUIDE.md) for the current design.

Workshop Activity and Corpus Preparation Plan

# Linguistics HPC Workshop: Corpus Processing and Parallel Computing

 ## Workshop Activity

 ### Goal

 Introduce linguistics faculty and students to HPC through a short, hands-on corpus-processing task.

 Participants will use HPC resources to process a large text corpus and compare **serial and parallel approaches** to corpus-based linguistic analysis.

 The activity is designed for approximately **15–20 minutes** within a one-hour workshop.

 ### Core linguistic task

 Participants will calculate **bigram frequencies** across a collection of text documents.

 A bigram is a pair of consecutive words:

```
natural language
language acquisition
syntactic structure
```

 The linguistic computation is intentionally simple. The primary HPC learning objective is to demonstrate how the same computation can be distributed across multiple CPUs.

 ### Core HPC concept

 The corpus consists of many independent text documents.

 The serial version processes documents one at a time:

```
Document 1 → Document 2 → Document 3 → Document 4 → ...
                         1 CPU
```

 The parallel version distributes documents across multiple worker processes:

```
                    ┌→ Documents 1–2500
                    ├→ Documents 2501–5000
Corpus ─────────────┼→ Documents 5001–7500
                    └→ Documents 7501–10000
                      CPU 1  CPU 2  CPU 3  CPU 4
                              │
                              ↓
                       Combine counts
```

 The two approaches perform the **same linguistic analysis** and should produce the same bigram counts. The difference is how the computational work is scheduled.

 ### Student experiment

 Students will:

 1. Run the serial version using one CPU.
2. Record the runtime.
3. Run the parallel version using four CPUs.
4. Compare the runtimes.
5. Calculate the approximate speedup.
6. Examine the resulting bigram frequencies.
7. Optionally repeat the experiment with eight CPUs.

 Example:

```
CPUs       Runtime       Speedup
--------------------------------
1          38.7 sec       1.0×
4          11.4 sec       3.4×
8           8.2 sec       4.7×
```

 These numbers are illustrative. The actual corpus size and expected timings will be determined through benchmarking on the target IU HPC system.

 ## Software

 The workshop will use two Python programs.

 ### `bigrams_serial.py`

 Processes all documents sequentially using one process.

 ### `bigrams_parallel.py`

 Uses Python's `multiprocessing` library to distribute documents across multiple processes.

 The parallel program obtains the number of processes from:

```
SLURM_CPUS_PER_TASK
```

 This allows the SLURM resource request to control the degree of parallelism.

 ## SLURM jobs

 Two SLURM scripts will be provided.

 ### `run_serial.slurm`

 Requests:

```
CPUs: 1
```

 and runs:

```
bigrams_serial.py
```

 ### `run_parallel.slurm`

 Requests:

```
CPUs: 4
```

 and runs:

```
bigrams_parallel.py
```

 IU-specific account and partition information will be added once the target cluster and allocation are confirmed.

 ## Corpus Strategy

 ### General approach

 Use a pre-staged collection of **Project Gutenberg** texts.

 The corpus will be prepared by the workshop organizers and placed in a shared location on the IU HPC filesystem.

 Students will **not download the corpus** and will not need to construct it themselves.

 The Python programs will read the corpus directly from the shared location.

 ### Why Gutenberg?

 Gutenberg is preferable to the Brown Corpus for this activity because it provides substantially more text and allows the computational workload to be scaled to produce a visible serial/parallel performance difference.

 Brown may still be useful as a small development/test corpus.

 ### Corpus structure

 The shared corpus should eventually look approximately like:

```
<SHARED_CORPUS>/
├── document_000001.txt
├── document_000002.txt
├── document_000003.txt
├── ...
└── document_00XXXX.txt
```

 The documents should be independent text files so that they can easily be distributed among parallel workers.

 The Python programs will use a configurable corpus path, preferably through an environment variable:

```
export CORPUS_DIR="<SHARED_CORPUS>"
```

 This avoids hard-coding an IU-specific path into the Python source.

 ## Corpus Preparation

 ### Important design principle

 The corpus should be large enough to make parallelization measurable but small enough that the workshop jobs complete quickly.

 The target is approximately:

```
Serial runtime:    20–45 seconds
Parallel runtime:   7–20 seconds
```

 These are targets rather than requirements.

 The final values will be determined empirically on the actual IU HPC system.

 ### Corpus preparation process

 The corpus should be constructed in stages.

 #### 1\. Acquire Gutenberg texts

 Obtain a manageable initial collection of Project Gutenberg plain-text files.

 Start with approximately:

```
20–50 books
```

 for initial testing.

 #### 2\. Clean the texts

 Perform basic preprocessing:

 - normalize whitespace;
- convert text to lowercase;
- remove or handle Gutenberg boilerplate where appropriate;
- preserve ordinary word sequences.

 The workshop does not require sophisticated linguistic tokenization.

 #### 3\. Create independent documents

 Rather than using only whole books, divide the texts into reasonably sized chunks.

 For example:

```
5,000 words per document
```

 This creates many independent work units for the parallel computation.

 Example:

```
Book 1
  → document_000001.txt
  → document_000002.txt
  → document_000003.txt

Book 2
  → document_000004.txt
  → document_000005.txt
  → ...
```

 This is useful because the parallel program can distribute individual documents among worker processes.

 #### 4\. Benchmark the corpus

 Run the serial and parallel programs on the actual IU HPC system.

 Test several CPU counts:

```
1 CPU
2 CPUs
4 CPUs
8 CPUs
```

 Record:

 - number of documents;
- approximate number of words;
- runtime;
- speedup.

 #### 5\. Adjust corpus size

 If the serial computation is too fast to demonstrate meaningful speedup, increase the corpus.

 If it takes too long, reduce the corpus.

 The final corpus should be frozen once appropriate timings have been established.

 ## Shared Filesystem Plan

 The preferred approach is to place the corpus in a shared, read-only location accessible to workshop participants.

 Students will point their jobs directly at this corpus.

 They will **not copy the corpus to scratch** unless testing shows that the shared filesystem cannot support the expected simultaneous workload.

 Conceptually:

```
                 Shared corpus
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       Student 1   Student 2   Student 3
          │           │           │
          ↓           ↓           ↓
       1 CPU       1 CPU       4 CPUs
```

 This eliminates a potentially confusing data-transfer step from the 15–20 minute activity.

 ### Filesystem testing

 Before the workshop, test the corpus with multiple simultaneous jobs.

 Approximately the expected number of workshop participants should submit jobs concurrently.

 Verify that:

 - the corpus remains accessible;
- jobs do not experience excessive I/O delays;
- runtime remains reasonably consistent;
- the shared filesystem can handle simultaneous reads.

 If simultaneous access causes an unacceptable bottleneck, reconsider using scratch storage or another staging strategy.

 ## Files to Prepare

 The final workshop package should contain:

```
linguistics-hpc/
├── bigrams_serial.py
├── bigrams_parallel.py
├── run_serial.slurm
├── run_parallel.slurm
└── README.md
```

 The corpus will live separately in the shared filesystem:

```
<SHARED_CORPUS>/
    document_000001.txt
    document_000002.txt
    ...
```

 ## Immediate Next Steps

 ### Step 1 — Confirm IU HPC environment

 Determine:

 - target IU cluster;
- account/allocation;
- partition;
- Python version/environment;
- shared filesystem location;
- expected number of workshop participants.

 ### Step 2 — Obtain initial Gutenberg texts

 Prepare approximately 20–50 Gutenberg texts for development and testing.

 ### Step 3 — Create initial corpus

 Run the corpus preparation script to:

 - clean the texts;
- divide them into independent documents;
- place them in the initial corpus directory.

 ### Step 4 — Test the serial code

 Run `bigrams_serial.py` on the IU cluster.

 Verify:

 - successful execution;
- sensible bigram results;
- runtime measurement.

 ### Step 5 — Test the parallel code

 Run `bigrams_parallel.py` with:

```
1 CPU
2 CPUs
4 CPUs
8 CPUs
```

 Verify:

 - results match the serial version;
- runtime decreases;
- parallelization behaves as expected.

 ### Step 6 — Tune corpus size

 Increase or decrease the corpus until the serial runtime is approximately 20–45 seconds.

 ### Step 7 — Test simultaneous users

 Run multiple copies of the job against the shared corpus.

 Verify that shared filesystem performance is acceptable.

 ### Step 8 — Freeze the workshop corpus

 Once the corpus size and workload are satisfactory, place the final corpus in the permanent shared location.

 ### Step 9 — Finalize SLURM scripts

 Replace placeholders with the actual IU:

```
<ACCOUNT>
<PARTITION>
<PYTHON_ENVIRONMENT>
<SHARED_CORPUS>
```

 ### Step 10 — Create student instructions

 Prepare a short README containing only the commands participants need.

 The goal is for the hands-on activity to require minimal setup:

```
sbatch run_serial.slurm
```

 then:

```
sbatch run_parallel.slurm
```

 followed by comparison of the results and runtimes.

 ## Workshop Learning Outcome

 By the end of the activity, participants should understand that:

 1. A corpus-based linguistic computation can be decomposed into many independent tasks.
2. Those tasks can be distributed across multiple CPUs.
3. HPC schedulers allow researchers to request the computational resources needed for the task.
4. Parallel execution can reduce runtime, although speedup is not necessarily linear.
5. The linguistic analysis itself does not have to change in order to benefit from parallel computing.