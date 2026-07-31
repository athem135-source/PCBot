# PCBot Standalone Widget - Deployment Guide

## 📦 What is widget-standalone.html?

A shareable, standalone webpage that embeds the PCBot widget. Perfect for:
- Google Sites embedding
- Sharing via link (with ngrok/cloudflare tunnel)
- Corporate intranet deployment
- Public website integration

---

## 🚀 Quick Start (Local Testing)

1. **Start the backend:**
   ```powershell
   cd "d:\PLANNING WORK\Chatbot\PND BOT MINI DEMO"
   .\run_widget.ps1
   ```

2. **Build the widget:**
   ```powershell
   cd frontend-widget
   npm run build
   ```

3. **Open in browser:**
   ```
   http://localhost:5001/widget-standalone.html
   ```

---

## 🌐 Deployment Options

### Option 1: ngrok (Quick Testing)

**Step 1:** Install ngrok from https://ngrok.com/

**Step 2:** Expose your local server:
```powershell
ngrok http 5001
```

You'll get a URL like: `https://abc123.ngrok.io`

**Step 3:** Share the link:
```
https://abc123.ngrok.io/widget-standalone.html
```

**No configuration needed** - the page auto-detects!

---

### Option 2: Cloudflare Tunnel (Free, Permanent)

**Step 1:** Install cloudflared:
```powershell
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

**Step 2:** Create tunnel:
```powershell
cloudflared tunnel --url http://localhost:5001
```

You'll get: `https://random-name.trycloudflare.com`

**Step 3:** Share the link:
```
https://random-name.trycloudflare.com/widget-standalone.html
```

---

### Option 3: Google Sites Embed

**Method A: Full Page Embed**

1. Create a new page on Google Sites
2. Insert → **Embed**
3. **Embed from the web** → Enter your ngrok/cloudflare URL:
   ```
   https://your-url.ngrok.io/widget-standalone.html
   ```

**Method B: Embed Code**

1. Insert → **Embed** → **Embed code**
2. Paste:
   ```html
   <iframe 
     src="https://your-url.ngrok.io/widget-standalone.html" 
     width="100%" 
     height="900px" 
     frameborder="0"
     style="border: none; border-radius: 8px;">
   </iframe>
   ```

---

### Option 4: Custom Domain Deployment

If deploying on a server with a custom domain:

**Step 1:** Copy these files to your web server:
```
widget-standalone.html
frontend-widget/dist/pdbot-widget.js → /assets/pdbot-widget.js
frontend-widget/src/assets/uraan-pak.png → /assets/uraan-pak.png
frontend-widget/src/assets/5Vs.png → /assets/5Vs.png
```

**Step 2:** Update CORS in `widget_api.py`:
```python
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://yourdomain.com",
            "https://sites.google.com"
        ]
    }
})
```

**Step 3:** Set API URL in the HTML:
```html
<script>
  window.WIDGET_API_URL = 'https://api.yourdomain.com';
</script>
<script src="widget-standalone.html"></script>
```

---

## 🔧 Configuration

### Auto-Detection (Default)

The widget automatically detects:
- `localhost` → Uses `http://localhost:5001`
- Other domains → Uses same origin or `window.WIDGET_API_URL`

### Manual Configuration

If you need to override the API URL, add this **before** the widget loads:

```html
<script>
  window.WIDGET_API_URL = 'https://your-backend-url.com';
</script>
```

---

## 📱 Features

✅ Fully responsive (desktop, tablet, mobile)
✅ Auto-detects environment (local vs deployed)
✅ Displays logos from backend
✅ Error handling if backend is down
✅ Clean, professional UI
✅ Works in iframes (Google Sites compatible)

---

## 🛡️ Security Notes

1. **CORS Configuration**: Update `widget_api.py` to allow your domain
2. **HTTPS Required**: For production, use HTTPS (ngrok/cloudflare provide this)
3. **API Key**: Consider adding authentication for public deployments

---

## 📊 Monitoring

Check if the widget is working:

1. **Backend Running**: Visit `http://localhost:5001/health` (should return OK)
2. **Widget Loading**: Open browser console, check for errors
3. **API Calls**: Network tab should show successful `/api/chat` requests

---

## 🆘 Troubleshooting

**Widget doesn't load:**
- Check backend is running: `http://localhost:5001/health`
- Check browser console for errors
- Verify CORS settings in `widget_api.py`

**Can't access from other devices:**
- Use ngrok or cloudflare tunnel (not just localhost)
- Check firewall isn't blocking port 5001

**Google Sites embed not working:**
- Use iframe method instead of direct embed
- Ensure HTTPS URL (ngrok/cloudflare provide this)

---

**Government of Pakistan**
*Ministry of Planning, Development & Special Initiatives*
