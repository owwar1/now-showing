@echo off
rem Brings in numbered posters from the assets folder, rebuilds the list, and uploads the board.
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed on this computer.
  pause
  exit /b 1
)
python publish-posters.py
echo.
pause
