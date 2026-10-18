@echo off
rem Opens the Now Showing board in full-screen kiosk mode.
rem To exit: press Alt+F4.
set "PAGE=%~dp0now-showing.html"
set "PROFILE=%TEMP%\now-showing-kiosk"

set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if exist "%CHROME%" (
  start "" "%CHROME%" --kiosk --user-data-dir="%PROFILE%" --no-first-run --disable-session-crashed-bubble --disable-infobars "%PAGE%"
  exit /b
)

set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
start "" "%EDGE%" --kiosk "%PAGE%" --edge-kiosk-type=fullscreen --user-data-dir="%PROFILE%" --no-first-run
