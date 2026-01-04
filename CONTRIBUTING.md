# Contributing to AEE Bot

Thank you for your interest in contributing to AEE Bot! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** before creating a new one
2. **Use the issue templates** when available
3. **Provide detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. **Check the roadmap** in [ROADMAP.md](ROADMAP.md)
2. **Open an issue** with the "enhancement" label
3. **Describe the use case** and benefits
4. **Consider implementation complexity**

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow the coding standards** below
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit the pull request** with a clear description

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- Telegram Bot Token (for testing)

### Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/aee-protocol.git
cd aee-protocol

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your test bot token

# Run the bot
python main.py
```

### Development Tools

```bash
# Install development dependencies
pip install black flake8 pytest pytest-cov mypy

# Code formatting
black aee/ *.py

# Linting
flake8 aee/ *.py

# Type checking
mypy aee/

# Run tests
pytest

# Test coverage
pytest --cov=aee --cov-report=html
```

## 📝 Coding Standards

### Python Style

- Follow **PEP 8** and **PEP 257**
- Use **Black** for code formatting
- Maximum line length: **88 characters**
- Use **type hints** for all functions and methods

### Code Organization

```python
"""
Module docstring explaining the purpose of this module.
"""

import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class ExampleClass:
    """Brief description of the class."""
    
    def __init__(self, param: str) -> None:
        """Initialize the example.
        
        Args:
            param: Description of the parameter
        """
        self.param = param
    
    def method(self, value: int) -> Optional[str]:
        """Process the value and return result.
        
        Args:
            value: The integer to process
            
        Returns:
            Processed string or None if error
            
        Raises:
            ValueError: If value is invalid
        """
        try:
            return str(value * 2)
        except Exception as e:
            logger.exception(f"Error processing value: {e}")
            return None
```

### Logging Standards

- Use the module-level logger: `logger = logging.getLogger(__name__)`
- Log levels:
  - `DEBUG`: Detailed execution information
  - `INFO`: Important events and successes
  - `WARNING`: Recoverable issues and validation failures
  - `ERROR`: Exceptions and system errors
- Include relevant context in log messages

### Error Handling

```python
try:
    # Operation that might fail
    result = some_operation()
except ValueError as e:
    logger.warning(f"Validation failed: {e}")
    # Handle validation error
except SQLAlchemyError as e:
    logger.exception(f"Database error: {e}")
    # Handle database error
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    # Handle unexpected error
    raise
