# MD Reader Project Specification

## Project Overview

MD Reader is an extensible tool for working with Markdown documentation that includes both a CLI interface and a web editor. The project is designed for convenient viewing, editing, and managing collections of Markdown files.

## System Architecture

### Main Components

1. **md_reader CLI** - Interactive command-line tool for viewing Markdown documentation
2. **web_editor** - Web-based Markdown file editor with graphical interface
3. **md_reader modules** - Library of reusable components

### Project Structure

```
md_reader/
├── md_reader/              # Core library
│   ├── cli.py             # CLI interface
│   ├── loader.py          # File loading
│   ├── toc.py             # Table of contents building
│   ├── viewer.py          # Content viewing
│   ├── tui.py             # Text-based UI
│   ├── cache.py           # Caching
│   ├── container.py       # DI container
│   ├── exceptions.py      # Exceptions
│   ├── interfaces.py      # Interfaces
│   ├── logger.py          # Logging
│   ├── validators.py      # Validation
│   └── enhanced_loader.py # Enhanced loading
├── web_editor/            # Web editor
│   ├── app.py            # Flask application
│   ├── run.py            # Launch script
│   ├── main.py           # Entry point for EXE
│   ├── templates/        # HTML templates
│   ├── static/           # Static files
│   └── uploads/          # Uploaded files
├── tests/                # Tests
├── docs/                 # Documentation
└── dist/                 # Compiled files
```

## Features

### CLI Mode (md_reader)

- Reading individual files or entire directories with Markdown files
- Automatic table of contents generation from headers
- Interactive search through headers with fuzzy matching
- Section viewing with syntax highlighting
- Table of contents caching for improved performance
- Safe path and file handling
- Centralized logging

### Web Editor

- Modern graphical interface with gradient design
- Live preview in real-time
- Code syntax highlighting
- Automatic table of contents with navigation
- Auto-save every 30 seconds
- Hotkeys for quick operations
- Drag-and-drop support for files
- Fully localized Russian interface
- Responsive design for different devices

## Technology Stack

### Dependencies

- **Python 3.9+**
- **Flask** - web framework
- **rich** - terminal output formatting
- **typer** - CLI interface
- **markdown-it-py** - Markdown parsing
- **python-Levenshtein** - fuzzy search
- **textual** - TUI interface
- **Jinja2** - templating
- **MarkupSafe** - safe HTML handling

## Security

- Path traversal attack protection
- File size validation
- File encoding checking
- User input sanitization
- Centralized error handling

## Performance

- Lazy file loading
- Multi-tier caching
- Parallel file processing
- Memory usage optimization

## Extensibility

- Interface-oriented architecture
- Dependency injection container
- Modular structure