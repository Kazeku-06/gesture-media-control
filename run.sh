#!/bin/bash

# Gesture Media Control - Easy Launch Script
# Usage: ./run.sh [option]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.7 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 7) else 1)'; then
        print_success "Python $PYTHON_VERSION detected"
    else
        print_error "Python $PYTHON_VERSION is not supported. Please upgrade to Python 3.7 or higher."
        exit 1
    fi
}

# Function to install dependencies
install_deps() {
    print_info "Installing dependencies..."

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi

    if command_exists pip3; then
        pip3 install -r requirements.txt
    elif command_exists pip; then
        pip install -r requirements.txt
    else
        print_error "pip not found. Please install pip first."
        exit 1
    fi

    print_success "Dependencies installed successfully"
}

# Function to check camera
check_camera() {
    print_info "Checking camera availability..."

    python3 -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print('Camera is working')
    else:
        print('Camera opened but cannot read frames')
    cap.release()
else:
    print('Cannot open camera')
    exit(1)
"
}

# Function to run the application
run_app() {
    print_info "Starting Gesture Media Control..."

    if [ ! -f "main.py" ]; then
        print_error "main.py not found!"
        exit 1
    fi

    python3 main.py
}

# Function to run tests
run_tests() {
    print_info "Running tests..."

    if [ ! -f "test_gesture_control.py" ]; then
        print_warning "test_gesture_control.py not found. Creating basic test..."
        cat > test_gesture_control.py << 'EOF'
#!/usr/bin/env python3
"""
Basic tests for Gesture Media Control
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    try:
        import cv2
        print("✓ OpenCV imported successfully")

        import mediapipe as mp
        print("✓ MediaPipe imported successfully")

        import numpy as np
        print("✓ NumPy imported successfully")

        from HandTrackingModule import HandDetector
        print("✓ HandTrackingModule imported successfully")

        from VolumeController import VolumeController
        print("✓ VolumeController imported successfully")

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_hand_detector():
    """Test HandDetector initialization"""
    try:
        from HandTrackingModule import HandDetector
        detector = HandDetector()
        if detector.available:
            print("✓ HandDetector initialized successfully")
            return True
        else:
            print("✗ HandDetector not available")
            return False
    except Exception as e:
        print(f"✗ HandDetector test failed: {e}")
        return False

def test_volume_controller():
    """Test VolumeController initialization"""
    try:
        from VolumeController import VolumeController
        vc = VolumeController()
        print("✓ VolumeController initialized successfully")
        return True
    except Exception as e:
        print(f"✗ VolumeController test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running Gesture Media Control Tests")
    print("=" * 40)

    tests = [
        ("Import Test", test_imports),
        ("Hand Detector Test", test_hand_detector),
        ("Volume Controller Test", test_volume_controller)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
EOF
    fi

    python3 test_gesture_control.py
}

# Function to show help
show_help() {
    echo "Gesture Media Control - Launch Script"
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  run          - Run the application (default)"
    echo "  install      - Install dependencies"
    echo "  test         - Run basic tests"
    echo "  check        - Check system requirements"
    echo "  camera       - Test camera functionality"
    echo "  help         - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh                     # Run the application"
    echo "  ./run.sh install             # Install dependencies"
    echo "  ./run.sh test                # Run tests"
    echo "  ./run.sh check               # Check system"
}

# Main script logic
case "${1:-run}" in
    "run")
        check_python
        run_app
        ;;
    "install")
        check_python
        install_deps
        ;;
    "test")
        check_python
        run_tests
        ;;
    "check")
        check_python
        print_info "System check completed"
        ;;
    "camera")
        check_python
        check_camera
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
