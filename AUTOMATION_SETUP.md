# Automated Eco Club Data Sync - Setup Guide

## ✅ Complete Automation hai ab!

## Setup (One-time only)

### 1. Credentials ready hain?
`.env` file me apni userid aur password hone chahiye:
```
ECO_USERID=your_userid
ECO_PASSWORD=your_password
```

### 2. Test Manual Run
Pehle ek baar manually test karein:
```powershell
python auto_sync.py
```

## Windows Task Scheduler Setup (Har ghante auto-run)

### Option 1: Simple Method (Recommended)

1. **Task Scheduler Open karein:**
   - Windows Key + R → type `taskschd.msc` → Enter

2. **Create Basic Task:**
   - Right side me "Create Basic Task" click karein
   - Name: `Eco Club Auto Sync`
   - Description: `Automatically downloads and uploads Eco Club data every hour`
   - Click Next

3. **Trigger (Kab chalega):**
   - Select: **Daily**
   - Click Next
   - Start date: Aaj ka date
   - Recur every: 1 days
   - Click Next

4. **Action:**
   - Select: **Start a program**
   - Click Next
   - Program/script: Browse karke select karein: `d:\Eco club\run_auto_sync.bat`
   - Click Next

5. **Advanced Settings:**
   - Finish par click karne se pehle, "Open Properties" checkbox check karein
   - Click Finish

6. **Properties me:**
   - **Triggers** tab me:
     - Select the trigger aur "Edit" click karein
     - "Repeat task every" checkbox enable karein
     - Select: **1 hour**
     - Duration: **Indefinitely**
     - Click OK
   
   - **Settings** tab me:
     - ✅ "Run task as soon as possible after a scheduled start is missed"
     - ✅ "If the task fails, restart every: 10 minutes"
     - Click OK

### Option 2: PowerShell Command (Advanced)

Administrator PowerShell me yeh command run karein:

```powershell
$action = New-ScheduledTaskAction -Execute "d:\Eco club\run_auto_sync.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 9999)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "Eco Club Auto Sync" -Action $action -Trigger $trigger -Settings $settings -Description "Auto download and upload Eco Club data every hour"
```

## Manual Run Commands

### Windows PowerShell:
```powershell
cd "d:\Eco club"
python auto_sync.py
```

### Double-click:
Simply double-click: `run_auto_sync.bat`

## Troubleshooting

### Agar Task Scheduler se nahi chal raha:
1. Task Scheduler me task ko right-click → **Run** karke test karein
2. Task History check karein errors ke liye
3. Make sure Python PATH me hai:
   ```powershell
   python --version
   ```

### Agar login fail ho raha:
- `.env` file check karein
- Credentials verify karein
- Website manually open karke check karein login working hai

### Agar download nahi ho raha:
- Chrome browser updated hai?
- ChromeDriver compatible hai?
- `auto_sync.py` me headless mode comment out karke browser dekhein

### Log dekhne ke liye:
Script me ek log file bana sakte hain. Agar chahiye to batayein!

## Files Overview

- `auto_sync.py` - Main automation script (fully automated)
- `run_auto_sync.bat` - Batch file to run the script
- `.env` - Your credentials (NEVER commit to git!)
- `auto_download_v2.py` - Semi-automated version (manual login)

## Next Steps

Agar aapko:
- Email notifications chahiye when sync completes
- Error alerts chahiye
- Detailed logging chahiye
- Dashboard chahiye to view sync history

To mujhe batayein, main add kar dunga! 🚀
