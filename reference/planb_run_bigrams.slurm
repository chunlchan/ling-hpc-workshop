#!/bin/bash
# Plan B batch script for the workshop: known to work with reference/bigrams_serial.py.
# Edit the account/partition lines if you use your own allocation or the debug partition.

# Job name shown in squeue
#SBATCH --job-name=bigrams
# Which queue (partition) to run in
#SBATCH --partition=general
# Which allocation is charged for the job
#SBATCH --account=c02318
# One CPU core: this is a serial (single-process) job
#SBATCH --cpus-per-task=1
# Memory limit: the job is killed if it needs more
#SBATCH --mem=4G
# Time limit (hours:minutes:seconds): the job is killed after this
#SBATCH --time=00:10:00
# Where the log files go (%u = your username, %j = the job number)
#SBATCH --output=/N/scratch/%u/bigrams_%j.out
#SBATCH --error=/N/scratch/%u/bigrams_%j.err

# Quartz provides software through modules, and a compute node starts without Python loaded.
# If this version no longer exists, run "module spider python" and choose another Python 3.
module load python/3.13.5

# Where the corpus is (read-only) and where results are written.
# If you downloaded your own copy of the corpus, change CORPUS_DIR to that folder.
export CORPUS_DIR=/N/project/rpworkshop/corpus/prepared_4k_concat/
export OUTPUT_DIR=/N/scratch/$USER

# Run the bigram counter
python3 bigrams_serial.py
