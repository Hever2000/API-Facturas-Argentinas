# Contributing to ZenithOCR

Thank you for your interest in contributing!

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/zenith-ocr.git`
3. Create a feature branch: `git checkout -b feature/your-feature`

## Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Run formatting before committing:
  ```bash
  black src/ --line-length 100
  isort src/
  ```

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/
```

## Commit Messages

Use conventional commits:

- `feat: add new feature`
- `fix: bug fix`
- `docs: update documentation`
- `refactor: code refactoring`
- `test: add tests`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update the CHANGELOG if applicable
5. Request review

## Questions?

Open an issue for questions about contributing.
