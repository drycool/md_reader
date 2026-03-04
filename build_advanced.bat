@echo off
chcp 65001 >nul
title Build MarkdownReader

cd /d "%~dp0web_editor"

if not exist "md_reader_exe.py" (
    echo ERROR: md_reader_exe.py not found in web_editor folder
    pause
    exit /b 1
)

echo ========================================
echo   Building MarkdownReader EXE
echo ========================================
echo.

echo Installing dependencies...
py -m pip install pyinstaller flask markdown --quiet 2>nul

echo.
echo Building EXE...
py -m PyInstaller --onefile --console --name "MarkdownReader" md_reader_exe.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

if exist "dist\MarkdownReader.exe" (
    echo.
    echo Copying to project root...
    copy /Y "dist\MarkdownReader.exe" "..\MarkdownReader.exe"
    echo.
    echo DONE: MarkdownReader.exe created!
) else (
    echo ERROR: EXE not found!
)

echo.
pause
