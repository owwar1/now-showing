@echo off
rem Reads the posters folder and updates the board's poster list.
rem Name each file with its number, then the unit, e.g. "1 Education and Training Unit.png"
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed on this computer, so the poster list can't be updated here.
  pause
  exit /b 1
)
echo Updating posters...
echo.
python update-posters.py
echo.
pause
