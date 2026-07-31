Setup scripts folder

Purpose:
- Contains setup and helper scripts used by the installer and runtime wrapper.
- Key files:
  - setup.bat           : Full one-time installation and initialization (venv, pip, Docker/Qdrant, Ollama checks)
  - run_backend.bat     : Backend wrapper - starts widget_api.py and writes logs to logs\pcbot-backend.log
  - run_calibration_test.bat : Launcher for the 300-question calibration test

Notes:
- Prefer using run_pcbot_ultimate.bat in the repository root to run common workflows.
- Avoid editing these scripts unless you understand Windows batch escaping and START semantics.
