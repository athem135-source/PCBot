# 🚀 Quick Start Guide - PCBot v4.0

## First Time Setup (One Time Only)

1. **Run Setup:**
   ```
   Double-click: setup.bat
   ```
   
   This will:
   - ✅ Create Python virtual environment
   - ✅ Install all dependencies (Flask, sentence-transformers, etc.)
   - ✅ Setup Qdrant vector database
   - ✅ Download Ollama Mistral model
   - ✅ Download embedding models
   - ✅ Run initial warmup (first run takes longer)

   **Time:** ~15-20 minutes (depending on internet speed)

## Daily Use

2. **Launch PCBot:**
   ```
   Double-click: run_widget_standalone.bat
   ```
   
   This will:
   - ✅ Check & start Qdrant
   - ✅ Check & start Ollama
   - ✅ Activate virtual environment
   - ✅ Start Flask backend
   - ✅ Open browser to landing page
   - ✅ Create Cloudflare tunnel for sharing

   **Time:** ~30 seconds

## File Organization

```
📁 Root Directory (You are here!)
├── setup.bat                    👈 Run this FIRST (one time)
├── run_widget_standalone.bat    👈 Run this DAILY (quick start)
├── run_pcbot.bat               (Alternative launcher with menu)
│
├── 📁 public/
│   ├── html/          (All web pages)
│   └── assets/        (Images, logos)
│
├── 📁 scripts/
│   └── setup/         (All batch scripts)
│
└── 📁 deployment/
    └── NETLIFY.md     (Cloud deployment guide)
```

## Troubleshooting

### "Embedding model not available"
- **Fix:** Run `setup.bat` again
- This installs sentence-transformers in virtual environment

### "Qdrant not found"
- **Install:** `winget install qdrant`
- Or download from: https://qdrant.tech/documentation/guides/installation/

### "Ollama not found"
- **Install:** Download from https://ollama.ai/download
- After install: `ollama pull mistral`

### "Virtual environment not found"
- **Fix:** Delete `.venv` folder and run `setup.bat` again

## Need Help?

- 📖 Full documentation: `README.md`
- 🌐 Netlify deployment: `deployment/NETLIFY.md`
- 🎬 Video tutorials: (coming soon)

## Version

**PCBot v4.0.0**
- ✅ Organized folder structure
- ✅ Auto-start services
- ✅ Netlify deployment ready
- ✅ Admin mode selector
- ✅ Password-protected features

---

**Developer:** M. Hassan Arif Afridi  
**Organization:** Government of Pakistan - Ministry of Planning, Development & Special Initiatives
