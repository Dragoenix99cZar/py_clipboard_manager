# Clipboard Manager

A modern, feature-rich clipboard manager built with PySide6 that runs in the system tray and provides persistent storage for text and image clipboard items.

## Features

- **System Tray Integration**: Runs quietly in the background with system tray icon
- **Multi-format Support**: Handles both text and image clipboard content
- **Persistent Storage**: Saves clipboard items to disk for later retrieval
- **Image Thumbnails**: Automatically generates thumbnails for image items using FFmpeg
- **Always-on-Top Option**: Window can stay on top of other applications
- **Easy Management**: Copy items back to clipboard or delete unwanted items
- **Modern UI**: Clean interface with icon-based buttons and scrollable item list

## Project Structure

```
clipboard_manager/
├── sync_app.py          # Main application file
├── sync_app.spec        # PyInstaller build configuration
├── config.json          # Application configuration
├── icon2.ico           # Main application icon
├── icons/              # UI icons directory
│   ├── copy.png        # Copy button icon
│   └── delete.png      # Delete button icon
├── items/              # Stored clipboard items (auto-created)
├── thumbs/             # Image thumbnails (auto-created)
├── build/              # PyInstaller build artifacts
└── dist/               # Compiled executable output
```

## File Descriptions

### Core Files

- **`sync_app.py`** (285 lines): Main application containing all GUI logic, clipboard handling, and file management
- **`config.json`**: Stores window position, size, preferences, and directory paths
- **`sync_app.spec`**: PyInstaller specification file for building standalone executable

### Directories

- **`icons/`**: Contains PNG icons for UI buttons (copy and delete operations)
- **`items/`**: Storage directory for clipboard items (text as .md files, images as .png)
- **`thumbs/`**: Auto-generated thumbnails for image items
- **`build/`**: Temporary build files created during PyInstaller compilation
- **`dist/`**: Final executable and dependencies after successful build

## Dependencies

### Python Packages
- **PySide6**: Qt6 bindings for Python (GUI framework)
- **pathlib**: File system path handling (built-in)
- **json**: Configuration file management (built-in)
- **uuid**: Unique filename generation (built-in)
- **subprocess**: External command execution (built-in)

### External Tools
- **FFmpeg**: Required for image thumbnail generation
  - Must be installed and available in system PATH
  - Used for scaling images to 160px width thumbnails

## Installation & Setup

### Prerequisites
1. Install Python 3.7+ 
2. Install FFmpeg and ensure it's in your system PATH

### Install Dependencies
```bash
# Install all Python dependencies
pip install -r requirements.txt

# Or install manually
pip install PySide6 pyinstaller
```

### Run from Source
```bash
python sync_app.py
```

## Build Instructions

### Create Standalone Executable
The project includes a PyInstaller specification file for building a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable using spec file
pyinstaller sync_app.spec

# Or build directly from Python file
pyinstaller --onefile --windowed --icon=icon2.ico --add-data "icon2.ico;." sync_app.py

# Executable will be created in dist/ directory
The direct PyInstaller command includes:

- --onefile: Creates a single executable file
- --windowed: Runs without console window (GUI mode)
- --icon=icon2.ico: Sets the application icon
- --add-data "icon2.ico;.": Bundles the icon file with the executable

This gives users flexibility to choose between using the pre-configured spec file or building directly from the Python file with command-line options. Both methods will create the executable in the dist/ directory.
```

### Build Configuration
The `sync_app.spec` file includes:
- Main script: `sync_app.py`
- Bundled data: `icon2.ico`
- Output name: `sync_app.exe`
- Single-file executable with UPX compression

## Usage

### Starting the Application
1. Run `python sync_app.py` or execute the built executable
2. The application will start minimized to the system tray
3. Look for the clipboard manager icon in your system tray

### Basic Operations
- **Show/Hide Window**: Click the tray icon or right-click → "Toggle Window"
- **Add Text**: Type in the text area and click "Add Text" or paste from clipboard
- **Add Images**: Click "Paste Image" to add current clipboard image
- **Copy Items**: Click the copy icon next to any stored item
- **Delete Items**: Click the delete icon to remove unwanted items
- **Always on Top**: Use View menu to toggle window staying on top

### Configuration
The application automatically creates a `config.json` file with:
- Window position and size
- Always-on-top preference
- Storage directory paths

## Technical Details

### Architecture
- **Main Classes**:
  - `TrayApp`: Application controller with system tray integration
  - `MainWindow`: Primary GUI window with clipboard item display
  - `ItemWidget`: Individual clipboard item representation

### Storage Format
- **Text Items**: Saved as `.md` files with UUID filenames
- **Image Items**: Saved as `.png` files with corresponding thumbnails
- **Thumbnails**: Generated as `.jpg` files in thumbs directory

### Configuration Schema
```json
{
  "window": {
    "x": 100,
    "y": 100, 
    "width": 400,
    "height": 600,
    "always_on_top": false
  },
  "paths": {
    "thumbs_dir": "thumbs",
    "items_dir": "items"
  }
}
```

## Troubleshooting

### Common Issues
- **FFmpeg not found**: Ensure FFmpeg is installed and in system PATH
- **Tray icon not visible**: Check system tray settings in your OS
- **Items not loading**: Verify `items/` and `thumbs/` directories exist and are writable

### Debug Mode
Run with Python to see console output for debugging:
```bash
python sync_app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
