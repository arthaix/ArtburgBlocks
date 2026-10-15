# Registers (or re-registers) the Windows task that runs tools\autosync.sh every 3 minutes, hidden, for this user.
#   powershell -ExecutionPolicy Bypass -File tools\autosync-install.ps1
#   Unregister-ScheduledTask -TaskName 'Artburg Blocks autosync' -Confirm:$false     # to remove it
$cmd = Join-Path $PSScriptRoot 'autosync.cmd'
$vbs = 'E:\Artburg Server\run-hidden.vbs'
$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('"{0}" "{1}"' -f $vbs, $cmd) -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 3)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName 'Artburg Blocks autosync' -Action $action -Trigger $trigger -Settings $settings `
    -Description 'Keeps Artburg Blocks the same on the server, the Prism client and the web map (C:\Users\arthaix\artburgblocks\tools\autosync.sh)' `
    -Force | Out-Null
Get-ScheduledTask -TaskName 'Artburg Blocks autosync' | Select-Object TaskName, State
