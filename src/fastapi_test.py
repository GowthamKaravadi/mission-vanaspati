# src/fastapi_test.py
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import io
from pathlib import Path
import sys
##add /docs after http://127.0.0.1:8000 to see the automatic API documentation
# Add the project root to the Python path to allow importing from 'src'
# This is necessary because we run uvicorn from the root directory.
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.predictor import Predictor

# --- 1. Initialize the Predictor ---
# This loads the model into memory only once when the app starts.
model_path = project_root / "models" / "plant_classifier_final.pth"
class_mapping_path = project_root / "models" / "class_mapping.json"

# Ensure the model and mapping files exist before starting
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found at {model_path}")
if not class_mapping_path.exists():
    raise FileNotFoundError(f"Class mapping file not found at {class_mapping_path}")

predictor = Predictor(model_path=model_path, class_mapping_path=class_mapping_path)


# --- 2. Create FastAPI app instance ---
app = FastAPI(
    title="Mission Vanaspati API",
    description="API for plant disease classification.",
    version="0.1.0"
)


# --- 3. Define API endpoints ---
@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Mission Vanaspati API!"}


@app.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    """
    Accepts an image file, runs it through the model, and returns the prediction.
    """
    try:
        # Read the image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')

        # Get prediction
        predicted_class, confidence = predictor.predict(image)

        return {
            "filename": file.filename,
            "predicted_class": predicted_class,
            "confidence": f"{confidence:.2%}"
        }
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

# To run this application:
# 1. Make sure you have fastapi and uvicorn installed:
#    pip install fastapi "uvicorn[standard]" python-multipart
# 2. In your terminal, navigate to the project root directory (Mission Vanaspati) and run:
#    uvicorn src.fastapi_test:app --reload

