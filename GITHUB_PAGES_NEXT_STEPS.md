# GitHub Pages Deployment - Complete Guide

## You've enabled GitHub Actions - Great! Here's what's next:

### Step 1: ✅ DONE - Enable GitHub Actions
You've already done this in Settings > Pages > Source: GitHub Actions

---

### Step 2: Verify Deployment is Running

1. **Go to the Actions tab** in your repository:
   ```
   https://github.com/athem135-source/PCBot/actions
   ```

2. **Look for the workflow** named "Deploy to GitHub Pages"
   - It should show as running or completed
   - Click on it to see the deployment progress

3. **Deployment Status**:
   - 🟡 **Yellow dot** = Currently deploying (1-2 minutes)
   - ✅ **Green checkmark** = Successfully deployed
   - ❌ **Red X** = Failed (check logs for errors)

---

### Step 3: Access Your Live Site

Once the workflow shows a green checkmark:

**Your PCBot is live at:**
```
https://athem135-source.github.io/PCBot/
```

**Direct links:**
- Landing Page: https://athem135-source.github.io/PCBot/html/landing.html
- Widget: https://athem135-source.github.io/PCBot/html/widget-standalone.html
- Mobile: https://athem135-source.github.io/PCBot/html/mobile.html

---

### Step 4: Important - Backend is NOT Deployed Yet

⚠️ **GitHub Pages only hosts static files (HTML, CSS, JS)**

The backend (Flask API with RAG) needs separate hosting:

#### Option A: Railway (Recommended - Free Tier)
1. Go to https://railway.app/
2. Sign in with GitHub
3. New Project > Deploy from GitHub repo
4. Select `athem135-source/PCBot`
5. Configure:
   - Start Command (Windows): `scripts\setup\run_backend.bat`  (Linux: `python widget_api.py`)
   - Environment: Add `PORT=5001`
6. Deploy
7. Copy your Railway URL (e.g., `https://pcbot-production.up.railway.app`)

#### Option B: Render (Free Tier)
1. Go to https://render.com/
2. New > Web Service
3. Connect GitHub > Select PCBot
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command (Windows): `scripts\setup\run_backend.bat`  (Linux: `python widget_api.py`)
5. Deploy
6. Copy your Render URL

#### Option C: Your Office Server
If you have a static IP:
1. Install Python, Qdrant, Ollama on server
2. Run `setup.bat`
3. Configure firewall: Allow port 5001
4. Run `scripts\setup\run_backend.bat` (Windows) or `python widget_api.py` (Linux)
5. Use: `http://your-ip:5001`

---

### Step 5: Connect Frontend to Backend

After deploying backend, update API URLs:

**Edit these files:**

1. **`public/html/widget-standalone.html`** (around line 45):
```javascript
const API_BASE_URL = 'https://your-backend-url.com'; // Change this
```

2. **`public/html/mobile.html`** (around line 30):
```javascript
const API_BASE_URL = 'https://your-backend-url.com'; // Change this
```

3. **`public/html/landing.html`** (around line 250):
```javascript
const API_BASE_URL = 'https://your-backend-url.com'; // Change this
```

**Commit and push:**
```bash
git add public/html/*.html
git commit -m "Update API URLs for production backend"
git push origin main
```

GitHub Actions will auto-deploy the changes (takes 1-2 minutes).

---

### Step 6: Configure CORS on Backend

**Edit `widget_api.py`** (around line 20):

```python
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://athem135-source.github.io",  # Add your GitHub Pages URL
            "https://your-backend-url.com"         # Add your backend URL
        ]
    }
})
```

Redeploy your backend after this change.

---

### Step 7: Test Everything

1. **Open your GitHub Pages site:**
   ```
   https://athem135-source.github.io/PCBot/
   ```

2. **Select User Mode or Admin Mode**

3. **Try asking a question** like:
   ```
   What is DDWP?
   ```

4. **Expected behavior:**
   - If backend is running: You get an AI response with sources
   - If backend is NOT running: You see "Backend not available" message

---

### Troubleshooting

#### ❌ "Failed to fetch" or "Backend not available"

