#!/bin/sh
# Create a folder of "guard" commands that stop an AI agent from submitting jobs.
#
# Usage:   sh make_guard.sh /path/to/guard_folder
#
# The folder gets stand-in versions of sbatch, srun and salloc. If a program is started with
# that folder at the front of its PATH, for example
#
#     PATH=/path/to/guard_folder:$PATH pi
#
# then any attempt to run those commands prints a message and fails. Only that program (and
# the commands it starts) is affected. Your normal shell, and any other terminal, still has the
# real sbatch, so students can submit the job themselves after leaving the agent.

set -e

dir="$1"
if [ -z "$dir" ]; then
    echo "Usage: sh make_guard.sh /path/to/guard_folder" >&2
    exit 1
fi

mkdir -p "$dir"

for cmd in sbatch srun salloc; do
    cat > "$dir/$cmd" <<STUB
#!/bin/sh
echo "BLOCKED: '$cmd' is disabled while this agent is running." >&2
echo "The student submits and runs jobs, not the agent." >&2
echo "Do not try another way to run or submit the job. Print the command for the student to type instead." >&2
exit 1
STUB
    chmod 755 "$dir/$cmd"
done

# Let everyone read and enter the folder (needed when it is shared)
chmod 755 "$dir"

echo "Created guard commands in $dir:"
ls -l "$dir"
