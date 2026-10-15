# USB Device Monitor - Improved Version using .NET ManagementEventWatcher
# More reliable USB connect/disconnect detection

$logFile = "C:\Users\reva4\Desktop\game\usb_monitor_log.txt"

# Clear and initialize log
"=== USB Monitor Started at $(Get-Date) ===" | Out-File -FilePath $logFile -Encoding UTF8

function Log-Message($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $entry -Encoding UTF8
    Write-Host $entry -ForegroundColor Cyan
}

function Get-USBDeviceInfo($deviceId) {
    try {
        $device = Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.DeviceID -eq $deviceId }
        if ($device) {
            return @{
                DeviceID = $device.DeviceID
                Name = $device.Name
                Description = $device.Description
                Manufacturer = $device.Manufacturer
                PNPDeviceID = $device.PNPDeviceID
                Status = $device.Status
                ClassGuid = $device.ClassGuid
                Service = $device.Service
            }
        }
    } catch {
        return @{Error = $_.Exception.Message}
    }
    return $null
}

function Show-DeviceEvent($action, $deviceId) {
    $info = Get-USBDeviceInfo $deviceId
    if ($info -and $info.Error) {
        Log-Message "$action - Error getting device info: $($info.Error)"
        return
    }
    if ($info) {
        $msg = "$action USB Device:`n"
        $msg += "  Name: $($info.Name)`n"
        $msg += "  DeviceID: $($info.DeviceID)`n"
        $msg += "  Description: $($info.Description)`n"
        $msg += "  Manufacturer: $($info.Manufacturer)`n"
        $msg += "  PNPDeviceID: $($info.PNPDeviceID)`n"
        $msg += "  Status: $($info.Status)`n"
        $msg += "  ClassGuid: $($info.ClassGuid)`n"
        $msg += "  Service: $($info.Service)"
        Log-Message $msg
    } else {
        Log-Message "$action - DeviceID: $deviceId (Details not found)"
    }
}

# Use .NET ManagementEventWatcher for reliable USB monitoring
Add-Type -AssemblyName System.Management

# Query for USB device arrival (connected)
$insertQuery = New-Object System.Management.WqlEventQuery("__InstanceCreationEvent", "TargetInstance ISA 'Win32_USBHub'")
$insertWatcher = New-Object System.Management.ManagementEventWatcher($insertQuery)
$insertWatcher.EventArrived += {
    $device = $Event.SourceEventArgs.NewEvent.TargetInstance
    $deviceId = $device.DeviceID
    Show-DeviceEvent "CONNECTED" $deviceId
}

# Query for USB device removal (disconnected)
$removeQuery = New-Object System.Management.WqlEventQuery("__InstanceDeletionEvent", "TargetInstance ISA 'Win32_USBHub'")
$removeWatcher = New-Object System.Management.ManagementEventWatcher($removeQuery)
$removeWatcher.EventArrived += {
    $device = $Event.SourceEventArgs.NewEvent.TargetInstance
    $deviceId = $device.DeviceID
    Show-DeviceEvent "DISCONNECTED" $deviceId
}

# Also monitor Win32_PnPEntity for more device types
$pnpInsertQuery = New-Object System.Management.WqlEventQuery("__InstanceCreationEvent", "TargetInstance ISA 'Win32_PnPEntity'")
$pnpInsertWatcher = New-Object System.Management.ManagementEventWatcher($pnpInsertQuery)
$pnpInsertWatcher.EventArrived += {
    $device = $Event.SourceEventArgs.NewEvent.TargetInstance
    if ($device.PNPClass -eq "USB" -or $device.ClassGuid -like "{36fc9e60-c465-11cf-8056-444553540000}" -or $device.DeviceID -like "USB*") {
        Show-DeviceEvent "PNP_CONNECTED" $device.DeviceID
    }
}

$pnpRemoveQuery = New-Object System.Management.WqlEventQuery("__InstanceDeletionEvent", "TargetInstance ISA 'Win32_PnPEntity'")
$pnpRemoveWatcher = New-Object System.Management.ManagementEventWatcher($pnpRemoveQuery)
$pnpRemoveWatcher.EventArrived += {
    $device = $Event.SourceEventArgs.NewEvent.TargetInstance
    if ($device.PNPClass -eq "USB" -or $device.ClassGuid -like "{36fc9e60-c465-11cf-8056-444553540000}" -or $device.DeviceID -like "USB*") {
        Show-DeviceEvent "PNP_DISCONNECTED" $device.DeviceID
    }
}

# Start all watchers
$insertWatcher.Start()
$removeWatcher.Start()
$pnpInsertWatcher.Start()
$pnpRemoveWatcher.Start()

Log-Message "All watchers started. Monitoring USB devices..."
Log-Message "=== Current USB Devices at Start ==="
Get-WmiObject -Class Win32_USBHub | ForEach-Object {
    Show-DeviceEvent "INITIAL" $_.DeviceID
}
Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.PNPClass -eq "USB" -or $_.DeviceID -like "USB*" } | ForEach-Object {
    Show-DeviceEvent "INITIAL_PNP" $_.DeviceID
}
Log-Message "=== Waiting for events... ==="

# Keep alive
try {
    while ($true) {
        Start-Sleep -Seconds 30
        # Heartbeat
        # Log-Message "Heartbeat - monitoring active"
    }
}
finally {
    $insertWatcher.Stop(); $insertWatcher.Dispose()
    $removeWatcher.Stop(); $removeWatcher.Dispose()
    $pnpInsertWatcher.Stop(); $pnpInsertWatcher.Dispose()
    $pnpRemoveWatcher.Stop(); $pnpRemoveWatcher.Dispose()
    Log-Message "Monitoring stopped at $(Get-Date)"
}