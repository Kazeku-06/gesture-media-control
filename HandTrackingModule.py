import cv2
import mediapipe as mp
import numpy as np
import math

class HandDetector:
    """
    Kelas untuk mendeteksi tangan menggunakan MediaPipe Hands
    """
    
    def __init__(self, mode=False, max_hands=2, detection_confidence=0.5, tracking_confidence=0.5):
        """
        Inisialisasi hand detector
        
        Args:
            mode: Static image mode (False untuk video)
            max_hands: Maximum number of hands to detect
            detection_confidence: Minimum confidence value for hand detection
            tracking_confidence: Minimum confidence value for hand tracking
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        
        # Inisialisasi MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        
        # Landmark indices untuk jari-jari
        self.tip_ids = [4, 8, 12, 16, 20]  # ujung jari: thumb, index, middle, ring, pinky
        
    def find_hands(self, img, draw=True):
        """
        Mendeteksi tangan dalam frame
        
        Args:
            img: Frame input (BGR)
            draw: Whether to draw landmarks on the image
            
        Returns:
            img: Frame dengan landmarks (jika draw=True)
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )
                
        return img
    
    def find_position(self, img, hand_number=0, draw=True):
        """
        Mendapatkan posisi landmarks tangan
        
        Args:
            img: Frame input
            hand_number: Index tangan yang ingin dideteksi
            draw: Whether to draw circles on landmarks
            
        Returns:
            landmarks_list: List berisi [id, x, y] untuk setiap landmark
        """
        self.landmarks_list = []
        h, w, c = img.shape
        
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_number]
            
            for id, landmark in enumerate(hand.landmark):
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                self.landmarks_list.append([id, cx, cy])
                
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                    
        return self.landmarks_list
    
    def fingers_up(self):
        """
        Mendeteksi jari mana yang terangkat
        
        Returns:
            fingers: List status jari [thumb, index, middle, ring, pinky]
                    1 = terangkat, 0 = tertekuk
        """
        fingers = []
        
        if not self.landmarks_list:
            return fingers
            
        # Thumb - perbandingan dengan landmark 3 (pangkal thumb)
        if self.landmarks_list[self.tip_ids[0]][1] > self.landmarks_list[self.tip_ids[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # 4 jari lainnya
        for id in range(1, 5):
            if self.landmarks_list[self.tip_ids[id]][2] < self.landmarks_list[self.tip_ids[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers
    
    def find_distance(self, p1, p2, img=None, draw=True, color=(255, 0, 0), thickness=3):
        """
        Menghitung jarak antara dua landmark
        
        Args:
            p1, p2: Indeks landmark
            img: Frame untuk menggambar
            draw: Whether to draw line and circles
            color: Warna garis
            thickness: Ketebalan garis
            
        Returns:
            distance: Jarak antara dua titik
            img: Frame dengan gambar (jika draw=True)
            info: Informasi koordinat [x1, y1, x2, y2, cx, cy]
        """
        if not self.landmarks_list:
            return 0, img, [0, 0, 0, 0, 0, 0]
            
        x1, y1 = self.landmarks_list[p1][1], self.landmarks_list[p1][2]
        x2, y2 = self.landmarks_list[p2][1], self.landmarks_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        if draw and img is not None:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)
            cv2.circle(img, (x1, y1), 8, color, cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, color, cv2.FILLED)
            cv2.circle(img, (cx, cy), 8, color, cv2.FILLED)
            
        length = math.hypot(x2 - x1, y2 - y1)
        info = [x1, y1, x2, y2, cx, cy]
        
        return length, img, info
    
    def detect_gesture(self):
        """
        Mendeteksi gesture tangan
        
        Returns:
            gesture: String nama gesture
        """
        if not self.landmarks_list:
            return "No Hand"
            
        fingers = self.fingers_up()
        
        # OK Gesture (thumb dan index membentuk lingkaran, jari lain mengepal)
        if fingers[1] == 1 and fingers[0] == 0 and sum(fingers[2:]) == 0:
            # Cek jarak antara thumb tip dan index tip
            distance, _, _ = self.find_distance(4, 8, draw=False)
            if distance < 50:  # Threshold untuk gesture OK
                return "OK"
                
        # Peace Gesture (index dan middle terangkat, jari lain mengepal)
        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return "Peace"
            
        # Volume Control Gesture (hanya thumb dan index yang terangkat)
        if fingers[1] == 1 and fingers[0] == 1 and sum(fingers[2:]) == 0:
            return "Volume Control"
            
        return "Unknown"