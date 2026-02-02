"""
Parser module: converts raw script text into structured scenes.json format.
"""
import json
import re
import sys
import argparse
from typing import List, Dict, Optional, Any


def parse_script(script_text: str) -> List[Dict[str, Any]]:
    """
    Parse raw script text into a list of scene dictionaries.
    
    Args:
        script_text: Raw text content of the script
        
    Returns:
        List of scene dictionaries with schema:
        - scene_id: unique identifier (1-based index or slug)
        - start_cue: optional string/time hint
        - description: scene description
        - characters: list of character names
        - dialogue: ordered list of {speaker, text} dicts
        - visual_prompts: explicit prompt(s) for visual generator
        - duration_hint: optional seconds per scene
        
    Raises:
        ValueError: If script is malformed or empty
    """
    if not script_text or not script_text.strip():
        raise ValueError("Script text is empty or contains only whitespace")
    
    scenes = []
    lines = script_text.split('\n')
    current_scene = None
    scene_counter = 0
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (they separate scenes)
        if not line:
            if current_scene:
                # Finalize current scene before starting new one
                scenes.append(_finalize_scene(current_scene, scene_counter))
                current_scene = None
            i += 1
            continue
        
        # Check for scene marker: "Scene N:" or "Scene N -" pattern
        scene_match = re.match(r'^Scene\s+(\d+)[:\-]?\s*(.*)$', line, re.IGNORECASE)
        if scene_match:
            # Save previous scene if exists
            if current_scene:
                scenes.append(_finalize_scene(current_scene, scene_counter))
            
            scene_counter += 1
            scene_num = int(scene_match.group(1))
            scene_title = scene_match.group(2).strip()
            
            current_scene = {
                'scene_id': f"scene_{scene_num:02d}",
                'start_cue': None,
                'description': scene_title if scene_title else f"Scene {scene_num}",
                'characters': [],
                'dialogue': [],
                'visual_prompts': [],
                'duration_hint': None
            }
            i += 1
            continue
        
        # If no scene marker found yet, create first scene
        if current_scene is None:
            scene_counter += 1
            current_scene = {
                'scene_id': f"scene_{scene_counter:02d}",
                'start_cue': None,
                'description': "",
                'characters': [],
                'dialogue': [],
                'visual_prompts': [],
                'duration_hint': None
            }
        
        # Check for narration
        narration_match = re.match(r'^Narration:\s*(.+)$', line, re.IGNORECASE)
        if narration_match:
            narration_text = narration_match.group(1).strip()
            current_scene['description'] = narration_text
            # Use narration as visual prompt if no explicit prompt
            if not current_scene['visual_prompts']:
                current_scene['visual_prompts'].append(narration_text)
            i += 1
            continue
        
        # Check for dialogue: "Character: text" or "CHARACTER: text"
        dialogue_match = re.match(r'^([A-Z][A-Za-z\s]+?):\s*(.+)$', line)
        if dialogue_match:
            speaker = dialogue_match.group(1).strip()
            text = dialogue_match.group(2).strip()
            
            if speaker not in current_scene['characters']:
                current_scene['characters'].append(speaker)
            
            current_scene['dialogue'].append({
                'speaker': speaker,
                'text': text
            })
            i += 1
            continue
        
        # Check for visual prompt marker
        visual_match = re.match(r'^Visual[:\-]?\s*(.+)$', line, re.IGNORECASE)
        if visual_match:
            prompt = visual_match.group(1).strip()
            current_scene['visual_prompts'].append(prompt)
            i += 1
            continue
        
        # Check for duration hint
        duration_match = re.match(r'^Duration[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:seconds?|sec|s)?$', line, re.IGNORECASE)
        if duration_match:
            current_scene['duration_hint'] = float(duration_match.group(1))
            i += 1
            continue
        
        # If line doesn't match any pattern, treat as description or narration
        if not current_scene['description']:
            current_scene['description'] = line
            if not current_scene['visual_prompts']:
                current_scene['visual_prompts'].append(line)
        else:
            # Append to description
            current_scene['description'] += " " + line
        
        i += 1
    
    # Don't forget the last scene
    if current_scene:
        scenes.append(_finalize_scene(current_scene, scene_counter))
    
    if not scenes:
        raise ValueError("No scenes found in script. Script must contain at least one scene.")
    
    return scenes


def _finalize_scene(scene: Dict[str, Any], scene_num: int) -> Dict[str, Any]:
    """Finalize a scene dictionary, ensuring all required fields are present."""
    # Ensure scene_id is set
    if not scene.get('scene_id'):
        scene['scene_id'] = f"scene_{scene_num:02d}"
    
    # Ensure description exists
    if not scene.get('description'):
        scene['description'] = f"Scene {scene_num}"
    
    # Ensure visual_prompts exists and has at least one entry
    if not scene.get('visual_prompts'):
        scene['visual_prompts'] = [scene['description']]
    
    # Remove None values for optional fields
    if scene.get('start_cue') is None:
        scene.pop('start_cue', None)
    if scene.get('duration_hint') is None:
        scene.pop('duration_hint', None)
    
    return scene


def parse_file(input_path: str, output_path: str) -> None:
    """
    Parse a script file and write the result to a JSON file.
    
    Args:
        input_path: Path to input script text file
        output_path: Path to output JSON file
    """
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            script_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        raise IOError(f"Error reading input file {input_path}: {e}")
    
    try:
        scenes = parse_script(script_text)
        scenes_json = {'scenes': scenes}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scenes_json, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Error writing output file {output_path}: {e}")


def main():
    """CLI entry point for the parser."""
    parser = argparse.ArgumentParser(description='Parse script text into scenes.json')
    parser.add_argument('--in', dest='input_file', required=True,
                       help='Input script text file')
    parser.add_argument('--out', dest='output_file', required=True,
                       help='Output JSON file')
    
    args = parser.parse_args()
    
    try:
        parse_file(args.input_file, args.output_file)
        print(f"Successfully parsed {args.input_file} -> {args.output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
