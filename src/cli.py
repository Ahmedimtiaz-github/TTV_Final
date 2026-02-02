"""
Command-line interface for the TTV pipeline.
"""
import os
import sys
import argparse
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.pipeline.parser import parse_file
from src.pipeline.visual_gen import generate_frames
from src.pipeline.audio_synth import synthesize, get_audio_duration
from src.pipeline.assembler import assemble


def ttv_run(script_path: str, out_path: str, fps: int = 24) -> None:
    """
    Run the complete TTV pipeline: parse → visual → audio → assemble.
    
    Args:
        script_path: Path to input script text file
        out_path: Path to output MP4 file
        fps: Frames per second for output video
    """
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory(prefix='ttv_run_') as tmpdir:
        scenes_json_path = os.path.join(tmpdir, 'scenes.json')
        frames_dir = os.path.join(tmpdir, 'frames')
        audio_file = os.path.join(tmpdir, 'audio.wav')
        
        # Step 1: Parse script
        print(f"Parsing script: {script_path}")
        parse_file(script_path, scenes_json_path)
        
        # Step 2: Generate frames
        print(f"Generating frames...")
        generate_frames(scenes_json_path, frames_dir, fps_hint=fps)
        
        # Step 3: Synthesize audio
        print(f"Synthesizing audio...")
        # Collect all dialogue and narration for audio
        with open(scenes_json_path, 'r', encoding='utf-8') as f:
            scenes_data = json.load(f)
        
        audio_text_parts = []
        for scene in scenes_data.get('scenes', []):
            # Add description/narration
            desc = scene.get('description', '')
            if desc:
                audio_text_parts.append(desc)
            
            # Add dialogue
            for dialogue_item in scene.get('dialogue', []):
                speaker = dialogue_item.get('speaker', '')
                text = dialogue_item.get('text', '')
                if speaker and text:
                    audio_text_parts.append(f"{speaker} says: {text}")
                elif text:
                    audio_text_parts.append(text)
        
        audio_text = '. '.join(audio_text_parts)
        if not audio_text.strip():
            audio_text = "Scene narration."
        
        synthesize(audio_text, audio_file)
        
        # Step 4: Assemble video
        print(f"Assembling video: {out_path}")
        assemble(frames_dir, audio_file, out_path, fps=fps)
        
        print(f"Complete! Output: {out_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Text-to-Video Pipeline')
    parser.add_argument('--script', required=True, help='Input script text file')
    parser.add_argument('--out', required=True, help='Output MP4 file path')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second (default: 24)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.script):
        print(f"Error: Script file not found: {args.script}", file=sys.stderr)
        sys.exit(1)
    
    try:
        ttv_run(args.script, args.out, fps=args.fps)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
