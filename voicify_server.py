from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import os
import uuid
import time

# Try to import Voicify TTS
try:
    from voicify import TextToSpeech as VoicifyTTS
    VOICIFY_AVAILABLE = True
except ImportError:
    VOICIFY_AVAILABLE = False
    print("Voicify not available. Install with: pip install voicify")

app = Flask(__name__)
CORS(app)

# Initialize Flask-RESTX API with Swagger documentation
api = Api(
    app,
    version='1.0',
    title='Voicify TTS API',
    description='Text-to-Speech API using Voicify or fallback TTS',
    doc='/swagger/'  # Swagger UI will be available at /swagger/
)

# Define request/response models for Swagger documentation
tts_request = api.model('TTSRequest', {
    'text': fields.String(required=True, description='Text to convert to speech', example='Hello, world!')
})

health_response = api.model('HealthResponse', {
    'status': fields.String(description='Service status', example='healthy'),
    'voicify_available': fields.Boolean(description='Whether Voicify is available'),
    'service': fields.String(description='Service name', example='voicify-tts')
})

def text_to_speech(text):
    """Generate speech audio from text and save to unique filename"""
    if not VOICIFY_AVAILABLE:
        raise RuntimeError(
            "Voicify TTS not available. "
            "Please install the voicify package to enable TTS functionality: "
            "pip install voicify"
        )
    
    try:
        # Generate unique filename to avoid concurrent access conflicts
        unique_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)  # millisecond timestamp
        filename = f"output_{timestamp}_{unique_id[:8]}.wav"
        output_file = os.path.abspath(filename)
        
        # Use Voicify TTS
        tts_engine = VoicifyTTS()
        tts_engine.write_voice(text)  # This writes output.wav
        
        # Check if Voicify created the default output.wav file
        default_file = os.path.abspath('output.wav')
        if os.path.exists(default_file):
            # Move the file to our unique name
            os.rename(default_file, output_file)
            
            # Read the generated file
            with open(output_file, 'rb') as f:
                audio_data = f.read()
            return audio_data, filename
        else:
            print("Voicify did not generate output.wav")
            return None, None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None, None

@api.route('/text-to-speech')
class TextToSpeech(Resource):
    @api.expect(tts_request)
    @api.doc('text_to_speech', 
             description='Convert text to speech using Voicify TTS and return audio file',
             responses={
                 200: 'Audio file (WAV/MP3 format depending on Voicify configuration)',
                 400: 'Bad Request - No text provided',
                 500: 'Internal Server Error - Voicify TTS not available or failed to generate speech',
                 503: 'Service Unavailable - Voicify TTS package not installed'
             })
    def post(self):
        """Convert text to speech and return audio file"""
        try:
            # Get text from form data or JSON
            if request.is_json:
                data = request.get_json()
                text = data.get('text')
            else:
                text = request.form.get('text')
            
            if not text:
                return {'error': 'No text provided'}, 400

            # Convert text to speech
            try:
                result = text_to_speech(text)
            except RuntimeError as e:
                if "Voicify TTS not available" in str(e):
                    return {
                        'error': 'Voicify TTS not available',
                        'message': 'Please install voicify package for TTS functionality',
                        'install_command': 'pip install voicify'
                    }, 503
                else:
                    raise
            
            if result is None:
                return {'error': 'Failed to generate speech'}, 500
            
            audio_data, filename = result
            
            if audio_data is None:
                return {'error': 'Failed to generate speech'}, 500

            # Return the audio file using the unique filename
            output_file = os.path.abspath(filename)
            
            # Detect audio format by checking file header
            mimetype = 'audio/wav'  # default
            with open(output_file, 'rb') as f:
                header = f.read(12)
                if header.startswith(b'ID3'):
                    mimetype = 'audio/mp3'
                elif header.startswith(b'RIFF'):
                    mimetype = 'audio/wav'
                elif header.startswith(b'OggS'):
                    mimetype = 'audio/ogg'
            
            # Store the file path for cleanup after response
            from flask import g
            g.temp_audio_file = output_file
            
            return send_file(
                output_file,
                as_attachment=True,
                mimetype=mimetype,
                download_name=filename
            )

        except Exception as e:
            # Clean up any temp files on error
            from flask import g
            if hasattr(g, 'temp_audio_file') and g.temp_audio_file and os.path.exists(g.temp_audio_file):
                try:
                    os.remove(g.temp_audio_file)
                except:
                    pass
            return {'error': f'Error generating speech: {str(e)}'}, 500

@api.route('/health')
class Health(Resource):
    @api.marshal_with(health_response)
    @api.doc('health_check', 
             description='Health check endpoint',
             responses={
                 200: 'Service health status'
             })
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'voicify_available': VOICIFY_AVAILABLE,
            'service': 'voicify-tts'
        }


@app.teardown_request
def cleanup_temp_files(error=None):
    """Clean up temporary audio files after each request."""
    from flask import g
    if hasattr(g, 'temp_audio_file') and g.temp_audio_file:
        try:
            if os.path.exists(g.temp_audio_file):
                os.remove(g.temp_audio_file)
                filename = os.path.basename(g.temp_audio_file)
                print(f"Cleaned up temporary file: {filename}")
        except OSError as e:
            print(f"Could not remove {g.temp_audio_file}: {e}")


def cleanup_old_audio_files():
    """Clean up ALL old audio files to prevent disk space issues"""
    try:
        cleaned_count = 0
        # Find and remove all audio files from previous runs
        for filename in os.listdir('.'):
            if filename.startswith('output_') and filename.endswith('.wav'):
                file_path = os.path.abspath(filename)
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except OSError as e:
                    print(f"Could not remove {filename}: {e}")
        
        if cleaned_count > 0:
            print(f"Cleaned up {cleaned_count} old audio files")
        else:
            print("No old audio files to clean up")
    except Exception as e:
        print(f"Error during cleanup: {e}")


if __name__ == '__main__':
    print("Starting Voicify TTS server...")
    print("Cleaning up old audio files...")
    cleanup_old_audio_files()
    print("Server will be available at: http://localhost:8001")
    print("Swagger documentation available at: http://localhost:8001/swagger/")
    print(f"Voicify available: {VOICIFY_AVAILABLE}")
    print("Generated files will use unique names to avoid conflicts")
    app.run(debug=True, host='0.0.0.0', port=8001)
