# PowerShell script to build Markdown Editor EXE
Write-Host "Building Markdown Editor EXE..." -ForegroundColor Cyan

# Change to the correct directory
Set-Location "C:\Users\369\.qoder\md_reader\web_editor"

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: main.py not found in current directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting PyInstaller build..." -ForegroundColor Yellow

# Run PyInstaller
python -m PyInstaller --onefile --console --name "MarkdownEditor" --add-data "templates;templates" --add-data "static;static" --add-data "demo.html;." --hidden-import "flask" --hidden-import "jinja2" --hidden-import "werkzeug" --hidden-import "markdown_it" --hidden-import "rich" --hidden-import "typer" --hidden-import "textual" --hidden-import "textual.app" --hidden-import "textual.widgets" --hidden-import "flask.templating" --hidden-import "flask.json" --hidden-import "markupsafe" --collect-all "flask" --collect-all "jinja2" --collect-all "markupsafe" --collect-all "werkzeug" main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    
    if (Test-Path "dist\MarkdownEditor.exe") {
        $fileInfo = Get-Item "dist\MarkdownEditor.exe"
        $sizeMB = [math]::Round($fileInfo.Length / 1MB, 1)
        Write-Host "EXE file created: dist\MarkdownEditor.exe" -ForegroundColor Green
        Write-Host "File size: $sizeMB MB" -ForegroundColor Green
        Write-Host "Ready to run MarkdownEditor.exe!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: EXE file not found in dist folder" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
}

Read-Host "Press Enter to continue"