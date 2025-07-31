# Contributing to Telegram Media Downloader

Thank you for your interest in contributing to the Telegram Media Downloader project! This document provides guidelines and information for contributors.

## Table of Contents

- Getting Started
- Development Setup
- Code Style
- Testing
- Submitting Changes
- Feature Requests
- Bug Reports
- Code of Conduct

## Getting Started

1. Fork the repository
   ```bash
   git clone https://github.com/1BitCode-Com/telegram-media-downloader.git
   cd telegram-media-downloader
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. Install development dependencies
   ```bash
   pip install flake8 pytest black
   ```

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Telegram API credentials (for testing)

### Environment Variables

Create a .env file for development:

```
# .env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TEST_TARGET=@test_group
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python test_downloader.py

# Run with coverage
python -m pytest --cov=telegram_media_downloader
```

## Code Style

We follow PEP 8 style guidelines with some modifications:

### Python Code Style

- Use 4 spaces for indentation
- Maximum line length: 127 characters
- Use snake_case for variables and functions
- Use PascalCase for classes
- Use UPPER_CASE for constants

### Code Formatting

We use black for code formatting:

```bash
# Format all Python files
black .

# Format specific file
black telegram_media_downloader.py
```

### Linting

We use flake8 for linting:

```bash
# Run flake8
flake8 .

# Run with specific configuration
flake8 --max-line-length=127 --ignore=E203,W503
```

## Testing

### Writing Tests

1. Test Structure
   ```python
   def test_function_name():
       """Test description"""
       # Arrange
       expected = "expected_value"
       
       # Act
       result = function_to_test()
       
       # Assert
       assert result == expected
   ```

2. Async Tests
   ```python
   import pytest
   
   @pytest.mark.asyncio
   async def test_async_function():
       """Test async function"""
       result = await async_function()
       assert result is not None
   ```

3. Mocking
   ```python
   from unittest.mock import patch, MagicMock
   
   def test_with_mock():
       with patch('module.function') as mock_func:
           mock_func.return_value = "mocked_value"
           result = function_under_test()
           assert result == "mocked_value"
   ```

### Test Categories

- Unit Tests: Test individual functions and classes
- Integration Tests: Test component interactions
- End-to-End Tests: Test complete workflows

## Submitting Changes

### Pull Request Process

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. Test your changes
   ```bash
   python -m pytest
   python test_downloader.py
   ```

4. Commit your changes
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. Push to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request
   - Use the PR template
   - Describe your changes clearly
   - Link any related issues

### Commit Message Format

We use conventional commit messages:

type(scope): description

[optional body]

[optional footer]

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Test changes
- chore: Maintenance tasks

Examples:
```
feat(downloader): add support for video downloads
fix(state): resolve resume download issue
docs(readme): update installation instructions
```

## Feature Requests

### Before Submitting

1. Check existing issues to avoid duplicates
2. Search the codebase to see if the feature exists
3. Consider the scope - is it within the project's goals?

### Submitting a Feature Request

Use the feature request template and include:

- Clear description of the feature
- Use case - why is this needed?
- Proposed implementation (if you have ideas)
- Alternatives considered (if any)

## Bug Reports

### Before Submitting

1. Check existing issues for similar bugs
2. Test with latest version from main branch
3. Try to reproduce the issue consistently

### Submitting a Bug Report

Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and logs
- Minimal reproduction case (if possible)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Be collaborative and constructive
- Be professional in all interactions
- Be helpful to newcomers

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other unethical or unprofessional conduct

### Enforcement

Violations will be addressed by project maintainers through:

1. Warning and education
2. Temporary restrictions
3. Permanent removal if necessary

## Getting Help

### Communication Channels

- GitHub Issues: For bugs and feature requests
- GitHub Discussions: For questions and general discussion
- Pull Requests: For code contributions

### Resources

- Python Documentation: https://docs.python.org/
- Telethon Documentation: https://docs.telethon.dev/
- PEP 8 Style Guide: https://www.python.org/dev/peps/pep-0008/

## Recognition

Contributors will be recognized in:

- README.md contributors section
- CHANGELOG.md for significant contributions
- GitHub contributors page

Thank you for contributing to Telegram Media Downloader! 