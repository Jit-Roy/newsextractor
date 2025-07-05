# Contributing to NewsExtractor

We love your input! We want to make contributing to NewsExtractor as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/Jit-Roy/newsextractor.git
cd newsextractor
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

4. Set up pre-commit hooks (optional but recommended):
```bash
pre-commit install
```

## Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **flake8** for linting
- **mypy** for type checking

Run these before submitting a PR:
```bash
black .
flake8 .
mypy .
```

## Testing

We use pytest for testing. Run the test suite with:
```bash
pytest tests/
```

For coverage reports:
```bash
pytest --cov=newsextractor tests/
```

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/Jit-Roy/newsextractor/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/Jit-Roy/newsextractor/issues/new).

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Feature Requests

We welcome feature requests! Please provide:

- A clear description of the feature
- Why this feature would be useful
- How it should work
- Any examples or mockups if applicable

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
