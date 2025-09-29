# Voicify Installation Guide

This guide explains how to make Voicify TTS available for development and testing.

## Problem

The `voicify` package is **not publicly available** on PyPI. This means:
- ❌ `pip install voicify` fails
- ❌ The application runs in fail-fast mode by default
- ❌ Integration tests fail expecting Voicify

## Solutions

### Option 1: Mock Voicify Package (Recommended for Development)

We've created a mock Voicify package that you can install for development and testing.

#### Install Mock Voicify

```bash
# Activate your virtual environment
source venv/bin/activate

# Install the mock Voicify package
pip install -e mock_voicify/
```

#### What Mock Voicify Provides

- ✅ **Realistic Audio Generation**: Creates proper WAV files with speech-like characteristics
- ✅ **Correct Format**: 22,050 Hz sample rate, mono, 16-bit (matches test expectations)
- ✅ **Dynamic Duration**: Audio length scales with text length
- ✅ **API Compatible**: Same interface as real VoicifyTTS
- ✅ **Development Friendly**: Clear logging and feedback

#### Test Mock Installation

```bash
python -c "
from voicify_server import VOICIFY_AVAILABLE, text_to_speech
print(f'Voicify available: {VOICIFY_AVAILABLE}')
if VOICIFY_AVAILABLE:
    result = text_to_speech('Test message')
    print(f'✅ Generated: {result[1]} ({len(result[0])} bytes)')
"
```

### Option 2: Real Voicify Installation

If you have access to the real Voicify package, you can install it directly:

#### From Private Registry
```bash
pip install voicify --index-url https://your-private-registry.com/
```

#### From Local Source
```bash
# If you have Voicify source code
pip install /path/to/voicify/source/
```

#### From Wheel File (Available in Repository)
```bash
# Install the real Voicify wheel file
pip install voicify-0.1.0-py3-none-any.whl

# Or install all requirements including Voicify
pip install -r requirements.txt  # Now includes wheel file
```

**Note**: The real Voicify package generates MP3 format (not WAV) and connects to a cloud API.

### Option 3: Package Requirements Update

If Voicify becomes publicly available, update `requirements.txt`:

```bash
echo "voicify>=1.0.0" >> requirements.txt
pip install -r requirements.txt
```

## Verification

After installation, verify Voicify availability:

```bash
# Check import
python -c "from voicify_server import VOICIFY_AVAILABLE; print(f'Available: {VOICIFY_AVAILABLE}')"

# Test API
curl -X POST http://localhost:8001/text-to-speech \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello world"}' \
     --output test.wav

# Test health endpoint
curl http://localhost:8001/health | jq
```

Expected response when Voicify is available:
```json
{
  "status": "healthy",
  "voicify_available": true,
  "service": "voicify-tts"
}
```

## Testing

With mock Voicify installed, integration tests should pass:

```bash
# Run integration tests
python -m pytest tests/test_integration.py -v

# Run all tests
make test
```

## Troubleshooting

### Mock Package Issues
- **Reinstall after changes**: `pip install -e mock_voicify/ --force-reinstall`
- **Check import**: `python -c "from voicify import TextToSpeech"`

### Real Voicify Issues
- **Authentication**: Ensure you have credentials for private registries
- **Version compatibility**: Check that your Voicify version works with the expected API
- **Dependencies**: Some Voicify packages may have additional native dependencies

### Test Failures
- **Sample rate mismatch**: Ensure mock generates 22050 Hz audio
- **Threading issues**: Mock Voicify should be thread-safe for concurrent requests

## Development Workflow

1. **Install Mock**: `pip install -e mock_voicify/`
2. **Develop**: Code with full Voicify functionality available
3. **Test**: Run complete test suite with realistic scenarios
4. **Deploy**: Remove mock package for production or CI
5. **CI**: Uses fail-fast mode (no Voicify) - tests should define this expectation

## File Structure

```
mock_voicify/
├── setup.py              # Package installation definition
├── voicify/
│   ├── __init__.py       # Package initialization
│   └── tts.py           # Mock TextToSpeech implementation
```

The mock package provides all the functionality needed for development and testing while being transparent about its mock nature.
