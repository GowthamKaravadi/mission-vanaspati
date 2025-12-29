from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from PIL import Image
import io
import os
from typing import Dict, List
from sqlalchemy.orm import Session
from datetime import timedelta

from config import active_config as cfg
from src.core.predictor import PlantDiseasePredictor
from src.database import get_db, User, Remedy, Feedback, init_db
from src.auth import (
    create_access_token,
    get_current_active_user,
    get_admin_user,
    validate_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


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

# Production CORS - restrict origins
ALLOWED_ORIGINS = os.getenv("FRONTEND_URL", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if os.getenv("ENVIRONMENT") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/auth/signup", tags=["Authentication"])
def signup(email: str, password: str, db: Session = Depends(get_db)) -> Dict:
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    validate_password(password)
    
    new_user = User(
        email=email,
        hashed_password=User.hash_password(password),
        is_active=True,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully",
        "email": new_user.email,
        "user_id": new_user.id
    }


@app.post("/auth/login", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Dict:
    # Try to find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username/email or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "is_admin": user.is_admin},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }


@app.get("/auth/me", tags=["Authentication"])
def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> Dict:
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }


@app.get("/admin/users", tags=["Admin"])
def get_all_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> List[Dict]:
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]


@app.put("/admin/users/{user_id}/toggle-admin", tags=["Admin"])
def toggle_admin_status(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = not user.is_admin
    db.commit()
    
    return {
        "message": f"Admin status updated for {user.email}",
        "is_admin": user.is_admin
    }


@app.delete("/admin/users/{user_id}", tags=["Admin"])
def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict:
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.email} deleted successfully"}


@app.get("/remedies", tags=["Remedies"])
def get_all_remedies(db: Session = Depends(get_db)) -> List[Dict]:
    remedies = db.query(Remedy).all()
    return [
        {
            "class_name": r.class_name,
            "description": r.description,
            "remedies": r.remedies
        }
        for r in remedies
    ]


@app.get("/remedies/{class_name}", tags=["Remedies"])
def get_remedy(class_name: str, db: Session = Depends(get_db)) -> Dict:
    remedy = db.query(Remedy).filter(Remedy.class_name == class_name).first()
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")
    
    return {
        "class_name": remedy.class_name,
        "description": remedy.description,
        "remedies": remedy.remedies
    }


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
async def predict_disease(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
) -> JSONResponse:
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Please upload an image."
        )
    
    # Check file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit. Please upload a smaller image."
        )
    
    try:
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Check minimum image dimensions
        width, height = image.size
        if width < 50 or height < 50:
            raise HTTPException(
                status_code=400,
                detail="Image is too small. Please upload a clear image of at least 50x50 pixels."
            )
        
        result = predictor.predict(image, return_all=True)
        
        # Check if it's a plant image
        if not result.get('is_plant', True):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'The uploaded image does not appear to be a plant leaf. Please upload a clear image of a plant leaf.')
            )
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
) -> JSONResponse:
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images allowed per batch request"
        )
    
    try:
        images = []
        filenames = []
        errors = []
        
        for file in files:
            if not file.content_type.startswith("image/"):
                errors.append(f"{file.filename}: Invalid file type")
                continue
            
            contents = await file.read()
            
            # Check file size
            if len(contents) > 10 * 1024 * 1024:
                errors.append(f"{file.filename}: File size exceeds 10MB")
                continue
            
            try:
                image = Image.open(io.BytesIO(contents)).convert('RGB')
                
                # Check minimum dimensions
                width, height = image.size
                if width < 50 or height < 50:
                    errors.append(f"{file.filename}: Image too small")
                    continue
                    
                images.append(image)
                filenames.append(file.filename)
            except Exception as e:
                errors.append(f"{file.filename}: Failed to process - {str(e)}")
        
        if not images:
            raise HTTPException(
                status_code=400,
                detail=f"No valid images found. Errors: {'; '.join(errors)}"
            )
        
        results = predictor.predict_batch(images, return_all=True)
        
        predictions = []
        non_plant_images = []
        
        for filename, result in zip(filenames, results):
            # Check if it's a plant image
            if not result.get('is_plant', True):
                non_plant_images.append(filename)
                predictions.append({
                    "filename": filename,
                    "predicted_class": "Not a plant image",
                    "confidence": 0.0,
                    "error": "Does not appear to be a plant leaf",
                    "top_predictions": []
                })
            else:
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
        
        response_data = {"predictions": predictions}
        if non_plant_images:
            response_data["warning"] = f"The following images do not appear to be plant leaves: {', '.join(non_plant_images)}"
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.post("/feedback", tags=["Feedback"])
def submit_feedback(
    subject: str,
    message: str,
    type: str = "bug",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Submit feedback or bug report
    
    Args:
        subject: Brief subject line
        message: Detailed feedback/bug description
        type: Type of feedback (bug, feature, general)
    """
    if type not in ["bug", "feature", "general"]:
        raise HTTPException(status_code=400, detail="Invalid feedback type")
    
    if not subject or not message:
        raise HTTPException(status_code=400, detail="Subject and message are required")
    
    feedback = Feedback(
        email=current_user.email,
        subject=subject,
        message=message,
        type=type
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return {
        "status": "success",
        "message": "Feedback submitted successfully",
        "feedback_id": feedback.id
    }


@app.get("/admin/feedback", tags=["Admin"])
def get_all_feedback(
    status: str = None,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get all feedback submissions (admin only)"""
    query = db.query(Feedback)
    
    if status:
        query = query.filter(Feedback.status == status)
    
    feedbacks = query.order_by(Feedback.created_at.desc()).all()
    
    return {
        "status": "success",
        "count": len(feedbacks),
        "feedback": [
            {
                "id": f.id,
                "email": f.email,
                "subject": f.subject,
                "message": f.message,
                "type": f.type,
                "status": f.status,
                "created_at": f.created_at.isoformat()
            }
            for f in feedbacks
        ]
    }


@app.patch("/admin/feedback/{feedback_id}", tags=["Admin"])
def update_feedback_status(
    feedback_id: int,
    status: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Update feedback status (admin only)"""
    if status not in ["pending", "reviewed", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.status = status
    db.commit()
    
    return {
        "status": "success",
        "message": f"Feedback status updated to {status}"
    }


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

