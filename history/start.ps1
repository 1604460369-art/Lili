# 公文校对助手 - PowerShell 启动脚本
# 如果 start.bat 不行，右键这个文件 -> "使用 PowerShell 运行"

Set-Location $PSScriptRoot

Write-Host "Starting server..." -ForegroundColor Cyan
Write-Host "Open http://127.0.0.1:5000 in your browser" -ForegroundColor Green
Write-Host ""

# Open browser
Start-Process "http://127.0.0.1:5000"

# Start Python server
python src\app.py

Read-Host "Press Enter to exit"
