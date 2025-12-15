# plant_classifier.py - Plant disease classification model
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision import models
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import time
import traceback

print("PLANT DISEASE CLASSIFICATION MODEL")
print("=" * 50)

class PlantImageDataset(Dataset):
    """Dataset for plant disease images"""
    def __init__(self, data_directories, transform=None):
        self.data_directories = [Path(d) for d in data_directories]
        self.transform = transform
        self.image_paths = []
        self.labels = []
        self.class_mapping = {}
        
        # Organize image data
        all_categories = set()
        for data_dir in self.data_directories:
            categories = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
            for category in categories:
                all_categories.add(category)
        
        self.class_mapping = {cls_name: i for i, cls_name in enumerate(sorted(list(all_categories)))}
        
        for data_dir in self.data_directories:
            for category_name in self.class_mapping.keys():
                category_dir = data_dir / category_name
                if category_dir.is_dir():
                    for image_path in category_dir.glob('*.jpg'):
                        self.image_paths.append(image_path)
                        self.labels.append(self.class_mapping[category_name])
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, index):
        image_path = self.image_paths[index]
        image_data = Image.open(image_path).convert('RGB')
        label = self.labels[index]
        
        if self.transform:
            image_data = self.transform(image_data)
        
        return image_data, label

class DiseaseClassificationModel(nn.Module):
    """
    Neural network for disease classification
    Uses a pre-trained ResNet50 model (Transfer Learning)
    """
    def __init__(self, num_categories):
        super(DiseaseClassificationModel, self).__init__()
        
        # 1. Load a pre-trained ResNet50 model
        #    Using DEFAULT weights is the modern way
        self.network = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        
        # 2. Freeze all the pre-trained layers
        for param in self.network.parameters():
            param.requires_grad = False
            
        # 3. Replace the final classifier layer (the "head")
        #    Get the number of input features for the final layer
        num_ftrs = self.network.fc.in_features
        
        #    Create a new head that outputs to num_categories
        self.network.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_categories)
        )
    
    def forward(self, x):
        return self.network(x)

class TransformedSubset(Dataset):
    """
    A wrapper to apply a specific transform to a subset of a dataset.
    """
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform
        # Copy the class_mapping attribute from the original dataset
        self.class_mapping = subset.dataset.class_mapping
    
    def __getitem__(self, index):
        # Get the original (un-transformed) PIL image and label
        image, label = self.subset[index]
        
        # Apply the correct transform
        if self.transform:
            image = self.transform(image)
            
        return image, label
    
    def __len__(self):
        return len(self.subset)
    

# Replace the old setup_training_data in plant_classifier.py
def setup_training_data():
    """Prepare data loaders for training"""
    print("[DEBUG] setup_training_data: STARTING")
    
    # 1. Define separate transform pipelines
    training_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    validation_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # 2. Create ONE dataset with NO transforms
    print("[DEBUG] setup_training_data: Creating PlantImageDataset...")
    full_dataset_no_transform = PlantImageDataset(
        ['data/PlantVillage', 'data/NewPlantDiseases'], 
        transform=None  # Load as PIL Images
    )
    print(f"[DEBUG] setup_training_data: PlantImageDataset created with {len(full_dataset_no_transform)} images.")
    
    # 3. Get class mapping
    class_mapping = full_dataset_no_transform.class_mapping
    
    # 4. Split the dataset
    print("[DEBUG] setup_training_data: Splitting dataset...")
    train_size = int(0.8 * len(full_dataset_no_transform))
    val_size = len(full_dataset_no_transform) - train_size
    train_subset, val_subset = torch.utils.data.random_split(
        full_dataset_no_transform, [train_size, val_size]
    )
    print("[DEBUG] setup_training_data: Dataset split.")
    
    # 5. Use the new wrapper to apply the *correct* transforms
    train_dataset = TransformedSubset(train_subset, training_transforms)
    val_dataset = TransformedSubset(val_subset, validation_transforms)
    
    # 6. Create data loaders
    print("[DEBUG] setup_training_data: Creating DataLoaders...")
    #    Optimized with num_workers and pin_memory for faster loading
    train_loader = DataLoader(
        train_dataset, 
        batch_size=32, 
        shuffle=True, 
        num_workers=4,  # Use 4 processes to load data
        pin_memory=True # Speeds up CPU-to-GPU transfer
    )
    val_loader = DataLoader(
        val_dataset, 
        batch_size=32, 
        shuffle=False, 
        num_workers=4, 
        pin_memory=True
    )
    print("[DEBUG] setup_training_data: DataLoaders created.")
    
    print(f" Training data prepared:")
    print(f"   - Training samples: {len(train_dataset)}")
    print(f"   - Validation samples: {len(val_dataset)}")
    print(f"   - Disease categories: {len(class_mapping)}")
    
    print("[DEBUG] setup_training_data: FINISHED")
    return train_loader, val_loader, len(class_mapping)

