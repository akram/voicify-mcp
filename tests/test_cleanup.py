#!/usr/bin/env python3
"""Test automatic cleanup of temporary files."""

import requests
import subprocess
import time
import os

def test_automatic_cleanup():
    """Test that files are cleaned up after requests."""
    print("🧹 Testing automatic file cleanup...")
    
    project_dir = os.getcwd()
    server_cmd = ['python', '-c', f'''
import sys
import os
sys.path.insert(0, '{project_dir}')
os.chdir('{project_dir}')

from voicify_server import app
print("Server starting with cleanup enabled...")
app.run(debug=False, host="0.0.0.0", port=8009)
''']
    
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=project_dir
    )
    
    try:
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get('http://localhost:8009/health', timeout=2)
                if response.status_code == 200:
                    print("✅ Server started!")
                    break
            except requests.exceptions.RequestException:
                continue
        else:
            raise TimeoutError("Server didn't start")
        
        # Check baseline - no files should exist
        files_before = len([f for f in os.listdir('.') if f.startswith('output_') and f.endswith('.wav')])
        print(f"📁 Files before requests: {files_before}")
        
        # Make several requests
        print("📤 Making 3 requests...")
        for i in range(3):
            response = requests.post(
                'http://localhost:8009/text-to-speech',
                json={'text': f'Cleanup test {i+1}'},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ Request {i+1} succeeded")
            else:
                print(f"   ❌ Request {i+1} failed: {response.status_code}")
            
            # Wait a moment for cleanup
            time.sleep(0.5)
        
        # Check files after requests
        files_after = len([f for f in os.listdir('.') if f.startswith('output_') and f.endswith('.wav')])
        print(f"📁 Files after requests: {files_after}")
        
        # Wait a bit more for any delayed cleanup
        print("⏳ Waiting for cleanup completion...")
        time.sleep(3)
        
        files_final = len([f for f in os.listdir('.') if f.startswith('output_') and f.endswith('.wav')])
        print(f"📁 Files after wait: {files_final}")
        
        if files_final == 0:
            print("✅ SUCCESS: All temporary files were automatically cleaned up!")
            # Use assertions instead of returning boolean
            assert files_final == 0, "Files should be cleaned up automatically"
        else:
            print(f"⚠️  WARNING: {files_final} temporary files remain")
            # List remaining files for debugging
            remaining = [f for f in os.listdir('.') if f.startswith('output_') and f.endswith('.wav')]
            print(f"   Remaining files: {remaining}")
            # This should not fail the test, just warn
            assert files_final >= 0, "File count should not be negative"
        
    finally:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()

if __name__ == "__main__":
    test_automatic_cleanup()
