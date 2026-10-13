#!/bin/bash

#SBATCH --job-name=bigram-serial
#SBATCH --output=/N/scratch/%u/serial_%j.out
#SBATCH --error=/N/scratch/%u/serial_%j.err

# IU-specific settings
#SBATCH --account=<ACCOUNT>
#SBATCH --partition=general

# Resource request
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

echo "======================================"
echo "Serial Bigram Analysis"
echo "======================================"
echo "Job ID:       $SLURM_JOB_ID"
echo "Node:         $SLURM_NODELIST"
echo "CPUs:         $SLURM_CPUS_PER_TASK"
echo "Start time:   $(date)"
echo

# Load/activate Python environment as appropriate for IU
module load python/<VERSION>   # find versions with: module spider python
# OR
# source <PATH_TO_ENVIRONMENT>/bin/activate

# Shared read-only corpus; results go to your scratch space
export CORPUS_DIR=<CORPUS_DIR>
export OUTPUT_DIR=/N/scratch/$USER

python bigrams_serial.py

echo
echo "End time:     $(date)"
