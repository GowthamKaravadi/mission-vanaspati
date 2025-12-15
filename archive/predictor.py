# src/predictor.py
# This file contains ALL model and prediction logic.

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from pathlib import Path
import json

# --- 1. MODEL ARCHITECTURE (Copied from plant_classifier.py) ---

class DiseaseClassificationModel(nn.Module):
    """
    Neural network for disease classification
    Uses a pre-trained ResNet50 model (Transfer Learning)
    """
    def __init__(self, num_categories):
        super(DiseaseClassificationModel, self).__init__()
        
        # 1. Load a pre-trained ResNet50 model
        self.network = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        
        # 2. Freeze all the pre-trained layers
        for param in self.network.parameters():
            param.requires_grad = False
            
        # 3. Replace the final classifier layer (the "head")
        num_ftrs = self.network.fc.in_features
        
        self.network.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_categories)
        )
    
    def forward(self, x):
        return self.network(x)

# --- 2. PREDICTOR CLASS (Our new logic) ---

class Predictor:
    """
    Handles loading the model and running predictions.
    This is the only class our app will need to import.
    """
    def __init__(self, model_path, class_mapping_path):
        """
        Initializes the predictor, loading the model and class mapping.
        
        Args:
            model_path (Path): Path to the .pth model file.
            class_mapping_path (Path): Path to the .json class mapping file.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load and invert class mapping
        try:
            with open(class_mapping_path, 'r') as f:
                class_mapping_from_file = json.load(f) # This is {"ClassName": 0}
            
            # Invert the dictionary to be {0: "ClassName"}
            self.class_mapping = {v: k for k, v in class_mapping_from_file.items()}
        except Exception as e:
            print(f"Error loading class mapping: {e}")
            raise
            
        num_classes = len(self.class_mapping)
        
        # Load the model structure (defined above in this same file)
        self.model = DiseaseClassificationModel(num_classes).to(self.device)
        
        # Load the saved weights
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        except Exception as e:
            print(f"Error loading model weights: {e}")
            raise
            
        self.model.eval()  # Set model to evaluation mode
        
        # Define the preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        print(f"Predictor loaded. Model: {model_path.name}, Classes: {num_classes}, Device: {self.device}")

    def _preprocess(self, image_pil: Image):
        """Preprocess a single PIL image."""
        image_tensor = self.transform(image_pil).unsqueeze(0)
        return image_tensor.to(self.device)

    def predict(self, image_pil: Image):
        """
        Run a full prediction on a single PIL image.
        
        Args:
            image_pil (PIL.Image): The image to classify.
            
        Returns:
            tuple: (class_name, confidence_score)
        """
        
        # Preprocess the image
        image_tensor = self._preprocess(image_pil)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # Get the top probability and its index
            top_prob, top_idx = torch.max(probabilities, 1)
            
            pred_index = top_idx.item()
            confidence = top_prob.item()
            
            # Translate index to class name
            class_name = self.class_mapping.get(pred_index, "Unknown Class")
            
            return class_name, confidence