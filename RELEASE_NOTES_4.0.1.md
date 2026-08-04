PCBot v4.0.1 - Release Notes
============================

Release date: 2026-08-04

Highlights
----------
- Added `setup_docker_engine.bat` for Windows Server environments using Docker Engine.
- Kept the native `setup.bat` path separate for non-Docker installs.
- Clarified support policy in README and SECURITY docs.
- Marked v3.x and earlier as unsupported.

Setup details
-------------
- Qdrant is now supported via Docker Engine on Windows Server.
- Ollama can optionally run in Docker, but host-based Ollama remains supported.
- The server setup is intended for clean installs on new PCs/servers.

Notes
-----
- This release does not re-index or re-chunk data by itself.
- Vector indexing and chunking still happen in the backend when it initializes against an empty Qdrant store.
- Existing Qdrant data persists unless you remove the Docker volume.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
