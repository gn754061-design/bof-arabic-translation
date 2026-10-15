param([int]$VK = 0x5A, [int]$HoldMs = 600, [int]$WaitMs = 3000, [string]$Out = "C:\Users\reva4\Desktop\game\font\s.png")
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class K2 {
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, IntPtr extra);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@
$p = Get-Process -Name mGBA | Select-Object -First 1
[void][K2]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 500
[void][K2]::keybd_event([byte]$VK, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds $HoldMs
[void][K2]::keybd_event([byte]$VK, 0, 2, [IntPtr]::Zero)
Start-Sleep -Milliseconds $WaitMs
"sent VK $VK hold ${HoldMs}ms"
