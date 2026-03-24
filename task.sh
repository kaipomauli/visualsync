#!/bin/sh
cd /home/hice1/gbatungwanayo3/Projects/visualsync || exit
python3 preprocess/run_dino_sam2.py \
    --workdir ~/scratch/ProjectsData/visualSync/Ryker \
    --output-dir gsam2 \
    --input-dir gpt_video \
    --sam2-checkpoint preprocess/pretrained/sam2.1_hiera_large.pt