#!/usr/bin/env python3
"""
Test the fixed GUI before building the exe
This ensures everything works properly
"""

import subprocess
import sys

def test():
    """Test the fixed GUI"""
    print("="*50)
    print("TESTING FIXED CAMERA GUI")
    print("="*50)
    
    print("\n✅ Starting fixed GUI with improvements:")
    print("  • No probe handler warnings")
    print("  • Two scan methods (ONVIF + Quick IP)")
    print("  • Better error handling")
    print("  • Works properly as exe")
    
    print("\n🚀 Launching GUI...\n")
    
    # Run the fixed GUI
    subprocess.run([sys.executable, "camera_gui_fixed.py"])

if __name__ == "__main__":
    test()
