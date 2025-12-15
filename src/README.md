# Source Scripts Documentation

## Production Scripts (Core Application)

### Training & Inference
- **`train.py`** - Main training orchestrator. Wires config, dataloaders, model, and trainer.
  - Usage: `python -m src.train`
  
- **`inference.py`** - CLI inference tool for single image prediction.
  - Usage: `python -m src.inference <image_path>`

### Web Applications
- **`app.py`** - Streamlit web interface for disease detection with treatment recommendations.
  - Usage: `streamlit run src/app.py`
  
- **`fastapi_test.py`** - RESTful API backend with endpoints for single/batch prediction.
  - Usage: `uvicorn src.fastapi_test:app --reload`
  - Docs: http://127.0.0.1:8000/docs

### Core Modules (`src/core/`)
- **`model.py`** - ResNet50-based DiseaseClassifier; model create/save/load utilities
- **`dataset.py`** - Dataset loader, transforms, dataloaders; class mapping persistence
- **`trainer.py`** - Training loops with AMP, scheduler, checkpointing
- **`predictor.py`** - High-level inference interface for single/batch predictions

---

## Utility Scripts (Development & Debugging)

### Environment & Setup
- **`check_nvidia.py`** - Check NVIDIA GPU and CUDA availability
- **`pytorch_gpu_detection.py`** - Verify PyTorch GPU detection
- **`verify_install.py`** - Verify all required packages are installed
- **`verify_data.py`** - Validate dataset structure and integrity

### Data Management
- **`check_duplicates.py`** - Scan dataset for duplicate images
- **`clean_duplicates.py`** - Remove duplicate images from dataset
- **`data_collection.py`** - Scripts for collecting/organizing plant disease images
- **`check_location.py`** - Verify dataset paths and file locations

### Debugging & Visualization
- **`debug_explore.py`** - Explore dataset statistics and distributions
- **`debug_matplotlib.py`** - Test matplotlib rendering and image display
- **`display_image.py`** - Display sample images from dataset

---

## Archived Scripts (`/archive/`)

These scripts have been replaced by the refactored `src/core/` modules:
- **`plant_classifier.py`** - Old model architecture → replaced by `src/core/model.py`
- **`model_trainer_latest.py`** - Old training logic → replaced by `src/core/trainer.py` + `src/train.py`
- **`predictor.py`** - Old prediction interface → replaced by `src/core/predictor.py`
- **`test model.py`** - Old model testing → now handled by smoke tests in refactored modules

---

## Quick Start

### Train a new model:
```bash
python -m src.train
```

### Run inference on an image:
```bash
python -m src.inference data/test_image.jpg
```

### Start Streamlit web app:
```bash
streamlit run src/app.py
```

### Start FastAPI backend:
```bash
uvicorn src.fastapi_test:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuration

All settings centralized in `config.py`:
- Model architecture (ResNet50, hidden units, dropout)
- Training hyperparameters (epochs, batch size, learning rate)
- Data paths and preprocessing
- Device settings (CPU/GPU)
- API configuration

Switch between development/production configs via `ENV` environment variable:
```bash
# Development (5 epochs, faster logging)
set ENV=development

# Production (20 epochs, optimized)
set ENV=production
```
