@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-workspace.ps1"
echo.
pause
