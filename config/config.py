"""
Configuration file for Gesture Media Control
Contains all constants, settings, and configuration management
"""

import json
import os
from typing import Dict, Any, Tuple

# Color definitions (BGR format for OpenCV)
class Colors:
    """Color constants for UI elements"""
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    CYAN = (255, 255, 0)
    ORANGE = (0, 165, 255)
    PURPLE = (255, 0, 255)
    PINK = (203, 192, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    BLACK = (0, 0, 0)

# Font settings
class Fonts:
    """Font constants for text rendering"""
    FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
    SCALE_SMALL = 0.4
    SCALE_MEDIUM = 0.6
    SCALE_LARGE = 0.8
    THICKNESS_THIN = 1
    THICKNESS_MEDIUM = 2
    THICKNESS_THICK = 3

# Camera settings
class Camera:
    """Camera configuration"""
    WIDTH = 640
    HEIGHT = 480
    FPS = 30
    BUFFER_SIZE = 1

# Performance settings
class Performance:
    """Performance optimization settings"""
    FRAME_SKIP = 2
    VOLUME_UPDATE_INTERVAL = 0.05  # seconds
    PULSE_ANIMATION_SPEED = 0.3
    SMOOTHING_FACTOR = 0.3

# Gesture settings
class Gestures:
    """Gesture detection thresholds and settings"""
    OK_DISTANCE_THRESHOLD = 60
    VOLUME_MIN_DISTANCE = 30
    VOLUME_MAX_DISTANCE = 200
    GESTURE_COOLDOWN = 1.0  # seconds

# UI settings
class UI:
    """UI layout and display settings"""
    VOLUME_BAR_WIDTH = 25
    VOLUME_BAR_HEIGHT = 250
    VOLUME_BAR_MARGIN = 30
    FPS_POSITION = (10, 25)
    VOLUME_POSITION = (10, 55)
    GESTURE_POSITION = (10, 85)
    STATUS_POSITION = (10, 460)

# Volume bar animation settings
class VolumeBar:
    """Volume bar visual settings"""
    ANIMATION_SPEED = 0.2
    PULSE_SIZE = 3
    MARKER_LENGTH_MAJOR = 8
    MARKER_LENGTH_MINOR = 5
    BORDER_THICKNESS = 1
    HIGHLIGHT_HEIGHT_RATIO = 0.1

class Config:
    """
    Main configuration class with persistence support
    """

    CONFIG_FILE = "gesture_config.json"

    # Default configuration
    DEFAULT_CONFIG = {
        "camera": {
            "width": Camera.WIDTH,
            "height": Camera.HEIGHT,
            "fps": Camera.FPS
        },
        "performance": {
            "frame_skip": Performance.FRAME_SKIP,
            "volume_update_interval": Performance.VOLUME_UPDATE_INTERVAL,
            "pulse_animation_speed": Performance.PULSE_ANIMATION_SPEED,
            "smoothing_factor": Performance.SMOOTHING_FACTOR
        },
        "gestures": {
            "ok_distance_threshold": Gestures.OK_DISTANCE_THRESHOLD,
            "volume_min_distance": Gestures.VOLUME_MIN_DISTANCE,
            "volume_max_distance": Gestures.VOLUME_MAX_DISTANCE,
            "gesture_cooldown": Gestures.GESTURE_COOLDOWN
        },
        "ui": {
            "volume_bar_width": UI.VOLUME_BAR_WIDTH,
            "volume_bar_height": UI.VOLUME_BAR_HEIGHT,
            "volume_bar_margin": UI.VOLUME_BAR_MARGIN,
            "show_fps": True,
            "show_performance_metrics": False
        },
        "colors": {
            "volume_bar_low": "green",
            "volume_bar_high": "red",
            "gesture_volume": "cyan",
            "gesture_ok": "orange",
            "gesture_peace": "yellow",
            "gesture_mute": "red",
            "gesture_unmute": "green",
            "gesture_prev": "purple",
            "gesture_brightness": "blue"
        },
        "controls": {
            "enable_keyboard_fallback": True,
            "keyboard_shortcuts": {
                "volume_up": "up",
                "volume_down": "down",
                "mute": "m",
                "play_pause": "space",
                "next_track": "right",
                "prev_track": "left"
            }
        }
    }

    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle missing keys
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()

    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        merged = default.copy()
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'camera.width')"""
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        try:
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            config[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            print(f"Error setting config {key_path}: {e}")
            return False

    # Convenience methods for common settings
    @property
    def camera_resolution(self) -> Tuple[int, int]:
        """Get camera resolution as tuple"""
        return (self.get('camera.width'), self.get('camera.height'))

    @property
    def volume_distance_range(self) -> Tuple[int, int]:
        """Get volume distance range as tuple"""
        return (self.get('gestures.volume_min_distance'), self.get('gestures.volume_max_distance'))

    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get color by name from config"""
        color_map = {
            "green": Colors.GREEN,
            "red": Colors.RED,
            "blue": Colors.BLUE,
            "yellow": Colors.YELLOW,
            "cyan": Colors.CYAN,
            "orange": Colors.ORANGE,
            "purple": Colors.PURPLE,
            "pink": Colors.PINK,
            "white": Colors.WHITE,
            "gray": Colors.GRAY,
            "black": Colors.BLACK
        }
        color_key = self.get(f'colors.{color_name}', 'white')
        return color_map.get(color_key, Colors.WHITE)

# Global config instance
config_instance = Config()
