# gpu_validator.py - Hardware validation for model training
import torch
import subprocess
import sys

print("🔍 HARDWARE VALIDATION FOR MODEL TRAINING")
print("=" * 50)

def validate_compute_environment():
    """Validate the computing environment for model training"""
    print("🔧 COMPUTE ENVIRONMENT VALIDATION")
    print("=" * 40)
    
    # Check framework availability
    print(f"✅ Deep Learning Framework: PyTorch {torch.__version__}")
    
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"✅ CUDA Compute Platform: {cuda_available}")
    
    if cuda_available:
        # GPU details
        device_count = torch.cuda.device_count()
        print(f"✅ Compute Devices: {device_count}")
        
        for i in range(device_count):
            device_name = torch.cuda.get_device_name(i)
            device_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"   Device {i}: {device_name}")
            print(f"     Memory: {device_memory:.1f} GB")
    else:
        print("❌ CUDA compute platform not available")
        
    return cuda_available

def test_compute_performance():
    """Test computational performance"""
    print("\n🚀 COMPUTATIONAL PERFORMANCE TEST")
    print("=" * 40)
    
    if not torch.cuda.is_available():
        print("❌ Skipping compute test - CUDA not available")
        return False
    
    try:
        # Set compute device
        compute_device = torch.device('cuda:0')
        print(f"✅ Using compute device: {compute_device}")
        
        # Create sample tensors
        tensor_a = torch.randn(2000, 2000).to(compute_device)
        tensor_b = torch.randn(2000, 2000).to(compute_device)
        
        # Perform matrix operations
        result = torch.matmul(tensor_a, tensor_b)
        
        print(f"✅ Computational test successful!")
        print(f"   Tensor dimensions: {result.shape}")
        print(f"   Compute device: {result.device}")
        
        return True
        
    except Exception as e:
        print(f"❌ Computational test failed: {e}")
        return False

def main():
    print("Validating compute environment for model training...")
    
    # Validate environment
    compute_available = validate_compute_environment()
    
    # Test performance
    if compute_available:
        compute_working = test_compute_performance()
    else:
        compute_working = False
    
    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 40)
    print(f"✅ Compute Platform: {'PASS' if compute_available else 'FAIL'}")
    print(f"✅ Performance Test: {'PASS' if compute_working else 'FAIL'}")
    
    if compute_available and compute_working:
        print("\n🎉 SUCCESS! Compute environment ready for model training!")
    else:
        print("\n🔧 Setup required for optimal performance")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")