import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import json


class PlantDiseaseDataset(Dataset):
    
    def __init__(
        self,
        data_directories: List[Path],
        transform: Optional[transforms.Compose] = None,
        valid_extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")
    ):
        self.transform = transform
        self.valid_extensions = valid_extensions
        
        self.image_paths = []
        self.labels = []
        
        all_classes = set()
        for data_dir in data_directories:
            if not data_dir.exists():
                print(f"Warning: Directory not found: {data_dir}")
                continue
            
            for class_dir in data_dir.iterdir():
                if class_dir.is_dir():
                    all_classes.add(class_dir.name)
        
        sorted_classes = sorted(list(all_classes))
        
        self.class_to_idx = {class_name: idx for idx, class_name in enumerate(sorted_classes)}
        
        self.idx_to_class = {idx: class_name for class_name, idx in self.class_to_idx.items()}
        
        # Now populate image_paths and labels
        for data_dir in data_directories:
            if not data_dir.exists():
                continue
            
            for class_name, class_idx in self.class_to_idx.items():
                class_dir = data_dir / class_name
                
                if not class_dir.exists():
                    continue
                
                for image_path in class_dir.iterdir():
                    if image_path.suffix in self.valid_extensions:
                        self.image_paths.append(image_path)
                        self.labels.append(class_idx)
        
        print(f"Loaded dataset:")
        print(f"  Total images: {len(self.image_paths):,}")
        print(f"  Number of classes: {len(self.class_to_idx)}")
        print(f"  Classes: {list(self.class_to_idx.keys())[:5]}..." if len(self.class_to_idx) > 5 else f"  Classes: {list(self.class_to_idx.keys())}")
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int]:
        image_path = self.image_paths[index]
        label = self.labels[index]
        
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            image = Image.new('RGB', (224, 224), color='black')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label
    
    def get_class_name(self, class_idx: int) -> str:
        return self.idx_to_class.get(class_idx, "Unknown")
    
    def get_class_distribution(self) -> Dict[str, int]:
        distribution = {}
        
        for label in self.labels:
            class_name = self.get_class_name(label)
            distribution[class_name] = distribution.get(class_name, 0) + 1
        
        return distribution
    
    def save_class_mapping(self, save_path: Path):
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(self.class_to_idx, f, indent=2)
        
        print(f"Class mapping saved to: {save_path}")


def get_train_transforms(image_size: Tuple[int, int] = (224, 224)) -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.RandomResizedCrop(
            size=image_size,
            scale=(0.8, 1.0),
            ratio=(0.9, 1.1)
        ),
        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
            hue=0.1
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def get_val_transforms(image_size: Tuple[int, int] = (224, 224)) -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def create_dataloaders(
    data_directories: List[Path],
    batch_size: int = 32,
    train_split: float = 0.8,
    num_workers: int = 4,
    pin_memory: bool = True,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, PlantDiseaseDataset]:
    torch.manual_seed(seed)
    
    print("Creating full dataset...")
    full_dataset = PlantDiseaseDataset(
        data_directories=data_directories,
        transform=None
    )
    
    total_size = len(full_dataset)
    train_size = int(train_split * total_size)
    val_size = total_size - train_size
    
    print(f"Splitting dataset:")
    print(f"  Training: {train_size:,} images ({train_split*100:.0f}%)")
    print(f"  Validation: {val_size:,} images ({(1-train_split)*100:.0f}%)")
    
    train_dataset, val_dataset = random_split(
        full_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(seed)
    )
    
    train_dataset.dataset.transform = get_train_transforms()
    val_dataset.dataset.transform = get_val_transforms()
    
    print("Creating DataLoaders...")
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=True if num_workers > 0 else False,
        prefetch_factor=2 if num_workers > 0 else None
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=True if num_workers > 0 else False,
        prefetch_factor=2 if num_workers > 0 else None
    )
    
    print("DataLoaders created successfully!")
    print(f"  Train batches: {len(train_loader)}")
    print(f"  Validation batches: {len(val_loader)}")
    
    return train_loader, val_loader, full_dataset


if __name__ == "__main__":
    from config import config
    
    print("Testing Dataset Module...")
    print()
    
    print("Test 1: Loading dataset...")
    data_dirs = config.get_data_directories()
    
    if not data_dirs:
        print("No data directories found. Please check your data setup.")
        exit(1)
    
    dataset = PlantDiseaseDataset(
        data_directories=data_dirs,
        transform=get_val_transforms()
    )
    print()
    
    print("Test 2: Getting single image...")
    image, label = dataset[0]
    print(f"Image shape: {image.shape}")
    print(f"Label: {label} ({dataset.get_class_name(label)})")
    print()
    
    print("Test 3: Class distribution...")
    distribution = dataset.get_class_distribution()
    print(f"Number of classes: {len(distribution)}")
    print("Top 5 classes by count:")
    for class_name, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {class_name}: {count:,} images")
    print()
    
    print("Test 4: Creating dataloaders...")
    train_loader, val_loader, full_dataset = create_dataloaders(
        data_directories=data_dirs,
        batch_size=16,
        train_split=0.8,
        num_workers=0
    )
    print()
    
    print("Test 5: Loading one batch...")
    images, labels = next(iter(train_loader))
    print(f"Batch shape: {images.shape}")
    print(f"Labels shape: {labels.shape}")
    print(f"Batch device: {images.device}")
    print()
    
    print("All tests passed!")
