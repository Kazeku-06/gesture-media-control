import platform
import os
import subprocess
import time

class VolumeController:
    """
    Kelas untuk mengontrol volume sistem dengan fallback options
    """
    
    def __init__(self):
        """
        Inisialisasi volume controller dengan multiple fallback
        """
        self.system = platform.system()
        self.current_volume = 50
        self.volume_available = False
        self.volume_interface = None
        
        print(f"Detected OS: {self.system}")
        
        # Try different initialization methods
        if self.system == "Windows":
            self._init_windows()
        elif self.system == "Darwin":  # macOS
            self._init_macos()
        elif self.system == "Linux":
            self._init_linux()
        else:
            print(f"Unsupported OS: {self.system}")
            
        if not self.volume_available:
            print("Volume control not available - running in simulation mode")
        
        # Set initial volume
        self.set_volume(self.current_volume)
    
    def _init_windows(self):
        """Initialize volume control for Windows"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            self.volume_range = self.volume_interface.GetVolumeRange()
            self.min_volume = self.volume_range[0]
            self.max_volume = self.volume_range[1]
            self.volume_available = True
            print("Windows volume control initialized successfully with pycaw")
            
        except ImportError as e:
            print(f"pycaw not available: {e}")
            print("Try: pip install pycaw")
            self._init_windows_fallback()
            
        except Exception as e:
            print(f"Error initializing Windows volume control: {e}")
            self._init_windows_fallback()
    
    def _init_windows_fallback(self):
        """Fallback for Windows without pycaw"""
        try:
            # Try using nircmd if available
            result = subprocess.run(['where', 'nircmd'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.volume_available = True
                self.windows_fallback = 'nircmd'
                print("Using nircmd for volume control")
            else:
                self.volume_available = False
                print("No fallback volume control available for Windows")
        except Exception as e:
            print(f"Error in Windows fallback: {e}")
            self.volume_available = False
    
    def _init_macos(self):
        """Initialize volume control for macOS"""
        try:
            # Test if osascript works
            test_cmd = "osascript -e 'get volume settings'"
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.volume_available = True
                print("macOS volume control initialized successfully")
            else:
                self.volume_available = False
                print("macOS volume control not available")
        except Exception as e:
            print(f"Error initializing macOS volume control: {e}")
            self.volume_available = False
    
    def _init_linux(self):
        """Initialize volume control for Linux"""
        try:
            # Try amixer first
            test_cmd = "amixer sget Master"
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.volume_available = True
                self.linux_mixer = 'amixer'
                print("Linux volume control initialized with amixer")
                return
                
            # Try pactl as fallback
            test_cmd = "pactl list sinks"
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.volume_available = True
                self.linux_mixer = 'pactl'
                print("Linux volume control initialized with pactl")
            else:
                self.volume_available = False
                print("Linux volume control not available")
                
        except Exception as e:
            print(f"Error initializing Linux volume control: {e}")
            self.volume_available = False
    
    def set_volume(self, volume_percent):
        """
        Mengatur volume sistem dengan multiple fallback methods
        """
        volume_percent = max(0, min(100, volume_percent))
        old_volume = self.current_volume
        self.current_volume = volume_percent
        
        if not self.volume_available:
            print(f"[SIMULATION] Volume set to: {volume_percent}%")
            return True
            
        try:
            if self.system == "Windows":
                return self._set_volume_windows(volume_percent)
            elif self.system == "Darwin":
                return self._set_volume_macos(volume_percent)
            elif self.system == "Linux":
                return self._set_volume_linux(volume_percent)
            else:
                return False
                
        except Exception as e:
            print(f"Error setting volume: {e}")
            self.current_volume = old_volume  # Rollback on error
            return False
    
    def _set_volume_windows(self, volume_percent):
        """Set volume for Windows"""
        if self.volume_interface:
            try:
                volume_scalar = volume_percent / 100.0
                volume_db = self.min_volume + (volume_scalar * (self.max_volume - self.min_volume))
                self.volume_interface.SetMasterVolumeLevel(volume_db, None)
                return True
            except Exception as e:
                print(f"Error with pycaw: {e}")
                return self._set_volume_windows_fallback(volume_percent)
        else:
            return self._set_volume_windows_fallback(volume_percent)
    
    def _set_volume_windows_fallback(self, volume_percent):
        """Fallback volume control for Windows"""
        try:
            if hasattr(self, 'windows_fallback') and self.windows_fallback == 'nircmd':
                cmd = f'nircmd setsysvolume {int(volume_percent * 655.35)}'
                subprocess.run(cmd, shell=True, capture_output=True)
                return True
        except Exception as e:
            print(f"Error with Windows fallback: {e}")
        return False
    
    def _set_volume_macos(self, volume_percent):
        """Set volume for macOS"""
        try:
            cmd = f"osascript -e 'set volume output volume {volume_percent}'"
            subprocess.run(cmd, shell=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Error setting macOS volume: {e}")
            return False
    
    def _set_volume_linux(self, volume_percent):
        """Set volume for Linux"""
        try:
            if hasattr(self, 'linux_mixer'):
                if self.linux_mixer == 'amixer':
                    cmd = f"amixer set Master {volume_percent}% > /dev/null 2>&1"
                elif self.linux_mixer == 'pactl':
                    cmd = f"pactl set-sink-volume @DEFAULT_SINK@ {volume_percent}%"
                
                subprocess.run(cmd, shell=True, capture_output=True)
                return True
        except Exception as e:
            print(f"Error setting Linux volume: {e}")
        return False
    
    def get_volume(self):
        """
        Mendapatkan volume saat ini
        """
        return self.current_volume