def execute_training(model, train_loader, val_loader, training_epochs=10):
    """Execute the model training process"""
    print(f"\n[DEBUG] execute_training: STARTING for {training_epochs} epochs...")
    
    # Training components
    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
    
    # Training metrics
    epoch_losses = []
    accuracy_metrics = []
    
    for epoch in range(training_epochs):
        print(f"\n Training Epoch {epoch+1}/{training_epochs}")
        
        # Training phase
        model.train()
        cumulative_loss = 0.0
        epoch_start = time.time()
        
        print(f"  [DEBUG] execute_training: Starting iteration over train_loader for Epoch {epoch+1}...")
        for batch_index, (images, labels) in enumerate(train_loader):
            # Move to compute device
            images = images.to(compute_device)
            labels = labels.to(compute_device)
            
            # Reset gradients
            optimizer.zero_grad()
            
            # Forward pass
            predictions = model(images)
            batch_loss = loss_function(predictions, labels)
            
            # Backward pass
            batch_loss.backward()
            optimizer.step()
            
            cumulative_loss += batch_loss.item()
            
            # Progress updates
            if (batch_index + 1) % 50 == 0:
                print(f'   Batch {batch_index+1}/{len(train_loader)}, Loss: {batch_loss.item():.4f}')
        print(f"  [DEBUG] execute_training: Finished iteration over train_loader for Epoch {epoch+1}.")
        
        # Validation phase
        model.eval()
        correct_predictions = 0
        total_samples = 0
        
        print(f"  [DEBUG] execute_training: Starting iteration over val_loader for Epoch {epoch+1}...")
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(compute_device)
                labels = labels.to(compute_device)
                
                predictions = model(images)
                _, predicted_classes = torch.max(predictions.data, 1)
                total_samples += labels.size(0)
                correct_predictions += (predicted_classes == labels).sum().item()
        print(f"  [DEBUG] execute_training: Finished iteration over val_loader for Epoch {epoch+1}.")
        
        # Calculate epoch metrics
        average_loss = cumulative_loss / len(train_loader)
        accuracy_percentage = 100 * correct_predictions / total_samples
        epoch_duration = time.time() - epoch_start
        
        epoch_losses.append(average_loss)
        accuracy_metrics.append(accuracy_percentage)
        
        print(f'   Average Loss: {average_loss:.4f}, Accuracy: {accuracy_percentage:.2f}%, Duration: {epoch_duration:.1f}s')
        
        # Adjust learning rate
        scheduler.step()
    
    print(f"\n[DEBUG] execute_training: FINISHED")
    return epoch_losses, accuracy_metrics

def visualize_training_progress(loss_history, accuracy_history):
    """Visualize training progress"""
    print("\n[DEBUG] visualize_training_progress: STARTING")
    
    figure, (loss_chart, accuracy_chart) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss chart
    loss_chart.plot(loss_history, 'b-', linewidth=2)
    loss_chart.set_title('Training Loss Progress')
    loss_chart.set_xlabel('Epoch')
    loss_chart.set_ylabel('Loss')
    loss_chart.grid(True, alpha=0.3)
    
    # Accuracy chart
    accuracy_chart.plot(accuracy_history, 'g-', linewidth=2)
    accuracy_chart.set_title('Validation Accuracy Progress')
    accuracy_chart.set_xlabel('Epoch')
    accuracy_chart.set_ylabel('Accuracy (%)')
    accuracy_chart.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.suptitle('Plant Disease Classification - Training Progress', y=1.02, fontsize=14)
    
    print("[DEBUG] visualize_training_progress: Showing plot...")
    plt.show()
    print("[DEBUG] visualize_training_progress: FINISHED")

def main():
    global compute_device
    print("\n[DEBUG] main: STARTING")
    
    # Determine compute device
    compute_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Compute device: {compute_device}")
    
    if compute_device.type == 'cpu':
        print("Using CPU for computation - performance may be limited")
        print("Consider GPU setup for faster training")
    
    try:
        print("[DEBUG] main: Calling setup_training_data()...")
        train_loader, val_loader, num_categories = setup_training_data()
        print("[DEBUG] main: setup_training_data() FINISHED.")
        
        # Initialize model
        print(f"\n[DEBUG] main: Initializing classification model...")
        classification_model = DiseaseClassificationModel(num_categories).to(compute_device)
        print("[DEBUG] main: Model initialized.")
        
        print("Model architecture prepared!")
        print(f"   Total parameters: {sum(p.numel() for p in classification_model.parameters()):,}")
        
        # Execute training
        print("[DEBUG] main: Calling execute_training()...")
        loss_history, accuracy_history = execute_training(
            classification_model, train_loader, val_loader, training_epochs=10
        )
        print("[DEBUG] main: execute_training() FINISHED.")
        
        # Visualize results
        print("[DEBUG] main: Calling visualize_training_progress()...")
        visualize_training_progress(loss_history, accuracy_history)
        print("[DEBUG] main: visualize_training_progress() FINISHED.")
        
        # Save trained model
        print("[DEBUG] main: Saving model...")
        model_path = 'models/plant_disease_classifier.pth'
        torch.save(classification_model.state_dict(), model_path)
        print(f"\nModel saved: {model_path}")
        
        print("\nTRAINING COMPLETED SUCCESSFULLY!")
        print(f"Final Accuracy: {accuracy_history[-1]:.2f}%")
        print("Plant disease classification model is ready!")
        
    except Exception as e:
        print(f"Training error in main: {e}")
        traceback.print_exc()
    
    print("[DEBUG] main: FINISHED")

if __name__ == "__main__":
    try:
        print("[DEBUG] __main__: Executing main()...")
        main()
        print("[DEBUG] __main__: main() finished.")
    except Exception as e:
        print(f"Unhandled error in __main__: {e}")
        traceback.print_exc()
    finally:
        print("[DEBUG] __main__: Script finished.")
