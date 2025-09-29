"""
Simple integration test to verify the server works end-to-end.
"""

import subprocess
import time
import requests
import pytest
import os
import socket
import random


def find_free_port():
    """Find an available port for testing."""
    while True:
        port = random.randint(8003, 9000)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            sock.close()
            continue


def test_server_basic_functionality():
    """Test basic server functionality by starting/stopping manually."""
    import signal
    
    # Start server using the simple script modification
    server_cmd = ['python', '-c', '''
import sys
import os
sys.path.insert(0, os.getcwd())

from voicify_server import app
app.run(debug=False, host="0.0.0.0", port=8002)
''']
    
    # Start server process
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    try:
        # Wait for server to start
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get('http://localhost:8002/health', timeout=2)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                continue
        else:
            raise TimeoutError("Server didn't start within 15 seconds")
            
        # Test health endpoint
        response = requests.get('http://localhost:8002/health', timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'voicify_available' in data
        assert 'service' in data
        assert data['service'] == 'voicify-tts'
        
        # Test TTS endpoint
        response = requests.post(
            'http://localhost:8002/text-to-speech',
            json={'text': 'Hello from integration test!'},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        assert response.status_code == 200
        assert 'audio/wav' in response.headers.get('Content-Type', '')
        assert len(response.content) > 100
        
        print(f"✅ Successfully tested server with {len(response.content)} audio bytes")
        
    finally:
        # Clean shutdown
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()


def test_server_error_handling():
    """Test error handling without mocks."""
    import signal
    
    # Start server
    server_cmd = ['python', '-c', '''
import sys
import os
sys.path.insert(0, os.getcwd())

from voicify_server import app
app.run(debug=False, host="0.0.0.0", port=8003)
''']
    
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    try:
        # Wait for server to start
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get('http://localhost:8003/health', timeout=2)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                continue
        else:
            raise TimeoutError("Server didn't start")
        
        # Test error case - no text provided
        assert requests.post(
            'http://localhost:8003/text-to-speech',
            json={},
            timeout=5
        ).status_code == 400
        
        # Test error case - empty text
        assert requests.post(
            'http://localhost:8003/text-to-speech',
            json={'text': ''},
            timeout=5
        ).status_code == 400
        
        # Server should still be responding to health check
        assert requests.get('http://localhost:8003/health', timeout=5).status_code == 200
        
        print("✅ Successfully tested error handling")
        
    finally:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()


def test_server_performance():
    """Test basic server performance."""
    import signal
    
    project_dir = os.getcwd()
    test_port = find_free_port()
    
    # Ensure no cached imports
    import_modules_command = f'''
import sys
import os
import importlib
sys.path.insert(0, '{project_dir}')
os.chdir('{project_dir}')

# Clear any cached modules
modules_to_clear = ['voicify_server']
for module_name in modules_to_clear:
    if module_name in sys.modules:
        del sys.modules[module_name]

from voicify_server import app
app.run(debug=False, host="0.0.0.0", port={test_port})
'''
    
    server_cmd = ['python', '-c', import_modules_command]
    
    server_process = subprocess.Popen(
        server_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    try:
        # Wait for server to start
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get(f'http://localhost:{test_port}/health', timeout=2)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                continue
        else:
            raise TimeoutError("Server didn't start")
        
        # Test multiple sequential requests (since they write to same file)
        start_time = time.time()

        responses = []
        for i in range(3):
            # Add small delay to avoid file conflicts
            time.sleep(0.5)
            response = requests.post(
                f'http://localhost:{test_port}/text-to-speech',
                json={'text': f'Performance test {i+1}'},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            responses.append(response)
            
            # Note: First request debug removed for cleaner output
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        for i, response in enumerate(responses):
            assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}"
            assert len(response.content) > 100
        
        assert total_time < 45  # Should complete within reasonable time
        
        print(f"✅ Performance test: 3 requests in {total_time:.2f} seconds")
        
    finally:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
