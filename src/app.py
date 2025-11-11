# src/app.py - Main application for Mission Vanaspati (Refactored)
import streamlit as st
import json
from pathlib import Path
from PIL import Image
import sys

# --- FIX FOR IMPORT ERROR ---
# Get the directory of the current script (which is /src)
SCRIPT_DIR = Path(__file__).parent
# Add this directory to the Python path so it can find predictor.py
sys.path.append(str(SCRIPT_DIR))
# ----------------------------

# Import the new Predictor class
try:
    from predictor import Predictor
except ImportError:
    st.error("Error: Could not find predictor.py. Ensure it's in the src folder.")
    sys.exit(1)

# --- CONFIGURATION (Corrected Paths) ---
try:
    # Get the root directory (one level up from /src)
    ROOT_DIR = SCRIPT_DIR.parent
    
    # Build paths relative to the ROOT_DIR
    MODEL_PATH = ROOT_DIR / 'models' / 'plant_classifier_final.pth'
    CLASS_MAPPING_PATH = ROOT_DIR / 'models' / 'class_mapping.json'
    KNOWLEDGE_BASE_PATH = ROOT_DIR / 'remedies.json'
    
    # Verify files exist
    if not MODEL_PATH.exists():
        st.error(f"Error: Model file not found at {MODEL_PATH}")
        sys.exit(1)
    if not CLASS_MAPPING_PATH.exists():
        st.error(f"Error: Class mapping not found at {CLASS_MAPPING_PATH}")
        sys.exit(1)

except Exception as e:
    st.error(f"Error setting up paths: {e}")
    sys.exit(1)


# --- RESOURCE LOADING (Simplified) ---

# Use st.cache_resource to load the predictor only once
@st.cache_resource
def load_predictor_and_remedies():
    """Load the predictor and knowledge base."""
    predictor = Predictor(MODEL_PATH, CLASS_MAPPING_PATH)
    
    if not KNOWLEDGE_BASE_PATH.exists():
        st.warning("Warning: remedies.json not found. App will only show predictions.")
        knowledge_base = {}
    else:
        with open(KNOWLEDGE_BASE_PATH, 'r') as f:
            knowledge_base = json.load(f)
            
    return predictor, knowledge_base

# --- MAIN STREAMLIT APP ---
def main():
    st.set_page_config(page_title="Mission Vanaspati", layout="wide")
    st.title("Mission Vanaspati: Plant Disease Detector")
    
    # Load resources
    try:
        predictor, knowledge_base = load_predictor_and_remedies()
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        st.stop()

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
                    
                    # --- PREDICTION (Simplified) ---
                    # Use the predictor class
                    class_name, confidence = predictor.predict(image)
                    
                    st.success(f"**Prediction:** {class_name}")
                    st.info(f"**Confidence:** {confidence * 100:.2f}%")
                    
                    # --- Display Remedy ---
                    if class_name in knowledge_base:
                        info = knowledge_base[class_name]
                        st.subheader("Description")
                        st.write(info['description'])
                        st.subheader("Recommended Treatment")
                        if 'remedies' in info and info['remedies']:
                            for step in info['remedies']:
                                st.write(f"- {step}")
                        else:
                            st.write("No specific treatment steps found in the knowledge base.")
                    else:
                        st.warning("No treatment information found for this class.")
                        
if __name__ == "__main__":
    main()