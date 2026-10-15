@echo off
REM Compass AI Engineering Enablement Coach - one-click launcher for Windows.
REM Needs only Python 3.9+ (standard library). No pip install, no internet, no API keys.
setlocal
cd /d "%~dp0"
title Compass Coach

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY (
  echo Python 3 was not found.
  echo Install Python 3.9 or newer from your company software center, then run this file again.
  pause
  exit /b 1
)

echo Starting Compass on http://127.0.0.1:8765/
echo Close this window or press Ctrl+C to stop.
%PY% -m compass %*
if errorlevel 1 pause
endlocal
