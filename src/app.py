# app.py - Main application for Mission Vanaspati
import streamlit as st
import torch
import json
from pathlib import Path
from PIL import Image
from torchvision import transforms
import sys

# We need to make sure the app can find plant_classifier.py
try:
    from plant_classifier import DiseaseClassificationModel
except ImportError:
    st.error("Error: Could not find plant_classifier.py. Ensure it's in the same folder.")
    sys.exit(1)

# --- CONFIGURATION ---
MODEL_PATH = Path('models/plant_classifier_final.pth')
CLASS_MAPPING_PATH = Path('models/class_mapping.json')
KNOWLEDGE_BASE_PATH = Path('remedies.json')

# --- MODEL LOADING ---

# Use st.cache_resource to load resources only once
@st.cache_resource
def load_resources():
    """Load model, class mapping, and knowledge base."""
    
    if not MODEL_PATH.exists() or not CLASS_MAPPING_PATH.exists():
        st.error("Error: Model or class mapping file not found. Please train the model first.")
        return None, None, None, None
    
    if not KNOWLEDGE_BASE_PATH.exists():
        st.warning("Warning: remedies.json not found. App will only show predictions.")
        knowledge_base = {}
    else:
        with open(KNOWLEDGE_BASE_PATH, 'r') as f:
            knowledge_base = json.load(f)

    # Load class mapping
    with open(CLASS_MAPPING_PATH, 'r') as f:
        # This is {"ClassName": 0}
        class_mapping_from_file = json.load(f)
    
    # Invert the dictionary to be {0: "ClassName"}
    class_mapping = {v: k for k, v in class_mapping_from_file.items()}
    num_classes = len(class_mapping)

    # Set up the device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Initialize the model
    model = DiseaseClassificationModel(num_classes).to(device)
    
    # Load the saved weights
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()  # Set model to evaluation mode
    
    print("All resources loaded successfully.")
    return model, class_mapping, device, knowledge_base

# --- IMAGE PREPROCESSING ---
def preprocess_image(image_pil: Image):
    """Load and preprocess a single image for inference."""
    
    # These transforms must MATCH the validation transforms
    inference_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Apply transforms and add a "batch" dimension (B, C, H, W)
    return inference_transform(image_pil).unsqueeze(0)

# --- PREDICTION ---
def predict_image(model, image_tensor, device, class_mapping):
    """Run inference on a single preprocessed image tensor."""
    
    with torch.no_grad(): # Disable gradient calculation
        image_tensor = image_tensor.to(device)
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        top_prob, top_idx = torch.max(probabilities, 1)
        
        pred_index = top_idx.item()
        confidence = top_prob.item()
        class_name = class_mapping.get(pred_index, "Unknown Class")
        
        return class_name, confidence

# --- MAIN STREAMLIT APP ---
def main():
    st.set_page_config(page_title="Mission Vanaspati", layout="wide")
    st.title("Mission Vanaspati: King Of Detection")
    
    # Load resources (this will only run once)
    model, class_mapping, device, knowledge_base = load_resources()
    
    if model is None:
        # Stop the app if model loading failed
        return

    st.write("Upload an image of a plant leaf to classify the disease.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')
        
        # Use columns for a cleaner layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption='Uploaded Image', use_column_width=True)
        
        with col2:
            if st.button('Classify Disease'):
                with st.spinner('Analyzing the leaf...'):
                    image_tensor = preprocess_image(image)
                    class_name, confidence = predict_image(model, image_tensor, device, class_mapping)
                    
                    st.success(f"**Prediction:** {class_name}")
                    st.info(f"**Confidence:** {confidence * 100:.2f}%")
                    
                    # --- Display Remedy ---
                    if class_name in knowledge_base:
                        info = knowledge_base[class_name]
                        st.subheader("Description")
                        st.write(info['description'])
                        st.subheader("Recommended Treatment")
                        for step in info['treatment']:
                            st.write(f"- {step}")
                    else:
                        st.warning("No treatment information found for this class.")
                        
if __name__ == "__main__":
    main()