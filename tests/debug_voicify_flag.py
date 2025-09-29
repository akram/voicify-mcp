#!/usr/bin/env python3
"""Debug VOICIFY_AVAILABLE flag in subprocess."""

import subprocess
import os

def test_voicify_flag_in_subprocess():
    """Check what VOICIFY_AVAILABLE is in subprocess."""
    project_dir = os.getcwd()
    
    server_cmd = ['python', '-c', f'''
import sys
import os
sys.path.insert(0, '{project_dir}')
os.chdir('{project_dir}')

# Import voicify_server and check flags
from voicify_server import VOICIFY_AVAILABLE
print(f"VOICIFY_AVAILABLE in subprocess: {{VOICIFY_AVAILABLE}}")

try:
    from voicify_server import VoicifyTTS
    print("VoicifyTTS imported successfully")
except Exception as e:
    print(f"VoicifyTTS import failed: {{e}}")

# Test if we can call text_to_speech
from voicify_server import text_to_speech
try:
    result = text_to_speech("Debug test")
    print(f"text_to_speech called successfully, result type: {{type(result)}}")
except Exception as e:
    print(f"text_to_speech failed: {{e}}")
    import traceback
    traceback.print_exc()
''']
    
    result = subprocess.run(server_cmd, capture_output=True, text=True)
    print("=== SUBPROCESS OUTPUT ===")
    print(result.stdout)
    if result.stderr:
        print("=== SUBPROCESS ERRORS ===")
        print(result.stderr)
    print(f"Return code: {result.returncode}")

if __name__ == "__main__":
    test_voicify_flag_in_subprocess()
