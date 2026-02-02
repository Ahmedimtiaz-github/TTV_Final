# TTV Pipeline Architecture

## Overview

The Text-to-Video (TTV) pipeline is a modular system that converts text scripts into synchronized audio-visual videos. The pipeline consists of four main stages: parsing, visual generation, audio synthesis, and assembly.

## Architecture Diagram

```
┌─────────────┐
│ Script Text │
│  (demo.txt) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │  (parser.py)
│             │
│ Converts to │
│ scenes.json │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Visual Gen  │   │ Audio Synth │
│(visual_gen) │   │(audio_synth)│
│             │   │             │
│ Generates   │   │ Generates   │
│ PNG frames  │   │ WAV audio   │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
                ▼
         ┌─────────────┐
         │  Assembler  │
         │(assembler)  │
         │             │
         │ Muxes frames│
         │ + audio →   │
         │   MP4 video │
         └─────────────┘
```

## Component Details

### 1. Parser (`src/pipeline/parser.py`)

**Input**: Raw script text file (`.txt`)
**Output**: Structured JSON file (`scenes.json`)

**Responsibilities**:
- Parse script text into structured scene objects
- Extract scene markers, narration, dialogue, visual prompts, and duration hints
- Handle multi-scene scripts separated by blank lines
- Validate input and provide clear error messages

**Key Functions**:
- `parse_script(script_text)`: Core parsing logic
- `parse_file(input_path, output_path)`: File I/O wrapper
- `main()`: CLI entry point

**Output Schema**: See [scene-schema.md](scene-schema.md)

### 2. Visual Generation (`src/pipeline/visual_gen.py`)

**Input**: `scenes.json` file
**Output**: Directory structure with PNG frames per scene

**Responsibilities**:
- Generate image frames for each scene
- Use PIL-based fallback renderer (no external models required)
- Implement caching to reuse identical visual prompts
- Organize frames in scene-specific folders (`scene_01/`, `scene_02/`, etc.)

**Key Functions**:
- `generate_frames(scenes_json, out_dir, fps_hint)`: Main entry point
- `_render_fallback_frame(prompt, scene_info)`: PIL-based rendering
- `_get_cache_key(prompt)`: Generate cache keys for prompts

**Output Structure**:
```
frames/
  scene_01/
    frame_000001.png
    frame_000002.png
    ...
  scene_02/
    frame_000001.png
    ...
  .cache/
    <hash>.png  (cached frames)
```

### 3. Audio Synthesis (`src/pipeline/audio_synth.py`)

**Input**: Text (dialogue + narration from scenes)
**Output**: WAV audio file

**Responsibilities**:
- Synthesize speech from text using offline TTS (pyttsx3)
- Provide fallback to gTTS if pyttsx3 fails (requires internet)
- Normalize audio (RMS normalization, silence trimming)
- Support voice and rate parameters

**Key Functions**:
- `synthesize(text, out_path, voice, rate)`: Main entry point
- `_synthesize_pyttsx3(...)`: Offline TTS implementation
- `_synthesize_gtts(...)`: Internet-based fallback
- `_normalize_audio(wav_path)`: Audio post-processing
- `get_audio_duration(audio_path)`: Utility function

**Dependencies**:
- Primary: `pyttsx3` (offline, free)
- Fallback: `gTTS` (requires internet)

### 4. Assembler (`src/pipeline/assembler.py`)

**Input**: 
- Directory of image frames
- Audio file (WAV/MP3)

**Output**: MP4 video file

**Responsibilities**:
- Combine image frames into video stream
- Mux audio with video
- Handle frame ordering and timing
- Use ffmpeg for encoding

**Key Functions**:
- `assemble(frames_dir, audio_file, out_path, fps)`: Main entry point
- `_check_ffmpeg()`: Verify ffmpeg availability

**Dependencies**:
- `ffmpeg` (system binary)
- `Pillow` (for image processing)

## Orchestration

### CLI Entry Point (`src/cli.py`)

The `ttv_run()` function orchestrates the full pipeline:

1. **Parse**: Convert script → scenes.json
2. **Visual**: Generate frames from scenes.json
3. **Audio**: Synthesize audio from dialogue/narration
4. **Assemble**: Combine frames + audio → MP4

**Usage**:
```bash
python -m src.cli --script <script.txt> --out <output.mp4>
```

### Demo Runner (`run_demo.py`)

Simple wrapper for quick demos:
```bash
python run_demo.py --demo --out demo_output.mp4
```

### API Module (`src/api.py`)

Provides backward-compatible API:
- `ttv_run()`: Can run full pipeline or assembly-only mode

## Data Flow

1. **Script → Scenes**: Parser extracts structured data
2. **Scenes → Frames**: Visual generator creates images per scene
3. **Scenes → Audio**: Audio synthesizer extracts text and generates speech
4. **Frames + Audio → Video**: Assembler combines into final MP4

## Design Principles

### 1. Offline/Free First
- All components work offline by default
- No paid APIs or cloud services
- Fallback implementations for zero-cost operation

### 2. Modularity
- Each component is independent and testable
- Clear interfaces between stages
- Easy to swap implementations (e.g., replace visual_gen with model-based renderer)

### 3. Deterministic
- Caching for reproducible outputs
- Seed-based randomness (where applicable)
- Consistent file naming

### 4. Error Handling
- Graceful degradation (fallbacks)
- Clear error messages
- Validation at each stage

## Extension Points

### Visual Generation
Replace `_render_fallback_frame()` with:
- Stable Diffusion integration
- DALL-E API calls
- Custom image generation models

### Audio Synthesis
Replace `_synthesize_pyttsx3()` with:
- Coqui TTS
- Azure Cognitive Services
- Custom TTS models

### Parser
Extend `parse_script()` to support:
- More script formats (Fountain, Final Draft)
- Timecode parsing
- Metadata extraction

## Testing Strategy

- **Unit Tests**: Each component tested independently
- **Integration Tests**: Full pipeline end-to-end
- **CI/CD**: Automated testing on PRs with artifact generation

## Performance Considerations

- **Caching**: Visual prompts cached to avoid re-rendering
- **Parallelization**: Future enhancement for parallel scene processing
- **Streaming**: Future enhancement for large scripts

## Dependencies

### Core
- Python 3.10+
- Pillow (image processing)
- pyttsx3 (offline TTS)
- numpy (audio processing)

### System
- ffmpeg (video encoding)

### Optional
- gTTS (TTS fallback, requires internet)
- pytest (testing)
