$Win32 = @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern int MessageBox(IntPtr hWnd, string text, string caption, uint type);}
"@
Add-Type -TypeDefinition $Win32
[Win32]::MessageBox([IntPtr]::Zero, "Welcome!", "Security", 0x10)
