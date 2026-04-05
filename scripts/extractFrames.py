"""
extract_frames.py
-----------------
Extract frames from a video file using ffmpeg (with CUDA GPU acceleration).
 
Usage examples:
  # Extract every frame
  python extract_frames.py video.mp4
 
  # Extract at 1 fps (one frame per second)
  python extract_frames.py video.mp4 --fps 1
 
  # Extract at 5 fps into a specific folder
  python extract_frames.py video.mp4 --fps 5 --out frames/
 
  # Extract frames between t=10s and t=20s at 2 fps
  python extract_frames.py video.mp4 --fps 2 --start 10 --end 20
 
  # Extract as PNG instead of JPG, with quality control
  python extract_frames.py video.mp4 --fps 1 --fmt png
 
  # Extract every Nth frame (e.g. every 30th frame)
  python extract_frames.py video.mp4 --every 30
 
  # Disable GPU acceleration (fallback to CPU)
  python extract_frames.py video.mp4 --no-cuda
"""
 
import argparse
import os
import subprocess
import sys
import json
import shutil
 
 
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg not found on PATH.", file=sys.stderr)
        sys.exit(1)
 
 
def check_cuda() -> bool:
    """Return True if ffmpeg was built with CUDA support and a GPU is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-hwaccels"],
            capture_output=True, text=True
        )
        return "cuda" in result.stdout.lower() or "cuda" in result.stderr.lower()
    except Exception:
        return False
 
 
def get_video_info(video_path: str) -> dict:
    """Return basic video info via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,nb_frames",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
 
    stream = data.get("streams", [{}])[0]
    fmt = data.get("format", {})
 
    # Parse fractional frame rate e.g. "30000/1001"
    avg_fps_str = stream.get("avg_frame_rate", "0/1")
    num, den = avg_fps_str.split("/")
    avg_fps = float(num) / float(den) if float(den) != 0 else 0.0
 
    return {
        "width": int(stream.get("width", 0)),
        "height": int(stream.get("height", 0)),
        "fps": avg_fps,
        "duration": float(fmt.get("duration", 0)),
        "n_frames": stream.get("nb_frames", "unknown"),
    }
 
 
