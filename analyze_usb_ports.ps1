# USB Port Analysis Script - Check if USB-C port supports data
$logFile = "C:\Users\reva4\Desktop\game\usb_port_analysis.txt"

function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    "$ts $msg" | Tee-Object -FilePath $logFile -Append
}

Log "=== USB PORT ANALYSIS STARTED ==="
Log ""

# 1. List all USB Controllers (Host Controllers)
Log "--- USB HOST CONTROLLERS ---"
Get-WmiObject Win32_USBController | ForEach-Object {
    Log "Controller: $($_.Name)"
    Log "  DeviceID: $($_.DeviceID)"
    Log "  PNPDeviceID: $($_.PNPDeviceID)"
    Log "  Status: $($_.Status)"
    Log ""
}

# 2. List all USB Root Hubs (Physical ports)
Log "--- USB ROOT HUBS (Physical Ports) ---"
Get-WmiObject Win32_USBHub | Where-Object { $_.DeviceID -like "USB\ROOT_HUB*" } | ForEach-Object {
    Log "Root Hub: $($_.Name)"
    Log "  DeviceID: $($_.DeviceID)"
    Log "  Status: $($_.Status)"
    Log "  Number of Ports: $($_.NumberOfPorts)"
    Log ""
}

# 3. List all USB devices with their hub/port info
Log "--- ALL USB DEVICES (with hub path) ---"
Get-WmiObject Win32_PnPEntity | Where-Object { $_.ClassGuid -eq "{36fc9e60-c465-11cf-8056-444553540000}" -or $_.DeviceID -like "USB*" } | ForEach-Object {
    Log "Device: $($_.Name)"
    Log "  DeviceID: $($_.DeviceID)"
    Log "  PNPDeviceID: $($_.PNPDeviceID)"
    Log "  Status: $($_.Status)"
    Log "  Manufacturer: $($_.Manufacturer)"
    Log "  ClassGuid: $($_.ClassGuid)"
    Log "  Service: $($_.Service)"
    Log ""
}

# 4. Check for USB-C / Thunderbolt specific devices
Log "--- USB-C / THUNDERBOLT DEVICES ---"
Get-WmiObject Win32_PnPEntity | Where-Object { 
    $_.Name -match "USB.C|Type.C|Thunderbolt" -or 
    $_.DeviceID -match "USB.C|Type.C|Thunderbolt" 
} | ForEach-Object {
    Log "USB-C/TBT Device: $($_.Name)"
    Log "  DeviceID: $($_.DeviceID)"
    Log "  Status: $($_.Status)"
    Log ""
}

# 5. Check PCI devices for USB controllers (including USB-C)
Log "--- PCI USB CONTROLLERS ---"
Get-WmiObject Win32_PnPEntity | Where-Object { 
    $_.DeviceID -like "PCI*" -and ($_.Name -like "*USB*" -or $_.Name -like "*xHCI*" -or $_.Name -like "*eXtensible*") 
} | ForEach-Object {
    Log "PCI USB Controller: $($_.Name)"
    Log "  DeviceID: $($_.DeviceID)"
    Log "  Status: $($_.Status)"
    Log "  ClassGuid: $($_.ClassGuid)"
    Log ""
}

Log "=== ANALYSIS COMPLETE ==="
Log ""
Log "INTERPRETATION:"
Log "- If your USB-C port appears as a Root Hub with NumberOfPorts > 0, it has data lines"
Log "- If devices connected to it appear in the device list, data works"
Log "- If only charging works, no devices will enumerate on that port"
Log "- Check 'Unknown USB Device (Device Descriptor Request Failed)' - indicates connection but enumeration failure"