# Gesture Media Control 🎮

An advanced hand gesture-based media control system using computer vision and machine learning. Control your system's volume, playback, and brightness through intuitive hand gestures detected via webcam.

## Features

- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand landmark detection
- **Gesture Recognition**: Supports multiple gestures for media control
- **Volume Control**: Smooth thumb-index finger distance-based volume adjustment
- **Media Playback**: Play/pause, next/previous track controls
- **Mute/Unmute**: Toggle system audio with fist/open hand gestures
- **Brightness Control**: Adjust screen brightness with open palm gesture
- **Visual Feedback**: Real-time skeleton overlay and gesture feedback
- **Performance Optimized**: Frame skipping and smoothing algorithms
- **Cross-platform**: Supports Windows, macOS, and Linux
- **Configurable**: JSON-based configuration with persistence

## Supported Gestures

| Gesture | Action | Description |
|---------|--------|-------------|
| 👌 **OK Gesture** | Play/Pause | Close thumb and index finger |
| ✌️ **Peace Sign** | Next Track | Index and middle fingers up |
| ✊ **Closed Fist** | Mute Toggle | All fingers closed |
| 👐 **Open Hand** | Unmute Toggle | All fingers spread apart |
| 👎 **Thumb Down** | Previous Track | Thumb pointing down |
| 🤏 **Thumb + Index** | Volume Control | Adjust distance for volume |
| 🖐️ **Open Palm** | Brightness | All fingers up, palm open |

## Quick Start

### Prerequisites

- Python 3.8+
- Webcam
- Linux/Windows/macOS

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gesture-media-control.git
   cd gesture-media-control
   ```

2. **Install dependencies:**
   ```bash
   pip install opencv-python mediapipe numpy
   ```

3. **For Windows volume control:**
   ```bash
   pip install pycaw
   ```

4. **Run the application:**
   ```bash
   # Option 1: Direct Python execution
   python main.py

   # Option 2: Using the provided shell script (Linux/macOS)
   ./run.sh
   ```

## Usage

### Basic Operation

1. Launch the application with `python main.py`
2. Position your hand in front of the webcam
3. Make gestures to control media playback
4. Press 'H' to toggle help overlay
5. Press 'Q' or 'ESC' to quit

### Advanced Usage

#### Using the Launch Script

The `run.sh` script provides additional functionality:

```bash
# Run the application
./run.sh run

# Install dependencies
./run.sh install

# Run tests
./run.sh test

# Check system requirements
./run.sh check

# Test camera
./run.sh camera

# Show help
./run.sh help
```

#### Keyboard Shortcuts

- **H**: Toggle help overlay
- **P**: Toggle performance metrics
- **R**: Reset gesture state
- **Q** or **ESC**: Quit application

### Configuration

The application uses `gesture_config.json` for persistent settings. You can modify:

- Camera resolution and FPS
- Performance settings (frame skipping, smoothing)
- Gesture thresholds and cooldowns
- UI colors and layout
- Keyboard shortcuts

## Architecture

```
gesture-media-control/
├── main.py                 # Application entry point
├── app.py                  # Main application logic
├── config/
│   ├── config.py          # Configuration management
│   └── __init__.py        # Config exports
├── ui/
│   └── ui_display.py      # UI rendering and visualization
├── services/
│   ├── gesture_handler.py # Gesture detection and actions
│   └── VolumeController.py # Cross-platform volume control
├── utils/
│   └── performance_optimizer.py # Performance utilities
├── HandTrackingModule.py  # Hand detection wrapper
└── run.sh                 # Linux startup script
```

## Technical Details

### Hand Detection

- **Library**: MediaPipe Hands
- **Model**: BlazePalm + Hand Landmark Model
- **Processing**: 640x480 resolution with optional frame skipping
- **Tracking**: Real-time landmark extraction (21 points per hand)

### Volume Control

- **Linux**: Uses `pactl` (PulseAudio) or `amixer` (ALSA)
- **Windows**: Uses `pycaw` (Windows Core Audio API)
- **macOS**: Uses `osascript` (AppleScript)

### Performance Optimizations

- Frame skipping for reduced CPU usage
- Exponential smoothing for volume control
- Configurable processing intervals
- FPS monitoring and metrics

## Contributing

We welcome contributions! Please follow these steps:

### Development Setup

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Make your changes and test thoroughly**

5. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

6. **Commit your changes:**
   ```bash
   git commit -am 'Add some feature'
   ```

7. **Push to the branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for function parameters and return values
- Add docstrings to all classes and methods
- Keep functions focused and modular

### Testing

- Write unit tests for new features
- Test on multiple platforms (Windows, macOS, Linux)
- Verify gesture recognition accuracy
- Test edge cases and error handling

## Requirements

### System Requirements

- **OS**: Linux, Windows 10+, macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum
- **Storage**: 100MB free space
- **Camera**: USB webcam or built-in camera

### Python Dependencies

```
opencv-python>=4.5.0
mediapipe>=0.8.0
numpy>=1.21.0
pycaw>=0.0.7  # Windows only
```

## Troubleshooting

### Common Issues

**Camera not detected:**
- Check camera permissions
- Try different camera index in config
- Restart the application

**Gestures not recognized:**
- Ensure good lighting
- Position hand clearly in frame
- Adjust gesture thresholds in config

**Volume control not working:**
- Check system audio settings
- Verify PulseAudio/ALSA on Linux
- Install pycaw on Windows

**Performance issues:**
- Increase frame skipping in config
- Close other applications
- Update graphics drivers

### Debug Mode

Run with debug logging:
```bash
python main.py --debug
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **MediaPipe** by Google for hand tracking
- **OpenCV** for computer vision
- **NumPy** for numerical computations
- **PyCAW** for Windows audio control

**Made with ❤️ for gesture-based interaction enthusiasts**
