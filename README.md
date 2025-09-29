# Voicify MCP Server

A Flask-based Text-to-Speech (TTS) server that integrates with the Model Context Protocol (MCP) ecosystem. This server provides a RESTful API for converting text to speech using Voicify TTS with fail-fast error handling when the dependency is unavailable.

## Features

- 🎤 **Text-to-Speech Conversion**: Convert text to audio using Voicify TTS
- ⚠️ **Fail-Fast Design**: Clear error handling when Voicify TTS dependency unavailable
- 📖 **Interactive Documentation**: Built-in Swagger UI documentation
- 🌐 **CORS Support**: Cross-origin resource sharing enabled for web applications
- 🔍 **Health Monitoring**: Health check endpoint for service monitoring
- 📦 **MCP Integration**: Ready for Model Context Protocol integration

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone git@github.com:akram/voicify-mcp.git
cd voicify-mcp
```

2. Install dependencies:
```bash
make install
```

3. Start the server:
```bash
make run
```

The server will start on `http://localhost:8001`

## API Endpoints

### Text-to-Speech Conversion

**POST** `/text-to-speech`

Converts text to speech and returns an audio file in WAV format.

**Request Body:**
```json
{
  "text": "Hello, world!"
}
```

**Response:**
- Audio file download (`audio/wav` format)
- File name: `output_YYYYMMDD_HHMMSS_UUID.wav`

**Error Responses:**
- **400 Bad Request**: No text provided
- **503 Service Unavailable**: Voicify not available (install with `pip install voicify`)

### Health Check

**GET** `/health`

Returns the service health status.

**Response:**
```json
{
  "status": "healthy",
  "voicify_available": true,
  "service": "voicify-tts"
}
```

## Interactive Documentation

Visit `http://localhost:8001/swagger/` to access the interactive Swagger UI documentation where you can:

- Test API endpoints directly
- View request/response schemas
- Explore authentication requirements (if any)

## Available Make Commands

- `make run` - Start the Voicify TTS server on port 8001
- `make install` - Install Python dependencies
- `make fix-numpy` - Fix NumPy compatibility issue (downgrade to <2.0)
- `make test` - Run unit tests
- `make test-cov` - Run tests with coverage report
- `make test-verbose` - Run tests with verbose output
- `make test-watch` - Run tests in watch mode (reruns on file changes)
- `make clean` - Clean up generated files (removes output.wav and Python cache)
- `make help` - Show available commands

## Project Structure

```
voicify-mcp/
├── voicify_server.py    # Main Flask application
├── requirements.txt      # Python dependencies
├── Makefile             # Build and run commands
├── README.md            # This file
├── TESTING.md           # Testing documentation
├── test_voicify_server.py # Unit tests
├── conftest.py          # Test configuration and fixtures
├── pytest.ini           # Pytest configuration
└── output.wav          # Generated audio file (created by server)
```

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-RESTX**: REST API framework with Swagger support
- **numpy**: Numerical computing library (version <2.0)

### Testing Dependencies

- **pytest**: Testing framework
- **pytest-flask**: Flask testing utilities
- **pytest-cov**: Code coverage reporting
- **pytest-watch**: File watching for auto-rerunning tests

## Fallback Behavior

When Voicify TTS is not available (due to import errors or missing dependencies), the server automatically falls back to generating simple sine wave audio. This ensures the service remains functional even without the Voicify dependency.

## Error Handling

The API provides proper error responses:

- **400 Bad Request**: When no text is provided
- **500 Internal Server Error**: When speech generation fails

## Testing

The project includes comprehensive unit tests and integration tests:

### Unit Tests
```bash
# Run all unit tests
make test

# Run tests with coverage report
make test-cov

# Run tests in watch mode (auto-rerun on changes)
make test-watch
```

### Integration Tests (No Mocks)
```bash
# Run integration tests that verify server works end-to-end
make test-integration
```

These integration tests verify:
- ✅ Server starts and stops correctly
- ✅ Real HTTP requests work (health and TTS endpoints)
- ✅ Actual audio generation and file downloads
- ✅ Error handling with real server responses
- ✅ End-to-end functionality without mocks

For detailed testing documentation, see [TESTING.md](TESTING.md).

## Development

To run in development mode:

```bash
python voicify_server.py
```

The server runs with debug mode enabled by default and will automatically reload when code changes are detected.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment with **comprehensive testing strategies**:

### Features
- ✅ **Multi-scenario testing**: Both fail-fast and Voicify integration tests
- ✅ **Cross-version compatibility**: Testing across Python 3.9-3.13
- ✅ **Clear error handling**: Fail-fast approach with proper HTTP status codes
- ✅ **Performance testing**: Concurrency and load testing scenarios
- ✅ **Code coverage reporting**: Comprehensive coverage analysis

### Testing Strategies

#### 1. **Fail-Fast Testing** (CI Compatible)
Since Voicify may not be available in CI environments, the pipeline tests the application's fail-fast behavior:
- ✅ Tests the RuntimeError when Voicify is unavailable
- ✅ Verifies proper HTTP 503 responses from API endpoints
- ✅ Ensures clear error messages with installation instructions

#### 2. **Voicify Integration Testing** (Mocked)
For comprehensive testing, we mock Voicify scenarios:
- ✅ Tests Voicify-specific code paths
- ✅ Verifies file generation and cleanup logic
- ✅ Tests API endpoints with realistic TTS responses

#### 3. **Integration & Performance Testing**
- ✅ Full server integration tests
- ✅ Concurrent request handling
- ✅ Performance benchmarking
- ✅ File cleanup verification

### Workflow Files
The CI uses multiple specialized workflows:

#### `ci.yml` - Basic CI Pipeline
- Module import verification
- Complete test suite execution
- Fallback mode validation

#### `comprehensive-test.yml` - Advanced Testing
- **Multi-job matrix testing**
- **Voicify mock integration tests**
- **Performance and concurrency tests**
- **Coverage report generation**

### Running Tests Locally
```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test files
python -m pytest tests/test_voicify_server.py -v
python -m pytest tests/test_integration.py -v
```

### Voicify Dependency Handling

The application uses a **fail-fast approach** for Voicify dependency:

- **With Voicify**: Uses real Voicify TTS for high-quality audio generation
- **Without Voicify**: Returns HTTP 503 error with clear installation instructions
- **CI Environment**: Tests fail-fast behavior (expected in CI without Voicify)
- **Development**: Install Voicify manually (`pip install voicify`) for TTS functionality

### Workflow Triggers
- **Push** to `main` or `develop`: Full comprehensive test suite
- **Pull Request** to `main` or `develop`: Core functionality tests
- **Manual Dispatch**: Can trigger comprehensive testing manually

### Status Badges
To add CI status badges to your README:
```markdown
![CI](https://github.com/[your-username]/voicify-mcp/workflows/CI%20Pipeline/badge.svg)
![Comprehensive Tests](https://github.com/[your-username]/voicify-mcp/workflows/Comprehensive%20Testing/badge.svg)
```

## License

[Add license information here]

## Support

For issues and questions, please open an issue on GitHub or contact [your-email@example.com].
