import subprocess

subprocess.run([
    '/home/hice1/gbatungwanayo3/.conda/envs/visualsync/bin/python', 'preprocess/run_dino_sam2.py',
    '--workdir', '~/scratch/ProjectsData',
    '--output-dir', 'gsam2',
    '--input-dir', 'gpt_video',
    '--sam2-checkpoint', './preprocess/pretrained/sam2.1_hiera_large.pt',
])
# subprocess.run(['/home/hice1/gbatungwanayo3/.conda/envs/visualsync/bin/python', 'preprocess/run_gpt.py',
#     '--workdir', 'Data/Ryker',
#     '--sample', '30'])
print('Done')