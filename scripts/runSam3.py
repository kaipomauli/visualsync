from ultralytics.models.sam import SAM3VideoSemanticPredictor
from pathlib import Path
import cv2

# Initialize semantic video predictor
overrides = dict(conf=0.6, task="segment", mode="predict", imgsz=644, model="/storage/ice-shared/cs8903s06/sam3.pt", half=True, save=True,vid_stride=2)
predictor = SAM3VideoSemanticPredictor(overrides=overrides)
predictor.save_dir = Path("/home/hice1/gbatungwanayo3/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/sam3")
predictor.save_dir.mkdir(parents=True, exist_ok=True)

# Track concepts using text prompts
results = predictor(source="/home/hice1/gbatungwanayo3/scratch/ProjectsData/visualSync/Ryker/scene1_cam1/CAM1_GX010106.MP4", text=["dog"], stream=True)

# Process results
for i, r in enumerate(results):
    annotated_frame = r.plot()  # numpy BGR array with masks drawn on
    cv2.imwrite(str(predictor.save_dir / f"frame_{i:05d}.jpg"), annotated_frame)