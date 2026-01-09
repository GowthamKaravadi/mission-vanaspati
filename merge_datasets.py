"""
Dataset Merger for Mission Vanaspati
=====================================
Merges all datasets into data/MergedDataset folder.

Run: python merge_datasets.py
"""

import os
import shutil
import zipfile
import urllib.request
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data")
MERGED_DIR = DATA_DIR / "MergedDataset"
DOWNLOAD_DIR = DATA_DIR / "downloads"

# Standardize class names to Plant___Disease format
CLASS_NAME_MAPPING = {
    # PlantVillage naming fixes
    "Pepper__bell___Bacterial_spot": "Pepper_bell___Bacterial_spot",
    "Pepper__bell___healthy": "Pepper_bell___healthy",
    "Tomato__Target_Spot": "Tomato___Target_Spot",
    "Tomato__Tomato_mosaic_virus": "Tomato___Tomato_mosaic_virus",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato_Bacterial_spot": "Tomato___Bacterial_spot",
    "Tomato_Early_blight": "Tomato___Early_blight",
    "Tomato_healthy": "Tomato___healthy",
    "Tomato_Late_blight": "Tomato___Late_blight",
    "Tomato_Leaf_Mold": "Tomato___Leaf_Mold",
    "Tomato_Septoria_leaf_spot": "Tomato___Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Tomato___Spider_mites_Two-spotted_spider_mite",
    "Pepper,_bell___Bacterial_spot": "Pepper_bell___Bacterial_spot",
    "Pepper,_bell___healthy": "Pepper_bell___healthy",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Tomato___Spider_mites_Two-spotted_spider_mite",
    "Cherry_(including_sour)___healthy": "Cherry___healthy",
    "Cherry_(including_sour)___Powdery_mildew": "Cherry___Powdery_mildew",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn___Cercospora_leaf_spot_Gray_leaf_spot",
    "Corn_(maize)___Common_rust_": "Corn___Common_rust",
    "Corn_(maize)___healthy": "Corn___healthy",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn___Northern_Leaf_Blight",
    "Grape___Esca_(Black_Measles)": "Grape___Esca_Black_Measles",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Grape___Leaf_blight_Isariopsis_Leaf_Spot",
    "Orange___Haunglongbing_(Citrus_greening)": "Orange___Haunglongbing_Citrus_greening",
    
    # PlantDoc naming
    "Apple Scab Leaf": "Apple___Apple_scab",
    "Apple leaf": "Apple___healthy",
    "Apple rust leaf": "Apple___Cedar_apple_rust",
    "Bell_pepper leaf spot": "Pepper_bell___Bacterial_spot",
    "Bell_pepper leaf": "Pepper_bell___healthy",
    "Blueberry leaf": "Blueberry___healthy",
    "Cherry leaf": "Cherry___healthy",
    "Corn Gray leaf spot": "Corn___Cercospora_leaf_spot_Gray_leaf_spot",
    "Corn leaf blight": "Corn___Northern_Leaf_Blight",
    "Corn rust leaf": "Corn___Common_rust",
    "Peach leaf": "Peach___healthy",
    "Potato leaf early blight": "Potato___Early_blight",
    "Potato leaf late blight": "Potato___Late_blight",
    "Potato leaf": "Potato___healthy",
    "Raspberry leaf": "Raspberry___healthy",
    "Soyabean leaf": "Soybean___healthy",
    "Soybean leaf": "Soybean___healthy",
    "Squash Powdery mildew leaf": "Squash___Powdery_mildew",
    "Strawberry leaf": "Strawberry___healthy",
    "Tomato Early blight leaf": "Tomato___Early_blight",
    "Tomato Septoria leaf spot": "Tomato___Septoria_leaf_spot",
    "Tomato leaf bacterial spot": "Tomato___Bacterial_spot",
    "Tomato leaf late blight": "Tomato___Late_blight",
    "Tomato leaf mosaic virus": "Tomato___Tomato_mosaic_virus",
    "Tomato leaf yellow virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato leaf": "Tomato___healthy",
    "Tomato mold leaf": "Tomato___Leaf_Mold",
    "Tomato two spotted spider mites leaf": "Tomato___Spider_mites_Two-spotted_spider_mite",
    "grape leaf black rot": "Grape___Black_rot",
    "grape leaf": "Grape___healthy",
    
    # Rice naming
    "Bacterial leaf blight": "Rice___Bacterial_leaf_blight",
    "Brown spot": "Rice___Brown_spot",
    "Leaf smut": "Rice___Leaf_smut",
    "Hispa": "Rice___Hispa",
    "Healthy": "Rice___healthy",
}


