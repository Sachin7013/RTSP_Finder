#!/usr/bin/env python3
"""
Download ffprobe.exe for Windows
This script downloads ffprobe which is needed to test camera streams
"""

import os
import urllib.request
import zipfile
import shutil

def download_ffprobe():
    """Download ffprobe.exe from official source"""
    
    print("📥 Downloading ffprobe for Windows...")
    
    # URL for Windows ffmpeg build (includes ffprobe)
    # Using a stable, reliable source
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    # Alternative simpler URL (smaller download)
    # This is from BtbN's builds which are reliable
    simple_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        # Create temp folder
        temp_dir = "temp_ffmpeg"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Download the zip file
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        
        print("Downloading from GitHub (this may take a minute)...")
        urllib.request.urlretrieve(simple_url, zip_path)
        
        print("✅ Download complete!")
        print("📦 Extracting ffprobe.exe...")
        
        # Extract the zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find ffprobe.exe in the extracted files
        ffprobe_found = False
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == "ffprobe.exe":
                    source_path = os.path.join(root, file)
                    dest_path = "ffprobe.exe"
                    
                    # Copy ffprobe.exe to current directory
                    shutil.copy2(source_path, dest_path)
                    ffprobe_found = True
                    print(f"✅ ffprobe.exe saved to: {os.path.abspath(dest_path)}")
                    break
            if ffprobe_found:
                break
        
        # Clean up temp files
        print("🧹 Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        
        if ffprobe_found:
            print("\n✅ Success! ffprobe.exe is ready to use!")
        else:
            print("\n❌ Error: Could not find ffprobe.exe in the download")
            
    except Exception as e:
        print(f"\n❌ Error downloading ffprobe: {e}")
        print("\nAlternative: You can manually download ffmpeg from:")
        print("  https://ffmpeg.org/download.html")
        print("  Extract it and copy ffprobe.exe to this folder")

if __name__ == "__main__":
    # Check if ffprobe.exe already exists
    if os.path.exists("ffprobe.exe"):
        print("✅ ffprobe.exe already exists!")
        response = input("Do you want to download it again? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing ffprobe.exe")
            exit(0)
    
    download_ffprobe()
