from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import os
import io
import wave
import struct
import math

# Try to import Voicify, fall back to simple TTS if not available
try:
    from voicify import TextToSpeech as VoicifyTTS
    VOICIFY_AVAILABLE = True
except ImportError:
    VOICIFY_AVAILABLE = False
    print("Voicify not available, using simple TTS fallback")

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
    """Generate speech audio from text and save to output.wav"""
    try:
        if VOICIFY_AVAILABLE:
            # Use Voicify TTS
            tts_engine = VoicifyTTS()
            tts_engine.write_voice(text)  # This writes output.wav
            
            # Read the generated file
            if os.path.exists('output.wav'):
                with open('output.wav', 'rb') as f:
                    audio_data = f.read()
                return audio_data
            else:
                print("Voicify did not generate output.wav")
                return None
        else:
            # Fallback to simple sine wave TTS
            sample_rate = 22050
            duration = min(len(text) * 0.1, 10.0)  # Duration based on text length, max 10 seconds
            frequency = 440.0

            frames = []
            for i in range(int(sample_rate * duration)):
                value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
                frames.append(struct.pack('<h', value))

            # Create WAV file
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(frames))

            wav_buffer.seek(0)
            audio_data = wav_buffer.getvalue()
            
            # Save to output.wav
            with open('output.wav', 'wb') as f:
                f.write(audio_data)
            
            return audio_data
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

@api.route('/text-to-speech')
class TextToSpeech(Resource):
    @api.expect(tts_request)
    @api.doc('text_to_speech', 
             description='Convert text to speech and return audio file',
             responses={
                 200: 'Audio file (WAV format)',
                 400: 'Bad Request - No text provided',
                 500: 'Internal Server Error - Failed to generate speech'
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
            audio_data = text_to_speech(text)
            
            if audio_data is None:
                return {'error': 'Failed to generate speech'}, 500

            # Return the audio file
            return send_file(
                'output.wav',
                as_attachment=True,
                mimetype='audio/wav',
                download_name='output.wav'
            )

        except Exception as e:
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


if __name__ == '__main__':
    print("Starting Voicify TTS server...")
    print("Server will be available at: http://localhost:8001")
    print("Swagger documentation available at: http://localhost:8001/swagger/")
    print(f"Voicify available: {VOICIFY_AVAILABLE}")
    app.run(debug=True, host='0.0.0.0', port=8001)
