# debug_explore.py - Let's find out why the script is exiting

# Import everything we need
import os
import sys
from pathlib import Path
import random

print("🚀 Script started successfully!")

def debug_dataset():
    print("🔍 Step 1: Checking if we can find the dataset...")
    
    # Let's check what's in our current directory first
    current_dir = Path('.')
    print(f"📁 Current directory: {current_dir.absolute()}")
    
    print("\n📂 Files in current directory:")
    for item in current_dir.iterdir():
        print(f"   {item.name}")
    
    print("\n🔍 Step 2: Looking for data folder...")
    dataset_path = Path('data/PlantVillage')
    print(f"📁 Looking for: {dataset_path.absolute()}")
    
    # Check if the path exists
    if dataset_path.exists():
        print("✅ Data folder exists!")
    else:
        print("❌ Data folder not found!")
        # Let's see what's actually in the data folder
        data_parent = Path('data')
        if data_parent.exists():
            print("📂 But data folder exists, here's what's inside:")
            for item in data_parent.iterdir():
                print(f"   {item.name}")
        return
    
    print("\n🔍 Step 3: Checking dataset structure...")
    
    # List all items in the PlantVillage folder
    items = list(dataset_path.iterdir())
    print(f"📊 Found {len(items)} items in PlantVillage folder")
    
    # Show first 10 items
    for i, item in enumerate(items[:10]):
        print(f"   {i+1}. {item.name} - {'Folder' if item.is_dir() else 'File'}")
    
    # Count how many are folders vs files
    folders = [item for item in items if item.is_dir()]
    files = [item for item in items if item.is_file()]
    
    print(f"\n📊 Breakdown: {len(folders)} folders, {len(files)} files")
    
    # If we have folders, show what's in the first one
    if folders:
        first_folder = folders[0]
        print(f"\n🔍 Looking inside first folder: {first_folder.name}")
        
        folder_items = list(first_folder.iterdir())
        print(f"   Contains {len(folder_items)} items")
        
        # Show first 5 items in this folder
        for i, item in enumerate(folder_items[:5]):
            print(f"      {i+1}. {item.name}")
    
    print("\n🎉 Debug completed!")

# Add try-catch to see any errors
try:
    debug_dataset()
    print("\n✅ Script finished successfully!")
except Exception as e:
    print(f"❌ Script crashed with error: {e}")
    print("Let's figure out what went wrong...")

# Keep the window open
input("\nPress Enter to exit...")