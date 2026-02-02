"""
Unit tests for the visual generation module.
"""
import pytest
import os
import json
import tempfile
from PIL import Image
from src.pipeline.visual_gen import generate_frames


def test_generate_frames_creates_scene_folders():
    """Test that generate_frames creates scene folders."""
    scenes_data = {
        'scenes': [
            {
                'scene_id': 'scene_01',
                'description': 'Test scene 1',
                'visual_prompts': ['A test scene'],
                'duration_hint': 2.0
            },
            {
                'scene_id': 'scene_02',
                'description': 'Test scene 2',
                'visual_prompts': ['Another test scene'],
                'duration_hint': 1.5
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_frames(scenes_data, tmpdir, fps_hint=24)
        
        # Check scene folders exist
        scene1_dir = os.path.join(tmpdir, 'scene_01')
        scene2_dir = os.path.join(tmpdir, 'scene_02')
        
        assert os.path.isdir(scene1_dir)
        assert os.path.isdir(scene2_dir)


def test_generate_frames_creates_valid_images():
    """Test that generated frames are valid PNG images."""
    scenes_data = {
        'scenes': [
            {
                'scene_id': 'scene_01',
                'description': 'Test scene',
                'visual_prompts': ['A beautiful landscape'],
                'duration_hint': 1.0
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_frames(scenes_data, tmpdir, fps_hint=24)
        
        scene_dir = os.path.join(tmpdir, 'scene_01')
        frame_path = os.path.join(scene_dir, 'frame_000001.png')
        
        assert os.path.exists(frame_path)
        
        # Verify it's a valid image and ensure the file handle is closed
        with Image.open(frame_path) as img:
            assert img.format == 'PNG'
            assert img.size[0] > 0 and img.size[1] > 0


def test_generate_frames_correct_number():
    """Test that correct number of frames are generated based on duration."""
    scenes_data = {
        'scenes': [
            {
                'scene_id': 'scene_01',
                'description': 'Test scene',
                'visual_prompts': ['Test prompt'],
                'duration_hint': 2.0  # 2 seconds at 24 fps = 48 frames
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_frames(scenes_data, tmpdir, fps_hint=24)
        
        scene_dir = os.path.join(tmpdir, 'scene_01')
        frames = [f for f in os.listdir(scene_dir) if f.startswith('frame_') and f.endswith('.png')]
        
        # Should have approximately 48 frames (2 seconds * 24 fps)
        assert len(frames) == 48


def test_generate_frames_from_json_file():
    """Test generate_frames with JSON file path."""
    scenes_data = {
        'scenes': [
            {
                'scene_id': 'scene_01',
                'description': 'File test',
                'visual_prompts': ['Test from file'],
                'duration_hint': 1.0
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, 'test_scenes.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(scenes_data, f)
        
        out_dir = os.path.join(tmpdir, 'frames')
        generate_frames(json_path, out_dir, fps_hint=24)
        
        scene_dir = os.path.join(out_dir, 'scene_01')
        assert os.path.isdir(scene_dir)
        assert len([f for f in os.listdir(scene_dir) if f.endswith('.png')]) > 0


def test_generate_frames_caching():
    """Test that caching works for identical prompts."""
    scenes_data = {
        'scenes': [
            {
                'scene_id': 'scene_01',
                'description': 'Test',
                'visual_prompts': ['Same prompt'],
                'duration_hint': 1.0
            },
            {
                'scene_id': 'scene_02',
                'description': 'Test 2',
                'visual_prompts': ['Same prompt'],  # Same prompt should be cached
                'duration_hint': 1.0
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_frames(scenes_data, tmpdir, fps_hint=24)
        
        # Check cache directory exists
        cache_dir = os.path.join(tmpdir, '.cache')
        assert os.path.isdir(cache_dir)
        
        # Check that cache files exist
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.png')]
        assert len(cache_files) > 0
