"""
Core module for Mission Vanaspati

This module contains the fundamental components for plant disease classification:
- model: Neural network architecture (ResNet50-based)
- dataset: Data loading and preprocessing
- trainer: Training logic and optimization
- predictor: Inference and prediction utilities
"""

from .model import DiseaseClassifier, create_model, save_model, load_model
from .predictor import PlantDiseasePredictor

__all__ = [
    "DiseaseClassifier",
    "create_model",
    "save_model",
    "load_model",
    "PlantDiseasePredictor",
]
