#!/usr/bin/env python3
"""
Quick Test Script - Test the GUI without building
Run this to make sure everything works before creating the .exe
"""

import sys
import subprocess

def test_gui():
    """Test if the GUI runs properly"""
    print("="*50)
    print("TESTING CAMERA FINDER GUI")
    print("="*50)
    
    print("\n🔍 Checking Python modules...")
    
    # Check required modules
    required = ["wsdiscovery", "onvif"]
    missing = []
    
    for module in required:
        try:
            __import__(module)
            print(f"  ✅ {module} - OK")
        except ImportError:
            print(f"  ❌ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print("\n⚠️  Missing modules! Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Modules installed! Please run this script again.")
        return
    
    print("\n✅ All modules OK!")
    print("\n🚀 Starting GUI application...")
    print("-"*50)
    print("The Camera Finder window should open now.")
    print("Test it by clicking the WiFi Cameras button.")
    print("-"*50)
    
    # Run the GUI
    subprocess.run([sys.executable, "camera_gui.py"])

if __name__ == "__main__":
    test_gui()
