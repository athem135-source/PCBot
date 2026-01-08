# Deployment Documentation

## Purpose
Comprehensive guides for deploying PCBot to various platforms.

## Available Guides

### `GITHUB_PAGES.md`
Complete guide for deploying frontend to GitHub Pages
- Auto-deployment via GitHub Actions
- Custom domain setup
- Backend deployment options (Railway, Render)
- CORS configuration
- Troubleshooting

### `NETLIFY.md`
Netlify deployment guide
- GitHub integration
- CLI deployment
- Drag-and-drop deployment
- Security headers configuration
- Environment variables

## Quick Links

**Frontend Deployment:**
- GitHub Pages (recommended for free static hosting)
- Netlify (alternative with advanced features)

**Backend Deployment:**
- Railway: https://railway.app/ (free tier)
- Render: https://render.com/ (free tier)
- Office server (self-hosted)

## Deployment Strategy

### Static Frontend
Deploy `public/` folder to GitHub Pages or Netlify

### Backend API
Deploy Flask app to Railway, Render, or dedicated server

### Services Required
- Qdrant vector database
- Ollama LLM server (or Groq API)
- Python virtual environment

See individual guides for detailed instructions.
