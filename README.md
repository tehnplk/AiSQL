# AiSQL - AI-Powered SQL Assistant

AiSQL is a PyQt6-based application that combines SQL query execution with AI assistance for database management and query optimization.

## Features

- Execute SQL queries against various database engines
- AI-powered query assistance and optimization
- Syntax highlighting for SQL queries
- Export results to Excel
- Save and load SQL queries
- Dark theme UI

## Prerequisites

- Python 3.8 or higher
- Required packages listed in `pyproject.toml`

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Building Executable

To build the Windows executable, run:

```bash
python build_exe.py
```

This will create a standalone executable in the `dist/main` directory.

## Usage

Run the application:

- Development: `python main.py`
- Executable: Run `dist/main/main.exe`

## Troubleshooting

If you encounter QPainter errors when running the executable, ensure that:

1. All Qt plugins are included in the build (handled by the spec file)
2. Icon files are properly packaged
3. The application is built with the latest spec file

To rebuild with a clean build:

```bash
python -m PyInstaller --clean main.spec
```