$vol = Get-CimInstance Win32_Volume | Where-Object { $_.Label -eq 'usb11' -and $_.DriveLetter }
if (-not $vol) { Write-Host "USB usb11 не найден"; exit 1 }
$path = Join-Path $vol.DriveLetter 'task.txt'
if (Test-Path $path) { Get-Content $path -TotalCount 20 } else { Write-Host "task.txt не найден" }
