import streamlit as st
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import active_config as cfg
from src.core.predictor import PlantDiseasePredictor


@st.cache_resource
def load_predictor():
    return PlantDiseasePredictor(
        model_path=cfg.MODEL_SAVE_PATH,
        class_mapping_path=cfg.CLASS_MAPPING_PATH,
        top_k=cfg.TOP_K_PREDICTIONS,
        confidence_threshold=cfg.CONFIDENCE_THRESHOLD,
    )


@st.cache_data
def load_knowledge_base():
    if not cfg.REMEDIES_PATH.exists():
        st.warning("Remedies database not found. Only predictions will be shown.")
        return {}
    
    with open(cfg.REMEDIES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def display_prediction_card(result: dict, knowledge_base: dict):
    
    st.markdown("---")
    
    st.markdown(f"### Prediction: **{result['class_name']}**")
    
    confidence = result['confidence']
    if confidence >= 0.8:
        confidence_color = "green"
    elif confidence >= 0.5:
        confidence_color = "orange"
    else:
        confidence_color = "red"
    
    st.markdown(
        f"**Confidence:** "
        f"<span style='color:{confidence_color};font-size:1.2em;'>"
        f"{confidence:.1%}"
        f"</span>",
        unsafe_allow_html=True
    )
    
    if 'top_k' in result and len(result['top_k']) > 1:
        with st.expander("View Alternative Predictions"):
            for i, pred in enumerate(result['top_k'][1:], 2):
                st.write(f"{i}. **{pred['class_name']}** - {pred['confidence']:.1%}")
    
    st.markdown("---")
    
    class_name = result['class_name']
    
    if class_name in knowledge_base:
        info = knowledge_base[class_name]
        
        st.markdown("### Disease Information")
        
        if 'description' in info and info['description']:
            st.write(info['description'])
        
        if 'remedies' in info and info['remedies']:
            st.markdown("### Recommended Treatment")
            for i, step in enumerate(info['remedies'], 1):
                st.write(f"{i}. {step}")
        
        if 'prevention' in info and info['prevention']:
            with st.expander("Prevention Tips"):
                for tip in info['prevention']:
                    st.write(f"• {tip}")
    else:
        st.info(
            "No treatment information available for this disease in our database. "
            "Please consult a plant pathology expert."
        )


def display_sidebar():
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/4CAF50/FFFFFF?text=Mission+Vanaspati", use_container_width=True)
        
        st.markdown("### About")
        st.write(
            "Mission Vanaspati uses deep learning to identify plant diseases "
            "from leaf images and provides treatment recommendations."
        )
        
        st.markdown("### Model Info")
        st.write(f"**Architecture:** ResNet50 (Transfer Learning)")
        st.write(f"**Classes:** 50 plant diseases")
        st.write(f"**Device:** {cfg.DEVICE.upper()}")
        
        st.markdown("### Supported Plants")
        plants = [
            "Apple", "Blueberry", "Cherry", "Corn",
            "Grape", "Orange", "Peach", "Pepper",
            "Potato", "Strawberry", "Tomato"
        ]
        st.write(", ".join(plants))
        
        st.markdown("---")
        st.caption("Built by Mission Vanaspati Team")


def main():
    st.set_page_config(
        page_title="Mission Vanaspati - Plant Disease Detector",
        page_icon="plant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    display_sidebar()
    
    st.title("Mission Vanaspati: Plant Disease Detector")
    st.markdown(
        "Upload a clear image of a plant leaf to identify diseases and get treatment recommendations."
    )
    
    try:
        predictor = load_predictor()
        knowledge_base = load_knowledge_base()
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        st.stop()
    
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear photo of a plant leaf. Best results with well-lit, focused images."
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Uploaded Image")
            image = Image.open(uploaded_file).convert('RGB')
            st.image(image, use_container_width=True)
            
            st.caption(f"Size: {image.size[0]} × {image.size[1]} pixels")
        
        with col2:
            st.markdown("#### Analysis")
            
            if st.button("Analyze Leaf", type="primary", use_container_width=True):
                with st.spinner("Analyzing the leaf..."):
                    try:
                        result = predictor.predict(image, return_all=True)
                        
                        display_prediction_card(result, knowledge_base)
                        
                    except Exception as e:
                        st.error(f"Prediction failed: {e}")
    else:
        st.info(
            "Upload an image to get started. "
            "For best results:\n"
            "- Use clear, well-lit photos\n"
            "- Focus on a single leaf\n"
            "- Avoid blurry or dark images"
        )
        
        with st.expander("See Example Images"):
            st.write("Here are examples of good quality images for analysis:")
            st.caption("(Placeholder - replace with actual sample images)")


if __name__ == "__main__":
    main()