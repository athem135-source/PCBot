# PCBot Netlify Deployment Guide

## Quick Deploy to Netlify

### Option 1: GitHub Integration (Recommended)
1. **Connect Repository:**
   - Go to [Netlify](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Select "GitHub" and authorize
   - Choose repository: `athem135-source/PCBot`

2. **Configure Build Settings:**
   - Build command: `echo "Static files - no build needed"`
   - Publish directory: `public`
   - Click "Deploy site"

3. **Environment Variables (if backend needed):**
   - Go to Site settings → Environment variables
   - Add:
     - `GROQ_API_KEY` (if using Groq)
     - `QDRANT_URL` (if using external Qdrant)

### Option 2: Netlify CLI
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod
```

### Option 3: Drag & Drop
1. Go to [Netlify Drop](https://app.netlify.com/drop)
2. Drag the `public` folder
3. Done!

## What Gets Deployed

### Static Files (Frontend Only)
- ✅ Landing page with mode selector
- ✅ Widget standalone (shareable)
- ✅ Mobile site (shareable)
- ✅ All assets (logos, images)
- ❌ Backend API (requires separate deployment)

### Architecture
```
Netlify (Frontend)          Your Server (Backend)
┌──────────────┐            ┌──────────────┐
│ Landing Page │            │ Flask API    │
│ Widget UI    │  ←──────→  │ RAG Engine   │
│ Mobile Site  │  (CORS)    │ Qdrant       │
└──────────────┘            │ Ollama       │
                            └──────────────┘
```

## Backend Deployment Options

### For Full Functionality, Deploy Backend Separately:

#### Option 1: Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Option 2: Render.com
1. Go to [Render Dashboard](https://dashboard.render.com)
2. New → Web Service
3. Connect GitHub repo
4. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `python widget_api.py`
   - Environment: Add API keys

#### Option 3: Your Office Server
- Keep running: `run_widget_standalone.bat`
- Use ngrok/Cloudflare tunnel
- Update frontend API URL in HTML files

## Post-Deployment Configuration

### Update API URLs
Edit these files in `public/html/`:

**landing.html:**
```javascript
const API_BASE = 'https://your-backend.com'; // Change from window.location.origin
```

**widget-standalone.html:**
```javascript
const API_URL = 'https://your-backend.com';
```

**mobile.html:**
```javascript
const API_URL = 'https://your-backend.com';
```

### CORS Configuration
Update `widget_api.py`:
```python
CORS(app, origins=['https://your-netlify-site.netlify.app'])
```

## Testing Deployment

1. **Frontend Only (Static):**
   - Visit: `https://your-site.netlify.app`
   - Mode selector should work
   - UI loads correctly
   - ⚠️ Chat won't work without backend

2. **With Backend:**
   - Deploy backend to Railway/Render
   - Update API URLs in frontend files
   - Push to GitHub (auto-deploys to Netlify)
   - Test full chat functionality

## Netlify Features Included

- ✅ Auto-deploy on Git push
- ✅ SSL certificate (HTTPS)
- ✅ CDN distribution
- ✅ Custom domain support
- ✅ Redirect rules configured
- ✅ Security headers
- ✅ Asset caching

## Custom Domain

1. Go to Site settings → Domain management
2. Add custom domain
3. Update DNS:
   - Add CNAME: `www` → `your-site.netlify.app`
   - Add A record: `@` → Netlify IP

## Troubleshooting

### "Page not found"
- Check `netlify.toml` redirect rules
- Ensure `public` folder structure is correct

### "API connection error"
- Backend not deployed
- CORS not configured
- Wrong API URL in frontend

### "Assets not loading"
- Check paths in HTML files
- Verify `/assets/*` folder exists
- Clear browser cache

## Security Notes

⚠️ **Important:**
- Admin password is validated server-side
- Session authentication requires backend
- Without backend, admin features won't work
- Frontend-only deployment = Read-only demo

## Next Steps

1. Deploy frontend to Netlify ✅
2. Deploy backend to Railway/Render
3. Update API URLs in frontend
4. Configure CORS
5. Test end-to-end
6. Set up custom domain (optional)

---

**Support:** M. Hassan Arif Afridi  
**Repository:** https://github.com/athem135-source/PCBot
