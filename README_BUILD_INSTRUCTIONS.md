# 📷 Camera Finder - Complete Build Guide for Beginners

## 🎯 What This Does
Creates a **portable Windows application** (no installation needed!) that finds cameras on your WiFi network and gives you their RTSP stream URLs.

---

## 📋 Prerequisites (What You Need First)

### 1. **Install Python** (if you don't have it)
- Go to: https://www.python.org/downloads/
- Download Python 3.12 or newer
- **IMPORTANT**: During installation, ✅ CHECK "Add Python to PATH"
- Click "Install Now"

### 2. **Check Python is Working**
Open Command Prompt (press `Win+R`, type `cmd`, press Enter) and type:
```
python --version
```
You should see something like: `Python 3.12.0`

---

## 🚀 Step-by-Step Build Instructions

### Method 1: **EASIEST - Just Double-Click** 🖱️

1. **Open the project folder** in Windows Explorer
2. **Double-click** `BUILD_APP.bat`
3. Press any key when prompted
4. Wait 2-3 minutes for it to complete
5. **Done!** Your app is in the `CameraFinder_Portable` folder

### Method 2: **Using Command Prompt** 💻

1. **Open Command Prompt** in the project folder:
   - Right-click in the folder
   - Select "Open in Terminal" or "Open PowerShell window here"

2. **Run these commands** one by one:

```bash
# Step 1: Install required packages
pip install -r requirements.txt

# Step 2: Download ffprobe (needed for testing cameras)
python download_ffprobe.py

# Step 3: Build the portable app
python build_portable_app.py
```

3. **Wait** for each step to complete
4. **Done!** Your app is in the `CameraFinder_Portable` folder

---

## ✅ What You Get

After building, you'll have a folder called **`CameraFinder_Portable`** containing:
- 📁 **CameraFinder.exe** - The main application
- 📁 **ffprobe.exe** - Tool for testing camera streams  
- 📁 Other support files

**This entire folder is portable!** You can:
- Copy it to a USB drive
- Move it to another computer
- Share it with others
- No installation needed!

---

## 🎮 How to Use the App

1. **Double-click** `CameraFinder.exe`
2. Click **"WiFi Cameras"** button
3. Enter camera **username** and **password** (usually "admin")
4. Wait 10-30 seconds for scanning
5. **Copy the RTSP URLs** that are found
6. Use these URLs in VLC Media Player or other software

---

## ❓ Common Questions

### **Q: Is Visual Studio or WPF needed?**
**A: NO!** ✅ We use Python with tkinter (built-in GUI library). No Visual Studio required!

### **Q: How is this portable?**
**A:** PyInstaller bundles everything into one folder. No installation needed - just copy and run!

### **Q: What if build fails?**
**A:** Usually it's because:
- Python not installed correctly
- Missing pip packages - run: `pip install -r requirements.txt`
- Antivirus blocking PyInstaller - temporarily disable it

### **Q: Can I share this with others?**
**A:** Yes! The `CameraFinder_Portable` folder works on any Windows PC. No Python needed on their computer!

---

## 🛠️ Troubleshooting

### **"python is not recognized"**
- Python not installed or not in PATH
- Reinstall Python and CHECK "Add to PATH"

### **"No module named 'wsdiscovery'"**
Run: `pip install -r requirements.txt`

### **Build takes forever**
- Normal! PyInstaller takes 2-3 minutes
- Antivirus might slow it down

### **App won't start**
- Try running as Administrator
- Check Windows Defender didn't quarantine it

---

## 📁 File Structure Explained

```
CameraAPI/
│
├── camera_gui.py           # Main GUI application (source code)
├── download_ffprobe.py     # Downloads ffprobe.exe
├── build_portable_app.py   # Build script (creates the exe)
├── BUILD_APP.bat          # Easy double-click build
├── requirements.txt       # Python packages needed
├── ffprobe.exe           # (Downloaded) Video stream tester
│
└── CameraFinder_Portable/  # (Created after build)
    ├── CameraFinder.exe   # Your portable app!
    ├── ffprobe.exe       
    └── [support files]
```

---

## 🎯 Summary for Complete Beginners

1. **Install Python** (one time only)
2. **Double-click** `BUILD_APP.bat`  
3. **Wait** 2-3 minutes
4. **Done!** Find your app in `CameraFinder_Portable`
5. **Copy** that folder anywhere - it's portable!

No Visual Studio, no complex setup, no installation needed on target PCs!

---

## 💡 Tips

- Keep the entire `CameraFinder_Portable` folder together
- The app needs to be on the same WiFi network as cameras
- Most cameras use username: "admin" 
- Try password: "admin", "12345", or check camera manual
- Works with ONVIF-compatible IP cameras

---

## 🆘 Need Help?

If you're stuck:
1. Make sure Python is installed with "Add to PATH" checked
2. Run Command Prompt as Administrator
3. Temporarily disable antivirus during build
4. All files must be in the same folder

The app is designed to be simple and beginner-friendly! 😊
