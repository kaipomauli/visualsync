#!/bin/sh
cd /home/hice1/gbatungwanayo3/Projects/visualsync || exit
python3 scripts/combineImagesInFolder.py \
    --input_dir ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/deva/Visualizations \
    --output_path ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/deva/Visualizations/scene1_cam1_Deva_vis.mp4 \
    --fps 30

python3 scripts/combineImagesInFolder.py \
    --input_dir ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam2/deva/Visualizations \
    --output_path ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam2/deva/Visualizations/scene1_cam2_Deva_vis.mp4 \
    --fps 30

python3 scripts/combineImagesInFolder.py \
    --input_dir ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam3/deva/Visualizations \
    --output_path ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam3/deva/Visualizations/scene1_cam3_Deva_vis.mp4 \
    --fps 30

python3 scripts/combineImagesInFolder.py \
    --input_dir ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam4/deva/Visualizations \
    --output_path ~/scratch/ProjectsData/visualSync/Ryker/scene1_cam4/deva/Visualizations/scene1_cam4_Deva_vis.mp4 \
    --fps 30

