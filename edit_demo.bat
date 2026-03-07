@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ================================================
echo   Markdown Reader - Demo Editor
echo ================================================
echo.
py web_editor/app.py markdown_files/demo.md edit
pause