def standardize_name(name):
    if name in CLASS_NAME_MAPPING:
        return CLASS_NAME_MAPPING[name]
    
    # Clean up
    name = name.strip().replace(",", "").replace("(", "").replace(")", "")
    name = name.replace(" ", "_").replace("__", "_")
    
    # Ensure Plant___Disease format
    if "___" not in name and "_" in name:
        parts = name.split("_")
        if len(parts) >= 2:
            name = f"{parts[0]}___{'_'.join(parts[1:])}"
    
    return name


def copy_images(src_dir, dest_dir, class_name):
    if not src_dir.exists():
        return 0
    
    std_name = standardize_name(class_name)
    target = dest_dir / std_name
    target.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for img in src_dir.iterdir():
        if img.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            dest = target / f"{src_dir.parent.name}_{img.name}"
            if dest.exists():
                dest = target / f"{src_dir.parent.name}_{count}_{img.name}"
            shutil.copy2(img, dest)
            count += 1
    return count


def merge_folder(source_dir, label=""):
    if not source_dir.exists():
        return 0
    
    print(f"  Merging {label or source_dir.name}...")
    total = 0
    for class_dir in source_dir.iterdir():
        if class_dir.is_dir():
            count = copy_images(class_dir, MERGED_DIR, class_dir.name)
            total += count
    return total


def download_plantdoc():
    print("\nDownloading PlantDoc dataset...")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DOWNLOAD_DIR / "PlantDoc.zip"
    
    if not zip_path.exists():
        url = "https://github.com/pratikkayal/PlantDoc-Dataset/archive/refs/heads/master.zip"
        try:
            print("  Downloading... (this may take a few minutes)")
            urllib.request.urlretrieve(url, zip_path)
            print("  Download complete!")
        except Exception as e:
            print(f"  Download failed: {e}")
            return None
    
    extract_dir = DOWNLOAD_DIR / "PlantDoc_extracted"
    if not extract_dir.exists():
        print("  Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
    
    # Find dataset folder
    for p in extract_dir.rglob("train"):
        if p.is_dir():
            return p.parent
    return None


def main():
    print("="*50)
    print("Merging All Datasets")
    print("="*50)
    
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    
    # Merge existing datasets
    print("\nStep 1: Merging existing datasets...")
    total += merge_folder(DATA_DIR / "PlantVillage", "PlantVillage")
    total += merge_folder(DATA_DIR / "NewPlantDiseases" / "train", "NewPlantDiseases/train")
    total += merge_folder(DATA_DIR / "NewPlantDiseases" / "valid", "NewPlantDiseases/valid")
    total += merge_folder(DATA_DIR / "NewPlantDiseases" / "test", "NewPlantDiseases/test")
    
    # Download and merge PlantDoc
    print("\nStep 2: PlantDoc dataset...")
    plantdoc = download_plantdoc()
    if plantdoc:
        total += merge_folder(plantdoc / "train", "PlantDoc/train")
        total += merge_folder(plantdoc / "test", "PlantDoc/test")
    
    # Check for Rice dataset
    print("\nStep 3: Rice Leaf dataset...")
    rice_paths = [
        DOWNLOAD_DIR / "rice-leaf-diseases",
        DATA_DIR / "Rice",
        DATA_DIR / "rice-leaf-diseases",
    ]
    rice_found = False
    for rp in rice_paths:
        if rp.exists():
            total += merge_folder(rp, "Rice Leaf Diseases")
            rice_found = True
            break
    
    if not rice_found:
        print("  Rice dataset not found. To add it:")
        print("  1. Download from: https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases")
        print("  2. Extract to: data/Rice/")
        print("  3. Run this script again")
    
    # Summary
    print("\n" + "="*50)
    print("DONE!")
    print("="*50)
    
    classes = [d.name for d in MERGED_DIR.iterdir() if d.is_dir()]
    images = sum(len(list((MERGED_DIR / c).iterdir())) for c in classes)
    
    print(f"Location: {MERGED_DIR.absolute()}")
    print(f"Classes: {len(classes)}")
    print(f"Total Images: {images:,}")
    print("\nYou can now run: python src/train.py")


if __name__ == "__main__":
    main()
