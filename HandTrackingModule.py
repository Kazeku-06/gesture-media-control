import cv2
import numpy as np
import math

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    print("MediaPipe not available. Please install: pip install mediapipe")
    MEDIAPIPE_AVAILABLE = False

class HandDetector:
    """
    Kelas untuk mendeteksi tangan yang dioptimalkan untuk performa
    """
    
    def __init__(self, mode=False, max_hands=1, detection_confidence=0.5, tracking_confidence=0.5):
        """
        Inisialisasi hand detector
        """
        if not MEDIAPIPE_AVAILABLE:
            print("ERROR: MediaPipe is required but not available")
            self.available = False
            return
            
        self.available = True
        self.mode = mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        
        try:
            # Inisialisasi MediaPipe Hands
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=self.mode,
                max_num_hands=self.max_hands,
                min_detection_confidence=self.detection_confidence,
                min_tracking_confidence=self.tracking_confidence
            )
            
            self.mp_draw = mp.solutions.drawing_utils
            
            # Optimasi: Predefine drawing specs
            self.landmark_drawing_spec = self.mp_draw.DrawingSpec(
                color=(0, 255, 0), thickness=1, circle_radius=1
            )
            self.connection_drawing_spec = self.mp_draw.DrawingSpec(
                color=(255, 0, 0), thickness=1, circle_radius=1
            )
            
            self.results = None
            self.landmarks_list = []
            
            # Landmark indices untuk jari-jari
            self.tip_ids = [4, 8, 12, 16, 20]
            
            # Cache untuk optimasi
            self._last_hands = None
            self._frame_count = 0
            
            print("HandDetector initialized successfully")
            
        except Exception as e:
            print(f"Error initializing MediaPipe: {e}")
            self.available = False
    
    def find_hands(self, img, draw=True):
        """
        Mendeteksi tangan dalam frame - dioptimalkan
        """
        if not self.available:
            return img
            
        # Skip frame untuk meningkatkan FPS (process setiap 2 frame)
        self._frame_count += 1
        process_this_frame = self._frame_count % 2 == 0
        
        if process_this_frame:
            # Resize image untuk performa yang lebih baik
            small_img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            img_rgb = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
            img_rgb.flags.writeable = False  # Optimasi memory
            
            self.results = self.hands.process(img_rgb)
            
            if self.results.multi_hand_landmarks and draw:
                for hand_landmarks in self.results.multi_hand_landmarks:
                    # Scale landmarks kembali ke ukuran asli
                    self._scale_landmarks(hand_landmarks, 2.0)
                    self.mp_draw.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.landmark_drawing_spec,
                        self.connection_drawing_spec
                    )
        else:
            # Gunakan hasil dari frame sebelumnya
            if self._last_hands and draw:
                for hand_landmarks in self._last_hands:
                    self.mp_draw.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.landmark_drawing_spec,
                        self.connection_drawing_spec
                    )
        
        return img
    
    def _scale_landmarks(self, landmarks, scale_factor):
        """
        Scale landmarks setelah processing di resolusi rendah
        """
        for landmark in landmarks.landmark:
            landmark.x *= scale_factor
            landmark.y *= scale_factor
    
    def find_position(self, img, hand_number=0, draw=False):
        """
        Mendapatkan posisi landmarks tangan - dioptimalkan
        """
        if not self.available:
            return []
            
        self.landmarks_list = []
        
        if self.results and self.results.multi_hand_landmarks:
            if hand_number < len(self.results.multi_hand_landmarks):
                hand = self.results.multi_hand_landmarks[hand_number]
                h, w, c = img.shape
                
                for id, landmark in enumerate(hand.landmark):
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    self.landmarks_list.append([id, cx, cy])
                    
                    if draw and id in self.tip_ids:  # Hanya gambar ujung jari
                        cv2.circle(img, (cx, cy), 3, (255, 0, 255), cv2.FILLED)
        
        # Cache hasil untuk frame skip
        if self.results and self.results.multi_hand_landmarks:
            self._last_hands = self.results.multi_hand_landmarks
        
        return self.landmarks_list
    
    def fingers_up(self):
        """
        Mendeteksi jari mana yang terangkat - dioptimalkan
        """
        fingers = []
        
        if len(self.landmarks_list) < 21:
            return fingers
            
        # Thumb - simplified logic
        if self.landmarks_list[self.tip_ids[0]][1] > self.landmarks_list[self.tip_ids[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # 4 jari lainnya - simplified
        for id in range(1, 5):
            if self.landmarks_list[self.tip_ids[id]][2] < self.landmarks_list[self.tip_ids[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers
    
    def find_distance(self, p1, p2, img=None, draw=True, color=(255, 0, 0), thickness=2):
        """
        Menghitung jarak antara dua landmark - dioptimalkan
        """
        if len(self.landmarks_list) < max(p1, p2) + 1:
            return 0, img, [0, 0, 0, 0, 0, 0]
            
        x1, y1 = self.landmarks_list[p1][1], self.landmarks_list[p1][2]
        x2, y2 = self.landmarks_list[p2][1], self.landmarks_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        if draw and img is not None:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)
            cv2.circle(img, (x1, y1), 4, color, cv2.FILLED)
            cv2.circle(img, (x2, y2), 4, color, cv2.FILLED)
            cv2.circle(img, (cx, cy), 4, color, cv2.FILLED)
            
        length = math.hypot(x2 - x1, y2 - y1)
        info = [x1, y1, x2, y2, cx, cy]
        
        return length, img, info
    
    def detect_gesture(self):
        """
        Mendeteksi gesture tangan - dioptimalkan dengan cache
        """
        if not self.landmarks_list:
            return "No Hand"
            
        fingers = self.fingers_up()
        if not fingers:
            return "Unknown"
        
        # Volume Control Gesture (thumb dan index terangkat, lainnya mengepal)
        if fingers[1] == 1 and fingers[0] == 1 and sum(fingers[2:]) == 0:
            return "Volume Control"
            
        # OK Gesture - simplified detection
        if fingers[1] == 1 and fingers[0] == 0 and sum(fingers[2:]) == 0:
            distance, _, _ = self.find_distance(4, 8, draw=False)
            if distance < 60:  # Increased threshold untuk stabil
                return "OK"
                
        # Peace Gesture - simplified
        if fingers[1] == 1 and fingers[2] == 1 and sum(fingers[3:]) == 0 and fingers[0] == 0:
            return "Peace"
            
        return "Unknown"