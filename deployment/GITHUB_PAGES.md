# GitHub Pages Deployment Guide for PCBot v4.0

## Overview
This guide shows how to deploy PCBot's frontend to GitHub Pages for free static hosting. The backend (Flask API) will need separate deployment.

## Quick Setup (5 minutes)

### Step 1: Enable GitHub Pages
1. Go to your repository on GitHub: https://github.com/athem135-source/PCBot
2. Click **Settings** > **Pages** (left sidebar)
3. Under "Build and deployment":
   - Source: **GitHub Actions**
   - Save

### Step 2: Push to GitHub
The GitHub Actions workflow is already configured (`.github/workflows/deploy-pages.yml`). Just push your code:

```bash
git add .
git commit -m "Deploy to GitHub Pages"
git push origin main
```

### Step 3: Wait for Deployment
1. Go to **Actions** tab in your repository
2. Watch the "Deploy to GitHub Pages" workflow run (takes 1-2 minutes)
3. Once complete, your site will be live at:
   - **https://athem135-source.github.io/PCBot/**

## What Gets Deployed

### Frontend (GitHub Pages)
✅ Landing page with mode selector
✅ Shareable widget interface
✅ Mobile site
✅ All assets (images, CSS, JS)

### Backend (Needs Separate Hosting)
❌ Flask API server (not included in GitHub Pages)
❌ Vector database (Qdrant)
❌ LLM server (Ollama)

## Backend Deployment Options

### Option 1: Railway (Recommended)
**Free Tier:** 500 hours/month + $5 credit

1. Go to https://railway.app/
2. Sign in with GitHub
3. Click **New Project** > **Deploy from GitHub repo**
4. Select `athem135-source/PCBot`
5. Add environment variables:
   ```
   PORT=5001
   QDRANT_HOST=localhost
   QDRANT_PORT=6338
   ```
6. Deploy
7. Copy your Railway URL (e.g., `https://pcbot-production.up.railway.app`)

### Option 2: Render
**Free Tier:** Limited hours/month

1. Go to https://render.com/
2. New **Web Service** from GitHub
3. Select `PCBot` repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command (Windows):** `scripts\setup\run_backend.bat`  (Linux: `python widget_api.py`)
   - **Environment Variables:** Same as Railway
5. Deploy
6. Copy your Render URL

### Option 3: Your Office Server
If you have a static IP or domain:

1. Install Python, Qdrant, Ollama on server
2. Run `setup.bat` to install dependencies
3. Configure firewall to allow port 5001
4. Start services:
   ```bash
   qdrant.exe
   ollama serve
   # Windows: scripts\setup\run_backend.bat    # Linux: python widget_api.py
   ```
5. Use your server URL: `http://your-domain.com:5001`

## Connect Frontend to Backend

### Update API URLs in Widget Files

1. **Edit `public/html/widget-standalone.html`:**
   ```javascript
   // Line 45 (approximately)
   const API_BASE_URL = 'https://your-backend-url.com'; // Change this
   ```

2. **Edit `public/html/mobile.html`:**
   ```javascript
   // Line 30 (approximately)
   const API_BASE_URL = 'https://your-backend-url.com'; // Change this
   ```

3. **Push changes:**
   ```bash
   git add public/html/widget-standalone.html public/html/mobile.html
   git commit -m "Update API URLs for production"
   git push origin main
   ```

### CORS Configuration (Important!)

Add your GitHub Pages URL to backend CORS whitelist:

**Edit `widget_api.py`:**
```python
# Around line 20
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://athem135-source.github.io",  # Add this
            "https://your-backend-url.com"
        ]
    }
})
```

## GitHub Pages URLs

After deployment, your site will be accessible at:

- **Landing Page:** https://athem135-source.github.io/PCBot/html/landing.html
- **Shareable Widget:** https://athem135-source.github.io/PCBot/html/widget-standalone.html
- **Mobile Site:** https://athem135-source.github.io/PCBot/html/mobile.html

**Note:** Root URL (https://athem135-source.github.io/PCBot/) redirects to landing page.

## Custom Domain (Optional)

### Use Your Own Domain

1. **Buy a domain** (e.g., from Namecheap, GoDaddy)
2. **Add CNAME record** in DNS settings:
   ```
   Type: CNAME
   Name: pcbot (or www)
   Value: athem135-source.github.io
   ```
3. **Configure in GitHub:**
   - Settings > Pages > Custom domain
   - Enter: `pcbot.yourdomain.com`
   - Save and wait for DNS verification

## Troubleshooting

### ❌ Pages Not Loading
**Solution:** Check Actions tab for build errors. Ensure `public/` folder exists.

### ❌ API Calls Failing
**Solutions:**
1. Verify backend is deployed and running
2. Check CORS configuration includes GitHub Pages URL
3. Ensure API_BASE_URL in HTML files points to backend
4. Check browser console for specific errors

### ❌ 404 Errors
**Solution:** GitHub Pages serves from repository root. URLs should include `/html/` path.

### ❌ Admin Mode Not Working
**Solution:** Admin mode requires backend authentication API. Deploy backend first.

## Comparison: GitHub Pages vs Netlify

| Feature | GitHub Pages | Netlify |
|---------|--------------|---------|
| **Setup** | GitHub Actions | Git push or CLI |
| **Custom Domain** | Free | Free |
| **SSL Certificate** | Free | Free |
| **Build Time** | 1-2 min | 30-60 sec |
| **Bandwidth** | 100 GB/month | 100 GB/month |
| **Deploy Triggers** | Push to main | Push to any branch |
| **Redirects** | Limited | Advanced |
| **Forms** | No | Yes |
| **Analytics** | No | Yes (paid) |

## Development Workflow

### Local Testing
```bash
# Terminal 1: Start backend
run_widget_standalone.bat

# Browser: Open http://localhost:5001
```

### Deploy to Production
```bash
git add .
git commit -m "Update features"
git push origin main
# GitHub Actions auto-deploys in 1-2 minutes
```

## Security Notes

⚠️ **Important:**
- Never commit API keys or passwords to repository
- Use environment variables for sensitive data
- GitHub Pages sites are public - don't expose backend URLs in code
- Use HTTPS for all API calls in production

## Support

### Useful Links
- **GitHub Pages Docs:** https://docs.github.com/en/pages
- **Actions Logs:** https://github.com/athem135-source/PCBot/actions
- **Repository Settings:** https://github.com/athem135-source/PCBot/settings

### Common Issues
1. **Workflow failing?** Check `.github/workflows/deploy-pages.yml` syntax
2. **Assets not loading?** Verify paths in HTML files use relative URLs
3. **Backend timeout?** Increase timeout in fetch() calls or upgrade backend hosting tier

---

**Last Updated:** 2025
**PCBot Version:** v3.4.0
