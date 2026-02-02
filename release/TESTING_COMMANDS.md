# Testing Commands - Exact PowerShell Instructions

## Quick Test (All Tests + Demo)

Run these commands in PowerShell from `C:\Users\ec\Documents\TTV_Final`:

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run all tests (with basetemp to avoid Windows permission issues)
pytest -q tests/ --basetemp=.pytest_tmp

# 3. Run demo
python run_demo.py --demo --out release/demo_output.mp4

# 4. Verify output
Get-Item release\demo_output.mp4 | Format-List Name,Length,FullName
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 release\demo_output.mp4
```

## Expected Results

- **Tests**: `22 passed` (all tests should pass)
- **Demo Output**: `demo_output.mp4` should exist with size > 50KB
- **Duration**: Should be approximately 4 seconds

## Troubleshooting

### If you see permission errors with pytest:

Always use `--basetemp=.pytest_tmp` flag:
```powershell
pytest -q tests/ --basetemp=.pytest_tmp
```

### If audioop warning appears:

This is normal on Python 3.13+. The code automatically falls back to numpy-based normalization. The warning is harmless.

### If ffmpeg/ffprobe not found:

Install ffmpeg and ensure it's in your PATH. See `docs/setup.md` for installation instructions.
