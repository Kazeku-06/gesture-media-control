import platform
import math

class VolumeController:
    """
    Kelas untuk mengontrol volume sistem
    """
    
    def __init__(self):
        """
        Inisialisasi volume controller berdasarkan platform
        """
        self.system = platform.system()
        self.current_volume = 50  # Default volume 50%
        
        # Inisialisasi berdasarkan platform
        if self.system == "Windows":
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
                
                # Set initial volume
                self.set_volume(self.current_volume)
                
            except ImportError:
                print("pycaw tidak tersedia, menggunakan fallback")
                self.volume_available = False
                
        else:  # macOS atau Linux
            self.volume_available = True
    
    def set_volume(self, volume_percent):
        """
        Mengatur volume sistem
        
        Args:
            volume_percent: Persentase volume (0-100)
        """
        volume_percent = max(0, min(100, volume_percent))  # Clamp nilai
        self.current_volume = volume_percent
        
        if not self.volume_available:
            return
            
        try:
            if self.system == "Windows":
                # Konversi persentase ke skala Windows
                volume_scalar = volume_percent / 100.0
                volume_db = self.min_volume + (volume_scalar * (self.max_volume - self.min_volume))
                self.volume_interface.SetMasterVolumeLevel(volume_db, None)
                
            elif self.system == "Darwin":  # macOS
                volume_scalar = volume_percent / 100.0
                os.system(f"osascript -e 'set volume output volume {volume_percent}'")
                
            elif self.system == "Linux":
                # Untuk Linux menggunakan alsamixer
                os.system(f"amixer set Master {volume_percent}%")
                
        except Exception as e:
            print(f"Error setting volume: {e}")
    
    def get_volume(self):
        """
        Mendapatkan volume saat ini
        
        Returns:
            current_volume: Volume saat ini (0-100)
        """
        return self.current_volume