"""
Visual generation module: generates frames from scenes.json using PIL fallback renderer.
"""
import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont


def generate_frames(scenes_json: str, out_dir: str, fps_hint: int = 24) -> None:
    """
    Generate frames for all scenes in scenes.json.
    
    Args:
        scenes_json: Path to scenes.json file or loaded dict
        out_dir: Output directory where scene folders will be created
        fps_hint: Frames per second hint (used to calculate frame count from duration_hint)
    """
    # Load scenes if path provided
    if isinstance(scenes_json, str):
        with open(scenes_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = scenes_json
    
    scenes = data.get('scenes', [])
    if not scenes:
        raise ValueError("No scenes found in scenes_json")
    
    os.makedirs(out_dir, exist_ok=True)
    
    # Cache directory for reusable frames
    cache_dir = os.path.join(out_dir, '.cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    for scene in scenes:
        scene_id = scene.get('scene_id', 'scene_unknown')
        scene_dir = os.path.join(out_dir, scene_id)
        os.makedirs(scene_dir, exist_ok=True)
        
        # Calculate number of frames for this scene
        duration = scene.get('duration_hint', 2.0)  # Default 2 seconds
        num_frames = max(1, int(duration * fps_hint))
        
        # Get visual prompts
        visual_prompts = scene.get('visual_prompts', [])
        if not visual_prompts:
            # Fallback to description
            visual_prompts = [scene.get('description', 'Scene')]
        
        # Generate frames for this scene
        _generate_scene_frames(
            scene_dir=scene_dir,
            visual_prompts=visual_prompts,
            scene_info=scene,
            num_frames=num_frames,
            cache_dir=cache_dir
        )


def _generate_scene_frames(
    scene_dir: str,
    visual_prompts: List[str],
    scene_info: Dict[str, Any],
    num_frames: int,
    cache_dir: str
) -> None:
    """Generate frames for a single scene."""
    # Use first visual prompt as primary
    primary_prompt = visual_prompts[0] if visual_prompts else "Scene"
    
    # Check cache first
    cache_key = _get_cache_key(primary_prompt)
    cached_frame = os.path.join(cache_dir, f"{cache_key}.png")
    
    if os.path.exists(cached_frame):
        # Reuse cached frame – copy into memory so we can safely close the file
        with Image.open(cached_frame) as img:
            base_frame = img.copy()
    else:
        # Generate new frame using PIL fallback
        base_frame = _render_fallback_frame(primary_prompt, scene_info)
        # Save to cache
        base_frame.save(cached_frame, format='PNG')
    
    # Generate numbered frames (can add slight variations if needed)
    for i in range(1, num_frames + 1):
        frame_path = os.path.join(scene_dir, f"frame_{i:06d}.png")
        # For now, use same frame for all (can add subtle variations later)
        frame = base_frame.copy()
        frame.save(frame_path, format='PNG')
        # Explicitly close to avoid open file handles on Windows
        frame.close()


def _render_fallback_frame(prompt: str, scene_info: Dict[str, Any]) -> Image.Image:
    """
    Render a fallback frame using PIL.
    Creates a simple but readable placeholder frame.
    """
    # Standard video frame size
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(30, 30, 50))
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default if not available
    try:
        # Try to use a larger font if available
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
            font_medium = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
            font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
        except:
            # Use default font
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Draw background gradient effect (simple)
    for y in range(height):
        color_ratio = y / height
        r = int(30 + color_ratio * 20)
        g = int(30 + color_ratio * 20)
        b = int(50 + color_ratio * 30)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw title/header
    title = scene_info.get('scene_id', 'Scene').upper().replace('_', ' ')
    draw.text((width // 2, 50), title, fill=(255, 255, 255), font=font_large, anchor='mm')
    
    # Draw visual prompt text (wrapped)
    prompt_lines = _wrap_text(prompt, width - 200, font_medium)
    y_start = height // 2 - (len(prompt_lines) * 30) // 2
    
    for i, line in enumerate(prompt_lines):
        y_pos = y_start + i * 30
        draw.text((width // 2, y_pos), line, fill=(220, 220, 255), font=font_medium, anchor='mm')
    
    # Draw scene description if different from prompt
    description = scene_info.get('description', '')
    if description and description != prompt:
        desc_lines = _wrap_text(description, width - 200, font_small)
        y_desc = height - 100
        for i, line in enumerate(desc_lines[:3]):  # Max 3 lines
            draw.text((width // 2, y_desc + i * 22), line, fill=(180, 180, 200), font=font_small, anchor='mm')
    
    # Draw border
    border_color = (100, 100, 150)
    draw.rectangle([10, 10, width - 10, height - 10], outline=border_color, width=2)
    
    return img


def _wrap_text(text: str, max_width: int, font: ImageFont.FreeTypeFont) -> List[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        # Approximate text width (rough estimate)
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    if not lines:
        lines = [text[:50]]  # Fallback
    
    return lines


def _get_cache_key(prompt: str) -> str:
    """Generate a cache key (hash) for a visual prompt."""
    return hashlib.md5(prompt.encode('utf-8')).hexdigest()
