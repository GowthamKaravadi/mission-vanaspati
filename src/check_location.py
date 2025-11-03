# check_location.py - Simple script to check where we are
import os
from pathlib import Path

print("📍 Checking our current location...")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {Path(__file__).absolute()}")

# List what's in the current directory
print("\n📂 Contents of current directory:")
for item in Path('.').iterdir():
    print(f"  {item.name}")

input("\nPress Enter to close...")