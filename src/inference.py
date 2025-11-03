# inference.py - Test your trained model on a single image
import torch
import json
from pathlib import Path
from PIL import Image
from torchvision import transforms
import sys

# Import the model class from your training script
try:
    from plant_classifier import DiseaseClassificationModel
except ImportError:
    print("Error: Could not find plant_classifier.py")
    print("Please make sure this script is in the same folder as plant_classifier.py")
    sys.exit(1)

print("PLANT DISEASE INFERENCE SCRIPT")
print("=" * 40)

# --- CONFIGURATION ---
MODEL_PATH = Path('models/plant_classifier_final.pth')
CLASS_MAPPING_PATH = Path('models/class_mapping.json')
# ---------------------

def load_model_and_classes():
    """Load the trained model and class mapping."""
    
    # 1. Check if files exist
    if not MODEL_PATH.exists():
        print(f"Error: Model file not found at {MODEL_PATH}")
        print("Please run model_trainer_latest.py to train and save the model.")
        return None, None, None
        
    if not CLASS_MAPPING_PATH.exists():
        print(f"Error: Class mapping not found at {CLASS_MAPPING_PATH}")
        print("Please ensure model_trainer_latest.py saves 'class_mapping.json'.")
        return None, None, None

    # 2. Load class mapping
    print(f"Loading class mapping from {CLASS_MAPPING_PATH}...")
    with open(CLASS_MAPPING_PATH, 'r') as f:
        class_mapping_from_file = json.load(f) # This is {"ClassName": 0}
        # JSON saves keys as strings, convert them back to integers
        class_mapping = {v: k for k, v in class_mapping_from_file.items()}
    
    num_classes = len(class_mapping)
    print(f"Found {num_classes} classes.")

    # 3. Set up the device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using compute device: {device}")

    # 4. Initialize the model (using the ResNet50 version)
    print("Initializing model architecture...")
    model = DiseaseClassificationModel(num_classes).to(device)
    
    # 5. Load the saved weights
    print(f"Loading trained weights from {MODEL_PATH}...")
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()  # Set model to evaluation mode (very important!)
    
    print("Model loaded successfully!")
    
    return model, class_mapping, device

def preprocess_image(image_path: Path):
    """Load and preprocess a single image for inference."""
    
    # These transforms must MATCH the validation transforms
    inference_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    try:
        image = Image.open(image_path).convert('RGB')
        # Apply transforms and add a "batch" dimension (B, C, H, W)
        return inference_transform(image).unsqueeze(0)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def predict_image(model, image_tensor, device, class_mapping):
    """Run inference on a single preprocessed image tensor."""
    
    with torch.no_grad(): # Disable gradient calculation
        # Move tensor to the correct device
        image_tensor = image_tensor.to(device)
        
        # Get model output (logits)
        outputs = model(image_tensor)
        
        # Apply Softmax to get probabilities
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        
        # Get the top probability and its index
        top_prob, top_idx = torch.max(probabilities, 1)
        
        # Convert from tensor to Python values
        pred_index = top_idx.item()
        confidence = top_prob.item()
        
        # Get the class name
        class_name = class_mapping.get(pred_index, "Unknown Class")
        
        return class_name, confidence

# --- Main execution ---
if __name__ == "__main__":
    # 1. Check for command-line argument
    if len(sys.argv) != 2:
        print("Usage: python inference.py \"<path_to_your_image.jpg>\"")
        sys.exit(1)
        
    image_file = Path(sys.argv[1])
    
    if not image_file.exists():
        print(f"Error: Image file not found at {image_file}")
        sys.exit(1)

    # 2. Load the model
    model, class_mapping, device = load_model_and_classes()
    
    if model is None:
        sys.exit(1) # Exit if model loading failed

    # 3. Process the image
    print(f"\nProcessing image: {image_file.name}...")
    image_tensor = preprocess_image(image_file)
    
    if image_tensor is None:
        sys.exit(1) # Exit if image processing failed

    # 4. Get prediction
    print("Running prediction...")
    class_name, confidence = predict_image(model, image_tensor, device, class_mapping)
    
    # 5. Show the result
    print("\n" + "=" * 40)
    print("PREDICTION COMPLETE")
    print(f"   Disease: {class_name}")
    print(f"   Confidence: {confidence * 100:.2f}%")
    print("=" * 40)