@echo off
REM ===================================================
REM Easy Build Script for Camera Finder
REM Just double-click this file to build the app!
REM ===================================================

echo ===================================================
echo CAMERA FINDER - EASY BUILD
echo ===================================================
echo.
echo This will create a portable Windows application
echo.
pause

REM Run the Python build script
python build_portable_app.py

echo.
echo ===================================================
echo BUILD COMPLETE!
echo ===================================================
echo.
echo If successful, your app is in: CameraFinder_Portable
echo.
pause
