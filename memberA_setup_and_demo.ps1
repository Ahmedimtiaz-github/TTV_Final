# memberA_setup_and_demo.ps1
# Creates Member A files (assembler, api, demo runner), sets up venv, installs minimal deps, runs demo.
# Usage:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\memberA_setup_and_demo.ps1

$RepoRoot = "C:\Users\ec\Documents\TTV"
if (!(Test-Path $RepoRoot)) {
    Write-Host "ERROR: Repo path not found: $RepoRoot" -ForegroundColor Red
    exit 1
}

Write-Host "Using repo root: $RepoRoot"

# Ensure directories
$pipelineDir = Join-Path $RepoRoot "src\pipeline"
if (!(Test-Path $pipelineDir)) { New-Item -ItemType Directory -Path $pipelineDir -Force | Out-Null }

# 1) assembler.py
$assembler = @'
import os
import shutil
import tempfile
import subprocess
from PIL import Image

def _check_ffmpeg():
    try:
        subprocess.run(['ffmpeg','-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def assemble(frames_dir, audio_file, out_path, fps=24):
    """
    Assemble ordered image frames + optional audio into an MP4 using ffmpeg.

    frames_dir: directory containing images (recursively). Images will be sorted by file path.
    audio_file: path to audio file (wav/mp3) or None
    out_path: output mp4 path
    fps: frames per second
    """
    frames = []
    for root, _, files in os.walk(frames_dir):
        for f in files:
            if f.lower().endswith(('.png','.jpg','.jpeg')):
                frames.append(os.path.join(root, f))
    frames = sorted(frames)
    if not frames:
        raise ValueError(f"No image frames found in {frames_dir}")

    if not _check_ffmpeg():
        raise RuntimeError("ffmpeg not found on PATH. Install ffmpeg and ensure it's available in PATH.")

    tmpdir = tempfile.mkdtemp()
    try:
        # Normalize and copy frames into a sequential filename pattern expected by ffmpeg
        for idx, src in enumerate(frames, start=1):
            img = Image.open(src).convert("RGB")
            dst = os.path.join(tmpdir, f"frame_{idx:06d}.png")
            img.save(dst, format="PNG")

        input_pattern = os.path.join(tmpdir, "frame_%06d.png")
        cmd = ['ffmpeg', '-y', '-r', str(fps), '-i', input_pattern]
        if audio_file:
            cmd += ['-i', audio_file, '-c:a', 'aac']
        cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-shortest', out_path]

        print("Running ffmpeg to assemble video...")
        subprocess.check_call(cmd)
        print("Video assembled to", out_path)
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

def get_duration_seconds(path):
    """Return duration of a media file using ffprobe, or None if unavailable."""
    try:
        out = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of',
                              'default=noprint_wrappers=1:nokey=1', path],
                             capture_output=True, text=True, check=True)
        return float(out.stdout.strip())
    except Exception:
        return None
'@
Set-Content -Path (Join-Path $pipelineDir "assembler.py") -Value $assembler -Encoding UTF8
Write-Host "Wrote src/pipeline/assembler.py"

# 2) src/api.py
$api = @'
import os
from pipeline import assembler

def ttv_run(frames_dir, audio_file, out_path, fps=24):
    """
    High-level wrapper to assemble frames and audio into a video.
    """
    if not os.path.isdir(frames_dir):
        raise ValueError("frames_dir does not exist: " + frames_dir)
    assembler.assemble(frames_dir, audio_file, out_path, fps=fps)
'@
Set-Content -Path (Join-Path $RepoRoot "src\api.py") -Value $api -Encoding UTF8
Write-Host "Wrote src/api.py"

# 3) run_demo.py at repo root - a simple CLI that will:
#    - create placeholder frames (Pillow)
#    - synthesize audio (pyttsx3)
#    - call src.api.ttv_run to assemble
$runDemo = @'
import os
import sys
import tempfile
import argparse
from PIL import Image, ImageDraw, ImageFont
import pyttsx3
import time
# ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from api import ttv_run

