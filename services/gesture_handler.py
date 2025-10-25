"""
Gesture Handler module for Gesture Media Control
Handles gesture detection, action mapping, and control logic
"""

import time
import math
from typing import Optional, Dict, Any, Callable, List
from config import config, Gestures
from HandTrackingModule import HandDetector
import numpy as np

class GestureAction:
    """
    Represents a gesture action with cooldown and callback
    """

    def __init__(self, name: str, callback: Callable, cooldown: float = Gestures.GESTURE_COOLDOWN):
        self.name = name
        self.callback = callback
        self.cooldown = cooldown
        self.last_triggered = 0

    def can_trigger(self) -> bool:
        """Check if action can be triggered (cooldown check)"""
        return time.time() - self.last_triggered >= self.cooldown

    def trigger(self, *args, **kwargs) -> bool:
        """Trigger the action if cooldown allows"""
        if self.can_trigger():
            self.last_triggered = time.time()
            try:
                self.callback(*args, **kwargs)
                return True
            except Exception as e:
                print(f"Error executing gesture action {self.name}: {e}")
                return False
        return False

class GestureHandler:
    """
    Handles gesture detection and action mapping
    """

    def __init__(self, volume_controller, brightness_controller=None):
        self.volume_controller = volume_controller
        self.brightness_controller = brightness_controller
        self.detector = None
        self.current_gesture = "No Hand"
        self.last_gesture = "No Hand"
        self.gesture_start_time = 0
        self.volume_smoothing_factor = config.get('performance.smoothing_factor')
        self.smooth_volume = volume_controller.get_volume()

        # Gesture action mappings
        self.actions = {
            "OK": GestureAction("Play/Pause", self._action_play_pause),
            "Peace": GestureAction("Next Track", self._action_next_track),
            "Mute": GestureAction("Mute Toggle", self._action_mute_toggle),
            "Unmute": GestureAction("Unmute Toggle", self._action_unmute_toggle),
            "Previous": GestureAction("Previous Track", self._action_prev_track),
            "Brightness": GestureAction("Brightness Control", self._action_brightness_control)
        }

        # Gesture state tracking
        self.volume_control_active = False
        self.brightness_control_active = False
        self.last_volume_distance = 0

        print("GestureHandler initialized")

    def set_detector(self, detector: HandDetector) -> None:
        """Set the hand detector instance"""
        self.detector = detector

    def detect_and_handle_gesture(self, img) -> Dict[str, Any]:
        """
        Main gesture detection and handling method
        Returns gesture info and any actions taken
        """
        if not self.detector or not self.detector.available:
            return {"gesture": "No Hand", "action_taken": False, "details": {}}

        # Get current gesture
        gesture = self.detector.detect_gesture()
        self.current_gesture = gesture

        action_taken = False
        details = {}

        # Handle continuous gestures (volume/brightness control)
        if gesture == "Volume Control":
            action_taken, vol_details = self._handle_volume_control(img)
            details.update(vol_details)
        elif gesture == "Brightness" and self.brightness_controller:
            action_taken, bright_details = self._handle_brightness_control(img)
            details.update(bright_details)
        else:
            # Reset continuous gesture states
            self.volume_control_active = False
            self.brightness_control_active = False

        # Handle discrete gestures (play/pause, etc.)
        if gesture in self.actions and gesture != self.last_gesture:
            if self.actions[gesture].trigger():
                action_taken = True
                details["discrete_action"] = gesture

        # Track gesture changes
        if gesture != self.last_gesture:
            self.gesture_start_time = time.time()
            self.last_gesture = gesture

        return {
            "gesture": gesture,
            "action_taken": action_taken,
            "details": details,
            "gesture_duration": time.time() - self.gesture_start_time
        }

    def _handle_volume_control(self, img) -> tuple[bool, Dict[str, Any]]:
        """Handle volume control gesture"""
        if not self.detector.landmarks_list:
            return False, {}

        # Calculate distance between thumb and index finger
        length, img, info = self.detector.find_distance(4, 8, img, draw=False)

        # Apply distance smoothing to reduce jitter
        if self.last_volume_distance == 0:
            self.last_volume_distance = length
        else:
            self.last_volume_distance = (self.last_volume_distance * 0.7 + length * 0.3)

        # Convert distance to volume
        min_dist, max_dist = config.volume_distance_range
        volume = np.interp(self.last_volume_distance, [min_dist, max_dist], [0, 100])
        volume = max(0, min(100, volume))

        # Apply smoothing
        self.smooth_volume = (self.smooth_volume * (1 - self.volume_smoothing_factor) +
                            volume * self.volume_smoothing_factor)

        # Set volume
        self.volume_controller.set_volume(int(self.smooth_volume))
        self.volume_control_active = True

        return True, {
            "volume_distance": self.last_volume_distance,
            "raw_volume": volume,
            "smooth_volume": self.smooth_volume,
            "volume_set": int(self.smooth_volume)
        }

    def _handle_brightness_control(self, img) -> tuple[bool, Dict[str, Any]]:
        """Handle brightness control gesture"""
        if not self.brightness_controller or not self.detector.landmarks_list:
            return False, {}

        # For brightness, we can use the same distance calculation
        # but map it to brightness levels instead
        length, img, info = self.detector.find_distance(4, 8, img, draw=False)

        # Smooth the distance
        if not hasattr(self, 'last_brightness_distance'):
            self.last_brightness_distance = length
        else:
            self.last_brightness_distance = (self.last_brightness_distance * 0.7 + length * 0.3)

        # Convert to brightness (0-100)
        min_dist, max_dist = config.volume_distance_range  # Reuse same range
        brightness = np.interp(self.last_brightness_distance, [min_dist, max_dist], [0, 100])
        brightness = max(0, min(100, brightness))

        # Set brightness
        self.brightness_controller.set_brightness(int(brightness))
        self.brightness_control_active = True

        return True, {
            "brightness_distance": self.last_brightness_distance,
            "brightness": brightness
        }

    def _action_play_pause(self) -> None:
        """Play/Pause media action"""
        print("Play/Pause triggered")
        # This would integrate with media control library
        # For now, just print - can be extended to control media players

    def _action_next_track(self) -> None:
        """Next track action"""
        print("Next track triggered")
        # Media control integration

    def _action_prev_track(self) -> None:
        """Previous track action"""
        print("Previous track triggered")
        # Media control integration

    def _action_mute_toggle(self) -> None:
        """Mute toggle action"""
        print("Mute toggle triggered")
        # Toggle mute using volume controller
        try:
            self.volume_controller.toggle_mute()
        except Exception as e:
            print(f"Error toggling mute: {e}")

    def _action_unmute_toggle(self) -> None:
        """Unmute toggle action"""
        print("Unmute toggle triggered")
        # Toggle mute using volume controller (same as mute toggle)
        try:
            self.volume_controller.toggle_mute()
        except Exception as e:
            print(f"Error toggling unmute: {e}")

    def _action_brightness_control(self) -> None:
        """Brightness control action (continuous)"""
        # This is handled in _handle_brightness_control
        pass

    def get_gesture_info(self) -> Dict[str, Any]:
        """Get current gesture information"""
        return {
            "current_gesture": self.current_gesture,
            "gesture_duration": time.time() - self.gesture_start_time,
            "volume_control_active": self.volume_control_active,
            "brightness_control_active": self.brightness_control_active,
            "smooth_volume": self.smooth_volume
        }

    def reset_state(self) -> None:
        """Reset gesture handler state"""
        self.current_gesture = "No Hand"
        self.last_gesture = "No Hand"
        self.gesture_start_time = time.time()
        self.volume_control_active = False
        self.brightness_control_active = False
        self.smooth_volume = self.volume_controller.get_volume()

