@echo off
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%"

cd /d "%PROJECT_DIR%web_editor"

echo ================================================
echo   Markdown Reader - Demo Editor
echo ================================================
echo.

REM Запуск редактора с демо файлом
py app.py "%PROJECT_DIR%markdown_files\demo.md" edit

pause
