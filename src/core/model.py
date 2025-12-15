import torch
import torch.nn as nn
from torchvision import models
from typing import Optional, Dict
from pathlib import Path


class DiseaseClassifier(nn.Module):
    
    def __init__(
        self,
        num_classes: int,
        pretrained: bool = True,
        freeze_backbone: bool = True,
        hidden_units: int = 512,
        dropout_rate: float = 0.5
    ):
        super(DiseaseClassifier, self).__init__()
        
        self.num_classes = num_classes
        self.hidden_units = hidden_units
        self.dropout_rate = dropout_rate
        
        if pretrained:
            weights = models.ResNet50_Weights.DEFAULT
            self.backbone = models.resnet50(weights=weights)
        else:
            self.backbone = models.resnet50(weights=None)
        
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        num_features = self.backbone.fc.in_features
        
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_features, hidden_units),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(hidden_units, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)
    
    def get_trainable_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def get_total_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())
    
    def print_model_summary(self):
        total_params = self.get_total_parameters()
        trainable_params = self.get_trainable_parameters()
        frozen_params = total_params - trainable_params
        
        print("=" * 70)
        print("MODEL ARCHITECTURE SUMMARY")
        print("=" * 70)
        print(f"Model: Disease Classifier (ResNet50 Backbone)")
        print(f"Number of Classes: {self.num_classes}")
        print(f"Hidden Units: {self.hidden_units}")
        print(f"Dropout Rate: {self.dropout_rate}")
        print("-" * 70)
        print(f"Total Parameters: {total_params:,}")
        print(f"Trainable Parameters: {trainable_params:,}")
        print(f"Frozen Parameters: {frozen_params:,}")
        print(f"Percentage Trainable: {100 * trainable_params / total_params:.2f}%")
        print("=" * 70)


def create_model(
    num_classes: int,
    pretrained: bool = True,
    freeze_backbone: bool = True,
    hidden_units: int = 512,
    dropout_rate: float = 0.5,
    device: str = "cuda"
) -> DiseaseClassifier:
    model = DiseaseClassifier(
        num_classes=num_classes,
        pretrained=pretrained,
        freeze_backbone=freeze_backbone,
        hidden_units=hidden_units,
        dropout_rate=dropout_rate
    )
    
    model = model.to(device)
    
    model.print_model_summary()
    
    return model


def save_model(
    model: DiseaseClassifier,
    save_path: Path,
    epoch: Optional[int] = None,
    optimizer_state: Optional[Dict] = None,
    metrics: Optional[Dict] = None
):
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "model_config": {
            "num_classes": model.num_classes,
            "hidden_units": model.hidden_units,
            "dropout_rate": model.dropout_rate
        }
    }
    
    if epoch is not None:
        checkpoint["epoch"] = epoch
    
    if optimizer_state is not None:
        checkpoint["optimizer_state_dict"] = optimizer_state
    
    if metrics is not None:
        checkpoint["metrics"] = metrics
    
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.save(checkpoint, save_path)
    
    print(f"Model saved successfully to: {save_path}")


def load_model(
    load_path: Path,
    device: str = "cuda",
    for_inference: bool = True
) -> DiseaseClassifier:
    if not load_path.exists():
        raise FileNotFoundError(f"Model file not found: {load_path}")
    
    checkpoint = torch.load(load_path, map_location=device)

    def _infer_config_from_state_dict(sd: dict) -> Dict:
        hidden_units = 512
        num_classes = None

        candidate_final_keys = [
            "backbone.fc.3.weight",
            "network.fc.3.weight",
            "fc.3.weight",
            "backbone.fc.weight",
            "network.fc.weight",
            "fc.weight",
        ]
        for k in candidate_final_keys:
            if k in sd and sd[k].ndim == 2:
                num_classes = sd[k].shape[0]
                break

        candidate_hidden_keys = [
            "backbone.fc.0.weight",
            "network.fc.0.weight",
            "fc.0.weight",
        ]
        for k in candidate_hidden_keys:
            if k in sd and sd[k].ndim == 2:
                hidden_units = sd[k].shape[0]
                break

        if num_classes is None:
            print("Warning: Could not infer number of classes from state_dict; defaulting to 38.")
            num_classes = 38

        return {"num_classes": int(num_classes), "hidden_units": int(hidden_units), "dropout_rate": 0.5}

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        config = checkpoint.get("model_config", {})
        if not config:
            config = _infer_config_from_state_dict(checkpoint["model_state_dict"]) 
            print("Warning: Model configuration not found; inferred from weights.")

        model = DiseaseClassifier(
            num_classes=config["num_classes"],
            pretrained=False,
            freeze_backbone=False,
            hidden_units=config.get("hidden_units", 512),
            dropout_rate=config.get("dropout_rate", 0.5),
        )

        model.load_state_dict(checkpoint["model_state_dict"], strict=True)

    elif isinstance(checkpoint, dict):
        raw_sd = checkpoint

        normalized_sd = {}
        for k, v in raw_sd.items():
            new_key = k
            if new_key.startswith("module."):
                new_key = new_key[len("module."):]
            if new_key.startswith("network."):
                new_key = "backbone." + new_key[len("network."):]
            if new_key.startswith("fc."):
                new_key = "backbone." + new_key
            normalized_sd[new_key] = v

        config = _infer_config_from_state_dict(normalized_sd)

        model = DiseaseClassifier(
            num_classes=config["num_classes"],
            pretrained=False,
            freeze_backbone=False,
            hidden_units=config.get("hidden_units", 512),
            dropout_rate=config.get("dropout_rate", 0.5),
        )

        missing, unexpected = model.load_state_dict(normalized_sd, strict=False)
        if missing:
            print(f"Warning: Missing keys when loading weights: {missing[:5]}{'...' if len(missing)>5 else ''}")
        if unexpected:
            print(f"Warning: Unexpected keys in weights: {unexpected[:5]}{'...' if len(unexpected)>5 else ''}")

    else:
        raise KeyError("Unsupported checkpoint format. Expected dict or state_dict.")
    
    model = model.to(device)
    
    if for_inference:
        model.eval()
    
    print(f"Model loaded successfully from: {load_path}")
    
    if "epoch" in checkpoint:
        print(f"Trained for {checkpoint['epoch']} epochs")
    
    if "metrics" in checkpoint:
        print(f"Metrics: {checkpoint['metrics']}")
    
    return model


if __name__ == "__main__":
    print("Testing Model Architecture...")
    print()
    
    print("Test 1: Creating model...")
    model = create_model(num_classes=38, device="cpu")
    print()
    
    print("Test 2: Testing forward pass...")
    dummy_input = torch.randn(4, 3, 224, 224)
    output = model(dummy_input)
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Output range: [{output.min():.2f}, {output.max():.2f}]")
    print()
    
    print("Test 3: Testing save and load...")
    test_path = Path("test_model.pth")
    save_model(model, test_path)
    loaded_model = load_model(test_path, device="cpu")
    test_path.unlink()
    print("Save and load successful!")
    print()
    
    print("All tests passed!")
