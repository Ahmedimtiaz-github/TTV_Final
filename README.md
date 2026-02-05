# TTV (Text-to-Video) Pipeline

Automated, modular Text-to-Video (TTV) system that transforms text scripts into synchronized audio-visual videos using free/open-source tools.

## Features

- **Parser**: Converts raw script text into structured scene data
- **Visual Generation**: Creates frames using PIL-based fallback renderer (zero-cost, offline)
- **Audio Synthesis**: Text-to-speech using offline TTS (pyttsx3)
- **Video Assembly**: Combines frames and audio into MP4 videos using ffmpeg
- **Full Pipeline**: End-to-end automation from script to video

## Quick Start

### Prerequisites

- Python 3.10+
- ffmpeg (see [docs/setup.md](docs/setup.md) for installation)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd C:\Users\ec\Documents\TTV_Final  # Windows
   # or
   cd /path/to/TTV_Final  # Linux
   ```

2. **Create and activate virtual environment:**
   
   **Windows PowerShell:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   **Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Run Demo

```bash
python run_demo.py --demo --out demo_output.mp4
```

### Run Full Pipeline

```bash
python -m src.cli --script data/sample_scripts/demo.txt --out output.mp4
```

## Usage

### Command-Line Interface

**Full Pipeline:**
```bash
python -m src.cli --script <script.txt> --out <output.mp4> [--fps 24]
```

**Parser Only:**
```bash
python -m src.parser --in <script.txt> --out <scenes.json>
```

**Demo:**
```bash
python run_demo.py --demo --out demo_output.mp4
```

### Script Format

Scripts should follow this format:

```
Scene 1: Exterior - Day
Narration: A quiet street in the morning. Camera pans right.

Scene 2: Interior - Cafe
Narration: Two friends meet and talk about a project.
Alice: Hello, how are you?
Bob: I'm doing well, thanks!
```

See [docs/scene-schema.md](docs/scene-schema.md) for detailed format documentation.

## Project Structure

```
TTV_Final/
├── src/
│   ├── pipeline/
│   │   ├── parser.py       # Script parser
│   │   ├── visual_gen.py   # Frame generation
│   │   ├── audio_synth.py  # Text-to-speech
│   │   └── assembler.py    # Video assembly
│   ├── cli.py              # CLI entry point
│   └── api.py              # API module
├── tests/                  # Unit and integration tests
├── data/
│   └── sample_scripts/     # Example scripts
├── assets/
│   └── visual_templates/   # PIL templates
├── docs/                   # Documentation
├── docker/                 # Docker configuration
└── infra/                  # Infrastructure configs
```

## Testing

Run all tests:
```bash
pytest -q tests/
```

Run specific test file:
```bash
pytest tests/test_parser.py
```

## Documentation

- [Setup Guide](docs/setup.md) - Installation and setup instructions
- [Scene Schema](docs/scene-schema.md) - JSON schema documentation
- [Architecture](docs/architecture.md) - Pipeline architecture overview
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

## Docker

Build and run using Docker:

```bash
docker build -t ttv-pipeline -f docker/Dockerfile .
docker run --rm -v $(pwd)/output:/app/output ttv-pipeline
```

Or use docker-compose:
```bash
cd infra
docker-compose up
```

## Requirements

### Python Dependencies
- `pillow>=10.0.0` - Image processing
- `pyttsx3>=2.90` - Offline TTS
- `numpy>=1.24.0` - Audio processing

### System Dependencies
- `ffmpeg` - Video encoding (see [docs/setup.md](docs/setup.md))

## Limitations

- Visual generation uses simple PIL-based placeholders (not AI-generated images)
- Audio uses basic TTS voices (not high-quality neural voices)
- No advanced video effects or transitions
- Single-threaded processing (no parallelization)

## Future Improvements

- Integration with Stable Diffusion for visual generation
- High-quality neural TTS (Coqui TTS, etc.)
- Parallel scene processing
- Video effects and transitions
- Subtitle generation
- Batch processing support

## License

This project uses only free/open-source tools. No paid APIs or cloud services are required.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## Support

For setup issues, see [docs/setup.md](docs/setup.md). For architecture questions, see [docs/architecture.md](docs/architecture.md).
