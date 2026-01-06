# Windows Task Scheduler ko setup karne ke liye PowerShell script

$taskName = "Eco Club Hourly Sync"
$scriptPath = "d:\Eco club\run_hourly_sync.bat"

# Create logs folder
$logsFolder = "d:\Eco club\logs"
if (-not (Test-Path $logsFolder)) {
    New-Item -ItemType Directory -Path $logsFolder | Out-Null
    Write-Host "✅ Created logs folder"
}

# Create task action
$action = New-ScheduledTaskAction -Execute $scriptPath

# Create trigger - every hour, starting from 9 AM
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At 9am -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)).Repetition

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 10) `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Automatically downloads and uploads Eco Club data every hour" `
        -Force

    Write-Host "✅ Task Scheduler setup complete!"
    Write-Host ""
    Write-Host "Task Name: $taskName"
    Write-Host "Schedule: Every 1 hour, starting at 9 AM daily"
    Write-Host "Script: $scriptPath"
    Write-Host "Logs: $logsFolder"
    Write-Host ""
    Write-Host "To view/modify: Open Task Scheduler (taskschd.msc)"
} catch {
    Write-Host "❌ Error: $_"
    Write-Host ""
    Write-Host "Run PowerShell as Administrator and try again"
}
