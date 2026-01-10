@echo off
REM ============================================
REM ECO CLUB - AUTO UPDATE AND PUSH
REM ============================================
REM 
REM Instructions:
REM 1. Download latest files from national website
REM 2. Replace these 2 files in D:\Eco club folder:
REM    - All_Schools_with_Notifications_UTTAR PRADESH.xlsx
REM    - UTTAR PRADESH.xlsx
REM 3. Double-click this file to auto-update everything!
REM ============================================

echo.
echo ========================================
echo    ECO CLUB - AUTO UPDATE ^& PUSH
echo ========================================
echo.
echo This will:
echo  1. Merge notification and tree data
echo  2. Generate summary Excel report
echo  3. Push to GitHub
echo  4. Update Streamlit dashboard
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Starting automated update...
echo.

REM Activate virtual environment and run script
call "D:\Eco club\venv\Scripts\activate.bat"
python "D:\Eco club\AUTO_UPDATE_AND_PUSH.py"

echo.
echo ========================================
echo Press any key to close this window...
pause >nul