def make_placeholder_frames(out_dir, frames=48, size=(1280,720), text_prefix="Demo"):
    os.makedirs(out_dir, exist_ok=True)
    for i in range(1, frames+1):
        img = Image.new("RGB", size, color=(40,40,40))
        draw = ImageDraw.Draw(img)
        txt = f"{text_prefix} - Frame {i}/{frames}"
        try:
            # Use default font (cross-platform)
            draw.text((40, size[1]//2 - 20), txt, fill=(230,230,230))
        except Exception:
            draw.text((40, size[1]//2 - 20), txt, fill=(230,230,230))
        fname = os.path.join(out_dir, f"frame_{i:06d}.png")
        img.save(fname, "PNG")
    return out_dir

def synthesize_tts(text, out_wav):
    engine = pyttsx3.init()
    # set slower rate for clarity
    rate = engine.getProperty("rate")
    engine.setProperty("rate", max(120, rate-30))
    engine.save_to_file(text, out_wav)
    engine.runAndWait()
    # tiny pause to ensure file close on some systems
    time.sleep(0.5)
    return out_wav

def demo(out_path):
    tmp = tempfile.mkdtemp(prefix="ttv_demo_")
    frames_dir = os.path.join(tmp, "frames")
    audio_file = os.path.join(tmp, "demo_audio.wav")
    print("Creating placeholder frames...")
    make_placeholder_frames(frames_dir, frames=48)
    print("Synthesizing demo TTS (offline)...")
    text = ("This is a demo video produced by the TTV pipeline. "
            "Frames are placeholders; replace visual generator with real models.")
    synthesize_tts(text, audio_file)
    print("Assembling final video (requires ffmpeg on PATH)...")
    ttv_run(frames_dir, audio_file, out_path, fps=24)
    print("Demo completed. Output:", out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run demo (placeholder frames + offline TTS)")
    parser.add_argument("--out", default="demo_output.mp4", help="Output mp4 path")
    args = parser.parse_args()
    if args.demo:
        demo(args.out)
    else:
        print("Run with --demo to produce demo_output.mp4")
'@
Set-Content -Path (Join-Path $RepoRoot "run_demo.py") -Value $runDemo -Encoding UTF8
Write-Host "Wrote run_demo.py"

# 4) tests/test_end_to_end.py
$test = @'
import os
import sys
import subprocess
import time
# ensure src is importable during tests
HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
PY = sys.executable

def test_end_to_end_demo_creates_mp4(tmp_path):
    out = os.path.join(tmp_path, "demo_output.mp4")
    cmd = [PY, os.path.join(REPO_ROOT, "run_demo.py"), "--demo", "--out", out]
    # run the demo (this will require ffmpeg and pyttsx3 to be installed)
    proc = subprocess.run(cmd, check=False)
    assert os.path.exists(out), "demo mp4 not created"
    assert os.path.getsize(out) > 1000, "demo mp4 size suspiciously small"
'@
Set-Content -Path (Join-Path $RepoRoot "tests\test_end_to_end.py") -Value $test -Encoding UTF8
Write-Host "Wrote tests/test_end_to_end.py"

# 5) update requirements.txt (append required libs if missing)
$reqPath = Join-Path $RepoRoot "requirements.txt"
$reqs = Get-Content $reqPath -ErrorAction SilentlyContinue
$toAdd = @("pillow","pyttsx3")
$missing = @()
foreach ($r in $toAdd) {
    if (!($reqs -match ("^\s*"+[regex]::Escape($r)+"\s*$"))) {
        $missing += $r
    }
}
if ($missing.Count -gt 0) {
    Add-Content -Path $reqPath -Value ("`n# Member A requirements (placeholder visuals + offline TTS)" + [string]::Join("`n",$missing))
    Write-Host "Appended requirements to requirements.txt: $($missing -join ', ')"
} else {
    Write-Host "requirements.txt already contains required packages."
}

# 6) Append demo instructions to README.md
$readmePath = Join-Path $RepoRoot "README.md"
$demoText = @"
## Demo (Member A - assembler/orchestrator)

Run a quick placeholder demo (creates placeholder frames + offline TTS and assembles them).
**Requires**: Python packages in `requirements.txt` and `ffmpeg` installed on PATH.

From repo root (Windows PowerShell):
```powershell
python -m pip install -r requirements.txt
python run_demo.py --demo --out demo_output.mp4
"@
Add-Content -Path $readmePath -Value $demoText
Write-Host "Appended demo instructions to README.md"

7) Create venv and install deps
Push-Location $RepoRoot
$venvDir = Join-Path $RepoRoot ".venv"
if (!(Test-Path $venvDir)) {
python -m venv $venvDir
Write-Host "Created virtual environment at $venvDir"
} else {
Write-Host "Virtual environment already exists at $venvDir"
}

$pythonExe = Join-Path $venvDir "Scripts\python.exe"
if (!(Test-Path $pythonExe)) { $pythonExe = "python" }

Write-Host "Installing python packages (pillow, pyttsx3)..."
& $pythonExe -m pip install --upgrade pip > $null
& $pythonExe -m pip install pillow pyttsx3 > $null
Write-Host "Packages installed."

8) Run the demo now
$outMp4 = Join-Path $RepoRoot "demo_output.mp4"
Write-Host "Running demo to produce $outMp4 ... (this requires ffmpeg on PATH)"
$runCmd = & $pythonExe (Join-Path $RepoRoot "run_demo.py") --demo --out $outMp4 2>&1
if (Test-Path $outMp4) {
Write-Host "Demo completed successfully. Output file:" $outMp4 -ForegroundColor Green
} else {
Write-Host "Demo did not produce the mp4. Inspect output below and ensure ffmpeg is installed and on PATH:" -ForegroundColor Yellow
Write-Host $runCmd
Write-Host "ffmpeg download: https://ffmpeg.org/download.html"
}

Pop-Location

Write-Host "Member A files created. If demo failed because ffmpeg is missing install ffmpeg and re-run:"
Write-Host "python run_demo.py --demo --out demo_output.mp4"

