import sys
import json
from pathlib import Path

import torch
from PIL import Image

from config import active_config as cfg
from src.core.model import load_model
from src.core.dataset import get_val_transforms


def load_class_mapping(path: Path):
    with open(path, "r") as f:
        mapping = json.load(f)
    return {v: k for k, v in mapping.items()}


def preprocess(image_path: Path):
    transforms = get_val_transforms(cfg.IMAGE_SIZE)
    image = Image.open(image_path).convert("RGB")
    tensor = transforms(image).unsqueeze(0)
    return tensor


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m src.inference <image_path>")
        sys.exit(1)

    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"File not found: {image_path}")
        sys.exit(1)

    device = torch.device(cfg.DEVICE)
    model = load_model(cfg.MODEL_SAVE_PATH, device=device.type, for_inference=True)
    idx_to_class = load_class_mapping(cfg.CLASS_MAPPING_PATH)

    tensor = preprocess(image_path).to(device)
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)
        conf, idx = probs.max(dim=1)

    class_name = idx_to_class.get(idx.item(), "Unknown")
    print(f"Prediction: {class_name}")
    print(f"Confidence: {conf.item()*100:.2f}%")


if __name__ == "__main__":
    main()