# Enhanced gesture detection methods for HandDetector
def detect_mute_gesture(self) -> str:
    """Detect mute gesture (closed fist)"""
    if not self.landmarks_list or len(self.landmarks_list) < 21:
        return "Unknown"

    fingers = self.fingers_up()
    if not fingers:
        return "Unknown"

    # All fingers down (closed fist)
    if sum(fingers) == 0:
        return "Mute"
    return "Unknown"

def detect_previous_gesture(self) -> str:
    """Detect previous track gesture (thumb down)"""
    if not self.landmarks_list or len(self.landmarks_list) < 21:
        return "Unknown"

    fingers = self.fingers_up()
    if not fingers:
        return "Unknown"

    # Only thumb down, others up (or thumb pointing down)
    thumb_tip = self.landmarks_list[4]
    thumb_base = self.landmarks_list[2]

    # Check if thumb is pointing down
    if thumb_tip[2] > thumb_base[2] and sum(fingers[1:]) >= 3:  # Thumb down, others up
        return "Previous"
    return "Unknown"

def detect_brightness_gesture(self) -> str:
    """Detect brightness control gesture (open palm)"""
    if not self.landmarks_list or len(self.landmarks_list) < 21:
        return "Unknown"

    fingers = self.fingers_up()
    if not fingers:
        return "Unknown"

    # All fingers up (open palm)
    if sum(fingers) == 5:
        return "Brightness"
    return "Unknown"

