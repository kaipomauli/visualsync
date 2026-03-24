import argparse
import logging
import subprocess
import os

"""
Recombine images from a folder into a video using GPU acceleration with CPU fallback.

Args:
    input_dir:      folder containing images
    output_path:    output video path e.g. 'output/video.mp4'
    fps:            frames per second
    image_pattern:  filename pattern e.g. 'frame_%06d.jpg'
    crf:            quality level (18=high quality, 28=smaller file)
"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("combineImages.log"),  # saves to file
        logging.StreamHandler()                    # still prints to terminal
    ]
)

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', required=True)
parser.add_argument("--output_path", required=True)
parser.add_argument("--fps", default=30)
parser.add_argument("--image_pattern", default="frame_%06d.jpg")
parser.add_argument("--crf", default=18)
args = parser.parse_args()

input_dir    = args.input_dir
output_path  = args.output_path
fps          = args.fps
image_pattern = args.image_pattern
crf          = args.crf

input_pattern = os.path.join(input_dir, image_pattern)

# Log first few files for debugging
files = sorted(os.listdir(input_dir))
logging.info(f"First 3 files: {files[:3]}")
logging.info(f"Pattern used: {input_pattern}")
logging.info(f"Total frames: {len([f for f in files if f.endswith(('.jpg', '.png'))])}")


def run_ffmpeg(cmd, fallback_cmd=None):
    """Run ffmpeg command with optional CPU fallback."""
    logging.info(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        if fallback_cmd:
            logging.warning("GPU encoding failed — falling back to CPU encoding (libx264)")
            logging.warning(f"GPU error was:\n{result.stderr.splitlines()[-1]}")  # just last line

            result = subprocess.run(
                fallback_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                logging.error(f"CPU fallback also failed:\n{result.stderr}")
                raise RuntimeError(f"FFmpeg CPU fallback error: {result.stderr}")

            logging.info(f"Video saved (CPU encoded) to {output_path}")

        else:
            logging.error(f"FFmpeg failed:\n{result.stderr}")
            raise RuntimeError(f"FFmpeg error: {result.stderr}")

    else:
        logging.info(f"Video saved (GPU encoded) to {output_path}")


# GPU command — h264_nvenc
gpu_cmd = [
    "ffmpeg",
    "-y",
    "-framerate", str(fps),
    "-i", input_pattern,
    "-c:v", "h264_nvenc",
    "-preset", "p4",
    "-rc:v", "vbr",
    "-cq", str(crf),
    "-b:v", "0",
    "-pix_fmt", "yuv420p",
    output_path
]

# CPU fallback — libx264
cpu_cmd = [
    "ffmpeg",
    "-y",
    "-framerate", str(fps),
    "-i", input_pattern,
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", str(crf),
    "-pix_fmt", "yuv420p",
    output_path
]

logging.info(f"Recombining frames from {input_dir} → {output_path} at {fps}fps")

try:
    run_ffmpeg(gpu_cmd, fallback_cmd=cpu_cmd)
except FileNotFoundError:
    logging.error("FFmpeg not found — is it installed?")
    raise