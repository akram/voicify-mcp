"""
Mock Voicify TTS Implementation
This provides a mock TextToSpeech class for development and testing.
"""

import os
import wave
import struct
import io
from .tts import TextToSpeech

__all__ = ['TextToSpeech']
