#!/usr/bin/env python3
"""
Improved build script for Camera Finder portable .exe
Simple, reliable, and handles all dependencies properly
"""

import os
import sys
import subprocess
import shutil

def print_header(text):
    """Print a nice header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_requirements():
    """Check that all required files exist"""
    print_header("Checking Requirements")
    
    required_files = [
        'camera_gui_fixed.py',
        'ffprobe.exe',
        'CameraFinder_Improved.spec'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            missing.append(file)
    
    if missing:
        print(f"\n❌ Missing required files: {', '.join(missing)}")
        return False
    
    return True

def install_pyinstaller():
    """Ensure PyInstaller is installed"""
    print_header("Installing/Updating PyInstaller")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--upgrade", "pyinstaller", "--quiet"
        ])
        print("✅ PyInstaller is ready")
        return True
    except Exception as e:
        print(f"❌ Failed to install PyInstaller: {e}")
        return False

def clean_previous_builds():
    """Clean up previous build artifacts"""
    print_header("Cleaning Previous Builds")
    
    folders_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['CameraFinder_Portable.exe']
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️  Removed {folder}/")
    
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Removed {file}")
    
    print("✅ Clean complete")

def build_executable():
    """Build the executable using PyInstaller"""
    print_header("Building Portable Executable")
    print("This may take 2-5 minutes...")
    print("Please wait...\n")
    
    try:
        # Run PyInstaller with the spec file
        result = subprocess.run(
            [
                sys.executable, "-m", "PyInstaller",
                "CameraFinder_Improved.spec",
                "--clean",
                "--noconfirm"
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            return True
        else:
            print(f"❌ Build failed with return code {result.returncode}")
            print("\nError output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def verify_executable():
    """Verify the built executable exists and show info"""
    print_header("Verifying Build")
    
    exe_path = os.path.join("dist", "CameraFinder_Portable.exe")
    
    if not os.path.exists(exe_path):
        print("❌ Executable not found!")
        print(f"Expected location: {os.path.abspath(exe_path)}")
        return False
    
    # Get file size
    size_bytes = os.path.getsize(exe_path)
    size_mb = size_bytes / (1024 * 1024)
    
    print(f"✅ Executable found!")
    print(f"📁 Location: {os.path.abspath(exe_path)}")
    print(f"📊 Size: {size_mb:.1f} MB ({size_bytes:,} bytes)")
    
    # Copy to root directory for easy access
    root_exe = "CameraFinder_Portable.exe"
    shutil.copy2(exe_path, root_exe)
    print(f"\n📦 Copied to: {os.path.abspath(root_exe)}")
    
    return True

def main():
    """Main build process"""
    print_header("Camera Finder - Portable EXE Builder")
    print("Creating a single-file Windows executable")
    print("No installation required on target computers!")
    
    # Step 1: Check requirements
    if not check_requirements():
        print("\n❌ Build cannot proceed - missing requirements")
        return 1
    
    # Step 2: Install PyInstaller
    if not install_pyinstaller():
        print("\n❌ Build cannot proceed - PyInstaller installation failed")
        return 1
    
    # Step 3: Clean previous builds
    clean_previous_builds()
    
    # Step 4: Build executable
    if not build_executable():
        print("\n❌ Build failed!")
        print("\nTroubleshooting:")
        print("1. Make sure all packages are installed: pip install -r requirements.txt")
        print("2. Check that Python and pip are working correctly")
        print("3. Try running: pip install --upgrade pyinstaller onvif-zeep wsdiscovery")
        return 1
    
    # Step 5: Verify
    if not verify_executable():
        print("\n❌ Verification failed!")
        return 1
    
    # Success!
    print_header("✅ BUILD SUCCESSFUL!")
    print("\n🎉 Your portable executable is ready!")
    print("\n📦 File: CameraFinder_Portable.exe")
    print("\n✨ Features:")
    print("   • Single portable file")
    print("   • Works on Windows 7/8/10/11")
    print("   • No Python required")
    print("   • No installation needed")
    print("   • Asks for username/password when started")
    print("   • Discovers cameras automatically")
    print("   • Provides RTSP URLs")
    print("\n🚀 Share this file with your friend!")
    print("   They just need to double-click it to run.")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        print("\n" + "=" * 60)
        input("Press Enter to close...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        input("Press Enter to close...")
        sys.exit(1)
