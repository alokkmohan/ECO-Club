# PowerShell script to create a scheduled task that runs every 2 hours
# Change these variables if needed
$TaskName = "EcoClubAutoSync2Hour"
$ScriptPath = "D:\Eco club\run_final_sync.bat"

# Trigger: Start at 12:00 AM, repeat every 2 hours for 1 day
$Trigger = New-ScheduledTaskTrigger -Once -At 00:00AM -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration (New-TimeSpan -Days 1)

$Action = New-ScheduledTaskAction -Execute $ScriptPath

Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Force

Write-Host "Scheduled task '$TaskName' created to run every 2 hours."
