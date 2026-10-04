# Contributing to the AINative Python SDK

Thanks for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip and virtualenv
- Git

### Setting Up Your Development Environment

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/python-sdk.git
cd python-sdk
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting

Format your code before committing:
```bash
black ainative/
isort ainative/
mypy ainative/
flake8 ainative/
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=ainative

# Specific module
pytest tests/test_zerodb.py
```

All new features should include tests.

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes — write code following the style guidelines above, add tests, update docs as needed
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`)
4. Push to your fork and open a pull request against this repo

### Pull Request Checklist

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black`, `isort`)
- [ ] Type checking passes (`mypy`)
- [ ] Linting passes (`flake8`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated

## Reporting Bugs

Please include:
1. A clear description of the issue
2. Your environment (Python version, OS, package version)
3. Minimal reproduction code
4. Expected vs. actual behavior
5. Full traceback if applicable

## Feature Requests

Please include the use case, a proposed solution, alternatives considered, and example usage.

## Questions?

- Check the [Documentation](https://docs.ainative.studio/sdk/python)
- Open a [GitHub Issue](https://github.com/AINative-Studio/python-sdk/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see [LICENSE](LICENSE)).
