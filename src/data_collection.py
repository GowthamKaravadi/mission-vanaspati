import os
import kaggle
from pathlib import Path

def download_plantvillage_dataset():
    data_dir = Path('data')
dataset_path = data_dir / 'PlantVillage'

if dataset_path.exists() and any(dataset_path.iterdir()):
    print(f"✅ Dataset already found at: {dataset_path}")
else:
    print(" Downloading PlantVillage Dataset...")
    data_dir.mkdir(exist_ok=True)
    
    try:
        kaggle.api.dataset_download_files(
            'emmarex/plantdisease',
            path=data_dir,
            unzip=True

        )
        print("✅ Dataset downloaded and extracted successfully!")

        dataset_path = data_dir / 'PlantVillage'
        if dataset_path.exists():
            print(f"📂 Dataset is available at: {dataset_path}")

            jpg_files = list(dataset_path.rglob('*.jpg'))
            png_files = list(dataset_path.rglob('*.png'))
            image_count = len(jpg_files) + len(png_files)

            print(f"🖼️ Total images found: {image_count}")


        else:
            print("❌ Dataset extraction failed or path not found.")

    
    except Exception as e:
        print(f"❌ An error occurred while downloading the dataset: {e}")


if __name__ == "__main__":
    download_plantvillage_dataset()
