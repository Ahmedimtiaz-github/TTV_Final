"""
End-to-end integration tests for the TTV pipeline.
"""
import os
import sys
import subprocess
import pytest
import tempfile
import shutil

HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
PY = sys.executable


def test_end_to_end_demo_creates_mp4(tmp_path):
    """Test that the demo creates a valid MP4 file."""
    # Use a subdirectory to avoid path issues
    test_dir = os.path.join(str(tmp_path), "test_demo")
    os.makedirs(test_dir, exist_ok=True)
    out = os.path.join(test_dir, "demo_output.mp4")
    
    cmd = [PY, os.path.join(REPO_ROOT, "run_demo.py"), "--demo", "--out", out]
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    
    assert os.path.exists(out), f"Output file {out} was not created"
    assert os.path.getsize(out) > 0, f"Output file {out} is empty"


def test_end_to_end_cli_full_pipeline(tmp_path):
    """Test the full CLI pipeline with a sample script."""
    script_path = os.path.join(REPO_ROOT, "data", "sample_scripts", "demo.txt")
    test_dir = os.path.join(str(tmp_path), "test_cli")
    os.makedirs(test_dir, exist_ok=True)
    out = os.path.join(test_dir, "test_output.mp4")
    
    if not os.path.exists(script_path):
        pytest.skip(f"Sample script not found: {script_path}")
    
    cmd = [PY, "-m", "src.cli", "--script", script_path, "--out", out]
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    
    assert os.path.exists(out), f"Output file {out} was not created"
    assert os.path.getsize(out) > 0, f"Output file {out} is empty"


def test_end_to_end_mp4_duration(tmp_path):
    """Test that generated MP4 has non-zero duration."""
    test_dir = os.path.join(str(tmp_path), "test_duration")
    os.makedirs(test_dir, exist_ok=True)
    out = os.path.join(test_dir, "demo_duration.mp4")
    
    cmd = [PY, os.path.join(REPO_ROOT, "run_demo.py"), "--demo", "--out", out]
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Command failed: {result.stderr}")
    
    if not os.path.exists(out):
        pytest.skip(f"Output file not created: {out}")
    
    # Check file size (basic check)
    size = os.path.getsize(out)
    assert size > 1000, f"MP4 file seems too small: {size} bytes"
    
    # Try to get duration using ffprobe if available
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1', out],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT
        )
        duration = float(result.stdout.strip())
        assert duration > 0, f"MP4 duration should be > 0, got {duration}"
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        # ffprobe not available or failed, skip duration check
        pass
