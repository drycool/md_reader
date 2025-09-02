# MD Reader User Guide

## Introduction

MD Reader is a powerful tool for working with Markdown documents that provides both a command-line interface for viewing and a web interface for editing files.

## Installation

### Requirements

- Python 3.9 or higher
- pip (Python package manager)

### Development Installation

```bash
# Clone the repository (if needed)
git clone <repository-url>
cd md_reader

# Install in development mode
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"
```

## CLI Usage

### Basic Commands

```bash
# View a single file in interactive mode
md-viewer open document.md

# View all files in a directory
md-viewer open /path/to/markdown/files

# Launch TUI interface
md-viewer tui /path/to/markdown/files
```

### Interactive Mode

After running the `md-viewer open` command, you'll enter interactive mode:

1. Enter a search query to search through headers
2. Select the desired result from the list
3. View the section content
4. Repeat search or enter 'q' to quit

### TUI Mode

TUI mode provides a graphical interface in the terminal:

```bash
md-viewer tui /path/to/markdown/files
```

## Web Editor Usage

### Launching the Web Editor

```bash
# Navigate to the web editor directory
cd web_editor

# Run the editor
python run.py
```

### Main Web Editor Features

1. **Editing** - edit Markdown files in the left panel
2. **Preview** - view the result in the right panel
3. **Auto-save** - files are automatically saved every 30 seconds
4. **Navigation** - use the table of contents for quick section access
5. **Hotkeys**:
   - `Ctrl+S` - Save file
   - `Ctrl+O` - Open file
   - `Ctrl+N` - New file
   - `Ctrl+Shift+O` - Quick file open
   - `F11` - Fullscreen mode

### Working with Files

- **Create file** - click the "New" button or use Ctrl+N
- **Open file** - select from list or drag file into editor
- **Save** - automatic or manual (Ctrl+S)
- **Export** - use export buttons to save as HTML or TXT

## Compiling to Executable

To create a standalone executable file:

```bash
# Install PyInstaller
pip install pyinstaller

# Compile main.py
pyinstaller --onefile web_editor/main.py
```

## Configuration

### Logging Setup

```python
from md_reader.logger import setup_logging

# Log to file
setup_logging(
    level="DEBUG",
    log_file="app.log",
    format_string="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

# Log to console
setup_logging(level="INFO")
```

### Validation Customization

```python
from md_reader.validators import FileContentValidator

# Change maximum file size (default is 10MB)
FileContentValidator.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
```

## Troubleshooting

### Common Issues

1. **Module import errors**:
   - Make sure you're in the project root directory
   - Check that the virtual environment is activated

2. **Web editor display issues**:
   - Check that all dependencies are installed
   - Ensure port 5000 is available

3. **Security errors**:
   - Check file access permissions
   - Ensure file paths don't go outside the allowed directory

## Support

If you have questions or issues, create an Issue in the project repository.