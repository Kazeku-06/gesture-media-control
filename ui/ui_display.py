"""
UI Display module for Gesture Media Control
Handles all visualization and drawing functions
"""

import cv2
import numpy as np
import math
import time
from typing import Tuple, Optional, List
from config import config, Colors, Fonts, UI, VolumeBar

class UIDisplay:
    """
    Handles all UI rendering and visualization
    """

    def __init__(self):
        """Initialize UI display components"""
        self.pulse_animation = 0
        self.last_pulse_time = time.time()
        self.fps_history = []  # For performance metrics
        self.max_fps_history = 30

    def update_pulse_animation(self) -> float:
        """Update pulse animation for visual effects"""
        current_time = time.time()
        delta_time = current_time - self.last_pulse_time

        if delta_time > 0.05:  # 20 FPS animation
            self.pulse_animation = (self.pulse_animation + 0.3) % (2 * math.pi)
            self.last_pulse_time = current_time

        return self.pulse_animation

    def draw_fps_display(self, img: np.ndarray, fps: float) -> None:
        """Draw FPS display with color coding"""
        if not config.get('ui.show_fps', True):
            return

        # Color code FPS
        if fps > 25:
            fps_color = Colors.GREEN
        elif fps > 15:
            fps_color = Colors.YELLOW
        else:
            fps_color = Colors.RED

        # Add to history for metrics
        self.fps_history.append(fps)
        if len(self.fps_history) > self.max_fps_history:
            self.fps_history.pop(0)

        cv2.putText(img, f'FPS: {int(fps)}', UI.FPS_POSITION,
                   Fonts.FONT, Fonts.SCALE_MEDIUM, fps_color, Fonts.THICKNESS_THIN)

        # Show performance metrics if enabled
        if config.get('ui.show_performance_metrics', False):
            avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
            min_fps = min(self.fps_history) if self.fps_history else 0
            cv2.putText(img, f'Avg: {int(avg_fps)} Min: {int(min_fps)}',
                       (10, UI.FPS_POSITION[1] + 25),
                       Fonts.FONT, Fonts.SCALE_SMALL, Colors.GRAY, Fonts.THICKNESS_THIN)

    def draw_volume_display(self, img: np.ndarray, volume: int, smooth_bar) -> None:
        """Draw volume percentage display"""
        volume_color = config.get_color('gesture_volume')
        cv2.putText(img, f'Volume: {volume}%', UI.VOLUME_POSITION,
                   Fonts.FONT, Fonts.SCALE_MEDIUM, volume_color, Fonts.THICKNESS_THIN)

    def draw_gesture_status(self, img: np.ndarray, gesture: str) -> None:
        """Draw current gesture status with color coding"""
        gesture_colors = {
            "Volume Control": config.get_color('gesture_volume'),
            "OK": config.get_color('gesture_ok'),
            "Peace": config.get_color('gesture_peace'),
            "Mute": config.get_color('gesture_mute'),
            "Unmute": config.get_color('gesture_unmute'),  # Will default to white if not defined
            "Previous": config.get_color('gesture_prev'),
            "Brightness": config.get_color('gesture_brightness'),
            "No Hand": Colors.GRAY,
            "Unknown": Colors.GRAY
        }

        color = gesture_colors.get(gesture, Colors.WHITE)
        cv2.putText(img, f'Gesture: {gesture}', UI.GESTURE_POSITION,
                   Fonts.FONT, Fonts.SCALE_MEDIUM, color, Fonts.THICKNESS_THIN)

    def draw_status_info(self, img: np.ndarray, status_text: str) -> None:
        """Draw status information at bottom of screen"""
        cv2.putText(img, status_text, UI.STATUS_POSITION,
                   Fonts.FONT, Fonts.SCALE_SMALL, Colors.GRAY, Fonts.THICKNESS_THIN)

    def draw_volume_control_info(self, img: np.ndarray, distance: float, volume: int) -> None:
        """Draw detailed volume control information"""
        h, w, _ = img.shape

        # Position for info display
        info_x = w - 150
        info_y = UI.VOLUME_POSITION[1]

        # Background for info
        cv2.rectangle(img, (info_x - 10, info_y - 20), (w - 10, info_y + 60),
                     Colors.DARK_GRAY, -1)
        cv2.rectangle(img, (info_x - 10, info_y - 20), (w - 10, info_y + 60),
                     Colors.GRAY, 1)

        # Info text
        cv2.putText(img, f'Dist: {int(distance)}px', (info_x, info_y),
                   Fonts.FONT, Fonts.SCALE_SMALL, Colors.BLUE, Fonts.THICKNESS_THIN)
        cv2.putText(img, f'Vol: {volume}%', (info_x, info_y + 20),
                   Fonts.FONT, Fonts.SCALE_SMALL, Colors.BLUE, Fonts.THICKNESS_THIN)

        # Add pulse effect
        pulse_scale = 0.8 + 0.2 * math.sin(self.pulse_animation)
        pulse_thickness = max(1, int(Fonts.THICKNESS_THIN * pulse_scale))

        cv2.rectangle(img, (info_x - 10, info_y - 20), (w - 10, info_y + 60),
                     Colors.BLUE, pulse_thickness)

    def draw_gesture_feedback(self, img: np.ndarray, gesture: str, center_position: Tuple[int, int]) -> None:
        """Draw visual feedback for gesture activation"""
        feedback_messages = {
            "OK": "PLAY/PAUSE",
            "Peace": "NEXT TRACK",
            "Mute": "MUTE TOGGLE",
            "Unmute": "UNMUTE TOGGLE",
            "Previous": "PREV TRACK",
            "Brightness": "BRIGHTNESS"
        }

        if gesture in feedback_messages:
            message = feedback_messages[gesture]
            text_size = cv2.getTextSize(message, Fonts.FONT, Fonts.SCALE_MEDIUM, Fonts.THICKNESS_MEDIUM)[0]

            # Center the message
            text_x = (img.shape[1] - text_size[0]) // 2
            text_y = center_position[1]

            # Background highlight
            padding = 10
            cv2.rectangle(img, (text_x - padding, text_y - 25),
                         (text_x + text_size[0] + padding, text_y + 5),
                         Colors.BLACK, -1)

            # Border with gesture color
            gesture_color = config.get_color(f'gesture_{gesture.lower()}')
            cv2.rectangle(img, (text_x - padding, text_y - 25),
                         (text_x + text_size[0] + padding, text_y + 5),
                         gesture_color, 2)

            # Text
            cv2.putText(img, message, (text_x, text_y),
                       Fonts.FONT, Fonts.SCALE_MEDIUM, gesture_color, Fonts.THICKNESS_MEDIUM)

    def draw_animated_volume_bar(self, img: np.ndarray, display_volume: int,
                               target_volume: int, pulse_animation: float) -> None:
        """Draw animated volume bar with smooth transitions and effects"""
        h, w, _ = img.shape

        # Volume bar dimensions
        bar_width = config.get('ui.volume_bar_width')
        bar_height = config.get('ui.volume_bar_height')
        margin = config.get('ui.volume_bar_margin')

        bar_x = margin
        bar_y = (h - bar_height) // 2

        # Background bar with subtle gradient
        for i in range(bar_height):
            ratio = i / bar_height
            intensity = int(255 * (0.2 + 0.1 * ratio))  # Subtle gradient
            cv2.line(img, (bar_x, bar_y + i), (bar_x + bar_width, bar_y + i),
                    (intensity, intensity, intensity), 1)

        # Volume fill with gradient colors
        fill_height = int((display_volume / 100) * bar_height)
        fill_y = bar_y + (bar_height - fill_height)

        if fill_height > 0:
            for i in range(fill_height):
                ratio = i / fill_height if fill_height > 0 else 0
                height_pos = fill_y + i

                # Color gradient based on volume level
                if display_volume < 50:
                    # Green to yellow gradient
                    green = 255
                    red = int(255 * (ratio * 2))
                    blue = 0
                else:
                    # Yellow to red gradient
                    green = int(255 * (1 - (ratio - 0.5) * 2))
                    red = 255
                    blue = 0

                color = (blue, green, red)
                cv2.line(img, (bar_x, height_pos), (bar_x + bar_width, height_pos), color, 1)

        # Highlight effect on top
        if fill_height > 0:
            highlight_height = max(3, int(fill_height * VolumeBar.HIGHLIGHT_HEIGHT_RATIO))
            for i in range(highlight_height):
                alpha = 1.0 - (i / highlight_height)
                highlight_color = (int(255 * alpha), int(255 * alpha), int(255 * alpha))
                pos = fill_y + i
                if pos < bar_y + bar_height:
                    cv2.line(img, (bar_x, pos), (bar_x + bar_width, pos), highlight_color, 1)

        # 3D border effect
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                     Colors.GRAY, VolumeBar.BORDER_THICKNESS)
        cv2.rectangle(img, (bar_x - 1, bar_y - 1),
                     (bar_x + bar_width + 1, bar_y + bar_height + 1),
                     Colors.DARK_GRAY, VolumeBar.BORDER_THICKNESS)

        # Percentage markers
        for percent in [0, 25, 50, 75, 100]:
            marker_y = bar_y + bar_height - int((percent / 100) * bar_height)
            marker_color = Colors.WHITE if percent % 50 == 0 else Colors.GRAY
            marker_length = VolumeBar.MARKER_LENGTH_MAJOR if percent % 50 == 0 else VolumeBar.MARKER_LENGTH_MINOR

            # Left markers
            cv2.line(img, (bar_x - marker_length, marker_y), (bar_x, marker_y),
                    marker_color, 1)
            # Right markers
            cv2.line(img, (bar_x + bar_width, marker_y),
                    (bar_x + bar_width + marker_length, marker_y),
                    marker_color, 1)

            # Text labels for major markers
            if percent % 50 == 0:
                cv2.putText(img, f'{percent}%',
                           (bar_x + bar_width + 10, marker_y + 5),
                           Fonts.FONT, Fonts.SCALE_SMALL, Colors.GRAY, Fonts.THICKNESS_THIN)

        # Target volume indicator (pulsing when different from display)
        if abs(display_volume - target_volume) > 2:
            target_height = bar_y + bar_height - int((target_volume / 100) * bar_height)
            pulse_scale = 0.8 + 0.2 * math.sin(pulse_animation)
            pulse_size = max(1, int(VolumeBar.PULSE_SIZE * pulse_scale))

            cv2.line(img, (bar_x - 5, target_height), (bar_x + bar_width + 5, target_height),
                    Colors.WHITE, pulse_size)

        # Current volume indicator (circle at the top)
        if fill_height > 0:
            current_height = bar_y + bar_height - fill_height
            indicator_radius = 4
            cv2.circle(img, (bar_x + bar_width // 2, current_height),
                      indicator_radius, Colors.WHITE, -1)
            cv2.circle(img, (bar_x + bar_width // 2, current_height),
                      indicator_radius, Colors.BLACK, 1)

    def draw_help_overlay(self, img: np.ndarray, show_help: bool = False) -> None:
        """Draw help overlay with gesture instructions"""
        if not show_help:
            return

        h, w = img.shape[:2]
        overlay_width = 300
        overlay_height = 200
        overlay_x = (w - overlay_width) // 2
        overlay_y = (h - overlay_height) // 2

        # Semi-transparent background
        overlay = img.copy()
        cv2.rectangle(overlay, (overlay_x, overlay_y),
                     (overlay_x + overlay_width, overlay_y + overlay_height),
                     (0, 0, 0), -1)
        cv2.addWeighted(img, 0.7, overlay, 0.3, 0, img)

        # Help content
        help_lines = [
            "GESTURE CONTROLS:",
            "Thumb + Index: Volume Control",
            "OK Gesture: Play/Pause",
            "Peace: Next Track",
            "Fist: Mute Toggle",
            "Open Hand: Unmute Toggle",
            "Thumb Down: Previous Track",
            "Open Palm: Brightness",
            "",
            "Press 'H' to hide, 'Q' to quit"
        ]

        y_offset = overlay_y + 30
        for line in help_lines:
            cv2.putText(img, line, (overlay_x + 20, y_offset),
                       Fonts.FONT, Fonts.SCALE_SMALL, Colors.WHITE, Fonts.THICKNESS_THIN)
            y_offset += 20

        # Border
        cv2.rectangle(img, (overlay_x, overlay_y),
                     (overlay_x + overlay_width, overlay_y + overlay_height),
                     Colors.WHITE, 2)

    def draw_performance_overlay(self, img: np.ndarray, metrics: dict) -> None:
        """Draw performance metrics overlay"""
        if not config.get('ui.show_performance_metrics', False):
            return

        h, w = img.shape[:2]
        overlay_width = 250
        overlay_height = 150
        overlay_x = w - overlay_width - 10
        overlay_y = 10

        # Semi-transparent background
        cv2.rectangle(img, (overlay_x, overlay_y),
                     (overlay_x + overlay_width, overlay_y + overlay_height),
                     (0, 0, 0), -1)
        cv2.rectangle(img, (overlay_x, overlay_y),
                     (overlay_x + overlay_width, overlay_y + overlay_height),
                     Colors.GRAY, 1)

        # Performance metrics
        metrics_lines = [
            "PERFORMANCE:",
            f"FPS: {metrics.get('fps', 0):.1f}",
            f"Avg FPS: {metrics.get('avg_fps', 0):.1f}",
            f"Min FPS: {metrics.get('min_fps', 0):.1f}",
            f"Frame Skip: {config.get('performance.frame_skip')}",
            f"CPU: {metrics.get('cpu_usage', 'N/A')}%"
        ]

        y_offset = overlay_y + 25
        for line in metrics_lines:
            cv2.putText(img, line, (overlay_x + 10, y_offset),
                       Fonts.FONT, Fonts.SCALE_SMALL, Colors.WHITE, Fonts.THICKNESS_THIN)
            y_offset += 20

    def draw_hand_skeleton(self, img: np.ndarray, detector) -> None:
        """Draw hand skeleton overlay with proper hand orientation"""
        if not detector or not detector.available:
            return

        # Always draw hand landmarks if available (not just on processed frames)
        if detector.results and detector.results.multi_hand_landmarks:
            for hand_landmarks in detector.results.multi_hand_landmarks:
                # Scale landmarks back to original image size (since detector processes at 0.5 scale)
                scaled_landmarks = self._scale_landmarks_for_display(hand_landmarks, img.shape)

                # Draw connections between landmarks
                self._draw_hand_connections(img, scaled_landmarks)

                # Draw landmark points
                self._draw_hand_landmarks(img, scaled_landmarks)

                # Draw finger labels for better understanding
                self._draw_finger_labels(img, scaled_landmarks)

    def _draw_hand_connections(self, img: np.ndarray, hand_landmarks) -> None:
        """Draw connections between hand landmarks"""
        h, w, _ = img.shape

        # Define hand connections (same as MediaPipe)
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index finger
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle finger
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring finger
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm connections
            (5, 9), (9, 13), (13, 17)
        ]

        for connection in connections:
            start_idx, end_idx = connection
            start_landmark = hand_landmarks.landmark[start_idx]
            end_landmark = hand_landmarks.landmark[end_idx]

            start_point = (int(start_landmark.x), int(start_landmark.y))
            end_point = (int(end_landmark.x), int(end_landmark.y))

            # Color code connections by finger
            if start_idx in [0, 1, 2, 3, 4]:  # Thumb
                color = Colors.RED
            elif start_idx in [5, 6, 7, 8]:  # Index
                color = Colors.BLUE
            elif start_idx in [9, 10, 11, 12]:  # Middle
                color = Colors.GREEN
            elif start_idx in [13, 14, 15, 16]:  # Ring
                color = Colors.YELLOW
            else:  # Pinky and palm
                color = Colors.PURPLE

            cv2.line(img, start_point, end_point, color, 2)

    def _draw_hand_landmarks(self, img: np.ndarray, hand_landmarks) -> None:
        """Draw hand landmark points"""
        h, w, _ = img.shape

        for idx, landmark in enumerate(hand_landmarks.landmark):
            x, y = int(landmark.x), int(landmark.y)

            # Different colors for different landmark types
            if idx == 0:  # Wrist
                color = Colors.WHITE
                radius = 6
            elif idx in [4, 8, 12, 16, 20]:  # Finger tips
                color = Colors.CYAN
                radius = 5
            elif idx in [1, 5, 9, 13, 17]:  # Finger bases
                color = Colors.ORANGE
                radius = 4
            else:  # Other joints
                color = Colors.GRAY
                radius = 3

            cv2.circle(img, (x, y), radius, color, -1)
            cv2.circle(img, (x, y), radius, Colors.BLACK, 1)  # Border

    def _scale_landmarks_for_display(self, hand_landmarks, img_shape):
        """Scale landmarks back to original image size for display"""
        h, w = img_shape[:2]

        # Create a copy of the landmarks with scaled coordinates
        scaled_landmarks = []
        for landmark in hand_landmarks.landmark:
            scaled_x = landmark.x * w
            scaled_y = landmark.y * h
            scaled_z = landmark.z  # z coordinate doesn't need scaling for display
            scaled_landmarks.append(type('ScaledLandmark', (), {
                'x': scaled_x,
                'y': scaled_y,
                'z': scaled_z
            })())

        # Return object with landmark attribute
        return type('ScaledHandLandmarks', (), {'landmark': scaled_landmarks})()

    def _draw_finger_labels(self, img: np.ndarray, hand_landmarks) -> None:
        """Draw finger labels for educational purposes"""
        h, w, _ = img.shape

        # Calculate hand size for dynamic scaling
        wrist = hand_landmarks.landmark[0]
        middle_finger_tip = hand_landmarks.landmark[12]
        hand_width = abs(middle_finger_tip.x - wrist.x)
        hand_height = abs(middle_finger_tip.y - wrist.y)
        hand_size = max(hand_width, hand_height)

        # Dynamic font scale based on hand size
        font_scale = max(0.3, min(0.6, hand_size / 200))
        font_thickness = max(1, int(font_scale * 3))

        # Finger tip indices and labels
        finger_tips = {
            4: "THUMB",
            8: "INDEX",
            12: "MIDDLE",
            16: "RING",
            20: "PINKY"
        }

        for tip_idx, label in finger_tips.items():
            landmark = hand_landmarks.landmark[tip_idx]
            x, y = int(landmark.x), int(landmark.y)

            # Position label dynamically based on hand orientation
            # Check if hand is pointing up or down
            wrist_y = wrist.y
            hand_direction = "up" if y < wrist_y else "down"

            if hand_direction == "up":
                label_y = y - int(20 * font_scale)
                if label_y < 20:  # Don't go off top of screen
                    label_y = y + int(30 * font_scale)
            else:
                label_y = y + int(30 * font_scale)
                if label_y > h - 20:  # Don't go off bottom of screen
                    label_y = y - int(20 * font_scale)

            # Small background for text with dynamic size
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
            padding = int(3 * font_scale)
            cv2.rectangle(img, (x - padding, label_y - int(15 * font_scale)),
                         (x + text_size[0] + padding, label_y + int(3 * font_scale)),
                         (0, 0, 0), -1)

            cv2.putText(img, label, (x, label_y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, Colors.WHITE, font_thickness)
