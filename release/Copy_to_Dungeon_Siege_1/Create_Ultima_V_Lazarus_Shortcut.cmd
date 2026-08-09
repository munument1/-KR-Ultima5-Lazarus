@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Create_Ultima_V_Lazarus_Shortcut.ps1"
set "shortcutResult=%ERRORLEVEL%"
echo.
if not "%shortcutResult%"=="0" echo Shortcut creation failed. Review the message above.
pause
exit /b %shortcutResult%
