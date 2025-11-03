# check_nvidia.py - Comprehensive NVIDIA system check
import subprocess
import sys

def check_nvidia_drivers():
    """Check NVIDIA drivers and GPU information"""
    print("🔍 CHECKING NVIDIA DRIVERS & GPU")
    print("=" * 50)
    
    try:
        # Run nvidia-smi to get GPU information
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ NVIDIA Drivers are installed!")
            print("\n📊 GPU Information:")
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if i < 10:  # Show first 10 lines
                    print(f"   {line}")
            return True
        else:
            print("❌ nvidia-smi failed")
            return False
            
    except FileNotFoundError:
        print("❌ nvidia-smi not found - NVIDIA drivers not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking NVIDIA: {e}")
        return False

def check_cuda_installation():
    """Check if CUDA is installed"""
    print("\n🔍 CHECKING CUDA INSTALLATION")
    print("=" * 40)
    
    try:
        # Check nvcc (CUDA compiler)
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ CUDA Toolkit is installed!")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'release' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ nvcc not found - CUDA Toolkit not installed")
            return False
    except Exception as e:
        print(f"❌ CUDA check failed: {e}")
        return False

def main():
    print("🎯 NVIDIA RTX 3050 SETUP VALIDATION")
    print("=" * 50)
    
    drivers_ok = check_nvidia_drivers()
    cuda_ok = check_cuda_installation()
    
    print("\n📊 VALIDATION SUMMARY:")
    print(f"   NVIDIA Drivers: {'✅' if drivers_ok else '❌'}")
    print(f"   CUDA Toolkit: {'✅' if cuda_ok else '❌'}")
    
    if drivers_ok and cuda_ok:
        print("\n🎉 Your NVIDIA setup looks good!")
        print("   Let's install TensorFlow with GPU support")
    else:
        print("\n🔧 SETUP REQUIRED:")
        if not drivers_ok:
            print("   1. Install NVIDIA drivers for RTX 3050")
        if not cuda_ok:
            print("   2. Install CUDA Toolkit 11.8")
            print("   3. Install cuDNN 8.6")
        
        print("\n🔗 Download Links:")
        print("   NVIDIA Drivers: https://www.nvidia.com/Download/index.aspx")
        print("   CUDA 11.8: https://developer.nvidia.com/cuda-11-8-0-download-archive")
        print("   cuDNN: https://developer.nvidia.com/cudnn (requires account)")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")