# Configuration Directory

## Purpose
Configuration files for PCBot settings and paths.

## Contents

### `manual_path.txt`
Contains the file path to the Manual for Development Projects 2024 PDF.

This file is used by the RAG pipeline to locate and process the manual document.

## Usage

If you move the manual PDF to a different location:
1. Open `manual_path.txt`
2. Update the path to the new location
3. Restart the application

Example:
```
D:\PLANNING WORK\Manual-for-Development-Projects-2024.pdf
```

## Notes
- Path should be absolute (full path from drive letter)
- Use forward slashes `/` or escaped backslashes `\\`
- File must exist and be accessible
- PDF must be the official Manual for Development Projects 2024
