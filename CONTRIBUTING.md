# Contributing to TTV Pipeline

Thank you for your interest in contributing to the TTV (Text-to-Video) pipeline project!

## Branch Naming Convention

Follow this naming convention for feature branches:

- `feature/parser` - Parser and data schema work
- `feature/visual-gen` - Visual generation work
- `feature/audio-devops` - Audio synthesis and DevOps work
- `feature/integration` - Integration and orchestration work
- `bugfix/<description>` - Bug fixes
- `docs/<description>` - Documentation updates

## Development Workflow

### 1. Setup

Follow the setup instructions in [docs/setup.md](docs/setup.md) to get your environment ready.

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write clear, documented code
- Follow existing code style
- Add unit tests for new functionality
- Update documentation as needed

### 4. Run Tests

Before committing, ensure all tests pass:

```bash
# Activate virtual environment first
pytest -q tests/
```

### 5. Commit Changes

Write clear commit messages:

```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what and why, not how.
```

### 6. Pull Request Checklist

Before submitting a PR, ensure:

- [ ] All tests pass (`pytest -q tests/`)
- [ ] End-to-end demo runs successfully (`python run_demo.py --demo`)
- [ ] Code follows existing style
- [ ] Documentation updated (if needed)
- [ ] No large binary files committed
- [ ] Branch name follows convention

## Code Style

- Use Python 3.10+ features
- Follow PEP 8 style guide
- Use type hints where helpful
- Write docstrings for public functions
- Keep functions focused and small

## Testing Guidelines

### Unit Tests

- One test file per module: `tests/test_<module>.py`
- Test normal cases, edge cases, and error cases
- Use descriptive test function names
- Use pytest fixtures for common setup

### Integration Tests

- Test full pipeline in `tests/test_end_to_end.py`
- Ensure tests work with fallback components (no external models)
- Keep test execution time reasonable (< 2 minutes)

## Project Structure

```
TTV_Final/
├── src/
│   ├── pipeline/      # Core pipeline modules
│   ├── cli.py         # CLI entry point
│   └── api.py         # API module
├── tests/             # Test files
├── data/              # Sample scripts and data
├── assets/            # Visual templates and assets
├── docs/              # Documentation
├── docker/            # Docker configuration
└── infra/             # Infrastructure configs
```

## Areas for Contribution

### High Priority

- Improve visual generation quality (better PIL templates)
- Add more script format support (Fountain, Final Draft)
- Performance optimizations (parallel processing)
- Better error messages and validation

### Medium Priority

- Additional TTS voices and languages
- Video effects and transitions
- Subtitle generation
- Batch processing support

### Documentation

- Tutorials and examples
- API documentation
- Architecture diagrams
- Video tutorials

## Questions?

If you have questions or need clarification:
1. Check existing documentation in `docs/`
2. Review existing code and tests
3. Make reasonable assumptions and document them

## License

This project uses free/open-source tools only. Ensure any contributions maintain this principle (no paid APIs or services).
