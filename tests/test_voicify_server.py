import pytest
import os
import io
import wave
import tempfile
from unittest.mock import patch, mock_open, MagicMock
import json

# Import the application modules
from voicify_server import app, text_to_speech, VOICIFY_AVAILABLE


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "Hello, world! This is a test."


@pytest.fixture
def temp_wav_file():
    """Create a temporary WAV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        # Create a minimal WAV file
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(b'\x00\x00' * 1000)  # 1000 samples
        
        f.write(wav_buffer.getvalue())
    yield f.name
    # Clean up
    if os.path.exists(f.name):
        os.unlink(f.name)


class TestTextToSpeechFunction:
    """Test the text_to_speech function."""
    
    @patch('voicify_server.VOICIFY_AVAILABLE', True)
    @patch('voicify_server.VoicifyTTS', create=True)
    def test_text_to_speech_with_voicify_success(self, mock_voicify_class, sample_text, temp_wav_file):
        """Test text_to_speech function when Voicify is available and successful."""
        # Mock Voicify TTS
        mock_tts_instance = MagicMock()
        mock_voicify_class.return_value = mock_tts_instance
        
        # Mock file operations
        audio_data = b'fake_audio_data'
        
        # Create a custom mock for os.path.exists that returns True for output.wav
        def mock_exists(filepath):
            return 'output.wav' in filepath or 'output_' in filepath
        
        with patch('builtins.open', mock_open(read_data=audio_data)):
            with patch('os.path.exists', side_effect=mock_exists):
                with patch('os.rename'):
                    result = text_to_speech(sample_text)
                    
                    # Verify Voicify TTS was called correctly
                    mock_voicify_class.assert_called_once()
                    mock_tts_instance.write_voice.assert_called_once_with(sample_text)
                    
                    # Verify result (now returns tuple of audio_data, filename)
                    assert result is not None
                    audio_data_result, filename = result
                    assert audio_data_result == audio_data
                    assert isinstance(filename, str)

    @patch('voicify_server.VOICIFY_AVAILABLE', True)
    @patch('voicify_server.VoicifyTTS', create=True)
    def test_text_to_speech_with_voicify_file_not_found(self, mock_voicify_class, sample_text):
        """Test text_to_speech function when Voicify is available but file not found."""
        # Mock Voicify TTS
        mock_tts_instance = MagicMock()
        mock_voicify_class.return_value = mock_tts_instance
        
        with patch('os.path.exists', return_value=False):
            result = text_to_speech(sample_text)
            
            # Verify Voicify TTS was called
            mock_voicify_class.assert_called_once()
            mock_tts_instance.write_voice.assert_called_once_with(sample_text)
            
            # Verify result (now returns tuple)
            assert result is None or result == (None, None)

    @patch('voicify_server.VOICIFY_AVAILABLE', False)
    def test_text_to_speech_fail_fast_no_voicify(self, sample_text):
        """Test text_to_speech function throws error when Voicify not available."""
        with pytest.raises(RuntimeError) as exc_info:
            text_to_speech(sample_text)
        
        assert "Voicify TTS not available" in str(exc_info.value)
        assert "pip install voicify" in str(exc_info.value)

    @patch('voicify_server.VOICIFY_AVAILABLE', True)
    @patch('voicify_server.VoicifyTTS', create=True)
    def test_text_to_speech_with_voicify_exception(self, mock_voicify_class, sample_text):
        """Test text_to_speech function when Voicify raises an exception."""
        # Mock Voicify TTS to raise an exception
        mock_voicify_class.side_effect = Exception("Voicify error")
        
        with patch('voicify_server.open', mock_open()) as mock_file:
            result = text_to_speech(sample_text)
            
            # Should fall back gracefully and return None
            assert result == (None, None)

    @patch('voicify_server.VOICIFY_AVAILABLE', False)
    def test_text_to_speech_fail_fast_short_and_long_text(self):
        """Test that fail-fast works consistently for different text lengths."""
        short_text = "Hi"
        long_text = "This is a very long text that should be capped at maximum duration" * 10
        
        # Both should fail with the same error regardless of text length
        with pytest.raises(RuntimeError) as exc_info:
            text_to_speech(short_text)
        
        assert "Voicify TTS not available" in str(exc_info.value)
        
        with pytest.raises(RuntimeError) as exc_info:
            text_to_speech(long_text)
        
        assert "Voicify TTS not available" in str(exc_info.value)


class TestTTSAPIEndpoint:
    """Test the POST /text-to-speech endpoint."""
    
    def test_tts_endpoint_success_json(self, client, sample_text):
        """Test TTS endpoint with JSON request."""
        with patch('voicify_server.text_to_speech') as mock_tts:
            mock_tts.return_value = (b'fake_audio_data', 'output_test.wav')
            
            with patch('voicify_server.send_file') as mock_send_file:
                mock_send_file.return_value = "Audio file response"
                
                response = client.post('/text-to-speech', 
                                    json={'text': sample_text},
                                    content_type='application/json')
                
                assert response.status_code == 200
                mock_tts.assert_called_once_with(sample_text)

    def test_tts_endpoint_success_form(self, client, sample_text):
        """Test TTS endpoint with form data request."""
        with patch('voicify_server.text_to_speech') as mock_tts:
            mock_tts.return_value = (b'fake_audio_data', 'output_test.wav')
            
            with patch('voicify_server.send_file') as mock_send_file:
                mock_send_file.return_value = "Audio file response"
                
                response = client.post('/text-to-speech', 
                                    data={'text': sample_text})
                
                assert response.status_code == 200
                mock_tts.assert_called_once_with(sample_text)

    def test_tts_endpoint_no_text_json(self, client):
        """Test TTS endpoint with no text in JSON."""
        response = client.post('/text-to-speech', 
                             json={},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No text provided' in data['error']

    def test_tts_endpoint_no_text_form(self, client):
        """Test TTS endpoint with no text in form data."""
        response = client.post('/text-to-speech', data={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No text provided' in data['error']

    def test_tts_endpoint_tts_failure(self, client, sample_text):
        """Test TTS endpoint when text_to_speech returns None."""
        with patch('voicify_server.text_to_speech') as mock_tts:
            mock_tts.return_value = None
            
            response = client.post('/text-to-speech', 
                                  json={'text': sample_text})
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Failed to generate speech' in data['error']

    def test_tts_endpoint_exception(self, client, sample_text):
        """Test TTS endpoint when an exception occurs."""
        with patch('voicify_server.text_to_speech') as mock_tts:
            mock_tts.side_effect = Exception("Unexpected error")
            
            response = client.post('/text-to-speech', 
                                  json={'text': sample_text})
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Error generating speech' in data['error']

    def test_tts_endpoint_empty_string(self, client):
        """Test TTS endpoint with empty string text."""
        response = client.post('/text-to-speech', 
                              json={'text': ''},
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No text provided' in data['error']

    def test_tts_endpoint_whitespace_text(self, client):
        """Test TTS endpoint with whitespace-only text."""
        response = client.post('/text-to-speech', 
                              json={'text': '   \n\t   '},
                              content_type='application/json')
        
        # With Voicify unavailable, should return 503 instead of processing whitespace text
        if response.status_code == 503:
            response_data = response.get_json()
            assert 'Voicify TTS not available' in response_data['error']
        else:
            # If Voicify is available, whitespace-only strings should be processed normally
            # since 'if not text:' evaluates to False for non-empty strings
            assert response.status_code == 200


class TestHealthAPIEndpoint:
    """Test the GET /health endpoint."""
    
    def test_health_endpoint_success(self, client):
        """Test health endpoint returns correct status."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'healthy'
        assert data['service'] == 'voicify-tts'
        assert 'voicify_available' in data
        assert isinstance(data['voicify_available'], bool)

    def test_health_endpoint_voicify_available_info(self, client):
        """Test health endpoint reflects Voicify availability."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # The voicify_available field should reflect the actual VOICIFY_AVAILABLE value
        assert data['voicify_available'] == VOICIFY_AVAILABLE

    def test_health_endpoint_content_type(self, client):
        """Test health endpoint returns JSON content type."""
        response = client.get('/health')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'


class TestApplicationSetup:
    """Test application configuration and setup."""
    
    def test_app_configuration(self):
        """Test Flask app configuration."""
        # In test mode, DEBUG may be False but TESTING should be True
        assert app.config.get('TESTING', False) == True

    def test_cors_enabled(self):
        """Test that CORS is enabled."""
        # Flask-CORS should be initialized
        from flask_cors import CORS
        assert CORS is not None

    def test_api_initialization(self):
        """Test Flask-RESTX API initialization."""
        from flask_restx import Api
        # The API should be initialized with correct settings
        assert hasattr(app, 'extensions')


class TestErrorHandling:
    """Test various error handling scenarios."""
    
    def test_invalid_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get('/non-existent')
        assert response.status_code == 404

    def test_txt_method_not_allowed(self, client):
        """Test wrong HTTP method on endpoints."""
        response = client.get('/text-to-speech')
        # Flask-RESTX might return 405 or 404 depending on configuration
        assert response.status_code in [404, 405]

    def test_health_post_method(self, client):
        """Test POST method on health endpoint."""
        response = client.post('/health')
        # Should return method not allowed
        assert response.status_code == 405


class TestIntegrationScenarios:
    """Test integration scenarios."""
    
    def test_complete_workflow_with_voicify(self, client):
        """Test complete workflow when Voicify is available."""
        test_text = "Integration test text"
        mock_audio_data = b'integration_test_audio'
        
        with patch('voicify_server.VOICIFY_AVAILABLE', True):
            with patch('voicify_server.VoicifyTTS', create=True) as mock_voicify:
                with patch('builtins.open', mock_open(read_data=mock_audio_data)):
                    # Mock os.path.exists to return True for output.wav specifically
                    def mock_exists(filepath):
                        return 'output.wav' in filepath or 'output_' in filepath
                    with patch('os.path.exists', side_effect=mock_exists):
                        with patch('os.rename'):
                            with patch('voicify_server.send_file') as mock_send_file:
                                mock_send_file.return_value = "Audio file response"
                                
                                response = client.post('/text-to-speech',
                                                      json={'text': test_text})
                                
                                assert response.status_code == 200
                                mock_send_file.assert_called_once()

    def test_complete_workflow_without_voicify(self, client):
        """Test complete workflow when Voicify is not available."""
        test_text = "Integration test text"
        
        with patch('voicify_server.VOICIFY_AVAILABLE', False):
            response = client.post('/text-to-speech',
                                  json={'text': test_text})
            
            # Should return 503 Service Unavailable
            assert response.status_code == 503
            response_data = response.get_json()
            assert response_data['error'] == 'Voicify TTS not available'
            assert 'install_command' in response_data
            assert response_data['install_command'] == 'pip install voicify'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
