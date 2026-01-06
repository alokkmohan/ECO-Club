@echo off
REM Automated hourly sync for Task Scheduler

cd /d "d:\Eco club"
python final_auto_sync.py

REM Exit code for Task Scheduler
exit /b 0
