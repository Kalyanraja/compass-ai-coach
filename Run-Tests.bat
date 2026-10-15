@echo off
REM Runs the acceptance tests and the recommendation-quality evaluation.
setlocal
cd /d "%~dp0"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY ( echo Python 3 was not found. & pause & exit /b 1 )
%PY% -m unittest discover -s tests -t . -v
%PY% -m compass eval
pause
endlocal
