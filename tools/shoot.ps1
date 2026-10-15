param([string]$Out = "C:\Users\reva4\Desktop\game\font\shot.png")
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class P {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetWindowDC(IntPtr hWnd);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$proc = Get-Process -Name "mGBA" | Select-Object -First 1
[void][P]::SetForegroundWindow($proc.MainWindowHandle)
Start-Sleep -Milliseconds 500
$r = New-Object P+RECT
[void][P]::GetWindowRect($proc.MainWindowHandle, [ref]$r)
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[void][P]::PrintWindow($proc.MainWindowHandle, $hdc, 0)
$g.ReleaseHdc($hdc)
$bmp.Save($Out)
"saved $Out ${w}x${h}"
