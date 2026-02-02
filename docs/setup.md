# Setup Guide

This guide explains how to set up the TTV (Text-to-Video) pipeline on Windows (PowerShell) and Linux.

## Prerequisites

- Python 3.10 or higher
- ffmpeg (for video assembly)
- pip (Python package manager)

## Windows Setup (PowerShell)

### 1. Install Python

If Python is not installed, download from [python.org](https://www.python.org/downloads/) and ensure "Add Python to PATH" is checked during installation.

Verify installation:
```powershell
python --version
```

### 2. Install ffmpeg

**Option A: Using Chocolatey (recommended)**
```powershell
choco install ffmpeg
```

**Option B: Manual installation**
1. Download ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH environment variable
4. Restart PowerShell

Verify installation:
```powershell
ffmpeg -version
```

### 3. Create Virtual Environment

Navigate to the project directory:
```powershell
cd C:\Users\ec\Documents\TTV_Final
```

Create a virtual environment:
```powershell
python -m venv venv
```

Activate the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies

With the virtual environment activated:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Verify Installation

Run the parser test:
```powershell
python -m src.parser --in data/sample_scripts/demo.txt --out data/sample_scripts/demo.json
```

Run unit tests:
```powershell
pip install pytest
pytest -q tests/
```

## Linux Setup

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip ffmpeg
```

### 2. Create Virtual Environment

Navigate to the project directory:
```bash
cd /path/to/TTV_Final
```

Create a virtual environment:
```bash
python3 -m venv venv
```

Activate the virtual environment:
```bash
source venv/bin/activate
```

### 3. Install Python Dependencies

With the virtual environment activated:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation

Run the parser test:
```bash
python -m src.parser --in data/sample_scripts/demo.txt --out data/sample_scripts/demo.json
```

Run unit tests:
```bash
pip install pytest
pytest -q tests/
```

## Running the Pipeline

### Quick Demo

Run the demo script:
```powershell
# Windows PowerShell
python run_demo.py --demo --out demo_output.mp4
```

```bash
# Linux
python run_demo.py --demo --out demo_output.mp4
```

### Full Pipeline

Run with a custom script:
```powershell
# Windows PowerShell
python -m src.cli --script data/sample_scripts/demo.txt --out output.mp4
```

```bash
# Linux
python -m src.cli --script data/sample_scripts/demo.txt --out output.mp4
```

## Troubleshooting

### pyttsx3 Issues

If pyttsx3 fails on Linux, you may need to install additional system packages:

**Ubuntu/Debian:**
```bash
sudo apt-get install -y espeak espeak-data libespeak1 libespeak-dev
```

**Fedora:**
```bash
sudo dnf install espeak espeak-devel
```

### ffmpeg Not Found

Ensure ffmpeg is in your PATH:
- Windows: Check `ffmpeg -version` in a new PowerShell window
- Linux: Check `which ffmpeg` and `ffmpeg -version`

### Import Errors

If you get import errors, ensure:
1. Virtual environment is activated
2. You're running commands from the project root directory
3. All dependencies are installed: `pip install -r requirements.txt`

### Audio Synthesis Issues

If pyttsx3 doesn't work, the pipeline will attempt to fall back to gTTS (requires internet). To use gTTS explicitly:
```bash
pip install gtts
```

Note: gTTS requires an internet connection and is not fully offline.

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Build the image
docker build -t ttv-pipeline -f docker/Dockerfile .

# Run the demo
docker run --rm -v $(pwd)/output:/app/output ttv-pipeline

# Or use docker-compose
cd infra
docker-compose up
```

## Next Steps

- Read [README.md](../README.md) for usage examples
- Check [docs/architecture.md](architecture.md) for pipeline architecture
- Review [docs/scene-schema.md](scene-schema.md) for script format details
