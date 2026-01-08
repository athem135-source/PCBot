# Frontend Widget

## Purpose
React-based chatbot widget built with TypeScript and Tailwind CSS.

## Directory Structure
- **`src/`**: React source code
- **`dist/`**: Built widget files (production)
- **`public/`**: Public assets
- **`node_modules/`**: Dependencies (gitignored)

## Development

### Setup
```bash
npm install
```

### Build Widget
```bash
npm run build
# Or use: build-widget.bat
```

### Development Mode
```bash
npm run dev
# Or use: run-widget.bat
```

## Build Output

The widget is built as:
- **`dist/pdbot-widget.iife.js`**: JavaScript bundle
- **`dist/pdbot-widget.css`**: Styles

These files are loaded by `public/html/widget-dev.html` for development testing.

## Features
- TypeScript for type safety
- Tailwind CSS for styling
- Vite for fast builds
- IIFE format for easy embedding
- Standalone deployment support

## Integration

### In HTML
```html
<link rel="stylesheet" href="/dist/pdbot-widget.css">
<script src="/dist/pdbot-widget.iife.js"></script>
```

### Standalone
Use `public/html/widget-standalone.html` which includes all widget code inline.
