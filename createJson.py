import json

tags = {
    "dynamic": ["person", "dog"],
    "reasoning": "manually specified"
}
filepaths=["Data/Ryker/scene1_cam1/gpt_video/tags.json","Data/Ryker/scene1_cam2/gpt_video/tags.json","Data/Ryker/scene1_cam3/gpt_video/tags.json","Data/Ryker/scene1_cam3/gpt_video/tags.json"]
for filepath in filepaths:
    with open(filepath, "w") as f:
        json.dump(tags, f)