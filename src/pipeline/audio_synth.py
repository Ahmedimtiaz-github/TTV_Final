"""
Audio synthesis module: Text-to-Speech using offline/free TTS libraries.
"""
import os
import sys
import time
import wave
import struct
import subprocess
from typing import Optional


def synthesize(text: str, out_path: str, voice: Optional[str] = None, rate: Optional[int] = None) -> str:
    """
    Synthesize speech from text using offline TTS.
    
    Args:
        text: Text to synthesize
        out_path: Output path for audio file (WAV or MP3)
        voice: Optional voice name (implementation-dependent)
        rate: Optional speech rate (words per minute)
        
    Returns:
        Path to generated audio file
        
    Raises:
        RuntimeError: If TTS synthesis fails
    """
    if not text or not text.strip():
        raise ValueError("Text input is empty")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else '.', exist_ok=True)
    
    # Try pyttsx3 first (pure offline)
    try:
        return _synthesize_pyttsx3(text, out_path, voice, rate)
    except Exception as e:
        # Fallback to gTTS if pyttsx3 fails (requires internet, but documented)
        print(f"Warning: pyttsx3 failed ({e}), trying gTTS fallback...", file=sys.stderr)
        try:
            return _synthesize_gtts(text, out_path)
        except Exception as e2:
            raise RuntimeError(f"Both pyttsx3 and gTTS failed. pyttsx3: {e}, gTTS: {e2}")


def _synthesize_pyttsx3(text: str, out_path: str, voice: Optional[str] = None, rate: Optional[int] = None) -> str:
    """Synthesize using pyttsx3 (offline, requires no internet)."""
    import pyttsx3
    
    engine = pyttsx3.init()
    
    # Set voice if specified
    if voice:
        voices = engine.getProperty('voices')
        for v in voices:
            if voice.lower() in v.name.lower():
                engine.setProperty('voice', v.id)
                break
    
    # Set rate if specified
    if rate:
        engine.setProperty('rate', rate)
    else:
        # Default to reasonable rate
        engine.setProperty('rate', 150)
    
    # Set volume
    engine.setProperty('volume', 0.9)
    
    # Save to file
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    
    # Wait a bit for file to be written
    time.sleep(0.5)
    
    if not os.path.exists(out_path):
        raise RuntimeError(f"pyttsx3 did not create output file: {out_path}")
    
    # Normalize audio (simple RMS normalization)
    _normalize_audio(out_path)
    
    return out_path


def _synthesize_gtts(text: str, out_path: str) -> str:
    """
    Fallback synthesis using gTTS (requires internet).
    This is a last resort fallback.
    """
    try:
        from gtts import gTTS
        import tempfile
        
        # gTTS outputs MP3, convert to WAV if needed
        if out_path.endswith('.wav'):
            mp3_path = out_path.replace('.wav', '.mp3')
        else:
            mp3_path = out_path
        
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(mp3_path)
        
        # Convert MP3 to WAV if needed
        if out_path.endswith('.wav') and mp3_path != out_path:
            _convert_mp3_to_wav(mp3_path, out_path)
            os.unlink(mp3_path)
        
        return out_path
    except ImportError:
        raise RuntimeError("gTTS not installed. Install with: pip install gtts")


def _normalize_audio(wav_path: str) -> None:
    """
    Simple audio normalization using the standard ``audioop`` module.

    - Computes RMS using ``audioop.rms``
    - Scales samples with ``audioop.mul``
    - Does *not* change the number of frames, so unpack/size errors are avoided

    If anything goes wrong, the original file is left untouched.
    """
    try:
        import wave
        try:
            import audioop
        except ImportError:
            # audioop was removed in Python 3.13+, use numpy fallback
            audioop = None

        # Read WAV file
        with wave.open(wav_path, "rb") as wav_in:
            params = wav_in.getparams()
            n_channels = wav_in.getnchannels()
            sampwidth = wav_in.getsampwidth()
            framerate = wav_in.getframerate()
            frames = wav_in.readframes(wav_in.getnframes())

        if not frames:
            return

        # If audioop is not available (Python 3.13+), use numpy fallback
        if audioop is None:
            import numpy as np
            # Convert bytes to numpy array
            if sampwidth == 2:
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            elif sampwidth == 1:
                audio_data = np.frombuffer(frames, dtype=np.uint8).astype(np.float32)
                audio_data = (audio_data - 128) / 128.0
            else:
                # Unsupported sample width, skip normalization
                return
            
            # Handle stereo to mono
            if n_channels == 2:
                audio_data = audio_data.reshape(-1, 2).mean(axis=1)
            
            # Normalize RMS
            current_rms = np.sqrt(np.mean(audio_data ** 2))
            if current_rms == 0:
                return
            
            target_rms = 0.3  # Normalized target
            factor = target_rms / current_rms
            audio_data = np.clip(audio_data * factor, -1.0, 1.0)
            
            # Convert back to int16
            normalized_frames = (audio_data * 32767).astype(np.int16).tobytes()
            
            # Write back
            with wave.open(wav_path, "wb") as wav_out:
                wav_out.setnchannels(1)  # Always mono after normalization
                wav_out.setsampwidth(2)
                wav_out.setframerate(framerate)
                wav_out.writeframes(normalized_frames)
            return

        # Use audioop if available (Python < 3.13)
        # If stereo, convert to mono for RMS/normalization but keep channel count the same
        mono_frames = (
            audioop.tomono(frames, sampwidth, 0.5, 0.5) if n_channels == 2 else frames
        )

        # Current RMS and target RMS (arbitrary but reasonable level)
        current_rms = audioop.rms(mono_frames, sampwidth)
        if current_rms == 0:
            # Silence – nothing to normalize
            return

        target_rms = 3000  # for 16‑bit audio this is a safe, not-too-loud level
        factor = float(target_rms) / float(current_rms)

        # Apply gain
        normalized_mono = audioop.mul(mono_frames, sampwidth, factor)

        # If original was stereo, duplicate mono back to stereo
        if n_channels == 2:
            normalized_frames = audioop.tostereo(normalized_mono, sampwidth, 1.0, 1.0)
        else:
            normalized_frames = normalized_mono

        # Write back normalized audio with original params
        with wave.open(wav_path, "wb") as wav_out:
            wav_out.setnchannels(n_channels)
            wav_out.setsampwidth(sampwidth)
            wav_out.setframerate(framerate)
            wav_out.writeframes(normalized_frames)

    except Exception as e:
        # If normalization fails, just continue with original file
        print(f"Warning: Audio normalization failed: {e}", file=sys.stderr)


def _convert_mp3_to_wav(mp3_path: str, wav_path: str) -> None:
    """Convert MP3 to WAV using ffmpeg."""
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', mp3_path, '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("ffmpeg not found. Cannot convert MP3 to WAV.")


def get_audio_duration(audio_path: str) -> float:
    """
    Get duration of audio file in seconds.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    try:
        import wave
        with wave.open(audio_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            return frames / float(sample_rate)
    except:
        # Try using ffprobe as fallback
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip())
        except:
            return 0.0
