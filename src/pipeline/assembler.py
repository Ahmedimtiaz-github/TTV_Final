import os
import shutil
import tempfile
import subprocess
from PIL import Image

def _check_ffmpeg():
    try:
        subprocess.run(['ffmpeg','-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def assemble(frames_dir, audio_file, out_path, fps=24):
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
        for idx, src in enumerate(frames, start=1):
            img = Image.open(src).convert("RGB")
            dst = os.path.join(tmpdir, f"frame_{idx:06d}.png")
            img.save(dst, format="PNG")
        input_pattern = os.path.join(tmpdir, "frame_%06d.png")
        cmd = ['ffmpeg','-y','-r',str(fps),'-i',input_pattern]
        if audio_file:
            cmd += ['-i', audio_file, '-c:a', 'aac']
        cmd += ['-c:v','libx264','-pix_fmt','yuv420p','-shortest', out_path]
        subprocess.check_call(cmd)
    finally:
        try: shutil.rmtree(tmpdir)
        except: pass
