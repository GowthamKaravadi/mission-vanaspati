# Import the tools we need
import os
from pathlib import Path

# This function will check our downloaded dataset
def verify_dataset():
    # Create the path to where our dataset should be
    dataset_path = Path('data/PlantVillage')
    
    # Check if the dataset folder exists
    if not dataset_path.exists():
        print("❌ Dataset not found! Please download first.")
        return False  # 'False' means the function failed
    
    print("📁 Dataset structure:")
    
    # 'iterdir()' gets all items in the dataset folder
    # 'for folder in dataset_path.iterdir():' means:
    # "For each item in the dataset folder, call it 'folder' and do something with it"
    for folder in dataset_path.iterdir():
        # 'is_dir()' checks if this item is a folder (not a file)
        if folder.is_dir():
            # Look for all .jpg and .png files in this folder
            jpg_images = list(folder.glob('*.jpg'))  # Find JPG files
            png_images = list(folder.glob('*.png'))  # Find PNG files
            all_images = jpg_images + png_images     # Combine both lists
            
            # Print the folder name and how many images it contains
            print(f"  {folder.name}: {len(all_images)} images")
    
    return True  # 'True' means everything worked

# If we run this file directly, run the verify_dataset function
if __name__ == "__main__":
    verify_dataset()