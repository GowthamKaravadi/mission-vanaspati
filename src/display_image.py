# display_images.py - Show actual plant disease images
import matplotlib.pyplot as plt
from pathlib import Path
import random
import cv2  # OpenCV for image reading

def display_sample_images():
    print("🖼️ Loading and displaying plant disease images...")
    
    # Path to our dataset
    dataset_path = Path('data/PlantVillage')
    
    # Get all categories
    categories = []
    for folder in dataset_path.iterdir():
        if folder.is_dir():
            images = list(folder.glob('*.jpg')) + list(folder.glob('*.png'))
            if images:  # Only add categories that have images
                categories.append({
                    'name': folder.name,
                    'images': images,
                    'path': folder
                })
    
    print(f"📁 Found {len(categories)} plant disease categories")
    
    # We'll display 2 images from each of the first 4 categories
    categories_to_show = categories[:4]
    
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 4, figsize=(15, 8))
    fig.suptitle('🌱 Plant Disease Samples - Mission Vanaspati', fontsize=16, fontweight='bold')
    
    row = 0
    for i, category in enumerate(categories_to_show):
        # Pick 2 random images from this category
        sample_images = random.sample(category['images'], min(2, len(category['images'])))
        
        for col, image_path in enumerate(sample_images):
            try:
                # Read the image using OpenCV
                # OpenCV reads images in BGR format, we convert to RGB for matplotlib
                image = cv2.imread(str(image_path))
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Display the image
                axes[col, row].imshow(image_rgb)
                axes[col, row].set_title(f"{category['name']}\n{image_path.name}", 
                                       fontsize=9, pad=5)
                axes[col, row].axis('off')  # Hide axes
                
            except Exception as e:
                print(f"❌ Error loading image {image_path}: {e}")
                # Show a blank image with error message
                axes[col, row].text(0.5, 0.5, f"Error\nloading\nimage", 
                                  ha='center', va='center', transform=axes[col, row].transAxes)
                axes[col, row].axis('off')
        
        row += 1
    
    # Adjust layout and display
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    print("✅ Images loaded successfully! Close the image window to continue...")
    plt.show()

def explore_single_category():
    """Show multiple images from one specific category"""
    print("\n🔍 Let's explore one category in detail...")
    
    dataset_path = Path('data/PlantVillage')
    
    # Get a specific category (Tomato diseases are usually interesting)
    tomato_categories = [f for f in dataset_path.iterdir() if f.is_dir() and 'Tomato' in f.name]
    
    if not tomato_categories:
        print("❌ No tomato categories found")
        return
    
    print("Available Tomato categories:")
    for i, category in enumerate(tomato_categories):
        images = list(category.glob('*.jpg')) + list(category.glob('*.png'))
        print(f"  {i+1}. {category.name} - {len(images)} images")
    
    # Pick the first tomato category
    chosen_category = tomato_categories[0]
    images = list(chosen_category.glob('*.jpg')) + list(chosen_category.glob('*.png'))
    
    print(f"\n📸 Showing 6 random images from: {chosen_category.name}")
    
    # Create a grid of images
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    fig.suptitle(f'🌱 {chosen_category.name} - Sample Images', fontsize=14, fontweight='bold')
    
    # Pick 6 random images
    sample_images = random.sample(images, min(6, len(images)))
    
    for i, image_path in enumerate(sample_images):
        row = i // 3
        col = i % 3
        
        try:
            image = cv2.imread(str(image_path))
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            axes[row, col].imshow(image_rgb)
            axes[row, col].set_title(image_path.name, fontsize=8, pad=3)
            axes[row, col].axis('off')
        except Exception as e:
            print(f"Error with image {image_path}: {e}")
            axes[row, col].text(0.5, 0.5, "Error", ha='center', va='center')
            axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    plt.show()

# Main execution
if __name__ == "__main__":
    print("🌿 MISSION VANASPATI - IMAGE EXPLORER")
    print("=" * 50)
    
    try:
        # First show overview of multiple categories
        display_sample_images()
        
        # Then show detailed view of one category
        explore_single_category()
        
        print("\n🎉 Image exploration complete!")
        print("💡 You can now see what the actual plant diseases look like!")
        
    except Exception as e:
        print(f"❌ Error during image display: {e}")
        print("This might be a display backend issue. The images are still there!")
    
    