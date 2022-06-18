#!/bin/sh


#SBATCH --partition=wr14         # partition (queue)
#SBATCH --tasks=32               # number of tasks per node
#SBATCH --mem=4G                # memory per node in MB <180G> (different units with suffix K|M|G|T)
#SBATCH --time=12:00:00           # total runtime of job allocation (format D-HH:MM:SS; first parts optional)
#SBATCH --output=slurm.%j.out    # filename for STDOUT (%N: nodename, %j: job-ID)
#SBATCH --error=slurm.%j.err     # filename for STDERR


python3 /scratch/vkalag2s/ASIRE-code-base/scripts/clear_sky_filter.py

