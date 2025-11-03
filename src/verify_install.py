import pkg_resources

required_packages = [
    'tensorflow', 'keras', 'opencv-python', 'pandas', 'numpy',
    'scikit-learn', 'streamlit', 'matplotlib', 'pillow', 'jupyter'
]

print("🔍 Verifying Package Installations:")
for package in required_packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"✅ {package:20} v{version}")
    except pkg_resources.DistributionNotFound:
        print(f"❌ {package:20} NOT INSTALLED")

print("\n🎯 Core functionality test:")
try:
    import tensorflow as tf
    import cv2
    import streamlit as st
    print("✅ All core libraries imported successfully!")
    print(f"✅ TensorFlow can access GPU: {tf.config.list_physical_devices('GPU')}")
except ImportError as e:
    print(f"❌ Import error: {e}")