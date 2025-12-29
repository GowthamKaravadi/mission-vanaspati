import streamlit as st
import json
import sys
from pathlib import Path
from PIL import Image
from datetime import datetime

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


def display_prediction_card(result: dict, knowledge_base: dict, show_tracker: bool = False):
    
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
            
            if show_tracker and "healthy" not in class_name.lower():
                if 'treatment_tracker' not in st.session_state:
                    st.session_state.treatment_tracker = {}
                
                tracker_key = f"{class_name}_{result.get('timestamp', 'default')}"
                
                if tracker_key not in st.session_state.treatment_tracker:
                    st.session_state.treatment_tracker[tracker_key] = [False] * len(info['remedies'])
                
                for i, step in enumerate(info['remedies'], 1):
                    checked = st.checkbox(
                        step,
                        value=st.session_state.treatment_tracker[tracker_key][i-1],
                        key=f"remedy_{tracker_key}_{i}"
                    )
                    st.session_state.treatment_tracker[tracker_key][i-1] = checked
                
                completed = sum(st.session_state.treatment_tracker[tracker_key])
                total = len(info['remedies'])
                progress = completed / total if total > 0 else 0
                
                st.progress(progress)
                st.caption(f"Progress: {completed}/{total} steps completed")
            else:
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




def main():
    st.set_page_config(
        page_title="Mission Vanaspati - Plant Disease Detector",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        mode = st.radio(
            "Upload Mode",
            ["Single Image", "Batch Upload"],
            help="Choose between single or multiple image analysis"
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Filter predictions below this confidence level"
        )
        
        show_tracker = st.checkbox(
            "Enable Treatment Tracker",
            value=False,
            help="Track your progress on treatment steps"
        )
        
        st.markdown("---")
        st.markdown("### 📜 Analysis History")
        
        if st.session_state.analysis_history:
            st.caption(f"Total analyses: {len(st.session_state.analysis_history)}")
            
            if st.button("Clear History", type="secondary"):
                st.session_state.analysis_history = []
                st.rerun()
            
            with st.expander("View History"):
                for idx, record in enumerate(reversed(st.session_state.analysis_history[-10:]), 1):
                    st.markdown(f"**{idx}.** {record['class_name']}")
                    st.caption(f"{record['confidence']:.1%} - {record['timestamp']}")
                    st.markdown("---")
        else:
            st.caption("No analyses yet")
    
    st.title("🌿 Mission Vanaspati: Plant Disease Detector")
    st.markdown(
        "Upload clear images of plant leaves to identify diseases and get treatment recommendations."
    )
    
    try:
        predictor = load_predictor()
        knowledge_base = load_knowledge_base()
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        st.stop()
    
    if mode == "Single Image":
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
                            
                            if result['confidence'] >= confidence_threshold:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                result['timestamp'] = timestamp
                                
                                st.session_state.analysis_history.append({
                                    'class_name': result['class_name'],
                                    'confidence': result['confidence'],
                                    'timestamp': timestamp
                                })
                                
                                display_prediction_card(result, knowledge_base, show_tracker)
                            else:
                                st.warning(
                                    f"Confidence ({result['confidence']:.1%}) is below threshold "
                                    f"({confidence_threshold:.1%}). Try a clearer image or adjust the threshold."
                                )
                            
                        except Exception as e:
                            st.error(f"Prediction failed: {e}")
        else:
            st.info(
                "📤 Upload an image to get started.\n\n"
                "**Tips for best results:**\n"
                "- Use clear, well-lit photos\n"
                "- Focus on a single leaf\n"
                "- Avoid blurry or dark images"
            )
    
    else:
        uploaded_files = st.file_uploader(
            "Choose images...",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="Upload multiple leaf images for batch analysis"
        )
        
        if uploaded_files:
            st.markdown(f"### 📊 Batch Analysis ({len(uploaded_files)} images)")
            
            if st.button("Analyze All Images", type="primary", use_container_width=True):
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                    
                    try:
                        image = Image.open(uploaded_file).convert('RGB')
                        result = predictor.predict(image, return_all=True)
                        
                        if result['confidence'] >= confidence_threshold:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            result['timestamp'] = timestamp
                            result['filename'] = uploaded_file.name
                            result['image'] = image
                            results.append(result)
                            
                            st.session_state.analysis_history.append({
                                'class_name': result['class_name'],
                                'confidence': result['confidence'],
                                'timestamp': timestamp
                            })
                    except Exception as e:
                        st.warning(f"Failed to process {uploaded_file.name}: {e}")
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                status_text.text("✅ Analysis complete!")
                progress_bar.empty()
                
                if results:
                    st.markdown("---")
                    st.markdown("### 📋 Results")
                    
                    cols_per_row = 3
                    for i in range(0, len(results), cols_per_row):
                        cols = st.columns(cols_per_row)
                        
                        for col_idx, result in enumerate(results[i:i+cols_per_row]):
                            with cols[col_idx]:
                                st.image(result['image'], use_container_width=True)
                                st.markdown(f"**{result['class_name']}**")
                                
                                confidence = result['confidence']
                                if confidence >= 0.8:
                                    color = "green"
                                elif confidence >= 0.5:
                                    color = "orange"
                                else:
                                    color = "red"
                                
                                st.markdown(
                                    f"<span style='color:{color};'>● {confidence:.1%}</span>",
                                    unsafe_allow_html=True
                                )
                                st.caption(result['filename'])
                    
                    st.markdown("---")
                    st.markdown("### 📊 Summary Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Analyzed", len(results))
                    
                    with col2:
                        avg_confidence = sum(r['confidence'] for r in results) / len(results)
                        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
                    
                    with col3:
                        diseases = [r['class_name'] for r in results if 'healthy' not in r['class_name'].lower()]
                        st.metric("Diseases Detected", len(diseases))
                else:
                    st.warning("No predictions met the confidence threshold. Try lowering the threshold.")
        else:
            st.info(
                "📤 Upload multiple images for batch analysis.\n\n"
                "**Batch mode benefits:**\n"
                "- Analyze multiple plants at once\n"
                "- Compare results side-by-side\n"
                "- Get summary statistics"
            )
        


if __name__ == "__main__":
    main()