**Causes:**
- Backend not deployed yet
- Backend URL not updated in HTML files
- CORS not configured properly

**Solutions:**
1. Verify backend is running (visit `https://your-backend-url.com/health`)
2. Check API_BASE_URL in HTML files matches backend URL
3. Verify CORS includes GitHub Pages URL

---

#### ❌ GitHub Actions workflow failed

**Common causes:**
- `.github/workflows/deploy-pages.yml` syntax error
- Permissions issue

**Solution:**
1. Go to Settings > Actions > General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Save
5. Re-run the workflow

---

#### ❌ 404 errors on GitHub Pages

**Cause:** Files not in `public/` folder

**Solution:**
1. Verify your files are in `public/html/` and `public/assets/`
2. Check `.github/workflows/deploy-pages.yml` copies `public/*` to `_site/`

---

### Step 8: Custom Domain (Optional)

Want to use your own domain (e.g., `pcbot.yourdomain.com`)?

1. **Buy a domain** from Namecheap, GoDaddy, etc.

2. **Add DNS record:**
   ```
   Type: CNAME
   Name: pcbot (or www)
   Value: athem135-source.github.io
   TTL: 3600
   ```

3. **Configure in GitHub:**
   - Settings > Pages > Custom domain
   - Enter: `pcbot.yourdomain.com`
   - Save
   - Wait for DNS verification (5-60 minutes)

4. **Enable HTTPS:**
   - GitHub automatically provisions SSL certificate
   - Takes 5-10 minutes after DNS verification

---

### What's Deployed?

| Item | Hosted Where? | Status |
|------|--------------|--------|
| **Frontend (HTML/CSS/JS)** | GitHub Pages | ✅ Automatic |
| **Landing Page** | GitHub Pages | ✅ Automatic |
| **Widget Interface** | GitHub Pages | ✅ Automatic |
| **Mobile Site** | GitHub Pages | ✅ Automatic |
| **Flask Backend** | Separate (Railway/Render) | ⏳ Manual |
| **Qdrant Vector DB** | Backend server | ⏳ Manual |
| **Ollama LLM** | Backend server | ⏳ Manual |

---

### Deployment Workflow

Every time you push to `main` branch:

1. **GitHub Actions runs** (`.github/workflows/deploy-pages.yml`)
2. **Copies `public/` folder** to deployment artifact
3. **Deploys to GitHub Pages** (takes 1-2 minutes)
4. **Your site updates automatically**

No manual deployment needed for frontend changes!

---

### Monitoring

**Check deployment status:**
```
https://github.com/athem135-source/PCBot/deployments
```

**View deployment logs:**
```
https://github.com/athem135-source/PCBot/actions
```

---

### Cost Summary

| Service | Free Tier | Cost |
|---------|-----------|------|
| **GitHub Pages** | Unlimited public repos | $0/month |
| **GitHub Actions** | 2000 minutes/month | $0/month |
| **Railway** | 500 hours/month + $5 credit | $0-5/month |
| **Render** | Limited hours | $0/month |
| **Cloudflare** | Unlimited bandwidth | $0/month |

**Total:** Free for frontend, $0-5/month for backend

---

### Support

If you encounter issues:

1. **Check workflow logs:**
   - Actions tab > Latest workflow > View logs

2. **Verify file structure:**
   ```
   PCBot/
   ├── public/
   │   ├── html/
   │   └── assets/
   └── .github/workflows/deploy-pages.yml
   ```

3. **Test locally:**
   ```powershell
   # Open index redirect
   start public/html/landing.html
   ```

---

### Next Steps After Successful Deployment

1. ✅ Share your live site: `https://athem135-source.github.io/PCBot/`
2. 🚀 Deploy backend to Railway/Render
3. 🔗 Update API URLs in HTML files
4. 🧪 Test full functionality
5. 📊 Monitor usage via GitHub insights
6. 🔒 Review security settings (CORS, HTTPS)
7. 📱 Test on mobile devices
8. 🌐 (Optional) Set up custom domain

---

**Congratulations! Your PCBot is now deployed on GitHub Pages! 🎉**

The frontend is live. Just deploy the backend and connect them via API URLs.
