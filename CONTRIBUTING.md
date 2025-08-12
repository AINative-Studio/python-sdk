# Contributing to AINative Python SDK

We welcome contributions to the AINative Python SDK! This document will help you get started.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AINative-Studio/python-sdk.git
   cd python-sdk
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Code Standards

### Style Guidelines
- Follow PEP 8 for code style
- Use type hints for all functions and methods
- Write comprehensive docstrings in Google format
- Maximum line length: 100 characters

### Code Formatting
We use several tools to maintain code quality:

```bash
# Format code
black ainative/
isort ainative/

# Lint code
flake8 ainative/

# Type checking
mypy ainative/
```

### Testing
All contributions must include tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ainative

# Run specific test file
pytest tests/test_client.py
```

We aim for 80%+ test coverage.

## Submitting Changes

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with tests
4. **Run the test suite** to ensure everything passes
5. **Commit your changes** with a clear message
6. **Push to your fork** and submit a pull request

### Commit Message Format
```
type(scope): description

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(zerodb): add vector search filtering

Add support for metadata filtering in vector search operations.
Includes new filter parameter and comprehensive tests.

Closes #123
```

## Pull Request Process

1. Ensure your PR has a clear title and description
2. Link any related issues
3. Include tests for new functionality
4. Update documentation if needed
5. Ensure all CI checks pass
6. Request review from maintainers

## Reporting Issues

When reporting issues, please include:

1. **Environment details** (Python version, OS, SDK version)
2. **Minimal code example** that reproduces the issue
3. **Expected vs actual behavior**
4. **Error messages** (full stack trace if available)

## Feature Requests

For feature requests:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and why it's needed
3. **Propose an implementation** if you have ideas
4. **Consider submitting a PR** if you can implement it

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. Please be respectful and inclusive in all interactions.

## Getting Help

- **Documentation**: https://docs.ainative.studio/sdk/python
- **Discord**: https://discord.gg/ainative
- **Issues**: https://github.com/AINative-Studio/python-sdk/issues

Thank you for contributing to AINative! 🚀