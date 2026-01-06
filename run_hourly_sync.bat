@echo off
REM Automated hourly sync - to be scheduled in Task Scheduler

cd /d "d:\Eco club"
python session_sync.py >> "d:\Eco club\logs\sync_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log" 2>&1
