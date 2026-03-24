#!/bin/sh
cd /home/hice1/gbatungwanayo3/Projects/visualsync || exit
python3 Tracking-Anything-with-DEVA/evaluation/eval_with_detections.py\
    --workdir ~/scratch/ProjectsData/visualSync/Ryker \
    --output-dir deva \
    --input-dir gsam2 \
    --dataset demo \
    --temporal_setting semionline \
    --detection_every 2 \
    --num_voting_frames 2\
    --amp