def extract_frames(
        video_path: str,
        out_dir: str = None,
        fps: float = None,
        every_n: int = None,
        start_s: float = None,
        end_s: float = None,
        fmt: str = "jpg",
        quality: int = 2,  # jpg: 2-31 (lower=better), png: 0-9
        scale_w: int = None,  # resize width  (keeps aspect if only one given)
        scale_h: int = None,  # resize height
        use_cuda: bool = True,
        verbose: bool = True,
        pattern: str = "frame_%06d",
):
    """
    Extract frames from video_path.
 
    Parameters
    ----------
    video_path : path to input video
    out_dir    : output folder (created if missing); default = <video_name>_frames/
    fps        : output frame rate (e.g. 1 = one frame per second)
    every_n    : keep every Nth frame from the native frame rate
    start_s    : start time in seconds
    end_s      : end time in seconds
    fmt        : 'jpg' or 'png'
    quality    : jpg quality 2-31 (2=best), png compression 0-9
    scale_w/h  : resize output frames
    use_cuda   : use CUDA GPU acceleration (falls back to CPU if unavailable)
    verbose    : print ffmpeg command
    """
    check_ffmpeg()
 
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
 
    # Detect CUDA availability
    cuda_available = use_cuda and check_cuda()
    if verbose:
        print(f"CUDA acceleration: {'enabled' if cuda_available else 'disabled'}")
 
    # Default output dir
    if out_dir is None:
        base = os.path.splitext(os.path.basename(video_path))[0]
        out_dir = f"{base}_frames"
    os.makedirs(out_dir, exist_ok=True)
 
    info = get_video_info(video_path)
    if verbose:
        print(f"Video:    {video_path}")
        print(f"Size:     {info['width']}x{info['height']}")
        print(f"FPS:      {info['fps']:.3f}")
        print(f"Duration: {info['duration']:.2f}s")
        print(f"Frames:   {info['n_frames']}")
        print(f"Output:   {out_dir}/")
        print()
 
    # ── Build ffmpeg command ──────────────────────────────────────────
    cmd = ["ffmpeg", "-y"]
 
    # CUDA hardware decoding — must come before -i
    if cuda_available:
        cmd += ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]
 
    # Seek to start (input-side seek = fast)
    if start_s is not None:
        cmd += ["-ss", str(start_s)]
 
    cmd += ["-i", video_path]
 
    # End time (output-side)
    if end_s is not None:
        duration = end_s - (start_s or 0)
        cmd += ["-t", str(duration)]
 
    # ── Video filters ─────────────────────────────────────────────────
    vf_parts = []
 
    if cuda_available:
        # When frames are in GPU memory we must download before CPU filters
        # hwdownload + format=nv12 brings frames back to CPU-accessible memory
        vf_parts.append("hwdownload")
        vf_parts.append("format=nv12")
 
    if every_n is not None:
        vf_parts.append(f"select=not(mod(n\\,{every_n}))")
        cmd += ["-vsync", "vfr"]
 
    if fps is not None:
        vf_parts.append(f"fps={fps}")
 
    if scale_w or scale_h:
        w = scale_w or -1
        h = scale_h or -1
        if cuda_available:
            # scale_cuda keeps scaling on GPU (before hwdownload)
            # Insert before hwdownload in the filter chain
            vf_parts.insert(0, f"scale_cuda={w}:{h}")
        else:
            vf_parts.append(f"scale={w}:{h}")
 
    if vf_parts:
        cmd += ["-vf", ",".join(vf_parts)]
 
    # Audio: none
    cmd += ["-an"]
 
    # Format-specific quality
    if fmt == "jpg":
        cmd += ["-q:v", str(quality)]
    elif fmt == "png":
        cmd += ["-compression_level", str(quality)]
 
    # Output pattern: frame_000001.jpg etc.
    out_pattern = os.path.join(out_dir, f"{pattern}.{fmt}")
    cmd.append(out_pattern)
 
    if verbose:
        print("+", " ".join(cmd))
        print()
 
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        if cuda_available:
            print("\nCUDA extraction failed, retrying with CPU...", file=sys.stderr)
            return extract_frames(
                video_path=video_path,
                out_dir=out_dir,
                fps=fps,
                every_n=every_n,
                start_s=start_s,
                end_s=end_s,
                fmt=fmt,
                quality=quality,
                scale_w=scale_w,
                scale_h=scale_h,
                use_cuda=False,  # fallback
                verbose=verbose,
                pattern=pattern
            )
        raise
 
    # Count output files
    frames = sorted(f for f in os.listdir(out_dir) if f.endswith(f".{fmt}"))
    print(f"\nExtracted {len(frames)} frames → {out_dir}/")
    return out_dir, frames
 
 
# ── CLI ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Extract frames from a video.")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("--out", "-o", help="Output directory")
    parser.add_argument("--fps", "-f", type=float, help="Output frames per second")
    parser.add_argument("--every", "-e", type=int, help="Keep every Nth frame")
    parser.add_argument("--start", "-s", type=float, help="Start time in seconds")
    parser.add_argument("--end", "-E", type=float, help="End time in seconds")
    parser.add_argument("--fmt", default="jpg", choices=["jpg", "png"],
                        help="Output image format (default: jpg)")
    parser.add_argument("--quality", "-q", type=int, default=2,
                        help="Quality: jpg 2-31 lower=better (default 2), png 0-9")
    parser.add_argument("--width", type=int, help="Scale output width")
    parser.add_argument("--height", type=int, help="Scale output height")
    parser.add_argument("--pattern", "-p", default="frame_%06d",
                        help="Frame filename pattern with printf placeholder "
                             "(default: 'frame_%%06d'). "
                             "Examples: 'rgb_%%06d', 'cam1_%%04d'")
    parser.add_argument("--no-cuda", action="store_true", help="Disable CUDA GPU acceleration")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()
 
    extract_frames(
        video_path=args.video,
        out_dir=args.out,
        fps=args.fps,
        every_n=args.every,
        start_s=args.start,
        end_s=args.end,
        fmt=args.fmt,
        quality=args.quality,
        scale_w=args.width,
        scale_h=args.height,
        use_cuda=not args.no_cuda,
        verbose=not args.quiet,
        pattern=args.pattern,
    )
 
 

if __name__ == "__main__":
    #Arguments: "~/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/prep0.mp4" --out "~/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/rgb" --fps 60
    main()