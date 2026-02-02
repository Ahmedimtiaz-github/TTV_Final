# Scene Schema Documentation

This document describes the JSON schema for scene objects used in the TTV pipeline.

## Overview

The parser converts raw script text into a structured JSON format containing an array of scene objects. Each scene represents a distinct segment of the video with its own visual and audio content.

## Schema Structure

The output JSON has the following top-level structure:

```json
{
  "scenes": [
    {
      "scene_id": "scene_01",
      "start_cue": null,
      "description": "Scene description text",
      "characters": ["Alice", "Bob"],
      "dialogue": [
        {
          "speaker": "Alice",
          "text": "Hello, how are you?"
        }
      ],
      "visual_prompts": ["A quiet street in the morning"],
      "duration_hint": 5.0
    }
  ]
}
```

## Field Descriptions

### `scene_id` (required, string)
- **Type**: String
- **Format**: Typically `scene_NN` where NN is a zero-padded 2-digit number (e.g., `scene_01`, `scene_02`)
- **Description**: Unique identifier for the scene. Used for organizing output frames and assets.
- **Example**: `"scene_01"`

### `start_cue` (optional, string or null)
- **Type**: String or null
- **Description**: Optional time hint or cue marker indicating when this scene should start. Can be a timestamp (e.g., "00:01:30") or a descriptive cue.
- **Example**: `"00:01:30"` or `"After fade in"`

### `description` (required, string)
- **Type**: String
- **Description**: Textual description of the scene. Typically extracted from narration or scene markers. Used as fallback for visual prompts if none are explicitly provided.
- **Example**: `"A quiet street in the morning. Camera pans right."`

### `characters` (required, array of strings)
- **Type**: Array of strings
- **Description**: List of character names that appear in this scene. Extracted from dialogue speakers.
- **Example**: `["Alice", "Bob"]`
- **Note**: Empty array `[]` if no characters/dialogue in scene

### `dialogue` (required, array of objects)
- **Type**: Array of dialogue objects
- **Description**: Ordered list of dialogue lines in the scene. Each dialogue object has:
  - `speaker` (string): Name of the character speaking
  - `text` (string): The dialogue text
- **Example**: 
  ```json
  [
    {
      "speaker": "Alice",
      "text": "Hello, how are you?"
    },
    {
      "speaker": "Bob",
      "text": "I'm doing well, thanks!"
    }
  ]
  ```
- **Note**: Empty array `[]` if no dialogue in scene

### `visual_prompts` (required, array of strings)
- **Type**: Array of strings
- **Description**: Explicit prompts for the visual generator. These are used to generate frames for the scene. If not explicitly provided in the script, defaults to the scene description.
- **Example**: `["A quiet street in the morning", "Camera pans right"]`
- **Note**: Must contain at least one prompt

### `duration_hint` (optional, float or null)
- **Type**: Float (seconds) or null
- **Description**: Suggested duration for this scene in seconds. Used to calculate the number of frames to generate (duration × fps).
- **Example**: `5.5` (for 5.5 seconds)
- **Default**: If not specified, a default duration (typically 2.0 seconds) is used

## Example scenes.json

```json
{
  "scenes": [
    {
      "scene_id": "scene_01",
      "description": "A quiet street in the morning. Camera pans right.",
      "characters": [],
      "dialogue": [],
      "visual_prompts": [
        "A quiet street in the morning"
      ]
    },
    {
      "scene_id": "scene_02",
      "description": "Two friends meet and talk about a project.",
      "characters": ["Alice", "Bob"],
      "dialogue": [
        {
          "speaker": "Alice",
          "text": "Hello, how are you?"
        },
        {
          "speaker": "Bob",
          "text": "I'm doing well, thanks!"
        }
      ],
      "visual_prompts": [
        "Two friends meet and talk about a project."
      ],
      "duration_hint": 10.0
    }
  ]
}
```

## Parser Behavior

The parser recognizes the following patterns in script text:

1. **Scene markers**: `Scene N:` or `Scene N -` where N is a number
2. **Narration**: Lines starting with `Narration:`
3. **Dialogue**: Lines in format `Character: text`
4. **Visual prompts**: Lines starting with `Visual:` or `Visual -`
5. **Duration hints**: Lines starting with `Duration:` followed by a number and optional "seconds"/"sec"/"s"
6. **Scene separation**: Blank lines separate scenes

## Usage

Generate a scenes.json file from a script:

```bash
python -m src.parser --in data/sample_scripts/demo.txt --out data/sample_scripts/demo.json
```

The generated JSON can then be used by:
- `visual_gen.py` to generate frames
- `audio_synth.py` to extract dialogue/narration for TTS
- The full pipeline orchestrator to create the final video
