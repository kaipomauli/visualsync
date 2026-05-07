from ultralytics.models.sam import SAM3VideoSemanticPredictor
from pathlib import Path
import cv2
import numpy as np
import json

overrides = dict(conf=0.5, task="segment", mode="predict", imgsz=644,
                 model="/storage/ice-shared/cs8903s06/sam3.pt",
                 half=True, save=False, vid_stride=2)

predictor = SAM3VideoSemanticPredictor(overrides=overrides)
save_dir = Path("/home/hice1/gbatungwanayo3/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/sam3")
mask_dir = save_dir / "background_masks"  # <-- this is what MASt3R needs
rgb_dir  = save_dir / "rgb"
save_dir.mkdir(parents=True, exist_ok=True)
mask_dir.mkdir(parents=True, exist_ok=True)
rgb_dir.mkdir(parents=True, exist_ok=True)

results = predictor(
    source="/home/hice1/gbatungwanayo3/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/prep0.mp4",
    text=["dog"],
    stream=True
)

annotations = []

for i, r in enumerate(results):
    frame_name = f"frame_{i:05d}"

    # Save raw RGB frame (needed by MASt3R)
    cv2.imwrite(str(rgb_dir / f"{frame_name}.jpg"), r.orig_img)

    # Build background mask: start with all 1s (everything is background)
    H, W = r.orig_img.shape[:2]
    bg_mask = np.ones((H, W), dtype=np.uint8)  # 1 = background, safe to match

    frame_data = {"frame_index": i, "orig_shape": [H, W], "detections": []}

    if r.masks is not None and len(r.masks) > 0:
        for n in range(len(r.masks)):
            # Get binary mask for this detection at original resolution
            dog_mask = r.masks.data[n].cpu().numpy().astype(bool)  # (H, W)

            # Zero out dog pixels in background mask
            bg_mask[dog_mask] = 0

            # Save detection info
            if r.boxes is not None and n < len(r.boxes):
                box   = r.boxes.xyxy[n].cpu().numpy()
                conf  = float(r.boxes.conf[n].cpu())
                cls   = int(r.boxes.cls[n].cpu())
                ys, xs = np.where(dog_mask)
                frame_data["detections"].append({
                    "class_id":     cls,
                    "class_name":   r.names[cls],
                    "confidence":   round(conf, 4),
                    "bbox_xyxy":    [round(float(v), 2) for v in box],
                    "mask_area_px": int(dog_mask.sum()),
                    "mask_centroid": [float(xs.mean()), float(ys.mean())] if len(xs) > 0 else None,
                })

    # Save background mask as PNG (0 = dog, 255 = background for easy viewing)
    cv2.imwrite(str(mask_dir / f"{frame_name}.png"), bg_mask * 255)

    annotations.append(frame_data)

with open(save_dir / "annotations.json", "w") as f:
    json.dump(annotations, f, indent=2)

print(f"Saved {len(annotations)} frames")
print(f"  RGB frames  → {rgb_dir}")
print(f"  BG masks    → {mask_dir}  (white=background, black=dog)")
print(f"  Annotations → {save_dir}/annotations.json")