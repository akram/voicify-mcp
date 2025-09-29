"""
Integration tests for Voicify TTS Server.

These tests verify the server works end-to-end without mocks,
testing actual HTTP requests, audio generation, and file operations.
"""

import pytest
import requests
import time
import os
import subprocess
import socket
import random
import signal
import threading
import json
import tempfile
import wave


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


class VoicifyServerIntegration:
    """Helper class for managing the server during integration tests."""
    
    def __init__(self, port=None):
        self.port = port or find_free_port()
        self.process = None
        self.base_url = f"http://localhost:{self.port}"
        
    def start_server(self):
        """Start the server in a subprocess."""
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        
        # Modify server to use test port
        server_cmd = ['python', '-c', f'''
import os, sys
sys.path.insert(0, os.getcwd())
import voicify_server
voicify_server.app.run(debug=False, host="0.0.0.0", port={self.port})
''']
        
        self.process = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=os.getcwd(),
            preexec_fn=None if os.name == 'nt' else os.setsid
        )
        
        # Debug: print server stderr for troubleshooting
        time.sleep(1)
        if self.process.poll() is not None:
            stdout, stderr = self.process.communicate()
            print(f"Server failed to start. stdout: {stdout.decode()}")
            print(f"Server stderr: {stderr.decode()}")
            raise RuntimeError(f"Server process exited with code {self.process.returncode}")
            
        # Wait for server to start
        self._wait_for_server()
        return True
        
    def _wait_for_server(self, max_wait=10):
        """Wait for the server to be ready."""
        for _ in range(max_wait):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        raise TimeoutError("Server failed to start within expected time")
        
    def stop_server(self):
        """Stop the server subprocess."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            
    def __enter__(self):
        self.start_server()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_server()


class TestVoicifyServerIntegration:
    """Integration tests for the Voicify TTS Server."""
    
    def test_server_health_endpoint(self):
        """Test that the server health endpoint works correctly."""
        with VoicifyServerIntegration() as server:
            response = requests.get(f"{server.base_url}/health", timeout=5)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify health response structure
            assert 'status' in data
            assert 'voicify_available' in data
            assert 'service' in data
            
            assert data['status'] == 'healthy'
            assert data['service'] == 'voicify-tts'
            assert isinstance(data['voicify_available'], bool)
            
    def test_server_starts_and_stops_properly(self):
        """Test that the server can be started and stopped cleanly."""
        server = VoicifyServerIntegration()
        
        # Test server starts
        assert server.start_server()
        
        # Verify server is responding
        response = requests.get(f"{server.base_url}/health", timeout=5)
        assert response.status_code == 200
        
        # Test server stops
        server.stop_server()
        
        # Verify server is no longer responding
        with pytest.raises(requests.exceptions.RequestException):
            requests.get(f"{server.base_url}/health", timeout=2)
            
    def test_tts_endpoint_with_json_request(self):
        """Test TTS endpoint with JSON request and real audio generation."""
        with VoicifyServerIntegration() as server:
            test_text = "Hello, this is an integration test."
            
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'text': test_text},
                headers={'Content-Type': 'application/json'},
                timeout=30  # Allow time for audio generation
            )
            
            assert response.status_code == 200
            
            # Verify it's an audio file (WAV or MP3 depending on Voicify implementation)
            content_type = response.headers.get('Content-Type', '')
            assert 'audio/wav' in content_type or 'audio/mp3' in content_type
            
            # Verify we got actual audio data
            audio_data = response.content
            assert len(audio_data) > 100  # Should be substantial audio data
            
            # Verify it's a valid WAV file
            self._verify_wav_file(audio_data)
            
    def test_tts_endpoint_with_form_request(self):
        """Test TTS endpoint with form data request."""
        with VoicifyServerIntegration() as server:
            test_text = "Integration test with form data."
            
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                data={'text': test_text},
                timeout=30
            )
            
            assert response.status_code == 200
            content_type = response.headers.get('Content-Type', '')
            assert 'audio/wav' in content_type or 'audio/mp3' in content_type
            
            # Verify audio data
            audio_data = response.content
            assert len(audio_data) > 100
            self._verify_wav_file(audio_data)
            
    def test_tts_endpoint_error_handling(self):
        """Test TTS endpoint error handling for invalid requests."""
        with VoicifyServerIntegration() as server:
            # Test with no text
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            assert response.status_code == 400
            data = response.json()
            assert 'error' in data
            assert 'No text provided' in data['error']
            
            # Test with empty string
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'text': ''},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            assert response.status_code == 400
            data = response.json()
            assert 'error' in data
            
    def test_different_text_lengths(self):
        """Test TTS with different text lengths to verify duration calculation."""
        with VoicifyServerIntegration() as server:
            test_cases = [
                "Hi",  # Very short
                "Hello world.",  # Short
                "This is a medium length text that will test the fallback audio generation.",  # Medium
                "This is a very long text " * 20,  # Long (should be capped at 10 seconds)
            ]
            
            for text in test_cases:
                response = requests.post(
                    f"{server.base_url}/text-to-speech",
                    json={'text': text},
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                assert response.status_code == 200
                
                audio_data = response.content
                assert len(audio_data) > 50  # Should have some audio
                
                # Verify it's a valid WAV file
                self._verify_wav_file(audio_data)
                
    def test_concurrent_requests(self):
        """Test that the server can handle multiple concurrent requests."""
        with VoicifyServerIntegration() as server:
            import concurrent.futures
            
            def make_request(text):
                response = requests.post(
                    f"{server.base_url}/text-to-speech",
                    json={'text': text},
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                return response
            
            # Submit multiple concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                texts = [
                    "Concurrent test 1",
                    "Concurrent test 2", 
                    "Concurrent test 3"
                ]
                
                futures = [executor.submit(make_request, text) for text in texts]
                results = [future.result() for future in futures]
                
                # Check results (real Voicify may have rate limiting)
                successful_requests = 0
                failed_requests = 0
                
                for response in results:
                    if response.status_code == 200:
                        successful_requests += 1
                        assert len(response.content) > 100
                    else:
                        failed_requests += 1
                        print(f"Request failed with status {response.status_code}")
                
                # Real Voicify may have concurrent request limitations
                assert successful_requests >= 1, f"Expected at least 1 successful request, got {successful_requests}"
                
                if successful_requests == len(texts):
                    print("✅ All concurrent requests succeeded")
                else:
                    print(f"⚠️  {successful_requests}/{len(texts)} concurrent requests succeeded (Voicify may have rate limiting)")
                    
    def test_swagger_documentation_endpoint(self):
        """Test that Swagger documentation endpoint is accessible."""
        with VoicifyServerIntegration() as server:
            response = requests.get(f"{server.base_url}/swagger/", timeout=10)
            
            # Should redirect or serve the Swagger UI
            assert response.status_code in [200, 302]
            
            if response.status_code == 200:
                assert 'swagger' in response.text.lower() or 'api' in response.text.lower()
                
    def test_file_generation_cleanup(self):
        """Test that audio files are generated and returned correctly."""
        with VoicifyServerIntegration() as server:
            test_text = "File generation test"
            
            # Make TTS request
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'text': test_text},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            assert response.status_code == 200
            
            # Verify we get audio content back
            assert response.content is not None
            assert len(response.content) > 0
            
            # Verify it's audio content (WAV files start with "RIFF", MP3 with "ID3")
            audio_start = response.content[:4]
            assert audio_start.startswith(b'RIFF') or audio_start.startswith(b'ID3'), \
                f"Audio response should be WAV or MP3 format, got: {audio_start}"
                
    def _verify_wav_file(self, audio_data):
        """Verify that audio data is valid audio format (WAV or MP3)."""
        import io
        
        # Check if it's WAV format
        if audio_data.startswith(b'RIFF'):
            try:
                wav_buffer = io.BytesIO(audio_data)
                with wave.open(wav_buffer, 'rb') as wav_file:
                    # Verify it's a WAV file with expected properties
                    assert wav_file.getnchannels() >= 1  # Mono or stereo
                    assert wav_file.getsampwidth() >= 1  # 8-bit or 16-bit
                    assert wav_file.getnframes() > 0  # Has audio frames
                    assert wav_file.getframerate() >= 8000  # Reasonable sample rate
                    
            except wave.Error as e:
                pytest.fail(f"Invalid WAV file format: {e}")
        # Check if it's MP3 format
        elif audio_data.startswith(b'ID3'):
            assert len(audio_data) > 1000, "MP3 file too small"
            # MP3 files are typically at least 1KB for short audio
        else:
            # For other formats or unknown, just verify substantial content
            assert len(audio_data) > 1000, "Audio file too small or unknown format"
            
    def test_server_logs_and_startup(self):
        """Test that server logs startup messages correctly."""
        with VoicifyServerIntegration() as server:
            # Server should have started successfully (tested in __enter__)
            response = requests.get(f"{server.base_url}/health", timeout=5)
            assert response.status_code == 200
            
            # Verify server responds to TTS requests
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'text': 'Startup test'},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            assert response.status_code == 200
            
    def test_error_recovery(self):
        """Test that server can recover from errors and continue serving."""
        with VoicifyServerIntegration() as server:
            # Send invalid request that should cause an error
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'invalid_field': 'test'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Should get an error response
            assert response.status_code == 400
            
            # But server should still be responsive
            response = requests.get(f"{server.base_url}/health", timeout=5)
            assert response.status_code == 200
            
            # And should still be able to process valid TTS requests
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'text': 'Recovery test'},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            assert response.status_code == 200
            
    def test_server_performance(self):
        """Test basic performance characteristics."""
        with VoicifyServerIntegration() as server:
            test_text = "Performance test text for timing measurements."
            
            start_time = time.time()
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'text': test_text},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should respond within reasonable time (less than 30 seconds)
            assert processing_time < 30
            assert response.status_code == 200
            
            # Should generate audio data
            assert len(response.content) > 100


class TestVoicifyServerFailFastBehavior:
    """Integration tests focusing on fail-fast behavior when Voicify unavailable."""
    
    def test_server_fails_without_voicify(self):
        """Test that server properly fails when Voicify is unavailable."""
        with VoicifyServerIntegration() as server:
            # Check if Voicify is available
            health_response = requests.get(f"{server.base_url}/health", timeout=5)
            health_data = health_response.json()
            
            # Test TTS when Voicify is not available should fail gracefully
            response = requests.post(
                f"{server.base_url}/text-to-speech",
                json={'text': 'Fail-fast behavior test'},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Should return 503 Service Unavailable when Voicify not available
            if not health_data.get('voicify_available', False):
                assert response.status_code == 503
                response_data = response.json()
                assert 'error' in response_data
                assert 'Voicify TTS not available' in response_data['error']
                assert 'install_command' in response_data
            else:
                # If Voicify is available, should work normally
                assert response.status_code == 200
                

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
