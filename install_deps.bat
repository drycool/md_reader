@echo off
chcp 65001 >nul
title Install Dependencies

echo ================================================
echo   Markdown Reader - Install Dependencies
echo ================================================
echo.

cd /d "%~dp0web_editor"

echo Installing Flask and markdown...
py -m pip install flask markdown

echo.
echo Done! Now run view_demo.bat
echo.

pause
