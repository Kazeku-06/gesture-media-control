"""
Main Application class for Gesture Media Control
Handles application lifecycle, initialization, and main loop
"""

import cv2
import numpy as np
import time
import math
import sys
import os
from typing import Optional, Dict, Any
from config import config
from ui.ui_display import UIDisplay
from services.gesture_handler import GestureHandler
from services.VolumeController import VolumeController
from HandTrackingModule import HandDetector
from utils.performance_optimizer import PerformanceOptimizer

class GestureMediaControlApp:
    """
    Main application class for Gesture Media Control
    """

    def __init__(self):
        """Initialize the application"""
        self.running = False
        self.camera = None
        self.detector = None
        self.volume_controller = None
        self.gesture_handler = None
        self.ui_display = None
        self.perf_optimizer = None

        # Application state
        self.show_help = False
        self.show_performance = config.get('ui.show_performance_metrics', False)

        # FPS tracking
        self.prev_time = 0
        self.current_time = 0
        self.fps = 0

        # Keyboard state
        self.last_key_time = 0
        self.key_cooldown = 0.1  # 100ms cooldown

    def initialize(self) -> bool:
        """
        Initialize all application components
        Returns True if initialization successful
        """
        try:
            print("Initializing Gesture Media Control...")

            # Initialize camera
            if not self._init_camera():
                return False

            # Initialize hand detector
            if not self._init_hand_detector():
                return False

            # Initialize volume controller
            if not self._init_volume_controller():
                return False

            # Initialize UI display
            self.ui_display = UIDisplay()

            # Initialize gesture handler
            self.gesture_handler = GestureHandler(self.volume_controller)
            self.gesture_handler.set_detector(self.detector)

            # Initialize performance optimizer
            self.perf_optimizer = PerformanceOptimizer()

            print("✓ All components initialized successfully")
            return True

        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            self.cleanup()
            return False

    def _init_camera(self) -> bool:
        """Initialize camera with optimized settings"""
        try:
            width, height = config.camera_resolution
            self.camera = cv2.VideoCapture(0)

            if not self.camera.isOpened():
                print("✗ Could not open camera")
                return False

            # Set camera properties for performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.camera.set(cv2.CAP_PROP_FPS, config.get('camera.fps'))
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # Test camera
            ret, test_frame = self.camera.read()
            if not ret:
                print("✗ Could not read from camera")
                return False

            print(f"✓ Camera initialized: {width}x{height}")
            return True

        except Exception as e:
            print(f"✗ Camera initialization failed: {e}")
            return False

    def _init_hand_detector(self) -> bool:
        """Initialize hand detector"""
        try:
            self.detector = HandDetector(
                detection_confidence=0.6,
                tracking_confidence=0.5,
                max_hands=1
            )

            if not self.detector.available:
                print("✗ Hand detector not available")
                return False

            print("✓ Hand detector initialized")
            return True

        except Exception as e:
            print(f"✗ Hand detector initialization failed: {e}")
            return False

    def _init_volume_controller(self) -> bool:
        """Initialize volume controller"""
        try:
            self.volume_controller = VolumeController()

            if not self.volume_controller.volume_available:
                print("⚠ Volume control not available - running in simulation mode")
            else:
                print("✓ Volume controller initialized")

            return True

        except Exception as e:
            print(f"✗ Volume controller initialization failed: {e}")
            return False

    def run(self) -> int:
        """
        Main application loop
        Returns exit code (0 for success, 1 for error)
        """
        if not self.initialize():
            return 1

        self.running = True
        self._print_startup_info()

        try:
            while self.running:
                if not self._process_frame():
                    break

            return 0

        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
            return 0
        except Exception as e:
            print(f"\nApplication error: {e}")
            return 1
        finally:
            self.cleanup()

    def _process_frame(self) -> bool:
        """
        Process a single frame
        Returns False if application should exit
        """
        # Read frame from camera
        success, img = self.camera.read()
        if not success:
            print("Failed to read from camera")
            return False

        # Flip image for mirror effect
        img = cv2.flip(img, 1)

        # Calculate FPS
        self.current_time = time.time()
        self.fps = 1 / (self.current_time - self.prev_time) if self.prev_time > 0 else 0
        self.prev_time = self.current_time

        # Process hand detection every frame for smooth skeleton tracking
        img = self.detector.find_hands(img)
        self.detector.find_position(img, draw=False)

        # Handle gestures (use performance optimizer for volume updates if needed)
        gesture_info = self.gesture_handler.detect_and_handle_gesture(img)

        # Update UI
        self._update_display(img, gesture_info)

        # Handle keyboard input
        if not self._handle_keyboard_input():
            return False

        # Show frame
        cv2.imshow("Gesture Media Control (Enhanced)", img)

        return True

    def _update_display(self, img: np.ndarray, gesture_info: Dict[str, Any]) -> None:
        """Update all display elements"""
        # Update pulse animation
        pulse_animation = self.ui_display.update_pulse_animation()

        # Get current volume for display
        current_volume = self.volume_controller.get_volume()

        # Draw UI elements
        self.ui_display.draw_fps_display(img, self.fps)
        self.ui_display.draw_volume_display(img, current_volume, None)  # TODO: Pass smooth bar
        self.ui_display.draw_gesture_status(img, gesture_info["gesture"])

        # Draw gesture-specific information
        if gesture_info["gesture"] == "Volume Control" and "details" in gesture_info:
            details = gesture_info["details"]
            if "volume_distance" in details:
                self.ui_display.draw_volume_control_info(
                    img, details["volume_distance"], details.get("volume_set", current_volume)
                )

        # Draw gesture feedback for discrete actions
        if gesture_info.get("action_taken") and "discrete_action" in gesture_info.get("details", {}):
            center_y = img.shape[0] // 2
            self.ui_display.draw_gesture_feedback(img, gesture_info["details"]["discrete_action"], (0, center_y))

        # Draw animated volume bar
        # Draw hand skeleton overlay
        self.ui_display.draw_hand_skeleton(img, self.detector)
        self.ui_display.draw_animated_volume_bar(img, current_volume, current_volume, pulse_animation)

        # Draw overlays
        self.ui_display.draw_help_overlay(img, self.show_help)

        # Draw performance overlay
        if self.show_performance:
            metrics = {
                "fps": self.fps,
                "avg_fps": self.ui_display.fps_history[-1] if self.ui_display.fps_history else self.fps,
                "min_fps": min(self.ui_display.fps_history) if self.ui_display.fps_history else self.fps,
                "cpu_usage": "N/A"  # TODO: Add CPU monitoring
            }
            self.ui_display.draw_performance_overlay(img, metrics)

        # Draw status info
        status_parts = []
        if config.get('ui.show_fps'):
            status_parts.append(f"FPS: {int(self.fps)}")
        status_parts.append("Press 'H' for help, 'Q' to quit")
        status_text = " | ".join(status_parts)

        self.ui_display.draw_status_info(img, status_text)

    def _handle_keyboard_input(self) -> bool:
        """
        Handle keyboard input
        Returns False if application should exit
        """
        current_time = time.time()
        if current_time - self.last_key_time < self.key_cooldown:
            return True

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            return False

        # Handle other keys
        if key == ord('h'):  # Help toggle
            self.show_help = not self.show_help
            self.last_key_time = current_time
        elif key == ord('p'):  # Performance overlay toggle
            self.show_performance = not self.show_performance
            config.set('ui.show_performance_metrics', self.show_performance)
            self.last_key_time = current_time
        elif key == ord('r'):  # Reset gesture state
            self.gesture_handler.reset_state()
            print("Gesture state reset")
            self.last_key_time = current_time

        return True

    def _print_startup_info(self) -> None:
        """Print startup information and controls"""
        print("\n" + "="*60)
        print("🎮 GESTURE MEDIA CONTROL (ENHANCED VERSION)")
        print("="*60)
        print("✓ Optimized for performance")
        print("✓ Enhanced gesture recognition")
        print("✓ Smooth animations")
        print("✓ Configuration persistence")
        print()
        print("🎯 CONTROLS:")
        print("  Volume Control: Thumb + Index finger")
        print("  Play/Pause:     OK gesture")
        print("  Next Track:     Peace gesture")
        print("  Mute Toggle:    Closed fist")
        print("  Unmute Toggle:  Open hand (spread fingers)")
        print("  Previous Track: Thumb down")
        print("  Brightness:     Open palm")
        print()
        print("⌨️  KEYBOARD SHORTCUTS:")
        print("  H: Toggle help overlay")
        print("  P: Toggle performance metrics")
        print("  R: Reset gesture state")
        print("  Q or ESC: Quit application")
        print("="*60)
        print()

    def cleanup(self) -> None:
        """Clean up application resources"""
        print("Cleaning up resources...")

        if self.camera:
            self.camera.release()

        cv2.destroyAllWindows()

        # Save configuration
        if config.save_config():
            print("✓ Configuration saved")
        else:
            print("⚠ Could not save configuration")

        print("✓ Application closed successfully")

def main():
    """Main entry point"""
    app = GestureMediaControlApp()
    exit_code = app.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
