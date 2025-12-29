# test_model.py - Validate your trained model
import torch
import matplotlib.pyplot as plt
from plant_classifier import DiseaseClassificationModel, PlantImageDataset
from torchvision import transforms

def test_single_image(model, image_path, class_names):
    """Test model on a single plant image"""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path).convert('RGB')
    input_tensor = transform(image).unsqueeze(0)
    
    model.eval()
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        predicted_class = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_class].item()
    
    print(f"Prediction: {class_names[predicted_class]}")
    print(f"Confidence: {confidence:.2%}")
    
    # Display image with prediction
    plt.imshow(image)
    plt.title(f"Predicted: {class_names[predicted_class]}\nConfidence: {confidence:.2%}")
    plt.axis('off')
    plt.show()

# Load your trained model
model = DiseaseClassificationModel(num_classes=38)
model.load_state_dict(torch.load('models/plant_classifier_final.pth'))
model.eval()

# Test with sample images
class_names = ['Tomato_Bacterial_spot', 'Tomato_Early_blight', ...] # Your class names
test_single_image(model, 'test_leaf.jpg', class_names)