def detect_unmute_gesture(self) -> str:
    """Detect unmute gesture (open hand/palm spread)"""
    if not self.landmarks_list or len(self.landmarks_list) < 21:
        return "Unknown"

    fingers = self.fingers_up()
    if not fingers:
        return "Unknown"

    # All fingers spread out (open hand) - similar to brightness but different context
    # For unmute, we want a more relaxed open hand gesture
    if sum(fingers) >= 4:  # At least 4 fingers up (allowing some flexibility)
        # Check if fingers are spread apart (not close together like OK gesture)
        # Calculate distances between finger tips to ensure they're spread
        try:
            # Check distance between index and middle finger tips
            dist_im, _, _ = self.find_distance(8, 12, draw=False)
            # Check distance between middle and ring finger tips
            dist_mr, _, _ = self.find_distance(12, 16, draw=False)

            # If fingers are spread apart (distance > threshold), it's unmute
            if dist_im > 50 and dist_mr > 50:  # Adjust threshold as needed
                return "Unmute"
        except:
            # Fallback: if distance calculation fails, just check finger count
            if sum(fingers) == 5:
                return "Unmute"

    return "Unknown"

# Monkey patch the HandDetector class to add new gesture methods
HandDetector.detect_mute_gesture = detect_mute_gesture
HandDetector.detect_previous_gesture = detect_previous_gesture
HandDetector.detect_brightness_gesture = detect_brightness_gesture
HandDetector.detect_unmute_gesture = detect_unmute_gesture

# Enhanced detect_gesture method
def enhanced_detect_gesture(self) -> str:
    """Enhanced gesture detection with more gestures"""
    if not self.landmarks_list:
        return "No Hand"

    fingers = self.fingers_up()
    if not fingers:
        return "Unknown"

    # Volume Control Gesture (thumb and index up, others down)
    if fingers[1] == 1 and fingers[0] == 1 and sum(fingers[2:]) == 0:
        return "Volume Control"

    # OK Gesture
    if fingers[1] == 1 and fingers[0] == 0 and sum(fingers[2:]) == 0:
        distance, _, _ = self.find_distance(4, 8, draw=False)
        if distance < config.get('gestures.ok_distance_threshold'):
            return "OK"

    # Peace Gesture
    if fingers[1] == 1 and fingers[2] == 1 and sum(fingers[3:]) == 0 and fingers[0] == 0:
        return "Peace"

    # New gestures
    mute = self.detect_mute_gesture()
    if mute != "Unknown":
        return mute

    prev = self.detect_previous_gesture()
    if prev != "Unknown":
        return prev

    bright = self.detect_brightness_gesture()
    if bright != "Unknown":
        return bright

    unmute = self.detect_unmute_gesture()
    if unmute != "Unknown":
        return unmute

    return "Unknown"

# Replace the original detect_gesture method
HandDetector.detect_gesture = enhanced_detect_gesture
