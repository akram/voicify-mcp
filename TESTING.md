# Testing Documentation

This document describes the testing setup and how to run tests for the Voicify MCP Server.

## Test Structure

### Unit Tests
The test suite is organized into several test classes in `test_voicify_server.py`:

### TestTextToSpeechFunction
- Tests for the `text_to_speech()` function
- Covers both Voicify-enabled and fallback scenarios
- Tests error handling and edge cases

### TestTTSAPIEndpoint
- Tests for the POST `/text-to-speech` endpoint
- Tests both JSON and form data requests
- Tests error conditions and edge cases

### TestHealthAPIEndpoint
- Tests for the GET `/health` endpoint
- Verifies proper health status reporting

### TestApplicationSetup
- Tests Flask application configuration
- Verifies CORS and API initialization

### TestErrorHandling
- Tests various error handling scenarios
- Tests invalid endpoints and methods

### TestIntegrationScenarios
- End-to-end workflow tests
- Tests complete request/response cycles

## Integration Tests (No Mocks)

Separate integration tests in `simple_integration_test.py` verify server functionality end-to-end:

### TestServerBasicFunctionality
- Starts actual server process in subprocess
- Makes real HTTP requests (no mocks)
- Verifies audio generation and file downloads
- Tests health endpoint functionality

### TestServerErrorHandling  
- Tests server error responses without mocks
- Verifies error recovery and continued functionality
- Tests invalid request handling

### TestServerPerformance
- Tests server responsiveness and timing
- Verifies server can handle sequential requests

### Integration Test Commands

```bash
# Run integration tests
make test-integration

# Run specific integration test
python -m pytest simple_integration_test.py::test_server_basic_functionality -v
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage report
make test-cov

# Run tests in watch mode (reruns on file changes)
make test-watch
```

### Individual Test Commands

```bash
# Run specific test file
python -m pytest test_voicify_server.py

# Run specific test class
python -m pytest test_voicify_server.py::TestTextToSpeechFunction

# Run specific test method
python -m pytest test_voicify_server.py::TestTextToSpeechFunction::test_text_to_speech_with_voicify_success

# Run tests matching a pattern
python -m pytest -k "voicify"

# Run tests with specific marker
python -m pytest -m unit
```

### Coverage Commands

```bash
# Generate HTML coverage report
python -m pytest --cov=voicify_server --cov-report=html

# Generate terminal coverage report
python -m pytest --cov=voicify_server --cov-report=term

# Generate both HTML and terminal reports
python -m pytest --cov=voicify_server --cov-report=html --cov-report=term
```

## Test Dependencies

The following packages are required for testing:

- `pytest`: Main testing framework
- `pytest-flask`: Flask-specific testing utilities
- `pytest-cov`: Code coverage reporting
- `pytest-watch`: File watching for auto-rerunning tests

## Test Configuration

### pytest.ini
Configuration file for pytest including:
- Test discovery patterns
- Output options
- Coverage settings
- Custom markers

### conftest.py
Shared fixtures and configuration including:
- Flask test client setup
- Mock audio data
- Sample texts for testing
- File cleanup utilities

## Test Coverage

The test suite aims for comprehensive coverage of:

1. **Core Functionality**
   - Text-to-speech conversion
   - Voicify integration
   - Fallback functionality

2. **API Endpoints**
   - Request/response handling
   - Error cases
   - Content type validation

3. **Error Handling**
   - Exception scenarios
   - Invalid input handling
   - Service failures

4. **Integration**
   - Complete workflow tests
   - Environment-specific behavior

## Mock Usage

Tests extensively use mocks to:

- Mock Voicify TTS library when not available
- Mock file system operations
- Mock external dependencies
- Test error conditions without actual failures

## Best Practices

1. **Test Isolation**: Each test is independent and doesn't rely on others
2. **Cleanup**: Temporary files are automatically cleaned up
3. **Mocking**: External dependencies are properly mocked
4. **Assertions**: Clear and specific assertions are used
5. **Documentation**: Each test is documented with docstrings

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention
2. Add appropriate docstrings
3. Use relevant fixtures from conftest.py
4. Test both success and failure cases
5. Update this documentation if needed

## Continuous Integration

The tests are designed to run in CI environments:
- No external dependencies required
- Deterministic behavior
- Fast execution time
- Comprehensive coverage reporting
