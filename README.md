# Voicify MCP Server

A Flask-based Text-to-Speech (TTS) server that integrates with the Model Context Protocol (MCP) ecosystem. This server provides a RESTful API for converting text to speech using Voicify TTS or a fallback sine wave generator.

## Features

- 🎤 **Text-to-Speech Conversion**: Convert text to audio using Voicify TTS
- 🔄 **Fallback Support**: Automatic fallback to simple sine wave TTS when Voicify is unavailable
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
- File name: `output.wav`

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
- `make clean` - Clean up generated files (removes output.wav and Python cache)
- `make help` - Show available commands

## Project Structure

```
voicify-mcp/
├── voicify_server.py    # Main Flask application
├── requirements.txt      # Python dependencies
├── Makefile             # Build and run commands
├── README.md            # This file
└── output.wav          # Generated audio file (created by server)
```

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-RESTX**: REST API framework with Swagger support
- **numpy**: Numerical computing library (version <2.0)

## Fallback Behavior

When Voicify TTS is not available (due to import errors or missing dependencies), the server automatically falls back to generating simple sine wave audio. This ensures the service remains functional even without the Voicify dependency.

## Error Handling

The API provides proper error responses:

- **400 Bad Request**: When no text is provided
- **500 Internal Server Error**: When speech generation fails

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

## License

[Add license information here]

## Support

For issues and questions, please open an issue on GitHub or contact [your-email@example.com].
