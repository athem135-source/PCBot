# Scripts Directory

## Purpose
Contains utility scripts and setup tools for PCBot deployment and management.

## Directory Structure

### `setup/` - Setup and Deployment Scripts
- **`setup.bat`**: Complete environment setup (venv, dependencies, models)
- **`run_widget_standalone.bat`**: Daily launcher with auto-services
- **`stats_dashboard.ps1`**: Statistics dashboard PowerShell script
- **`run_calibration_test.bat`**: 300-question test suite launcher
- **`start_tunnel.ps1`**: Cloudflare tunnel for external access

### Root Scripts (Legacy/Deprecated)
- **`run.bat`**, **`start.bat`**: Old launchers (use root-level versions instead)
- **`diagnose.bat`**: System diagnostics tool
- **`run_updated_pndbot.ps1`**: Streamlit launcher (legacy)

## Recommended Usage

**For daily use, use the root-level scripts:**
- `setup.bat` (root) - First-time setup
- `run_widget_standalone.bat` (root) - Daily launcher

These are copies of the scripts in `setup/` for easier user access.
- **create_shortcut.bat** - Create desktop shortcut

## PowerShell Scripts (.ps1)

- **run.ps1** - PowerShell launcher with better error handling
- **run_updated_pndbot.ps1** - Launcher with automatic updates check
- **generate_detailed_report.ps1** - Generate diagnostic reports

## Python Scripts (.py)

- **rebuild_vectordb.py** - Rebuild Qdrant vector database from scratch

## Usage

### First Time Setup (Windows)

```cmd
# Run setup (installs dependencies, checks services)
setup.bat

# Start application
start.bat
```

### Daily Usage

```cmd
# Quick start
run.bat

# OR with PowerShell
powershell -ExecutionPolicy Bypass -File scripts\run.ps1
```

### Rebuild Vector Database

```bash
# Rebuild from current manual
python scripts/rebuild_vectordb.py
```

### Diagnostics

```cmd
# Check system health
diagnose.bat
```

## Notes

- All scripts should be run from the **project root directory**
- PowerShell scripts may require execution policy bypass
- Python scripts assume virtual environment is activated
