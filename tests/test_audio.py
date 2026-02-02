"""
Unit tests for the audio synthesis module.
"""
import pytest
import os
import tempfile
from src.pipeline.audio_synth import synthesize, get_audio_duration


def test_synthesize_creates_audio_file():
    """Test that synthesize creates a valid audio file."""
    text = "This is a test sentence for TTS."
    
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, 'test_audio.wav')
        
        result_path = synthesize(text, out_path)
        
        assert os.path.exists(result_path)
        assert result_path == out_path


def test_synthesize_audio_duration():
    """Test that synthesized audio has non-zero duration."""
    text = "This is a longer test sentence to ensure we get some audio output."
    
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, 'test_audio.wav')
        
        synthesize(text, out_path)
        
        assert os.path.exists(out_path)
        
        duration = get_audio_duration(out_path)
        assert duration > 0, f"Audio duration should be > 0, got {duration}"


def test_synthesize_empty_text():
    """Test that synthesize raises error for empty text."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, 'test.wav')
        
        with pytest.raises(ValueError, match="empty"):
            synthesize("", out_path)
        
        with pytest.raises(ValueError, match="empty"):
            synthesize("   ", out_path)


def test_synthesize_with_voice_parameter():
    """Test synthesize with voice parameter (may not work on all systems)."""
    text = "Testing voice parameter."
    
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, 'test_voice.wav')
        
        # Should not raise error even if voice not found
        try:
            synthesize(text, out_path, voice="test_voice")
            assert os.path.exists(out_path)
        except Exception as e:
            # Acceptable if voice not available
            assert "voice" in str(e).lower() or "not found" in str(e).lower()


def test_synthesize_with_rate_parameter():
    """Test synthesize with rate parameter."""
    text = "Testing rate parameter."
    
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, 'test_rate.wav')
        
        synthesize(text, out_path, rate=120)
        
        assert os.path.exists(out_path)
        duration = get_audio_duration(out_path)
        assert duration > 0


def test_get_audio_duration():
    """Test get_audio_duration function."""
    text = "This is a test."
    
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, 'test_duration.wav')
        
        synthesize(text, out_path)
        
        duration = get_audio_duration(out_path)
        assert isinstance(duration, float)
        assert duration >= 0
