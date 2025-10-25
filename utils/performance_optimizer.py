"""
Performance Optimizer module for Gesture Media Control
Handles frame skipping and performance optimizations
"""

import time
from config import config

class PerformanceOptimizer:
    """
    Class untuk optimasi performa
    """

    def __init__(self):
        self.frame_skip = config.get('performance.frame_skip')
        self.frame_count = 0
        self.last_volume_update = 0
        self.volume_update_interval = config.get('performance.volume_update_interval')

    def should_process_frame(self) -> bool:
        """Decision apakah frame ini harus diproses"""
        self.frame_count += 1
        return self.frame_count % self.frame_skip == 0

    def should_update_volume(self) -> bool:
        """Decision apakah volume harus diupdate"""
        current_time = time.time()
        if current_time - self.last_volume_update > self.volume_update_interval:
            self.last_volume_update = current_time
            return True
        return False
