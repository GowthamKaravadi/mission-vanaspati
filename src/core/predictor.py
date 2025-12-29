import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

import torch
import numpy as np
from PIL import Image, ImageFilter

from src.core.model import load_model
from src.core.dataset import get_val_transforms


class PlantDiseasePredictor:
    
    def __init__(
        self,
        model_path: Union[str, Path],
        class_mapping_path: Union[str, Path],
        device: Optional[str] = None,
        confidence_threshold: float = 0.0,
        top_k: int = 3,
    ):
        self.model_path = Path(model_path)
        self.class_mapping_path = Path(class_mapping_path)
        self.confidence_threshold = confidence_threshold
        self.top_k = top_k
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        
        print(f"Loading model from {self.model_path}...")
        self.model = load_model(
            self.model_path,
            device=self.device.type,
            for_inference=True
        )
        
        self.idx_to_class = self._load_class_mapping()
        self.num_classes = len(self.idx_to_class)
        
        self.transform = get_val_transforms()
        
        print(f"Predictor ready: {self.num_classes} classes on {self.device}")
    
    def _load_class_mapping(self) -> Dict[int, str]:
        with open(self.class_mapping_path, 'r') as f:
            class_to_idx = json.load(f)
        
        idx_to_class = {v: k for k, v in class_to_idx.items()}
        return idx_to_class
    
    def _is_plant_image(self, image: Image.Image) -> Tuple[bool, str]:
        """
        Check if image contains plant-like characteristics.
        Returns (is_plant, reason)
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Check if image is too uniform (like text on paper or solid colors)
        std_dev = np.std(img_array)
        if std_dev < 20:
            return False, "Image appears to be too uniform (text, drawing, or solid color), not a natural photograph"
        
        # Check for green pixels (plants typically have green)
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # Green dominant pixels (typical for plant leaves)
        green_dominant = (g > r) & (g > b) & (g > 50)
        green_ratio = np.sum(green_dominant) / (img_array.shape[0] * img_array.shape[1])
        
        # Plant images should have at least 10% green pixels
        if green_ratio < 0.10:
            return False, "Image does not contain sufficient plant-like colors. Please upload a photo of a plant leaf."
        
        # Check for texture complexity (leaves have veins and texture)
        # Convert to grayscale for edge detection
        gray_image = image.convert('L')
        edges = gray_image.filter(ImageFilter.FIND_EDGES)
        edge_array = np.array(edges)
        edge_density = np.sum(edge_array > 30) / (edge_array.shape[0] * edge_array.shape[1])
        
        # Leaves have moderate edge density (0.05 to 0.4)
        # Too few edges = solid color object, too many = text/noise
        if edge_density < 0.05:
            return False, "Image appears to be a solid colored object, not a natural leaf. Please upload a photo of a plant leaf with visible texture."
        
        if edge_density > 0.5:
            return False, "Image contains too much noise or text patterns, not a natural photograph"
        
        # Check color variance in green channel - leaves have variation
        green_channel = img_array[:,:,1]
        green_std = np.std(green_channel)
        if green_std < 15:
            return False, "Image has uniform green color (like painted surface), not a natural leaf with texture variation"
        
        # Check aspect ratio - extremely wide/tall images are suspicious
        width, height = image.size
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 5:
            return False, "Image has unusual aspect ratio, not typical of plant photographs"
        
        return True, "Valid plant image"
    
    def _preprocess_image(self, image: Union[str, Path, Image.Image]) -> torch.Tensor:
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            image = image.convert('RGB')
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
        
        tensor = self.transform(image).unsqueeze(0)
        return tensor
    
    def predict(
        self,
        image: Union[str, Path, Image.Image],
        return_all: bool = False
    ) -> Dict[str, any]:
        # Load image if needed
        if isinstance(image, (str, Path)):
            pil_image = Image.open(image).convert('RGB')
        else:
            pil_image = image.convert('RGB')
        
        # First check if it's actually a plant image
        is_plant, reason = self._is_plant_image(pil_image)
        if not is_plant:
            result = {
                'class_name': 'Not a plant image',
                'class_idx': -1,
                'confidence': 0.0,
                'error': reason,
                'is_plant': False
            }
            return result
        
        tensor = self._preprocess_image(pil_image).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)
        
        top_prob, top_idx = probabilities[0].max(dim=0)
        
        result = {
            'class_name': self.idx_to_class.get(top_idx.item(), 'Unknown'),
            'class_idx': top_idx.item(),
            'confidence': top_prob.item(),
            'is_plant': True
        }
        
        if return_all:
            top_k_probs, top_k_indices = probabilities[0].topk(self.top_k)
            
            top_k_predictions = []
            for prob, idx in zip(top_k_probs, top_k_indices):
                prob_val = prob.item()
                if prob_val >= self.confidence_threshold:
                    top_k_predictions.append({
                        'class_name': self.idx_to_class.get(idx.item(), 'Unknown'),
                        'class_idx': idx.item(),
                        'confidence': prob_val,
                    })
            
            result['top_k'] = top_k_predictions
        
        return result
    
    def predict_batch(
        self,
        images: List[Union[str, Path, Image.Image]],
        return_all: bool = False
    ) -> List[Dict[str, any]]:
        # First validate all images
        pil_images = []
        results = []
        valid_indices = []
        
        for i, img in enumerate(images):
            # Load image if needed
            if isinstance(img, (str, Path)):
                pil_image = Image.open(img).convert('RGB')
            else:
                pil_image = img.convert('RGB')
            
            # Check if it's a plant image
            is_plant, reason = self._is_plant_image(pil_image)
            if not is_plant:
                results.append({
                    'class_name': 'Not a plant image',
                    'class_idx': -1,
                    'confidence': 0.0,
                    'error': reason,
                    'is_plant': False
                })
            else:
                pil_images.append(pil_image)
                valid_indices.append(i)
                results.append(None)  # Placeholder
        
        # Process valid images
        if pil_images:
            tensors = [self._preprocess_image(img) for img in pil_images]
            batch = torch.cat(tensors, dim=0).to(self.device)
            
            with torch.no_grad():
                logits = self.model(batch)
                probabilities = torch.softmax(logits, dim=1)
            
            for j, i in enumerate(valid_indices):
                probs = probabilities[j]
                top_prob, top_idx = probs.max(dim=0)
                
                result = {
                    'class_name': self.idx_to_class.get(top_idx.item(), 'Unknown'),
                    'class_idx': top_idx.item(),
                    'confidence': top_prob.item(),
                    'is_plant': True
                }
                
                if return_all:
                    top_k_probs, top_k_indices = probs.topk(self.top_k)
                    
                    top_k_predictions = []
                    for prob, idx in zip(top_k_probs, top_k_indices):
                        prob_val = prob.item()
                        if prob_val >= self.confidence_threshold:
                            top_k_predictions.append({
                                'class_name': self.idx_to_class.get(idx.item(), 'Unknown'),
                                'class_idx': idx.item(),
                                'confidence': prob_val,
                            })
                    
                    result['top_k'] = top_k_predictions
                
                results[i] = result
        
        return results
    
    def get_all_classes(self) -> List[str]:
        return sorted(self.idx_to_class.values())
    
    def get_class_info(self, class_name: str) -> Optional[Dict[str, any]]:
        class_idx = None
        for idx, name in self.idx_to_class.items():
            if name == class_name:
                class_idx = idx
                break
        
        if class_idx is None:
            return None
        
        return {
            'class_name': class_name,
            'class_idx': class_idx,
        }
    
    def __repr__(self) -> str:
        return (
            f"PlantDiseasePredictor("
            f"model={self.model_path.name}, "
            f"classes={self.num_classes}, "
            f"device={self.device})"
        )
