#!/usr/bin/env python3
"""
Build Script - Creates a portable Windows application
This script creates a portable .exe that can run on any Windows computer

Steps:
1. Install dependencies
2. Download ffprobe if needed
3. Create the .exe using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def check_python():
    """Check if Python is installed properly"""
    print("🐍 Checking Python version...")
    version = sys.version
    print(f"  Python {version}")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        return False
    print("✅ Python version is good!")
    return True

def install_requirements():
    """Install required Python packages"""
    print("\n📦 Installing required packages...")
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        print("Try running: pip install -r requirements.txt")
        return False

def check_ffprobe():
    """Check if ffprobe.exe exists"""
    print("\n🎥 Checking for ffprobe.exe...")
    if os.path.exists("ffprobe.exe"):
        print("✅ ffprobe.exe found!")
        return True
    else:
        print("❌ ffprobe.exe not found!")
        print("Running download script...")
        try:
            subprocess.check_call([sys.executable, "download_ffprobe.py"])
            return os.path.exists("ffprobe.exe")
        except:
            print("Please run: python download_ffprobe.py")
            return False

def build_exe():
    """Build the portable executable using PyInstaller"""
    print("\n🔨 Building portable application...")
    
    # PyInstaller command with options
    command = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # Create a folder with all files (portable)
        "--windowed",  # No console window (GUI only)
        "--name", "CameraFinder",  # Name of the exe
        "--icon", "NONE",  # You can add an icon file here
        "--add-data", "ffprobe.exe;.",  # Include ffprobe.exe
        "--noconfirm",  # Overwrite without asking
        "--clean",  # Clean temporary files
        "camera_gui.py"  # The main Python file
    ]
    
    print("Running PyInstaller...")
    print("This may take 1-2 minutes...")
    
    try:
        subprocess.check_call(command)
        print("✅ Build successful!")
        return True
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False

def organize_output():
    """Organize the output files into a nice portable folder"""
    print("\n📁 Organizing portable application...")
    
    dist_folder = "dist/CameraFinder"
    portable_folder = "CameraFinder_Portable"
    
    if os.path.exists(dist_folder):
        # Remove old portable folder if exists
        if os.path.exists(portable_folder):
            # Remove old portable folder if it exists (clean up previous builds)
            shutil.rmtree(portable_folder)
        
        # Move dist folder to portable folder
        shutil.move(dist_folder, portable_folder)
        
        print(f"✅ Portable app created in: {os.path.abspath(portable_folder)}")
        print("\n📂 Portable folder contains:")
        print("  • CameraFinder.exe - The main application")
        print("  • ffprobe.exe - For testing camera streams")
        print("  • Supporting files - Required libraries")
        
        return True
    else:
        print("❌ Build output not found!")
        return False

def create_readme():
    """Create a simple README file for users"""
    readme_content = """CAMERA FINDER - PORTABLE APPLICATION
====================================

HOW TO USE:
-----------
1. Double-click CameraFinder.exe to start the application
2. Click "WiFi Cameras" button
3. Enter camera username and password (usually "admin")
4. Wait for the scan to complete (10-30 seconds)
5. Copy the RTSP URLs that are found

REQUIREMENTS:
------------
• Windows 7/8/10/11
• Connected to the same WiFi network as your cameras
• Camera username and password

TROUBLESHOOTING:
---------------
• Make sure Windows Firewall is not blocking the app
• Try running as Administrator if cameras aren't found
• Ensure cameras are ONVIF-compatible

PORTABLE:
---------
This entire folder can be copied to any Windows computer.
No installation required!
"""
    
    with open("CameraFinder_Portable/README.txt", "w") as f:
        f.write(readme_content)
    print("\n📄 Created README.txt with instructions")

def main():
    """Main build process"""
    print("="*50)
    print("CAMERA FINDER - BUILD SCRIPT")
    print("Creating Portable Windows Application")
    print("="*50)
    
    # Step 1: Check Python
    if not check_python():
        return
    
    # Step 2: Install packages
    if not install_requirements():
        print("\n⚠️  Fix the package installation and try again")
        return
    
    # Step 3: Check ffprobe
    if not check_ffprobe():
        print("\n⚠️  ffprobe.exe is required. Please download it first.")
        return
    
    # Step 4: Build the exe
    if not build_exe():
        print("\n⚠️  Build failed. Check the error messages above.")
        return
    
    # Step 5: Organize output
    if not organize_output():
        return
    
    # Step 6: Create README
    create_readme()
    
    # Success!
    print("\n" + "="*50)
    print("🎉 SUCCESS! Portable app is ready!")
    print("="*50)
    print("\n📁 Your portable app is in: CameraFinder_Portable")
    print("📦 You can copy this folder to any Windows computer")
    print("🚀 Run CameraFinder.exe to start the application")
    print("\nNo installation needed - it's completely portable!")
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
