# model_trainer.py - Main training orchestration with progress tracking
import torch
import time
import numpy as np
from tqdm import tqdm
# We import these from your other file
from plant_classifier import DiseaseClassificationModel, setup_training_data, visualize_training_progress
import torch.optim as optim
import torch.nn as nn
import json
import os
import traceback

print("PLANT DISEASE CLASSIFICATION - TRAINING ORCHESTRATION")
print("=" * 60)

class TrainingProgressTracker:
    """Tracks and displays training progress in real-time"""
    
    def __init__(self, total_epochs):
        self.total_epochs = total_epochs
        self.epoch_times = []
        self.batch_times = []
        self.current_epoch = 0
        
    def start_epoch(self):
        """Start timing for a new epoch"""
        self.epoch_start_time = time.time()
        self.batch_times = []
        
    def record_batch_time(self, batch_time):
        """Record time for a single batch"""
        self.batch_times.append(batch_time)
        
    def end_epoch(self):
        """Complete epoch timing and calculate metrics"""
        epoch_time = time.time() - self.epoch_start_time
        self.epoch_times.append(epoch_time)
        self.current_epoch += 1
        
        return {
            'epoch_time': epoch_time,
            'avg_batch_time': np.mean(self.batch_times) if self.batch_times else 0,
            'batches_per_second': len(self.batch_times) / epoch_time if epoch_time > 0 else 0
        }
    
    def get_eta(self):
        """Calculate estimated time remaining"""
        if not self.epoch_times:
            return "Calculating..."
        
        avg_epoch_time = np.mean(self.epoch_times)
        remaining_epochs = self.total_epochs - self.current_epoch
        remaining_seconds = avg_epoch_time * remaining_epochs
        
        # Convert to readable time
        if remaining_seconds < 60:
            return f"{remaining_seconds:.0f}s"
        elif remaining_seconds < 3600:
            return f"{remaining_seconds/60:.1f}m"
        else:
            return f"{remaining_seconds/3600:.1f}h"

