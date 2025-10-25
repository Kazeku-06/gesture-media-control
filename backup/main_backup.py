import cv2
import numpy as np
import time
import math
from HandTrackingModule import HandDetector
from VolumeController import VolumeController

class PerformanceOptimizer:
    """
    Class untuk optimasi performa
    """
    def __init__(self):
        self.frame_skip = 2  # Process setiap 2 frame
        self.frame_count = 0
        self.last_volume_update = 0
        self.volume_update_interval = 0.05  # Update volume setiap 50ms
        
    def should_process_frame(self):
        """Decision apakah frame ini harus diproses"""
        self.frame_count += 1
        return self.frame_count % self.frame_skip == 0
    
    def should_update_volume(self):
        """Decision apakah volume harus diupdate"""
        current_time = time.time()
        if current_time - self.last_volume_update > self.volume_update_interval:
            self.last_volume_update = current_time
            return True
        return False

class SmoothVolumeBar:
    """
    Class untuk animasi smooth volume bar
    """
    def __init__(self, animation_speed=0.2):
        self.animation_speed = animation_speed
        self.display_volume = 0  # Volume yang ditampilkan (dengan animasi)
        self.target_volume = 0   # Volume target (aktual)
        self.last_update_time = time.time()
        
    def update(self, target_volume):
        """
        Update volume bar dengan animasi smooth
        """
        self.target_volume = target_volume
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Smooth animation menggunakan linear interpolation
        if abs(self.display_volume - self.target_volume) > 0.5:
            # Calculate step based on animation speed and delta time
            step = (self.target_volume - self.display_volume) * self.animation_speed * delta_time * 60
            self.display_volume += step
            
            # Clamp to target if very close
            if abs(self.display_volume - self.target_volume) < 1:
                self.display_volume = self.target_volume
        else:
            self.display_volume = self.target_volume
            
        return int(self.display_volume)
    
    def get_display_volume(self):
        """Get current displayed volume"""
        return int(self.display_volume)

