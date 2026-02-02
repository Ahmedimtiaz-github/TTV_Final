"""
API module: provides high-level entry points for the TTV pipeline.
"""
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.pipeline import assembler

def ttv_run(frames_dir=None, audio_file=None, out_path=None, fps=24, script_path=None):
    """
    High-level TTV pipeline runner.
    
    Can be called in two modes:
    1. Full pipeline mode: provide script_path and out_path
    2. Assembly-only mode: provide frames_dir, audio_file, and out_path
    
    Args:
        frames_dir: Directory containing frames (assembly-only mode)
        audio_file: Path to audio file (assembly-only mode)
        out_path: Output MP4 file path
        fps: Frames per second (default: 24)
        script_path: Input script text file (full pipeline mode)
    """
    if script_path:
        # Full pipeline mode - import here to avoid circular dependency
        from src.cli import ttv_run as ttv_run_full
        ttv_run_full(script_path, out_path, fps=fps)
    else:
        # Assembly-only mode (backward compatibility)
        if not frames_dir or not audio_file:
            raise ValueError("Either script_path (full mode) or frames_dir+audio_file (assembly mode) must be provided")
        if not os.path.isdir(frames_dir):
            raise ValueError("frames_dir does not exist: " + frames_dir)
        assembler.assemble(frames_dir, audio_file, out_path, fps=fps)
