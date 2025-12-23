@echo off
cd /d "D:\Eco club"
git add .
git commit -m "Add district summary totals and fix metrics confusion - metrics now show complete totals while status filter only affects table"
git push
pause