def main():
    """
    Fungsi utama yang dioptimalkan untuk performa dengan animasi smooth
    """
    # Optimasi: Kurangi resolusi untuk kamera low-end
    w_cam, h_cam = 640, 480
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera properties untuk performa
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w_cam)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h_cam)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    # Inisialisasi detector tangan yang dioptimalkan
    detector = HandDetector(
        detection_confidence=0.6,
        tracking_confidence=0.5,
        max_hands=1
    )
    
    # Check if hand detector is available
    if not detector.available:
        print("Error: Hand detector not available. Please check MediaPipe installation.")
        cap.release()
        return
    
    # Inisialisasi volume controller
    volume_controller = VolumeController()
    
    # Inisialisasi performance optimizer
    perf_optimizer = PerformanceOptimizer()
    
    # Inisialisasi smooth volume bar
    smooth_bar = SmoothVolumeBar(animation_speed=0.3)  # Speed bisa diatur 0.1-0.5
    
    # Variabel untuk FPS calculation
    prev_time = 0
    current_time = 0
    
    # Variabel untuk smoothing volume
    smooth_volume = volume_controller.get_volume()
    smoothing_factor = 0.3
    
    # Variabel untuk gesture control
    last_gesture_time = 0
    gesture_cooldown = 1.0
    
    # Optimasi: Predefine colors dan fonts
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    CYAN = (255, 255, 0)
    ORANGE = (0, 165, 255)
    
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE_SMALL = 0.5
    FONT_SCALE_MEDIUM = 0.6
    FONT_THICKNESS = 1
    
    # Variabel untuk efek visual
    pulse_animation = 0
    last_pulse_time = time.time()
    
    print("Gesture-Controlled Media System (Optimized + Smooth Animation) Started!")
    print("Optimizations applied:")
    print("- Lower resolution (640x480)")
    print("- Frame skipping (process every 2nd frame)")
    print("- Smooth volume bar animation")
    print("- Optimized volume update frequency")
    print()
    print("Controls:")
    print("- Thumb + Index: Volume Control")
    print("- OK Gesture: Play/Pause")
    print("- Peace Gesture: Next Track")
    print("- Press 'q' or ESC to exit")
    
    while True:
        # Baca frame dari kamera
        success, img = cap.read()
        if not success:
            print("Failed to read from camera")
            break
            
        # Flip gambar horizontal untuk mirror effect
        img = cv2.flip(img, 1)
        
        # Optimasi: Skip processing untuk beberapa frame
        if perf_optimizer.should_process_frame():
            # Deteksi tangan (hanya di frame yang diproses)
            img = detector.find_hands(img)
            landmarks_list = detector.find_position(img, draw=False)
        else:
            # Gunakan landmarks dari frame sebelumnya
            landmarks_list = detector.landmarks_list
        
        # Hitung dan tampilkan FPS (selalu update)
        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time > 0 else 0
        prev_time = current_time
        
        # Update smooth volume bar animation
        display_volume = smooth_bar.update(volume_controller.get_volume())
        
        # Update pulse animation untuk efek visual
        pulse_delta = current_time - last_pulse_time
        if pulse_delta > 0.05:  # 20 FPS untuk animasi
            pulse_animation = (pulse_animation + 0.3) % (2 * math.pi)
            last_pulse_time = current_time
        
        # Optimasi: Simple FPS display dengan warna berdasarkan performa
        fps_color = GREEN if fps > 20 else YELLOW if fps > 10 else RED
        cv2.putText(img, f'FPS: {int(fps)}', (10, 25), 
                   FONT, FONT_SCALE_MEDIUM, fps_color, FONT_THICKNESS)
        
        # Tampilkan volume dengan animasi
        volume_text_color = CYAN
        cv2.putText(img, f'Volume: {display_volume}%', (10, h_cam - 20), 
                   FONT, FONT_SCALE_MEDIUM, volume_text_color, FONT_THICKNESS)
        
        if landmarks_list:
            # Deteksi gesture
            gesture = detector.detect_gesture()
            current_time = time.time()
            
            # Tampilkan gesture status dengan efek visual
            gesture_color = GREEN
            if gesture == "Volume Control":
                gesture_color = CYAN
            elif gesture == "OK":
                gesture_color = ORANGE
            elif gesture == "Peace":
                gesture_color = YELLOW
                
            cv2.putText(img, f'Gesture: {gesture}', (10, 50), 
                       FONT, FONT_SCALE_MEDIUM, gesture_color, FONT_THICKNESS)
            
            if gesture == "Volume Control":
                # Kontrol volume dengan optimasi update frequency
                length, img, info = detector.find_distance(4, 8, img, color=CYAN, thickness=2)
                
                # Konversi jarak ke volume
                min_dist, max_dist = 30, 200
                volume = np.interp(length, [min_dist, max_dist], [0, 100])
                volume = max(0, min(100, volume))
                
                # Smoothing volume changes
                smooth_volume = smooth_volume * (1 - smoothing_factor) + volume * smoothing_factor
                
                # Optimasi: Update volume hanya pada interval tertentu
                if perf_optimizer.should_update_volume():
                    volume_controller.set_volume(int(smooth_volume))
                
                # Tampilkan informasi dengan efek visual
                if fps > 10:
                    # Efek pulse pada text informasi
                    pulse_scale = 0.7 + 0.3 * math.sin(pulse_animation)
                    pulse_thickness = max(1, int(1 * pulse_scale))
                    
                    cv2.putText(img, f'Dist: {int(length)}px', (info[4]-40, info[5]-20), 
                               FONT, FONT_SCALE_SMALL, BLUE, pulse_thickness)
                    cv2.putText(img, f'Vol: {int(smooth_volume)}%', (info[4]-40, info[5]-5), 
                               FONT, FONT_SCALE_SMALL, BLUE, pulse_thickness)
            
            elif gesture == "OK" and (current_time - last_gesture_time) > gesture_cooldown:
                # Efek visual untuk gesture OK
                gesture_text = "PLAY/PAUSE"
                text_size = cv2.getTextSize(gesture_text, FONT, FONT_SCALE_MEDIUM, FONT_THICKNESS)[0]
                text_x = (w_cam - text_size[0]) // 2
                
                # Background highlight
                cv2.rectangle(img, (text_x-10, 65), (text_x + text_size[0] + 10, 85), 
                             (0, 0, 0), -1)
                cv2.rectangle(img, (text_x-10, 65), (text_x + text_size[0] + 10, 85), 
                             ORANGE, 2)
                
                cv2.putText(img, gesture_text, (text_x, 80), 
                           FONT, FONT_SCALE_MEDIUM, ORANGE, FONT_THICKNESS)
                print("Play/Pause triggered")
                last_gesture_time = current_time
                
            elif gesture == "Peace" and (current_time - last_gesture_time) > gesture_cooldown:
                # Efek visual untuk gesture Peace
                gesture_text = "NEXT TRACK"
                text_size = cv2.getTextSize(gesture_text, FONT, FONT_SCALE_MEDIUM, FONT_THICKNESS)[0]
                text_x = (w_cam - text_size[0]) // 2
                
                # Background highlight
                cv2.rectangle(img, (text_x-10, 65), (text_x + text_size[0] + 10, 85), 
                             (0, 0, 0), -1)
                cv2.rectangle(img, (text_x-10, 65), (text_x + text_size[0] + 10, 85), 
                             YELLOW, 2)
                
                cv2.putText(img, gesture_text, (text_x, 80), 
                           FONT, FONT_SCALE_MEDIUM, YELLOW, FONT_THICKNESS)
                print("Next track triggered")
                last_gesture_time = current_time
        
        # Gambar volume bar dengan animasi smooth
        draw_animated_volume_bar(img, display_volume, smooth_bar.target_volume, pulse_animation)
        
        # Tampilkan frame
        cv2.imshow("Gesture Media Control (Smooth Animation)", img)
        
        # Exit dengan menekan 'q' atau ESC
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed successfully")