class TrainingOrchestrator:
    """Orchestrates the complete training process with progress tracking"""
    
    def __init__(self):
        self.compute_device = None
        self.model = None
        self.training_data = None
        self.validation_data = None
        self.progress_tracker = None
        
    def setup_environment(self):
        """Setup the training environment"""
        print("SETTING UP TRAINING ENVIRONMENT")
        print("=" * 40)
        
        # Determine compute device
        self.compute_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Compute device: {self.compute_device}")
        
        if self.compute_device.type == 'cuda':
            device_name = torch.cuda.get_device_name(0)
            device_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU: {device_name}")
            print(f"GPU Memory: {device_memory:.1f} GB")
        else:
            print("Warning: CPU training - consider GPU for better performance")
    
    def prepare_data(self):
        """Prepare training and validation data"""
        print("\nPREPARING TRAINING DATA")
        print("=" * 40)
        
        # This function is imported from plant_classifier.py
        self.training_data, self.validation_data, num_categories = setup_training_data()
        return num_categories
    
    def initialize_model(self, num_categories):
        """Initialize the classification model"""
        print("\nINITIALIZING CLASSIFICATION MODEL")
        print("=" * 40)
        
        # This class is imported from plant_classifier.py
        self.model = DiseaseClassificationModel(num_categories).to(self.compute_device)
        
        # Calculate model statistics
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        print(f"Model initialized successfully!")
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
        print(f"Output categories: {num_categories}")
        
        return self.model
    
    def execute_training_cycle(self, epochs=10):
        """Execute the complete training cycle with progress tracking"""
        print(f"\nEXECUTING TRAINING CYCLE ({epochs} EPOCHS)")
        print("=" * 40)
        
        if not self.model or not self.training_data or not self.validation_data:
            raise ValueError("Model and data must be initialized before training")
        
        # Initialize progress tracker
        self.progress_tracker = TrainingProgressTracker(epochs)
        
        # Training components
        loss_function = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
        
        # Training metrics
        epoch_losses = []
        accuracy_metrics = []
        
        print("Starting model training with real-time progress tracking...")
        print()
        
        for epoch in range(epochs):
            # Start epoch timing
            self.progress_tracker.start_epoch()
            
            # Training phase
            self.model.train()
            cumulative_loss = 0.0
            correct_predictions = 0
            total_samples = 0
            
            # Create progress bar for batches
            batch_progress = tqdm(
                self.training_data, 
                desc=f'Epoch {epoch+1}/{epochs}',
                unit='batch',
                bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'
            )
            
            for batch_idx, (images, labels) in enumerate(batch_progress):
                batch_start_time = time.time()
                
                # Move data to compute device
                images = images.to(self.compute_device)
                labels = labels.to(self.compute_device)
                
                # Reset gradients
                optimizer.zero_grad()
                
                # Forward pass
                predictions = self.model(images)
                batch_loss = loss_function(predictions, labels)
                
                # Backward pass
                batch_loss.backward()
                optimizer.step()
                
                # Calculate batch accuracy
                _, predicted_classes = torch.max(predictions.data, 1)
                batch_correct = (predicted_classes == labels).sum().item()
                batch_accuracy = 100.0 * batch_correct / labels.size(0)
                
                # Update metrics
                cumulative_loss += batch_loss.item()
                correct_predictions += batch_correct
                total_samples += labels.size(0)
                
                # Record batch time
                batch_time = time.time() - batch_start_time
                self.progress_tracker.record_batch_time(batch_time)
                
                # Update progress bar in real-time
                running_accuracy = 100.0 * correct_predictions / total_samples
                running_loss = cumulative_loss / (batch_idx + 1)
                
                # Get performance metrics
                performance_metrics = self.progress_tracker.end_epoch() if batch_idx == len(self.training_data) - 1 else {}
                avg_batch_time = np.mean(self.progress_tracker.batch_times) if self.progress_tracker.batch_times else 0
                
                # Update progress bar description
                batch_progress.set_postfix({
                    'Loss': f'{running_loss:.4f}',
                    'Acc': f'{running_accuracy:.2f}%',
                    'Batch Time': f'{avg_batch_time:.3f}s',
                    'ETA': self.progress_tracker.get_eta()
                })
            
            batch_progress.close()
            
            # Complete epoch timing
            epoch_metrics = self.progress_tracker.end_epoch()
            
            # Validation phase
            validation_accuracy = self._run_validation()
            epoch_accuracy = validation_accuracy  # Use validation accuracy for epoch
            
            # Store metrics
            epoch_loss = cumulative_loss / len(self.training_data)
            epoch_losses.append(epoch_loss)
            accuracy_metrics.append(epoch_accuracy)
            
            # Print epoch summary
            print(f'   Epoch {epoch+1} Summary:')
            print(f'      Loss: {epoch_loss:.4f}')
            print(f'      Accuracy: {epoch_accuracy:.2f}%')
            print(f'      Time: {epoch_metrics["epoch_time"]:.1f}s')
            print(f'      Batches/sec: {epoch_metrics["batches_per_second"]:.1f}')
            print(f'      Learning Rate: {scheduler.get_last_lr()[0]:.6f}')
            
            # Update learning rate
            scheduler.step()
        
        return epoch_losses, accuracy_metrics
    
    def _run_validation(self):
        """Run validation and return accuracy"""
        self.model.eval()
        correct_predictions = 0
        total_samples = 0
        
        with torch.no_grad():
            for images, labels in self.validation_data:
                images = images.to(self.compute_device)
                labels = labels.to(self.compute_device)
                
                predictions = self.model(images)
                _, predicted_classes = torch.max(predictions.data, 1)
                total_samples += labels.size(0)
                correct_predictions += (predicted_classes == labels).sum().item()
        
        if total_samples == 0:
            print("Warning: No samples found in validation data.")
            return 0.0
            
        return 100.0 * correct_predictions / total_samples
    
    def save_trained_model(self, file_path='models/plant_classifier_final.pth'):
        """Save the trained model"""
        print(f"\nSAVING TRAINED MODEL")
        print("=" * 40)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        torch.save(self.model.state_dict(), file_path)
        print(f"Model saved: {file_path}")
        
        return file_path
    
    def print_training_summary(self, loss_history, accuracy_history):
        """Print comprehensive training summary"""
        print("\nTRAINING SUMMARY")
        print("=" * 40)
        
        if not self.progress_tracker or not self.progress_tracker.epoch_times:
            print("Warning: No training progress was tracked.")
            return

        # Calculate statistics
        total_training_time = sum(self.progress_tracker.epoch_times)
        avg_epoch_time = np.mean(self.progress_tracker.epoch_times)
        max_accuracy = max(accuracy_history)
        final_accuracy = accuracy_history[-1]
        final_loss = loss_history[-1]
        
        print(f"Total Training Time: {total_training_time:.1f}s ({total_training_time/60:.1f}m)")
        print(f"Average Epoch Time: {avg_epoch_time:.1f}s")
        print(f"Final Loss: {final_loss:.4f}")
        print(f"Final Accuracy: {final_accuracy:.2f}%")
        print(f"Peak Accuracy: {max_accuracy:.2f}%")
        print(f"Accuracy Improvement: {max_accuracy - accuracy_history[0]:.2f}%")
        print(f"Compute Device: {self.compute_device}")
        
        # Performance assessment
        if final_accuracy > 85:
            assessment = "EXCELLENT - Model is highly accurate!"
        elif final_accuracy > 70:
            assessment = "GOOD - Model is performing well!"
        elif final_accuracy > 50:
            assessment = "FAIR - Model has learned basic patterns"
        else:
            assessment = "NEEDS IMPROVEMENT - Consider more training or data"
        
        print(f"Assessment: {assessment}")

