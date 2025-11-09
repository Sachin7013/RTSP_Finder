#!/usr/bin/env python3
"""
Build a SINGLE portable .exe file - No installation required!
This creates ONE .exe file that works on any Windows computer
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
    return True

def install_packages():
    """Install required packages for building"""
    print("\n📦 Installing build requirements...")
    packages = [
        "pyinstaller",
        "wsdiscovery", 
        "onvif-zeep"
    ]
    
    for pkg in packages:
        print(f"  Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
    
    print("✅ All packages installed")
    return True

def download_ffprobe():
    """Download ffprobe.exe if not present"""
    if os.path.exists("ffprobe.exe"):
        print("✅ ffprobe.exe already exists")
        return True
        
    print("\n📥 Downloading ffprobe...")
    
    # Simple direct download URL for ffprobe
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        print("  Downloading from GitHub...")
        temp_dir = "temp_ffmpeg_download"
        os.makedirs(temp_dir, exist_ok=True)
        
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        urllib.request.urlretrieve(url, zip_path)
        
        print("  Extracting ffprobe.exe...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find and copy ffprobe.exe
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == "ffprobe.exe":
                    source = os.path.join(root, file)
                    shutil.copy2(source, "ffprobe.exe")
                    print("✅ ffprobe.exe downloaded successfully")
                    shutil.rmtree(temp_dir)
                    return True
                    
        print("❌ Could not find ffprobe.exe in download")
        shutil.rmtree(temp_dir)
        return False
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return False

def create_spec_file():
    """Create a custom .spec file for PyInstaller with all fixes"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'wsdiscovery',
    'wsdiscovery.daemon',
    'wsdiscovery.actions',
    'wsdiscovery.threaded',
    'onvif',
    'onvif.client',
    'zeep',
    'zeep.wsdl',
    'zeep.xsd',
    'zeep.transports',
    'lxml',
    'lxml.etree',
    'lxml._elementpath',
    'urllib3',
    'requests',
    'certifi',
]

a = Analysis(
    ['camera_gui_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ffprobe.exe', '.'),  # Include ffprobe.exe in the bundle
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CameraFinder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here
)
'''
    
    with open("CameraFinder.spec", "w") as f:
        f.write(spec_content)
    
    print("✅ Created custom spec file")
    return True

def build_exe():
    """Build the single portable .exe"""
    print("\n🔨 Building single portable .exe...")
    print("This may take 2-3 minutes...\n")
    
    # Clean previous builds
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Build using the spec file
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "CameraFinder.spec",
            "--clean",
            "--noconfirm"
        ])
        print("\n✅ Build successful!")
        return True
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return False

def verify_exe():
    """Verify the built exe exists and show info"""
    exe_path = "dist/CameraFinder.exe"
    
    if not os.path.exists(exe_path):
        print("❌ EXE not found at expected location")
        return False
    
    # Get file size
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    
    print("\n" + "="*60)
    print("🎉 SUCCESS! Your portable EXE is ready!")
    print("="*60)
    print(f"\n📁 Location: {os.path.abspath(exe_path)}")
    print(f"📊 Size: {size_mb:.1f} MB")
    print("\n✅ This is a SINGLE PORTABLE FILE that:")
    print("   • Works on any Windows 7/8/10/11 computer")
    print("   • Requires NO Python installation")
    print("   • Requires NO additional downloads")
    print("   • Includes ffprobe for stream testing")
    print("   • Just double-click to run!")
    
    # Copy to root directory for easy access
    final_exe = "CameraFinder_Portable.exe"
    shutil.copy2(exe_path, final_exe)
    print(f"\n📦 Also copied to: {os.path.abspath(final_exe)}")
    
    return True

def main():
    """Main build process"""
    print("="*60)
    print("CAMERA FINDER - SINGLE EXE BUILDER")
    print("Creating a truly portable Windows application")
    print("="*60)
    
    # Step 1: Check Python
    if not check_python():
        return 1
    
    # Step 2: Install packages
    try:
        install_packages()
    except Exception as e:
        print(f"❌ Failed to install packages: {e}")
        return 1
    
    # Step 3: Download ffprobe
    if not download_ffprobe():
        print("\n⚠️  ffprobe.exe is required for stream testing")
        print("You can manually download ffmpeg and copy ffprobe.exe here")
        response = input("Continue without ffprobe? (y/n): ")
        if response.lower() != 'y':
            return 1
    
    # Step 4: Create spec file
    if not create_spec_file():
        return 1
    
    # Step 5: Build the exe
    if not build_exe():
        return 1
    
    # Step 6: Verify
    if not verify_exe():
        return 1
    
    print("\n✅ Build complete! Your portable EXE is ready to use!")
    print("No installation required - just double-click to run!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
