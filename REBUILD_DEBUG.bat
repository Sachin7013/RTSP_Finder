@echo off
echo.
echo =====================================================
echo    REBUILDING WITH FIXES
echo =====================================================
echo.
echo Fixes applied:
echo   ✅ ONVIF WSDL files properly bundled
echo   ✅ RTSP path priority fixed (ch0_0.264 before live/channel0)
echo   ✅ Better error handling
echo.
pause

echo.
echo Cleaning...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist  
if exist CameraFinder_Debug.exe del CameraFinder_Debug.exe

echo Building DEBUG version...
python -m PyInstaller CameraFinder_Debug.spec --clean --noconfirm

if exist dist\CameraFinder_Debug.exe (
    copy dist\CameraFinder_Debug.exe CameraFinder_Debug.exe
    echo.
    echo =====================================================
    echo ✅ BUILD SUCCESSFUL!
    echo =====================================================
    echo.
    echo Now test CameraFinder_Debug.exe
    echo.
    echo You should see:
    echo   ✅ ONVIF WSDL folder found (no warning!)
    echo   ✅ cameras with CORRECT URLs

    echo.
) else (
    echo ❌ BUILD FAILED!
)
pause
