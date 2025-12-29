from pathlib import Path
import torch


class Config:
    
    PROJECT_ROOT = Path(__file__).parent
    
    DATA_DIR = PROJECT_ROOT / "data"
    PLANTVILLAGE_DIR = DATA_DIR / "PlantVillage"
    NEWPLANTDISEASES_DIR = DATA_DIR / "NewPlantDiseases"
    TRAIN_DIR = NEWPLANTDISEASES_DIR / "train"
    VALID_DIR = NEWPLANTDISEASES_DIR / "valid"
    TEST_DIR = NEWPLANTDISEASES_DIR / "test"
    
    MODELS_DIR = PROJECT_ROOT / "models"
    MODEL_SAVE_PATH = MODELS_DIR / "plant_classifier_final.pth"
    CLASS_MAPPING_PATH = MODELS_DIR / "class_mapping.json"
    
    LOGS_DIR = PROJECT_ROOT / "logs"
    PLOTS_DIR = PROJECT_ROOT / "plots"
    
    REMEDIES_PATH = PROJECT_ROOT / "remedies.json"
    
    MODEL_NAME = "resnet50"
    USE_PRETRAINED = True
    FREEZE_BACKBONE = False
    
    HIDDEN_UNITS = 512
    DROPOUT_RATE = 0.5
    
    NUM_EPOCHS = 20
    
    BATCH_SIZE = 32
    
    LEARNING_RATE = 0.0001
    LR_SCHEDULER = "cosine"  # "step" or "cosine"
    LR_STEP_SIZE = 7  # For StepLR
    LR_GAMMA = 0.1  # For StepLR
    LR_MIN = 1e-6  # For CosineAnnealingLR
    
    OPTIMIZER = "adamw"
    WEIGHT_DECAY = 1e-4
    
    # Two-stage training
    TWO_STAGE_TRAINING = True
    STAGE1_EPOCHS = 5  # Train head only
    STAGE2_EPOCHS = 15  # Fine-tune full model
    
    # MixUp augmentation
    USE_MIXUP = True
    MIXUP_ALPHA = 0.2  # Controls mixing strength
    
    IMAGE_SIZE = (224, 224)
    NORMALIZE_MEAN = [0.485, 0.456, 0.406]
    NORMALIZE_STD = [0.229, 0.224, 0.225]
    
    TRAIN_SPLIT = 0.8
    VAL_SPLIT = 0.2
    
    RANDOM_ROTATION = 15
    RANDOM_HORIZONTAL_FLIP = True
    COLOR_JITTER_BRIGHTNESS = 0.2
    COLOR_JITTER_CONTRAST = 0.2
    COLOR_JITTER_SATURATION = 0.2
    COLOR_JITTER_HUE = 0.1
    
    NUM_WORKERS = 4
    PIN_MEMORY = True
    PREFETCH_FACTOR = 2
    PERSISTENT_WORKERS = True
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    USE_MIXED_PRECISION = True if torch.cuda.is_available() else False
    
    SAVE_EVERY_N_EPOCHS = 5
    SAVE_BEST_MODEL = True
    
    EARLY_STOPPING_PATIENCE = 10
    EARLY_STOPPING_MIN_DELTA = 0.001
    
    LOG_EVERY_N_BATCHES = 50
    
    DATABASE_PATH = PROJECT_ROOT / "vanaspati.db"
    
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_RELOAD = True
    
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
    
    CONFIDENCE_THRESHOLD = 0.5
    TOP_K_PREDICTIONS = 3
    
    @classmethod
    def validate_paths(cls):
        required_dirs = [
            cls.MODELS_DIR,
            cls.LOGS_DIR,
            cls.PLOTS_DIR
        ]
        
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)
        
        return True
    
    @classmethod
    def get_data_directories(cls):
        data_dirs = []
        
        if cls.PLANTVILLAGE_DIR.exists():
            data_dirs.append(cls.PLANTVILLAGE_DIR)
        
        if cls.TRAIN_DIR.exists():
            data_dirs.append(cls.TRAIN_DIR)
        
        return data_dirs
    
    @classmethod
    def print_config(cls):
        print("=" * 70)
        print("MISSION VANASPATI - CONFIGURATION")
        print("=" * 70)
        print(f"Device: {cls.DEVICE}")
        print(f"Model: {cls.MODEL_NAME}")
        print(f"Image Size: {cls.IMAGE_SIZE}")
        print(f"Batch Size: {cls.BATCH_SIZE}")
        print(f"Learning Rate: {cls.LEARNING_RATE}")
        print(f"Epochs: {cls.NUM_EPOCHS}")
        print(f"Data Directories: {len(cls.get_data_directories())}")
        print("=" * 70)


config = Config()


class DevelopmentConfig(Config):
    NUM_EPOCHS = 5
    LOG_EVERY_N_BATCHES = 10
    API_RELOAD = True


class ProductionConfig(Config):
    NUM_EPOCHS = 20
    USE_MIXED_PRECISION = True
    API_RELOAD = False
    SAVE_EVERY_N_EPOCHS = 10


import os
ENV = os.getenv("ENV", "development")

if ENV == "production":
    active_config = ProductionConfig()
else:
    active_config = DevelopmentConfig()