```

### Database Operations

```python
def database_operation(param: str) -> Model:
    """Perform database operation with proper session handling."""
    session = None
    try:
        session = DatabaseManager.get_session()
        
        # Perform operation
        result = session.query(Model).filter_by(field=param).first()
        
        logger.info(f"Database operation successful: {result}")
        return result
        
    except Exception as e:
        logger.exception(f"Database operation failed: {e}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/
│   ├── test_database.py
│   ├── test_certificate.py
│   └── test_telegram_bot.py
├── integration/
│   ├── test_bot_flow.py
│   └── test_database_integration.py
└── fixtures/
    ├── sample_files/
    └── test_data.json
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from aee.database import DatabaseManager

class TestDatabaseManager:
    """Test cases for DatabaseManager."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    def test_add_preservation_success(self, mock_session):
        """Test successful preservation addition."""
        # Arrange
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        
        # Act
        with patch('aee.database.DatabaseManager.get_session', return_value=mock_session):
            result = DatabaseManager.add_preservation(
                file_hash="abcd1234",
                file_name="test.txt",
                mime_type="text/plain",
                file_size=100,
                user_id="123456"
            )
        
        # Assert
        assert result is not None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    def test_add_preservation_duplicate_hash(self, mock_session):
        """Test handling of duplicate hash."""
        # Arrange
        mock_session.query.return_value.filter_by.return_value.first.return_value = Mock()
        
        # Act & Assert
        with patch('aee.database.DatabaseManager.get_session', return_value=mock_session):
            with pytest.raises(ValueError, match="El archivo ya ha sido preservado"):
                DatabaseManager.add_preservation(
                    file_hash="abcd1234",
                    file_name="test.txt",
                    mime_type="text/plain",
                    file_size=100,
                    user_id="123456"
                )
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_database.py

# Run with coverage
pytest --cov=aee --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_database.py::TestDatabaseManager::test_add_preservation_success
```

## 📖 Documentation

### Code Documentation

- All public functions and classes must have docstrings
- Use Google-style or NumPy-style docstrings
- Include type hints in function signatures

### README Updates

- Update installation instructions if dependencies change
- Add new features to the features list
- Update configuration examples
- Keep version information current

### API Documentation

- Document new API endpoints in SPECIFICATION.md
- Include request/response examples
- Document error conditions
- Update database schema documentation

## 🔄 Release Process

### Version Bump

1. Update version in `aee/__init__.py`
2. Update version in README.md badges
3. Update CHANGELOG.md
4. Create git tag: `git tag v3.1.0`

### Pre-release Checklist

- [ ] All tests pass
- [ ] Code coverage >90%
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Security scan passed

### Release Steps

1. **Create release branch**: `git checkout -b release/v3.1.0`
2. **Update version numbers**
3. **Update documentation**
4. **Run full test suite**
5. **Merge to main**: `git checkout main && git merge release/v3.1.0`
6. **Create tag**: `git tag v3.1.0`
7. **Push to GitHub**: `git push origin main --tags`
8. **Create GitHub release** with changelog

## 🏷️ Labeling System

### Issue Labels

- `bug`: Bug reports
- `enhancement`: Feature requests
- `documentation`: Documentation issues
- `good first issue`: Good for newcomers
- `help wanted`: Community help requested
- `security`: Security-related issues
- `performance`: Performance improvements

### Pull Request Labels

- `ready for review`: Ready for maintainers to review
- `work in progress`: Still being developed
- `needs changes`: Requires modifications
- `approved`: Approved for merge

## 🚀 Deployment

### Testing Deployment

```bash
# Build Docker image
docker build -t aee-bot:test .

# Run test container
docker run -d --name aee-test -p 8000:8000 aee-bot:test

# Test health check
curl http://localhost:8000/health

# Cleanup
docker stop aee-test && docker rm aee-test
```

### Production Deployment

1. **Environment variables** must be configured
2. **Database migrations** must be applied
3. **Health checks** must pass
4. **Monitoring** must be configured
5. **Backup procedures** must be verified

## 🔐 Security Considerations

### Security Best Practices

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Implement proper error handling
- Use HTTPS for all communications
- Regular security audits

### Reporting Security Issues

1. **Do not use public issues** for security vulnerabilities
2. **Email security@aee-bot.io** with details
3. **Include steps to reproduce** (if safe)
4. **Wait for acknowledgment** before disclosing
5. **Follow responsible disclosure** practices

## 📞 Getting Help

### Community Support

- **GitHub Issues**: For bug reports and feature requests
- **Discord**: For general discussion and questions
- **Documentation**: Check existing docs first

### Maintainer Support

- **Email**: maintainers@aee-bot.io
- **Slack**: Internal team channel
- **Code Review**: Request through GitHub

## 🏆 Recognition

### Contributor Recognition

- Contributors listed in README.md
- Top contributors in GitHub stats
- Annual contributor awards
- Special recognition for security contributions

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Report code of conduct violations

---

## 📋 Quick Contribution Checklist

Before submitting a contribution, ensure:

- [ ] Code follows style guidelines
- [ ] Tests pass with >90% coverage
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Security considerations addressed
- [ ] Performance impact considered
- [ ] Breaking changes documented
- [ ] Backward compatibility maintained

---

Thank you for contributing to AEE Bot! Your contributions help make digital preservation more accessible and secure for everyone.

**For questions**: Join our [Discord community](https://discord.gg/aee-bot) or open an issue.
