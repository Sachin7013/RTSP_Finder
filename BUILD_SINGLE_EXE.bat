@echo off
REM =====================================================
REM Build a SINGLE portable EXE file
REM No installation required on target computers!
REM =====================================================

cls
echo =====================================================
echo    CAMERA FINDER - SINGLE EXE BUILDER
echo =====================================================
echo.
echo This will create ONE portable .exe file that:
echo   - Works on any Windows computer
echo   - Needs NO Python installation
echo   - Needs NO package installation
echo   - Includes everything needed
echo.
echo Press any key to start building...
pause > nul

echo.
echo Building your portable EXE...
echo.

REM Run the build script
python build_single_exe.py

echo.
echo =====================================================
echo If successful, your portable EXE is ready:
echo   - CameraFinder_Portable.exe (single file!)
echo =====================================================
echo.
pause