def draw_animated_volume_bar(img, display_volume, target_volume, pulse_animation, 
                           bar_width=25, bar_height=250, margin=30):
    """
    Volume bar dengan animasi smooth dan efek visual
    """
    h, w, _ = img.shape
    
    # Posisi volume bar
    bar_x = margin
    bar_y = (h - bar_height) // 2
    
    # Background bar dengan gradient
    for i in range(bar_height):
        ratio = i / bar_height
        color_ratio = int(255 * ratio)
        cv2.line(img, (bar_x, bar_y + i), (bar_x + bar_width, bar_y + i), 
                (color_ratio//2, color_ratio//2, color_ratio//2), 1)
    
    # Volume fill dengan animasi smooth
    fill_height = int((display_volume / 100) * bar_height)
    fill_y = bar_y + (bar_height - fill_height)
    
    # Gradient color untuk volume fill
    for i in range(fill_height):
        ratio = i / fill_height if fill_height > 0 else 0
        height_pos = fill_y + i
        
        # Gradient dari hijau ke merah
        if display_volume < 50:
            # Hijau ke kuning
            green = 255
            red = int(255 * (ratio * 2))
            blue = 0
        else:
            # Kuning ke merah
            green = int(255 * (1 - (ratio - 0.5) * 2))
            red = 255
            blue = 0
            
        color = (blue, green, red)
        cv2.line(img, (bar_x, height_pos), (bar_x + bar_width, height_pos), color, 1)
    
    # Efek highlight pada bagian atas volume bar
    if fill_height > 0:
        highlight_height = max(3, fill_height // 10)
        for i in range(highlight_height):
            alpha = 1.0 - (i / highlight_height)
            highlight_color = (int(255 * alpha), int(255 * alpha), int(255 * alpha))
            pos = fill_y + i
            if pos < bar_y + bar_height:
                cv2.line(img, (bar_x, pos), (bar_x + bar_width, pos), highlight_color, 1)
    
    # Border bar dengan efek 3D
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                 (100, 100, 100), 1)
    cv2.rectangle(img, (bar_x-1, bar_y-1), (bar_x + bar_width + 1, bar_y + bar_height + 1), 
                 (50, 50, 50), 1)
    
    # Marker setiap 25%
    for percent in [0, 25, 50, 75, 100]:
        marker_y = bar_y + bar_height - int((percent / 100) * bar_height)
        marker_color = (200, 200, 200) if percent % 50 == 0 else (150, 150, 150)
        marker_length = 8 if percent % 50 == 0 else 5
        
        cv2.line(img, (bar_x - marker_length, marker_y), (bar_x, marker_y), 
                marker_color, 1)
        cv2.line(img, (bar_x + bar_width, marker_y), (bar_x + bar_width + marker_length, marker_y), 
                marker_color, 1)
        
        # Text marker
        if percent % 50 == 0:
            text_offset = 15 if percent == 0 else 12
            cv2.putText(img, f'{percent}%', 
                       (bar_x + bar_width + 10, marker_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (200, 200, 200), 1)
    
    # Efek pulse pada target volume indicator
    pulse_scale = 0.8 + 0.2 * math.sin(pulse_animation)
    target_height = bar_y + bar_height - int((target_volume / 100) * bar_height)
    pulse_size = int(3 * pulse_scale)
    
    # Target indicator (garis kecil yang berdenyut)
    if abs(display_volume - target_volume) > 2:  # Hanya show jika ada perbedaan
        cv2.line(img, (bar_x - 5, target_height), (bar_x + bar_width + 5, target_height), 
                (255, 255, 255), pulse_size)
    
    # Current volume indicator (bulat di ujung)
    current_height = bar_y + bar_height - fill_height
    indicator_radius = 4
    cv2.circle(img, (bar_x + bar_width//2, current_height), 
              indicator_radius, (255, 255, 255), -1)
    cv2.circle(img, (bar_x + bar_width//2, current_height), 
              indicator_radius, (0, 0, 0), 1)

if __name__ == "__main__":
    main()