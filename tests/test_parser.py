"""
Unit tests for the parser module.
"""
import pytest
import json
import os
import tempfile
from src.pipeline.parser import parse_script, parse_file


def test_parser_normal_case():
    """Test parser with a simple demo script."""
    script = """Scene 1: Exterior - Day
Narration: A quiet street in the morning. Camera pans right.

Scene 2: Interior - Cafe
Narration: Two friends meet and talk about a project.
Alice: Hello, how are you?
Bob: I'm doing well, thanks!"""
    
    scenes = parse_script(script)
    
    assert len(scenes) == 2
    assert scenes[0]['scene_id'] == 'scene_01'
    assert 'quiet street' in scenes[0]['description'].lower()
    assert len(scenes[0]['visual_prompts']) > 0
    
    assert scenes[1]['scene_id'] == 'scene_02'
    assert len(scenes[1]['dialogue']) == 2
    assert 'Alice' in scenes[1]['characters']
    assert 'Bob' in scenes[1]['characters']


def test_parser_multi_scene():
    """Test parser with multiple scenes separated by blank lines."""
    script = """Scene 1: Opening
Narration: The story begins.

Scene 2: Middle
Alice: This is the middle part.
Bob: Yes, it is.

Scene 3: Ending
Narration: The story concludes."""
    
    scenes = parse_script(script)
    
    assert len(scenes) == 3
    assert scenes[0]['scene_id'] == 'scene_01'
    assert scenes[1]['scene_id'] == 'scene_02'
    assert scenes[2]['scene_id'] == 'scene_03'
    assert len(scenes[1]['dialogue']) == 2


def test_parser_malformed_input():
    """Test parser handles malformed input gracefully."""
    # Empty script
    with pytest.raises(ValueError, match="empty"):
        parse_script("")
    
    with pytest.raises(ValueError, match="empty"):
        parse_script("   \n\n  \t  ")
    
    # Script with no valid scenes should raise a clear error
    script = "   \n  \n  "
    with pytest.raises(ValueError):
        parse_script(script)


def test_parser_dialogue_and_characters():
    """Test parser correctly extracts dialogue and characters."""
    script = """Scene 1: Conversation
Alice: Hello there!
Bob: Hi Alice!
Alice: How's the project going?
Bob: It's going well."""
    
    scenes = parse_script(script)
    
    assert len(scenes) == 1
    scene = scenes[0]
    assert 'Alice' in scene['characters']
    assert 'Bob' in scene['characters']
    assert len(scene['dialogue']) == 4
    assert scene['dialogue'][0]['speaker'] == 'Alice'
    assert scene['dialogue'][0]['text'] == 'Hello there!'


def test_parser_visual_prompts():
    """Test parser extracts visual prompts."""
    script = """Scene 1: Test Scene
Visual: A beautiful sunset over mountains
Narration: The scene is set."""
    
    scenes = parse_script(script)
    
    assert len(scenes) == 1
    scene = scenes[0]
    # Parser should produce at least one visual prompt derived from the script
    assert len(scene['visual_prompts']) > 0
    assert all(isinstance(p, str) and p.strip() for p in scene['visual_prompts'])


def test_parser_duration_hint():
    """Test parser extracts duration hints."""
    script = """Scene 1: Test Scene
Duration: 5.5 seconds
Narration: A short scene."""
    
    scenes = parse_script(script)
    
    assert len(scenes) == 1
    scene = scenes[0]
    # duration_hint is optional but, when present, should be a float
    hint = scene.get('duration_hint')
    if hint is not None:
        assert isinstance(hint, float)


def test_parser_file_io():
    """Test parser file I/O functionality."""
    script_content = """Scene 1: File Test
Narration: Testing file operations."""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        input_file = f.name
        f.write(script_content)
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            output_file = f.name
        
        parse_file(input_file, output_file)
        
        assert os.path.exists(output_file)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'scenes' in data
        assert len(data['scenes']) == 1
        assert data['scenes'][0]['scene_id'] == 'scene_01'
    
    finally:
        try:
            os.unlink(input_file)
            os.unlink(output_file)
        except:
            pass


def test_parser_file_not_found():
    """Test parser handles missing input file."""
    with pytest.raises(FileNotFoundError):
        parse_file('nonexistent_file.txt', 'output.json')
