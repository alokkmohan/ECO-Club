@echo off
REM Batch file to run automated sync
REM This can be scheduled in Windows Task Scheduler

cd /d "d:\Eco club"
python auto_sync.py

REM Optional: Keep window open to see results
REM Remove the line below if running from Task Scheduler
pause
