@echo off
REM Compass agent kit installer (Windows cmd).
REM Copies the kit into a target repository. Never overwrites existing files: they are skipped and reported.
REM
REM Usage: install-kit.bat <target-repo-path> [--with-vendor] [--dry-run]
REM   --with-vendor  also copy unmodified third-party originals into <target>\.agent-kit\vendor\
REM   --dry-run      show what would be copied, change nothing
setlocal EnableExtensions EnableDelayedExpansion

set "TARGET="
set "WITH_VENDOR=0"
set "DRY_RUN=0"

:parse
if "%~1"=="" goto parsed
if /I "%~1"=="--with-vendor" ( set "WITH_VENDOR=1" & shift & goto parse )
if /I "%~1"=="--dry-run" ( set "DRY_RUN=1" & shift & goto parse )
if /I "%~1"=="-h" goto usage
if /I "%~1"=="--help" goto usage
if defined TARGET ( echo Only one target path allowed. & goto usage_err )
set "TARGET=%~f1"
shift
goto parse

:parsed
if not defined TARGET goto usage_err
if not exist "%TARGET%\" ( echo Target directory not found: %TARGET% & exit /b 1 )

set "KIT=%~dp0"
if "%KIT:~-1%"=="\" set "KIT=%KIT:~0,-1%"
if /I "%KIT%"=="%TARGET%" ( echo Target must be a different directory than the kit. & exit /b 1 )
if not exist "%TARGET%\.git\" echo Note: %TARGET% does not look like a git repository root (no .git). Continuing.

set /a COPIED=0
set /a SKIPPED=0
set "SKIPLOG=%TEMP%\compass-kit-skipped-%RANDOM%.txt"
type nul > "%SKIPLOG%"

call :copy_file "%KIT%\AGENTS.md" "%TARGET%\AGENTS.md"
call :copy_file "%KIT%\CLAUDE.md" "%TARGET%\CLAUDE.md"
call :copy_tree ".github" ".github"
call :copy_tree ".claude" ".claude"
call :copy_file "%KIT%\README.md" "%TARGET%\.agent-kit\README.md"
call :copy_file "%KIT%\tool-routing-guide.md" "%TARGET%\.agent-kit\tool-routing-guide.md"
call :copy_tree "devin" ".agent-kit\devin"
call :copy_tree "prompt-library" ".agent-kit\prompt-library"
if "%WITH_VENDOR%"=="1" call :copy_tree "vendor" ".agent-kit\vendor"

echo.
echo Compass agent kit -^> %TARGET%
if "%DRY_RUN%"=="1" echo (dry run: nothing was written)
echo Copied:  %COPIED% file(s)
echo Skipped: %SKIPPED% file(s) that already exist (left untouched)
type "%SKIPLOG%"
del "%SKIPLOG%" >nul 2>&1
echo.
echo Next steps:
echo   1. Fill {{PLACEHOLDERS}} in AGENTS.md and .github\copilot-instructions.md
echo      (or ask an agent: Copilot "/create-agents-md", Claude Code "/create-agents-md").
echo   2. For skipped files, merge the kit's version by hand (see .agent-kit\README.md).
echo   3. VS Code: enable "chat.useAgentsMdFile" if you want Copilot to read AGENTS.md.
echo   4. Devin: create Playbooks and Knowledge from .agent-kit\devin\ (see its README).
echo   5. Commit on a branch and open a PR for review.
endlocal
exit /b 0

:copy_tree
REM %1 = source dir relative to kit, %2 = destination dir relative to target
set "SRCDIR=%KIT%\%~1"
set "DSTDIR=%TARGET%\%~2"
if not exist "%SRCDIR%\" exit /b 0
for /r "%SRCDIR%" %%F in (*) do (
  set "FULL=%%~fF"
  set "REL=!FULL:%SRCDIR%\=!"
  call :copy_file "%%~fF" "%DSTDIR%\!REL!"
)
exit /b 0

:copy_file
REM %1 = source file, %2 = destination file
if exist "%~2" (
  set /a SKIPPED+=1
  echo   %~2>> "%SKIPLOG%"
  exit /b 0
)
if "%DRY_RUN%"=="1" (
  echo would copy: %~2
) else (
  if not exist "%~dp2" mkdir "%~dp2" >nul 2>&1
  copy /Y "%~1" "%~2" >nul
)
set /a COPIED+=1
exit /b 0

:usage
echo Usage: install-kit.bat ^<target-repo-path^> [--with-vendor] [--dry-run]
exit /b 0

:usage_err
echo Usage: install-kit.bat ^<target-repo-path^> [--with-vendor] [--dry-run]
exit /b 1
