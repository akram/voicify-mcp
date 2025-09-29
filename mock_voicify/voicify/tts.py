"""
Mock TextToSpeech implementation
Generates realistic-sounding audio data for development/testing.
"""

import os
import wave
import struct
import io
import random


class TextToSpeech:
    """Mock TextToSpeech class that generates realistic audio data."""
    
    def __init__(self):
        print("🎤 Mock Voicify TTS initialized (development mode)")
    
    def write_voice(self, text):
        """
        Simulate Voicify TTS voice generation.
        Creates a mock WAV file with realistic format.
        """
        print(f"🔊 Mock TTS generating audio for: '{text}'")
        
        # Generate realistic audio data (not just sine wave)
        sample_rate = 22050  # Match expected sample rate for tests
        duration = max(len(text) * 0.08, 1.0)  # Realistic duration
        
        # Generate audio with multiple frequency components
        audio_data = self._generate_realistic_audio(text, sample_rate, duration)
        
        # Write to the expected output file
        with open('output.wav', 'wb') as f:
            f.write(audio_data)
        
        print(f"✅ Mock audio generated: output.wav ({len(audio_data)} bytes)")
    
    def _generate_realistic_audio(self, text, sample_rate, duration):
        """Generate more realistic audio than simple sine wave."""
        frames = []
        num_samples = int(sample_rate * duration)
        
        # Use text-based random seed for consistent output for same text
        random.seed(hash(text) % 2**31)
        
        for i in range(num_samples):
            # Mix multiple frequencies for more realistic sound
            t = i / sample_rate
            
            # Generate voice-like audio with harmonics
            voice = 0.0
            for harmonic in range(1, 6):
                amplitude = 0.5 / harmonic  # Decreasing amplitude for harmonics
                voice += amplitude * random.uniform(-1, 1)
            
            # Add speech-like pattern
            voice *= 0.7 + 0.3 * (i % 10 == 0)
            
            # Convert to proper format
            sample_value = min(max(int(voice * 32767), -32767), 32767)
            frames.append(struct.pack('<h', sample_value))
        
        # Create WAV file structure
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(frames))
        
        return wav_buffer.getvalue()
