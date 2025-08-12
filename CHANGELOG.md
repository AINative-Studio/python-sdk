# Changelog

All notable changes to the AINative Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-12

### Added
- Initial release of AINative Python SDK
- Core client with authentication support
- ZeroDB operations module
  - Project management (create, read, update, delete, suspend, activate)
  - Vector operations (upsert, search, delete)
  - Memory management (create, search, list, get related)
  - Analytics and usage tracking
- Agent Swarm module
  - Swarm orchestration and management
  - Agent configuration and control
  - Task distribution and monitoring
- CLI tool for quick operations
- Comprehensive error handling with custom exceptions
- Support for async operations
- Built-in retry logic and rate limiting
- Full test coverage (80%+)
- Examples and documentation

### Features
- **Authentication**: API key and secret support
- **Multi-tenant**: Organization ID support
- **Performance**: Connection pooling and async support
- **Reliability**: Automatic retries with exponential backoff
- **Developer Experience**: Type hints, comprehensive docs, and CLI

### Dependencies
- httpx>=0.24.0
- pydantic>=2.0.0
- python-dateutil>=2.8.0
- typing-extensions>=4.0.0
- aiohttp>=3.8.0 (for async support)

### Python Support
- Python 3.8+
- Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12