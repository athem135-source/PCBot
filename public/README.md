# Public Directory

## Purpose
Static frontend files ready for deployment to GitHub Pages, Netlify, or other static hosting platforms.

## Directory Structure

### `html/` - HTML Interfaces
- **`landing.html`**: Mode selector page (User/Admin modes)
- **`widget-standalone.html`**: Shareable widget interface
- **`widget-dev.html`**: Development widget (built React components)
- **`mobile.html`**: Mobile-optimized interface

### `assets/` - Static Assets
- **Images**: Organization logos, screenshots, icons
- **Screenshots**: Interface demonstrations for documentation

## Deployment

### GitHub Pages
Files are auto-deployed from this directory via GitHub Actions (`.github/workflows/deploy-pages.yml`)

### Netlify
Configured via `netlify.toml` in project root to publish from `public/` directory

### Local Testing
Open HTML files directly in browser or use a local server:
```bash
python -m http.server 8000
# Visit http://localhost:8000/html/landing.html
```

## Notes
- All HTML files use relative paths for portability
- Backend API URL needs to be configured in production
- CORS must be enabled on backend for cross-origin requests