def main():
    """Main training orchestration function"""
    orchestrator = TrainingOrchestrator()
    
    try:
        # Step 1: Setup environment
        orchestrator.setup_environment()
        
        # Step 2: Prepare data
        num_categories = orchestrator.prepare_data()
        
        # --- NEW BLOCK TO SAVE CLASS MAPPING ---
        print("Saving class mapping...")
        try:
            # Get the mapping from the train_loader's dataset
            # We access .dataset to get the TransformedSubset
            # then .subset.dataset to get the original PlantImageDataset
            class_mapping = orchestrator.training_data.dataset.class_mapping
            os.makedirs('models', exist_ok=True) # Ensure 'models' dir exists
            with open('models/class_mapping.json', 'w') as f:
                json.dump(class_mapping, f, indent=2)
            print("Class mapping saved to models/class_mapping.json")
        except AttributeError:
             print("Error: Could not find 'class_mapping'. Make sure your TransformedSubset class in plant_classifier.py has this attribute.")
        except Exception as e:
            print(f"Warning: Could not save class mapping: {e}")
        # --- END OF NEW BLOCK ---
        
        # Step 3: Initialize model
        orchestrator.initialize_model(num_categories)
        
        # Step 4: Execute training with progress tracking
        loss_history, accuracy_history = orchestrator.execute_training_cycle(epochs=10)
        
        # Step 5: Print comprehensive summary
        orchestrator.print_training_summary(loss_history, accuracy_history)
        
        # Step 6: Visualize results (imported from plant_classifier.py)
        visualize_training_progress(loss_history, accuracy_history)
        
        # Step 7: Save model
        model_path = orchestrator.save_trained_model()
        
        # Final message
        print("\nTRAINING ORCHESTRATION COMPLETED!")
        print("=" * 40)
        print("Your plant disease classifier is ready for deployment!")
        print("Next steps:")
        print("   - Run inference.py to test the model with new images")
        print("   - Run app.py to launch the Streamlit web application")
        
    except Exception as e:
        print(f"Training orchestration failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()