# -*- mode: python ; coding: utf-8 -*-
"""
Improved PyInstaller spec for Camera Finder
Properly bundles all dependencies for a portable .exe
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

# Collect all ONVIF and related packages
onvif_datas, onvif_binaries, onvif_hiddenimports = collect_all('onvif')
# Also explicitly collect ONVIF WSDL files (critical!)
onvif_wsdl_files = collect_data_files('onvif', includes=['**/*.wsdl', '**/*.xsd'])
onvif_datas.extend(onvif_wsdl_files)

zeep_datas, zeep_binaries, zeep_hiddenimports = collect_all('zeep')
wsdiscovery_datas, wsdiscovery_binaries, wsdiscovery_hiddenimports = collect_all('wsdiscovery')

# Combine all collected data
all_datas = onvif_datas + zeep_datas + wsdiscovery_datas
all_binaries = onvif_binaries + zeep_binaries + wsdiscovery_binaries
all_hiddenimports = onvif_hiddenimports + zeep_hiddenimports + wsdiscovery_hiddenimports

# Add ffprobe.exe to the bundle - CRITICAL!
if os.path.exists('ffprobe.exe'):
    all_datas.append(('ffprobe.exe', '.'))
    print("✅ ffprobe.exe will be bundled")
else:
    print("⚠️ WARNING: ffprobe.exe not found! Stream testing will fail!")

# Additional hidden imports that might be missed
additional_hidden = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.messagebox',
    'lxml',
    'lxml.etree',
    'lxml._elementpath',
    'requests',
    'urllib3',
    'certifi',
    'socket',
    'threading',
    'subprocess',
]

all_hiddenimports.extend(additional_hidden)

a = Analysis(
    ['camera_gui_fixed.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
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
        'PySide2',
        'PySide6',
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
    name='CameraFinder_Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see debug messages
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
