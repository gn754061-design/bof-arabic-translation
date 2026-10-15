param([string[]]$Keys, [string]$Out = "C:\Users\reva4\Desktop\game\font\shot.png", [int]$WaitMs = 3000)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class K {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr p);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, IntPtr extra);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$proc = Get-Process -Name "mGBA" | Select-Object -First 1
$h = $proc.MainWindowHandle
# force foreground via AttachThreadInput
$fg = [K]::GetForegroundWindow()
$fgThread = [K]::GetWindowThreadProcessId($fg, [IntPtr]::Zero)
$myThread = [K]::GetCurrentThreadId()
$target = [K]::GetWindowThreadProcessId($h, [IntPtr]::Zero)
[void][K]::AttachThreadInput($myThread, $target, $true)
[void][K]::AttachThreadInput($myThread, $fgThread, $true)
[void][K]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 600

$VK = @{ "ENTER" = 0x0D; "Z" = 0x5A; "X" = 0x58; "ESC" = 0x1B; "UP" = 0x26; "DOWN" = 0x28; "LEFT" = 0x25; "RIGHT" = 0x27; "BACK" = 0x08 }
foreach ($k in $Keys) {
    $vk = $VK[$k]
    if (-not $vk) { continue }
    [void][K]::keybd_event([byte]$vk, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 120
    [void][K]::keybd_event([byte]$vk, 0, 2, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 350
}
Start-Sleep -Milliseconds $WaitMs
$r = New-Object K+RECT
[void][K]::GetWindowRect($h, [ref]$r)
$w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap $w, $hh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[void][K]::PrintWindow($h, $hdc, 0)
$g.ReleaseHdc($hdc)
$bmp.Save($Out)
"saved $Out"
