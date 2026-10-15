# USB Device Monitor Script
# Monitors USB device connect/disconnect events and logs details

$logFile = "C:\Users\reva4\Desktop\game\usb_monitor_log.txt"
$showDetails = $true

# Create log file if not exists
if (-not (Test-Path $logFile)) {
    New-Item -ItemType File -Path $logFile -Force | Out-Null
    Add-Content -Path $logFile -Value "=== USB Monitor Started at $(Get-Date) ==="
}

function Log-Message($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $entry
    Write-Host $entry -ForegroundColor Cyan
}

function Get-USBDeviceDetails($device) {
    $details = @{}
    $details["DeviceID"] = $device.DeviceID
    $details["Name"] = $device.Name
    $details["Description"] = $device.Description
    $details["Manufacturer"] = $device.Manufacturer
    $details["PNPDeviceID"] = $device.PNPDeviceID
    $details["Status"] = $device.Status
    $details["ClassGuid"] = $device.ClassGuid
    return $details
}

function Show-DeviceInfo($action, $device) {
    $details = Get-USBDeviceDetails $device
    $msg = "$action Device:`n"
    $msg += "  Name: $($details.Name)`n"
    $msg += "  DeviceID: $($details.DeviceID)`n"
    $msg += "  Description: $($details.Description)`n"
    $msg += "  Manufacturer: $($details.Manufacturer)`n"
    $msg += "  PNPDeviceID: $($details.PNPDeviceID)`n"
    $msg += "  Status: $($details.Status)`n"
    $msg += "  ClassGuid: $($details.ClassGuid)"
    Log-Message $msg
}

# Register WMI event watchers
$insertQuery = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBControllerDevice'"
$removeQuery = "SELECT * FROM __InstanceDeletionEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBControllerDevice'"

Log-Message "Starting USB monitoring... Press Ctrl+C to stop"

$insertWatcher = Register-WmiEvent -Query $insertQuery -SourceIdentifier "USBInsert" -Action {
    $device = $Event.SourceEventArgs.NewEvent.TargetInstance.Dependent
    $usbDevice = Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.DeviceID -eq $device }
    if ($usbDevice) {
        Show-DeviceInfo "CONNECTED" $usbDevice
    }
}

$removeWatcher = Register-WmiEvent -Query $removeQuery -SourceIdentifier "USBRemove" -Action {
    $device = $Event.SourceEventArgs.NewEvent.TargetInstance.Dependent
    $usbDevice = Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.DeviceID -eq $device }
    if ($usbDevice) {
        Show-DeviceInfo "DISCONNECTED" $usbDevice
    }
}

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 10
    }
}
finally {
    Unregister-Event -SourceIdentifier "USBInsert" -Force -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier "USBRemove" -Force -ErrorAction SilentlyContinue
    Log-Message "USB monitoring stopped at $(Get-Date)"
}