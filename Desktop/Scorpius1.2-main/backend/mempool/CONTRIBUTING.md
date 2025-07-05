# Contributing to Elite Mempool System

Thank you for your interest in contributing to the Elite Mempool System! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Performance Considerations](#performance-considerations)
- [Security Guidelines](#security-guidelines)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend development)
- Docker and Docker Compose
- Git
- PostgreSQL (for local development)
- Redis (for caching and pub/sub)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/elite-mempool-system.git
   cd elite-mempool-system
   ```

## Development Environment

### Local Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r config/config/requirements-dev.txt
   pip install -r requirements-analytics.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start services with Docker:**
   ```bash
   docker-compose up -d postgres redis kafka
   ```

5. **Run database migrations:**
   ```bash
   python -m alembic upgrade head
   ```

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up

# Start only development services
docker-compose up postgres redis kafka

# Run tests in container
docker-compose run --rm api pytest
```

## Contributing Guidelines

### Types of Contributions

- **Bug Fixes**: Fix issues in existing code
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Performance**: Optimize existing code
- **Tests**: Add or improve test coverage
- **Refactoring**: Improve code structure without changing functionality

### Issue Reporting

Before creating an issue:

1. Check if the issue already exists
2. Use the issue templates provided
3. Include relevant details:
   - OS and environment
   - Python version
   - Error messages and stack traces
   - Steps to reproduce

### Feature Requests

For new features:

1. Check existing feature requests
2. Describe the use case and benefits
3. Consider the impact on existing functionality
4. Provide mockups or examples if applicable

## Pull Request Process

### Before Submitting

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes:**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test your changes:**
   ```bash
   # Run tests
   pytest

   # Run linting
   black . --check
   isort . --check-only
   flake8 .
   mypy .

   # Run security checks
   bandit -r .
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new MEV detection algorithm"
   # Use conventional commit format
   ```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pull Request Requirements

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] PR title follows conventional commit format
- [ ] Description explains the changes and motivation

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- Line length: 100 characters
- Use double quotes for strings
- Use type hints for all functions and methods
- Use docstrings for all public functions, classes, and modules

### Code Formatting

We use the following tools:

```bash
# Format code
black .
isort .

# Check formatting
black . --check
isort . --check-only
flake8 .
mypy .
```

### Documentation Style

- Use Google-style docstrings
- Include type information in docstrings
- Provide examples for complex functions
- Keep line length under 80 characters in docstrings

Example:
```python
async def detect_mev_opportunity(
    self, 
    transaction: MempoolEvent,
    min_profit_usd: float = 1.0
) -> List[MEVOpportunity]:
    """
    Detect MEV opportunities from a mempool transaction.

    Args:
        transaction: The mempool transaction to analyze
        min_profit_usd: Minimum profit threshold in USD

    Returns:
        List of detected MEV opportunities

    Raises:
        ValueError: If transaction data is invalid
        ConnectionError: If unable to fetch required data

    Example:
        >>> detector = MEVDetector(web3, network_id=1)
        >>> opportunities = await detector.detect_mev_opportunity(tx)
        >>> print(f"Found {len(opportunities)} opportunities")
    """
```

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── performance/    # Performance tests
├── fixtures/       # Test fixtures
└── conftest.py     # Pytest configuration
```

### Writing Tests

1. **Unit Tests:**
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution

2. **Integration Tests:**
   - Test component interactions
   - Use test database
   - May be slower

3. **Performance Tests:**
   - Benchmark critical paths
   - Monitor resource usage
   - Regression testing

### Test Guidelines

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestMEVDetector:
    """Test suite for MEV detector functionality."""
    
    @pytest.fixture
    async def detector(self, mock_web3):
        """Create MEV detector instance for testing."""
        return MEVDetector(mock_web3, network_id=1)
    
    async def test_detect_arbitrage_opportunity(self, detector, sample_transaction):
        """Test arbitrage opportunity detection."""
        # Arrange
        expected_profit = 100.0
        
        # Act
        opportunities = await detector.detect_mev_opportunity(sample_transaction)
        
        # Assert
        assert len(opportunities) > 0
        assert opportunities[0].estimated_profit_usd >= expected_profit
    
    async def test_invalid_transaction_raises_error(self, detector):
        """Test that invalid transaction data raises appropriate error."""
        with pytest.raises(ValueError, match="Invalid transaction"):
            await detector.detect_mev_opportunity(None)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_mev_detector.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run performance tests
pytest tests/performance/ -m performance

# Run tests in parallel
pytest -n auto
```

## Documentation

### Types of Documentation

1. **Code Documentation:**
   - Docstrings in code
   - Type hints
   - Inline comments for complex logic

2. **API Documentation:**
   - FastAPI automatic docs
   - Additional examples and use cases

3. **User Documentation:**
   - README.md
   - Setup and configuration guides
   - Troubleshooting guides

4. **Developer Documentation:**
   - Architecture overview
   - Contributing guidelines
   - API reference

### Building Documentation

```bash
# Install documentation dependencies
pip install -r docs/config/config/requirements-dev.txt

# Build documentation
cd docs
make html

# Serve documentation locally
make serve
```

## Performance Considerations

### Critical Performance Areas

1. **Mempool Monitoring:**
   - WebSocket connection efficiency
   - Event processing latency
   - Memory usage for transaction storage

2. **MEV Detection:**
   - Algorithm efficiency
   - Parallel processing
   - Caching strategies

3. **Execution Engine:**
   - Transaction building speed
   - Gas estimation accuracy
   - Bundle submission latency

### Performance Testing

```python
import time
import asyncio
from memory_profiler import profile

@profile
async def benchmark_mev_detection():
    """Benchmark MEV detection performance."""
    start_time = time.time()
    
    # Simulate detection workload
    for i in range(1000):
        await detector.detect_mev_opportunity(sample_transactions[i])
    
    end_time = time.time()
    print(f"Processed 1000 transactions in {end_time - start_time:.2f}s")
```

### Optimization Guidelines

- Use async/await for I/O operations
- Implement connection pooling
- Cache frequently accessed data
- Use appropriate data structures
- Profile before optimizing
- Monitor memory usage

## Security Guidelines

### Security Best Practices

1. **Input Validation:**
   - Validate all user inputs
   - Sanitize data before processing
   - Use type checking

2. **Authentication & Authorization:**
   - Secure API endpoints
   - Implement rate limiting
   - Use proper session management

3. **Private Key Management:**
   - Never log private keys
   - Use environment variables
   - Implement key rotation

4. **Network Security:**
   - Use HTTPS/WSS for all connections
   - Validate SSL certificates
   - Implement connection timeouts

### Security Testing

```bash
# Run security checks
bandit -r .

# Check dependencies for vulnerabilities
safety check

# Run SAST scanning
semgrep --config=auto .
```

## Community

### Getting Help

- **Discord**: Join our Discord server for real-time discussion
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Documentation**: Check our comprehensive docs

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Annual contributor highlights

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the Elite Mempool System! Your contributions help make MEV detection and execution more accessible and efficient for everyone.
