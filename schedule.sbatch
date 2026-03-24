#!/bin/bash

#SBATCH --job-name=dino_sam2
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --gres=gpu:1
#SBATCH --constraint="HX00"
#SBATCH --mem=64G
#SBATCH --time=3:00:00
#SBATCH --output=./logs/deva_%j.out
#SBATCH --mail-type=END,FAIL

cd $SLURM_SUBMIT_DIR

module load anaconda3
conda activate visualsync
bash task_runDeva.sh