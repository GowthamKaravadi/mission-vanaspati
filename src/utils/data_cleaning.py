from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image

from config import config
from src.core.dataset import PlantDiseaseDataset


def file_hash(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(roots: List[Path]) -> Dict[str, List[Path]]:
    hashes: Dict[str, List[Path]] = {}
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"} and p.is_file():
                try:
                    h = file_hash(p)
                    hashes.setdefault(h, []).append(p)
                except Exception:
                    continue
    return {h: ps for h, ps in hashes.items() if len(ps) > 1}


def remove_duplicates(dupes: Dict[str, List[Path]], keep_first: bool = True) -> List[Path]:
    removed: List[Path] = []
    for paths in dupes.values():
        to_remove = paths[1:] if keep_first else paths[:-1]
        for p in to_remove:
            try:
                p.unlink(missing_ok=True)
                removed.append(p)
            except Exception:
                continue
    return removed


def regenerate_class_mapping(save_path: Path | None = None) -> Path:
    if save_path is None:
        save_path = config.CLASS_MAPPING_PATH
    dataset = PlantDiseaseDataset(
        data_directories=config.get_data_directories(),
        transform=None,
    )
    dataset.save_class_mapping(save_path)
    return save_path


def validate_images(roots: List[Path]) -> List[Path]:
    bad: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"} and p.is_file():
                try:
                    Image.open(p).verify()
                except Exception:
                    bad.append(p)
    return bad


if __name__ == "__main__":
    print("Mission Vanaspati - Data Cleaning")
    roots = config.get_data_directories()
    print(f"Roots: {roots}")

    print("\n1) Validating images...")
    bad = validate_images(roots)
    print(f"Corrupted images: {len(bad)}")

    print("\n2) Finding duplicates (hash-based)...")
    dupes = find_duplicates(roots)
    total_dupes = sum(len(v) for v in dupes.values())
    print(f"Duplicate groups: {len(dupes)} | Total dupes: {total_dupes}")

    if dupes:
        print("\n3) Removing duplicates (keep first)...")
        removed = remove_duplicates(dupes, keep_first=True)
        print(f"Removed: {len(removed)}")

    print("\n4) Regenerating class mapping...")
    out = regenerate_class_mapping()
    print(f"Saved mapping to: {out}")
    print("\nDone.")
