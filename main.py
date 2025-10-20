import cv2
import numpy as np
import time
import math
from HandTrackingModule import HandDetector
from VolumeController import VolumeController

def main():
    """
    Fungsi utama untuk Gesture-Controlled Media System
    """
    # Inisialisasi variabel
    w_cam, h_cam = 1280, 720
    cap = cv2.VideoCapture(0)
    cap.set(3, w_cam)  # Set width
    cap.set(4, h_cam)  # Set height
    
    # Inisialisasi detector tangan
    detector = HandDetector(detection_confidence=0.7, max_hands=1)
    
    # Inisialisasi volume controller
    volume_controller = VolumeController()
    
    # Variabel untuk FPS calculation
    prev_time = 0
    current_time = 0
    
    # Variabel untuk smoothing volume
    smooth_volume = volume_controller.get_volume()
    smoothing_factor = 0.2
    
    # Variabel untuk gesture control
    last_gesture_time = 0
    gesture_cooldown = 1.0  # Cooldown 1 detik antara gesture
    
    print("Gesture-Controlled Media System Started!")
    print("Controls:")
    print("- Thumb + Index: Volume Control")
    print("- OK Gesture: Play/Pause")
    print("- Peace Gesture: Next Track")
    
    while True:
        # Baca frame dari kamera
        success, img = cap.read()
        if not success:
            print("Failed to read from camera")
            break
            
        # Flip gambar horizontal untuk mirror effect
        img = cv2.flip(img, 1)
        
        # Deteksi tangan
        img = detector.find_hands(img)
        landmarks_list = detector.find_position(img, draw=False)
        
        # Hitung dan tampilkan FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time > 0 else 0
        prev_time = current_time
        
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if landmarks_list:
            # Deteksi gesture
            gesture = detector.detect_gesture()
            current_time = time.time()
            
            # Tampilkan gesture status
            cv2.putText(img, f'Gesture: {gesture}', (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if gesture == "Volume Control":
                # Kontrol volume dengan jarak antara thumb dan index
                length, img, info = detector.find_distance(4, 8, img, color=(0, 255, 0))
                
                # Konversi jarak ke volume (30-200 pixels -> 0-100%)
                min_dist, max_dist = 30, 200
                volume = np.interp(length, [min_dist, max_dist], [0, 100])
                volume = max(0, min(100, volume))  # Clamp nilai
                
                # Smoothing volume changes
                smooth_volume = smooth_volume * (1 - smoothing_factor) + volume * smoothing_factor
                
                # Set volume
                volume_controller.set_volume(int(smooth_volume))
                
                # Tampilkan informasi jarak dan volume
                cv2.putText(img, f'Distance: {int(length)}px', (info[4]-50, info[5]-30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(img, f'Volume: {int(smooth_volume)}%', (info[4]-50, info[5]-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            elif gesture == "OK" and (current_time - last_gesture_time) > gesture_cooldown:
                # Play/Pause dengan OK gesture
                cv2.putText(img, "PLAY/PAUSE", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                print("Play/Pause triggered")
                last_gesture_time = current_time
                
            elif gesture == "Peace" and (current_time - last_gesture_time) > gesture_cooldown:
                # Next track dengan Peace gesture
                cv2.putText(img, "NEXT TRACK", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                print("Next track triggered")
                last_gesture_time = current_time
        
        # Gambar volume bar
        draw_volume_bar(img, volume_controller.get_volume())
        
        # Tampilkan frame
        cv2.imshow("Gesture-Controlled Media System", img)
        
        # Exit dengan menekan 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

def draw_volume_bar(img, volume, bar_width=30, bar_height=300, margin=50):
    """
    Menggambar volume bar di sisi kiri frame
    
    Args:
        img: Frame untuk menggambar
        volume: Persentase volume (0-100)
        bar_width: Lebar volume bar
        bar_height: Tinggi volume bar
        margin: Margin dari tepi
    """
    h, w, _ = img.shape
    
    # Posisi volume bar
    bar_x = margin
    bar_y = (h - bar_height) // 2
    
    # Background bar (abu-abu)
    cv2.rectangle(img, (bar_x, bar_y), 
                 (bar_x + bar_width, bar_y + bar_height), 
                 (50, 50, 50), -1)
    
    # Volume fill (hijau)
    fill_height = int((volume / 100) * bar_height)
    fill_y = bar_y + (bar_height - fill_height)
    
    # Warna berdasarkan volume (hijau -> kuning -> merah)
    if volume < 50:
        color = (0, 255, 0)  # Hijau
    elif volume < 80:
        color = (0, 255, 255)  # Kuning
    else:
        color = (0, 0, 255)  # Merah
        
    cv2.rectangle(img, (bar_x, fill_y), 
                 (bar_x + bar_width, bar_y + bar_height), 
                 color, -1)
    
    # Border bar
    cv2.rectangle(img, (bar_x, bar_y), 
                 (bar_x + bar_width, bar_y + bar_height), 
                 (255, 255, 255), 2)
    
    # Teks volume
    cv2.putText(img, f'{int(volume)}%', 
               (bar_x - 10, bar_y + bar_height + 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

if __name__ == "__main__":
    main()