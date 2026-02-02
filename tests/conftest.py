import sys
import pathlib
import os

# Ensure project root (containing `src`) is on sys.path so `import src` works
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

