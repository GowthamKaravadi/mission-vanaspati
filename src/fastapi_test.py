from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from typing import Dict, List

from config import active_config as cfg
from src.core.predictor import PlantDiseasePredictor


predictor = PlantDiseasePredictor(
    model_path=cfg.MODEL_SAVE_PATH,
    class_mapping_path=cfg.CLASS_MAPPING_PATH,
    top_k=cfg.TOP_K_PREDICTIONS,
    confidence_threshold=cfg.CONFIDENCE_THRESHOLD,
)


app = FastAPI(
    title="Mission Vanaspati API",
    description="Plant disease classification API using deep learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root() -> Dict[str, str]:
    return {
        "message": "Welcome to Mission Vanaspati API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    return {
        "status": "healthy",
        "model_loaded": True,
        "num_classes": predictor.num_classes,
        "device": str(predictor.device),
    }


@app.get("/classes", tags=["Info"])
def get_classes() -> Dict[str, List[str]]:
    return {
        "classes": predictor.get_all_classes(),
        "count": predictor.num_classes
    }


@app.post("/predict", tags=["Prediction"])
async def predict_disease(file: UploadFile = File(...)) -> JSONResponse:
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Please upload an image."
        )
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        result = predictor.predict(image, return_all=True)
        
        return JSONResponse(
            content={
                "predicted_class": result['class_name'],
                "confidence": round(result['confidence'], 4),
                "top_predictions": [
                    {
                        "class_name": pred['class_name'],
                        "confidence": round(pred['confidence'], 4)
                    }
                    for pred in result['top_k']
                ],
                "filename": file.filename,
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(files: List[UploadFile] = File(...)) -> JSONResponse:
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images allowed per batch request"
        )
    
    try:
        images = []
        filenames = []
        
        for file in files:
            if not file.content_type.startswith("image/"):
                continue
            
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            images.append(image)
            filenames.append(file.filename)
        
        if not images:
            raise HTTPException(
                status_code=400,
                detail="No valid images found in request"
            )
        
        results = predictor.predict_batch(images, return_all=True)
        
        predictions = []
        for filename, result in zip(filenames, results):
            predictions.append({
                "filename": filename,
                "predicted_class": result['class_name'],
                "confidence": round(result['confidence'], 4),
                "top_predictions": [
                    {
                        "class_name": pred['class_name'],
                        "confidence": round(pred['confidence'], 4)
                    }
                    for pred in result.get('top_k', [result])
                ]
            })
        
        return JSONResponse(content={"predictions": predictions})
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    print("=" * 70)
    print("Mission Vanaspati API Started")
    print(f"Model: {cfg.MODEL_SAVE_PATH.name}")
    print(f"Classes: {predictor.num_classes}")
    print(f"Device: {predictor.device}")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    print("Mission Vanaspati API Shutting Down")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "fastapi_test:app",
        host=cfg.API_HOST,
        port=cfg.API_PORT,
        reload=cfg.API_RELOAD
    )

