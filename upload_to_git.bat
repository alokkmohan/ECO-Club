@echo off
REM Quick script to upload Excel files to Git
REM Run this after manually downloading the files

echo ============================================================
echo Uploading Eco Club Data to Git
echo ============================================================

cd /d "d:\Eco club"

echo.
echo Adding files to git...
git add "UTTAR PRADESH.xlsx"
git add "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"

echo.
echo Committing changes...
git commit -m "Updated Eco Club data - %date% %time%"

echo.
echo Pushing to GitHub...
git push

echo.
echo ============================================================
echo Upload Complete!
echo ============================================================
pause
