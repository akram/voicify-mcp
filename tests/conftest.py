"""
Configuration and fixtures for pytest testing.
"""

import pytest
import tempfile
import os


@pytest.fixture(autouse=True)
def cleanup_output_files():
    """Clean up output.wav files created during testing."""
    yield
    
    # Clean up any test-generated files
    output_files = ['output.wav']
    for file_path in output_files:
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except (OSError, IOError):
                pass  # Ignore cleanup errors in tests


@pytest.fixture
def mock_audio_data():
    """Provide mock audio data for testing."""
    import io
    import wave
    
    # Create a minimal WAV file
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(22050)
        wav_file.writeframes(b'\x00\x00' * 1000)  # 1000 samples
    
    return wav_buffer.getvalue()


@pytest.fixture
def sample_texts():
    """Provide various sample texts for testing."""
    return {
        'short': "Hi",
        'medium': "Hello, world! This is a test.",
        'long': "This is a much longer text that will test the duration calculation " * 5,
        'empty': "",
        'whitespace': "   \n\t   ",
        'special_chars': "Hello, world! 123 @#$%^&*()",
        'unicode': "Hello, world! 🌍 سلام مرحبا"
    }
