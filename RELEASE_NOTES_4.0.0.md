PCBot v4.0.0 — Release Notes
=================================

Release date: 2026-07-30

Overview
--------
This release (4.0.0) collects a set of bug fixes, stability hardenings, and small feature updates that were necessary after model and dependency changes following the 3.x line. The focus was on making the Windows launcher and standalone widget reliable, improving tunnel detection, fixing backend crashes, hardening service startup (Qdrant/Ollama), and consolidating admin and feedback UX.

Key fixes & changes
-------------------
- Launcher & startup
  - Fixed Windows batch quoting/encoding issues that caused "... was unexpected at this time." Errors caused by stray non-ASCII characters, stray CRs, and fragile parenthesized IF blocks were removed.
  - Reworked the standalone launcher (run_widget_standalone.bat) to:
    - Wait for backend /health before opening a tunnel or browser (prevents Cloudflare routing to an unavailable backend).
    - Start cloudflared in an isolated PowerShell window and use robust UTF-8/UTF-16-safe detection for the trycloudflare quick-tunnel URL (replaces fragile FINDSTR logic).
    - Capture tunnel output in a safe temporary file and fall back to local host if the URL is not detected.
  - Added SHOW_CONSOLE mode to backend runner so developers can run the backend visibly for live logs.

- Backend (Flask)
  - Removed duplicate route registration that could cause the Flask app to crash on startup (AssertionError: view function mapping overwriting existing endpoint).
  - Added /feedback/submit endpoint and file-based feedback/feedback.jsonl storage (JSON Lines) for simple audit and admin review.
  - Added more robust /admin/status and /admin/statistics payloads to support multiple UI shapes (backwards-compatible changes).
  - Hardened health checks and added additional error messages to make troubleshooting easier when Qdrant or Ollama are unavailable.

- Qdrant & Ollama
  - Improved Qdrant auto-start logic on Windows: attempts local binary, then docker run fallback for container name `pcbot-qdrant` (requires Docker installed and sufficient permissions).
  - Clearer error messages when Qdrant is unreachable (WinError 10061) and guidance in README for starting container manually.
  - Dashboard now reads qdrant_status, ollama_status, model_loaded, and embedding_ready from multiple response shapes.

- Cloudflare / Tunnel
  - Replaced FINDSTR-based Unicode parsing with PowerShell Get-Content -Raw (handles BOM/Unicode formats).
  - cloudflared is still used in quick-tunnel (trycloudflare) mode by default — these tunnels are ephemeral and account-less. For production stability, create a named tunnel with a Cloudflare account and origin cert.

- Admin UI & UX
  - Consolidated admin tools into a single Admin Console entry and unified Admin Dashboard showing Version, Sessions, Qdrant, Ollama, Model, Embedding, and Feedback counts.
  - Feedback button matches option-card styling and is displayed in User mode only (admin controls hidden), per the requested UX.
  - Centered and enlarged widget and mobile cards on the landing page (non-mobile) and enlarged chat icon per request.

- Misc & documentation
  - Added RELEASE_NOTES_4.0.0.md to the repo with these details.
  - Updated README.md with v4.0.0 notes and guidance for tunnel usage and Qdrant Docker start instructions.
  - Added security recommendations and persistence notes (feedback and sessions currently file-based; consider SQLite for persistence and easier admin queries).

Known limitations & recommendations
---------------------------------
- Qdrant docker auto-start requires Docker CLI on PATH and appropriate permissions. If Docker is not usable, start Qdrant manually:
  docker run -d --name pcbot-qdrant -p 6338:6338 qdrant/qdrant

- cloudflared quick tunnels (trycloudflare) are ephemeral. For production, create a named Cloudflare Tunnel with an origin cert. See: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps

- Feedback and sessions are stored in JSONL or in-memory respectively. For production auditing, migrate to SQLite or another persistent store and add admin viewer + CSV export.

- Model loading: local Ollama model auto-warmup remains required. If large model changes occur (Mistral/LLaMA updates), you may need to re-download or reconfigure model paths.

Contact & support
-----------------
If you prefer, this release can be packaged into a GitHub release with the prebuilt artifacts and a more detailed changelog. Reply to this issue/comment with: "Create release now" and confirm you are signed in to GitHub CLI on this machine.


