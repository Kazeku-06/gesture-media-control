# Contributing to Gesture Media Control 🤝

Thank you for your interest in contributing to Gesture Media Control! We welcome contributions from developers of all skill levels. This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- Git
- A webcam for testing
- Basic knowledge of computer vision concepts

### Quick Setup

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/gesture-media-control.git
   cd gesture-media-control
   ```
3. **Set up the development environment** (see below)
4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### 1. Install Dependencies

```bash
# Install core dependencies
pip install opencv-python mediapipe numpy

# Install development dependencies
pip install pytest black flake8 mypy

# Windows users (for volume control)
pip install pycaw
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies in virtual environment
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Run basic tests
python -c "import cv2, mediapipe, numpy; print('Dependencies OK')"

# Run the application
python main.py
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- ** Bug Fixes**: Fix existing issues
- ** New Features**: Add new functionality
- ** Documentation**: Improve docs, tutorials, examples
- ** UI/UX**: Improve user interface and experience
- ** Performance**: Optimize code performance
- ** Testing**: Add or improve tests
- ** Localization**: Add support for new languages

### Finding Issues to Work On

- Check the [Issues](https://github.com/yourusername/gesture-media-control/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Comment on issues you'd like to work on to avoid duplicate work

### Reporting Bugs

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Step-by-step instructions
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, hardware
- **Screenshots/Logs**: If applicable

## Development Guidelines

### Code Style

We follow PEP 8 with some modifications:

```python
# Good: Clear, readable code with type hints
def process_frame(self, frame: np.ndarray) -> np.ndarray:
    """
    Process a video frame for gesture detection.

    Args:
        frame: Input video frame as numpy array

    Returns:
        Processed frame with overlays
    """
    # Implementation here
    pass
```

### Naming Conventions

- **Classes**: `CamelCase` (e.g., `GestureHandler`)
- **Functions/Methods**: `snake_case` (e.g., `detect_gesture`)
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_CONFIG`)
- **Private methods**: `_underscore_prefix` (e.g., `_draw_hand_landmarks`)

### Documentation

- Use docstrings for all classes, methods, and functions
- Follow Google/NumPy docstring format
- Include type hints for parameters and return values
- Document exceptions that may be raised

### Error Handling

```python
# Good: Proper error handling with informative messages
try:
    result = self.detector.process(frame)
except Exception as e:
    logging.error(f"Hand detection failed: {e}")
    return None
```

### Logging

Use appropriate log levels:

```python
import logging

logger = logging.getLogger(__name__)

# Debug: Detailed information for developers
logger.debug("Processing frame with resolution: %dx%d", width, height)

# Info: General information about program execution
logger.info("Hand detector initialized successfully")

# Warning: Something unexpected but not critical
logger.warning("Camera resolution lower than recommended")

# Error: Serious problem that needs attention
logger.error("Failed to initialize volume controller: %s", str(e))
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_gesture_handler.py

# Run with coverage
pytest --cov=gesture_media_control --cov-report=html

# Run tests in verbose mode
pytest -v
```

### Writing Tests

```python
import pytest
import numpy as np
from services.gesture_handler import GestureHandler

class TestGestureHandler:
    def test_initialization(self):
        """Test that GestureHandler initializes correctly."""
        handler = GestureHandler(volume_controller=None)
        assert handler.current_gesture == "No Hand"
        assert handler.gesture_start_time > 0

    def test_gesture_detection_no_hand(self):
        """Test gesture detection when no hand is present."""
        handler = GestureHandler(volume_controller=None)
        result = handler.detect_and_handle_gesture(np.zeros((480, 640, 3), dtype=np.uint8))
        assert result["gesture"] == "No Hand"
        assert not result["action_taken"]
```

### Test Coverage

Aim for high test coverage, especially for:

- Core gesture detection logic
- Error handling paths
- Cross-platform compatibility
- Edge cases and boundary conditions

## Submitting Changes

### 1. Commit Guidelines

Follow conventional commit format:

```bash
# Good commit messages
git commit -m "feat: add brightness control gesture"
git commit -m "fix: resolve skeleton scaling issue"
git commit -m "docs: update gesture recognition tutorial"
git commit -m "refactor: optimize frame processing pipeline"

# Bad commit messages
git commit -m "fixed bug"
git commit -m "updated code"
git commit -m "changes"
```

### 2. Pull Request Process

1. **Ensure your code passes all tests:**
   ```bash
   pytest
   flake8 .
   mypy .
   ```

2. **Update documentation** if needed

3. **Create a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Screenshots/videos for UI changes
   - Reference to any related issues

4. **Wait for review** and address any feedback

### 3. PR Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] Cross-platform testing done

## Screenshots (if applicable)
Add screenshots or videos demonstrating the changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes
```

## Community

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Pull Request Comments**: For code review discussions

### Getting Help

- Check existing issues and documentation first
- Use clear, descriptive titles for new issues
- Provide as much context as possible
- Be patient and respectful when asking for help

### Recognition

Contributors will be recognized in:

- The project's README.md contributors section
- Release notes for significant contributions
- GitHub's contributor insights

## Development Workflow

1. **Choose an issue** or create one
2. **Fork and clone** the repository
3. **Create a feature branch**
4. **Make changes** following guidelines
5. **Write tests** for new functionality
6. **Test thoroughly** on multiple platforms
7. **Commit** with clear messages
8. **Push** to your fork
9. **Create a Pull Request**
10. **Address feedback** from reviewers
11. **Merge** when approved

## Resources

- [Python Documentation](https://docs.python.org/3/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [MediaPipe Documentation](https://developers.google.com/mediapipe)
- [NumPy Documentation](https://numpy.org/doc/)
- [PEP 8 Style Guide](https://pep8.org/)

---

Thank you for contributing to Gesture Media Control! Your efforts help make gesture-based interaction more accessible and powerful. 🚀
