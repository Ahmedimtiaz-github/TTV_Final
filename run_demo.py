"""
Demo runner: provides a simple demo command for the TTV pipeline.
"""
import os
import sys
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from src.cli import ttv_run

def demo(out_path: str):
    """
    Run a demo using the sample script.
    
    Args:
        out_path: Output MP4 file path
    """
    script_path = os.path.join(os.path.dirname(__file__), "data", "sample_scripts", "demo.txt")
    
    if not os.path.exists(script_path):
        print(f"Error: Demo script not found: {script_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Running demo with script: {script_path}")
    ttv_run(script_path, out_path, fps=24)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TTV Demo Runner')
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--out", default="demo_output.mp4", help="Output MP4 file")
    args = parser.parse_args()
    
    if args.demo:
        demo(args.out)
    else:
        print("Run with --demo to execute the demo")
        print("Or use: python -m src.cli --script <script.txt> --out <output.mp4>")
