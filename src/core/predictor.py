import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

import torch
from PIL import Image

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
        tensor = self._preprocess_image(image).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)
        
        top_prob, top_idx = probabilities[0].max(dim=0)
        
        result = {
            'class_name': self.idx_to_class.get(top_idx.item(), 'Unknown'),
            'class_idx': top_idx.item(),
            'confidence': top_prob.item(),
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
        tensors = [self._preprocess_image(img) for img in images]
        batch = torch.cat(tensors, dim=0).to(self.device)
        
        with torch.no_grad():
            logits = self.model(batch)
            probabilities = torch.softmax(logits, dim=1)
        
        results = []
        for i in range(len(images)):
            probs = probabilities[i]
            top_prob, top_idx = probs.max(dim=0)
            
            result = {
                'class_name': self.idx_to_class.get(top_idx.item(), 'Unknown'),
                'class_idx': top_idx.item(),
                'confidence': top_prob.item(),
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
            
            results.append(result)
        
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


if __name__ == "__main__":
    from config import active_config as cfg
    
    print("Testing Predictor...")
    print()
    
    predictor = PlantDiseasePredictor(
        model_path=cfg.MODEL_SAVE_PATH,
        class_mapping_path=cfg.CLASS_MAPPING_PATH,
        top_k=5
    )
    print()
    
    data_dirs = cfg.get_data_directories()
    if data_dirs:
        test_image = None
        for data_dir in data_dirs:
            for class_dir in data_dir.iterdir():
                if class_dir.is_dir():
                    for img_path in class_dir.iterdir():
                        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                            test_image = img_path
                            break
                    if test_image:
                        break
            if test_image:
                break
        
        if test_image:
            print(f"Testing with: {test_image}")
            print()
            
            result = predictor.predict(test_image, return_all=True)
            
            print("Top Prediction:")
            print(f"  Class: {result['class_name']}")
            print(f"  Confidence: {result['confidence']:.2%}")
            print()
            
            print("Top 5 Predictions:")
            for i, pred in enumerate(result['top_k'], 1):
                print(f"  {i}. {pred['class_name']}: {pred['confidence']:.2%}")
            print()
            
            print("All available classes:")
            classes = predictor.get_all_classes()
            print(f"  Total: {len(classes)}")
            print(f"  Sample: {classes[:5]}...")
        else:
            print("No test image found in dataset")
    else:
        print("No data directories found")
    
    print()
    print("Predictor test complete!")
