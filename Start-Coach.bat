@echo off
REM Compass AI Workflow Coach - one-click launcher for Windows.
REM Needs only Python 3.9+ (standard library). No pip install, no internet, no API keys.
REM
REM   Start-Coach.bat                         open Compass
REM   Start-Coach.bat C:\code\my-repo         open the Workflow coach on that project (or drag a folder onto this file)
REM   Start-Coach.bat C:\code\my-repo ABC-123 also fetch Jira issue ABC-123 (if Jira is set up in Setup)
REM   Start-Coach.bat --project C:\code\my-repo --jira ABC-123
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

set "ARGS=%*"
if not "%~1"=="" if exist "%~1\" (
  if not "%~2"=="" (set ARGS=--project "%~f1" --jira %~2) else (set ARGS=--project "%~f1")
)

echo Starting Compass on http://127.0.0.1:8765/
echo First time? Open Setup in the app and answer 8 quick questions.
echo Close this window or press Ctrl+C to stop.
%PY% -m compass %ARGS%
if errorlevel 1 pause
endlocal
