@echo off
echo Building Markdown Editor EXE...

cd /d "C:\Users\369\.qoder\md_reader\web_editor"

if not exist "main.py" (
    echo ERROR: main.py not found in current directory
    pause
    exit /b 1
)

echo Starting PyInstaller build...

python -m PyInstaller --onefile --console --name "MarkdownEditor" --add-data "templates;templates" --add-data "static;static" --add-data "demo.html;." --hidden-import "flask" --hidden-import "jinja2" --hidden-import "werkzeug" --hidden-import "markdown_it" --hidden-import "rich" --hidden-import "typer" --hidden-import "textual" --hidden-import "textual.app" --hidden-import "textual.widgets" --hidden-import "flask.templating" --hidden-import "flask.json" --hidden-import "markupsafe" --collect-all "flask" --collect-all "jinja2" --collect-all "markupsafe" --collect-all "werkzeug" main.py

if %errorlevel% equ 0 (
    echo.
    echo Build completed successfully!
    if exist "dist\MarkdownEditor.exe" (
        echo EXE file created: dist\MarkdownEditor.exe
        dir "dist\MarkdownEditor.exe"
        echo Ready to run MarkdownEditor.exe!
    ) else (
        echo ERROR: EXE file not found in dist folder
    )
) else (
    echo ERROR: Build failed
)

echo.
pause