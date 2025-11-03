# debug_matplotlib.py - Let's find the exact matplotlib issue

print("🔍 Debugging matplotlib...")

# Test 1: Can we import matplotlib at all?
try:
    import matplotlib
    print("✅ matplotlib base package - OK")
    print(f"   Version: {matplotlib.__version__}")
except Exception as e:
    print(f"❌ matplotlib base package - FAILED: {e}")
    exit()

# Test 2: Can we import pyplot specifically?
try:
    import matplotlib.pyplot as plt
    print("✅ matplotlib.pyplot - OK")
except Exception as e:
    print(f"❌ matplotlib.pyplot - FAILED: {e}")
    print("   This might be a backend issue")

# Test 3: Check matplotlib configuration
try:
    import matplotlib
    print(f"✅ Matplotlib backend: {matplotlib.get_backend()}")
    print(f"✅ Matplotlib config directory: {matplotlib.get_configdir()}")
except Exception as e:
    print(f"❌ Matplotlib config check - FAILED: {e}")

# Test 4: Try a simple plot (this might reveal the real issue)
try:
    import matplotlib.pyplot as plt
    # Create a simple plot without displaying it
    plt.figure()
    plt.plot([1, 2, 3], [4, 5, 6])
    plt.title("Test Plot")
    plt.close()  # Close without showing
    print("✅ Simple plot creation - OK")
except Exception as e:
    print(f"❌ Plot creation - FAILED: {e}")
    print("   This is likely a GUI/display backend issue")

print("\n🎯 Debug complete!")
input("Press Enter to exit...")