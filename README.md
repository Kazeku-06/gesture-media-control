# Gesture-Controlled Media System 🎮👋

## 📖 Deskripsi Proyek

**Gesture-Controlled Media System** adalah aplikasi computer vision canggih yang memungkinkan pengguna mengontrol volume media komputer menggunakan gesture tangan melalui webcam. Sistem ini mendeteksi gerakan jari secara real-time dan menerjemahkannya menjadi perintah volume yang presisi.

Dibangun dengan teknologi terdepan dalam bidang computer vision dan human-computer interaction, proyek ini menawarkan pengalaman kontrol media yang intuitif dan natural. Dengan hanya menggunakan gerakan tangan, pengguna dapat menyesuaikan volume tanpa perlu menyentuh keyboard atau mouse.

Sistem ini dirancang modular dan dapat dikembangkan lebih lanjut untuk mendukung berbagai gesture kontrol media lainnya seperti play/pause, next track, mute, dan banyak lagi. Teknologi ini membuka peluang untuk interaksi manusia-komputer yang lebih immersive di masa depan.


## ⚙️ Persyaratan Sistem

### 📋 Requirements Minimum
- **Python** ≥ 3.7 (disarankan 3.10+)
- **Sistem Operasi**: Windows 10/11 (disarankan), macOS, atau Linux
- **Webcam**: Internal atau eksternal dengan resolusi 720p
- **CPU**: Minimal Intel i5 Gen 8 atau AMD Ryzen 5 setara
- **RAM**: 4GB (8GB recommended)

### 🔧 Dependencies
Proyek ini menggunakan library Python berikut:
- **OpenCV** - Computer vision dan processing video
- **MediaPipe** - Deteksi landmark tangan real-time
- **NumPy** - Perhitungan matematika dan array operations
- **Pycaw** - Kontrol audio sistem Windows

## 🚀 Instalasi

### Langkah 1: Clone Repository
```bash
git clone https://github.com/Kazeku-06/gesture-media-control.git
cd gesture-media-control
```

### Langkah 2: Install Dependencies
```bash
# Menggunakan requirements.txt
pip install -r requirements.txt

# Atau install manual satu per satu
pip install opencv-python mediapipe numpy pycaw comtypes
```

### 📦 Penjelasan Dependencies
File `requirements.txt` berisi:
```txt
opencv-python>=4.5.0    # Computer vision dan video processing
mediapipe>=0.8.9        # Hand tracking dan landmark detection
numpy>=1.19.0           # Matematika dan array operations
comtypes>=1.1.7         # COM utilities untuk Windows
pycaw>=20181226         # Windows audio control
```

### 🔄 Alternatif jika Pycaw Tidak Kompatibel
Jika mengalami masalah dengan pycaw, gunakan alternatif berikut:

**Untuk Windows:**
```python
# Menggunakan Windows API langsung
import ctypes
ctypes.windll.user32.SendMessageA(0xFFFF, 0x319, 0, 0xA0000 << 16)
```

**Cross-platform dengan pynput:**
```bash
pip install pynput
```
```python
from pynput.keyboard import Key, Controller
keyboard = Controller()
# Gunakan keyboard media controls
```

### Langkah 3: Jalankan Aplikasi
```bash
python main.py
```

## 🎮 Cara Penggunaan

### 🔄 Langkah-langkah Operasi
1. **Jalankan aplikasi** dengan perintah `python main.py`
2. **Pastikan kamera aktif** dan tidak terhalang
3. **Posisikan tangan** dalam frame kamera dengan jelas
4. **Gunakan gesture berikut** untuk kontrol:

### ✋ Gesture yang Didukung

#### 📊 Volume Control
- **Gesture**: Angkat **jempol dan telunjuk** bersamaan
- **Aksi**: Atur volume dengan mengubah jarak antara kedua jari
  - 👌 Jarak dekat = Volume rendah (0%)
  - 👆 Jarak jauh = Volume tinggi (100%)
- **Visual**: Bar volume real-time di sisi layar

#### ⏯️ Media Control
- **👌 OK Gesture**: Trigger play/pause media
- **✌️ Peace Gesture**: Skip ke track berikutnya

### 🎯 Tips Penggunaan Optimal
- Pastikan **pencahayaan cukup** untuk deteksi tangan yang akurat
- **Background sederhana** untuk mengurangi false detection
- **Jarak optimal** dari kamera: 30-80 cm
- **Gesture konsisten** dan jelas

## 🔬 Penjelasan Teknis

### 🏗️ Arsitektur Sistem

```
Input Camera → Hand Detection → Landmark Processing → Gesture Recognition → Volume Control
```

### 📐 Algoritma Deteksi Gesture

#### 1. **Hand Landmark Detection**
```python
# MediaPipe mendeteksi 21 landmark titik tangan
landmarks = [
    (x1, y1),  # 0: Pergelangan tangan
    (x2, y2),  # 1: Ibu jari pangkal
    # ... hingga 21 titik
]
```

#### 2. **Distance Calculation**
```python
# Hitung jarak Euclidean antara jempol (4) dan telunjuk (8)
def calculate_distance(thumb_tip, index_tip):
    return math.sqrt((thumb_tip.x - index_tip.x)**2 + 
                    (thumb_tip.y - index_tip.y)**2)
```

#### 3. **Volume Mapping**
```python
# Konversi jarak ke volume (0-100%)
min_distance = 30  # pixels
max_distance = 200 # pixels
volume = np.interp(distance, [min_distance, max_distance], [0, 100])
```

#### 4. **System Volume Control**
```python
# Pycaw mengontrol volume sistem Windows
volume_interface.SetMasterVolumeLevel(volume_db, None)
```

### ⚡ Optimasi Performa
- **Frame skipping** untuk meningkatkan FPS
- **Resolution scaling** untuk kamera low-end
- **Smooth interpolation** untuk perubahan volume yang halus

## 🎨 Kustomisasi

### 🎨 Mengubah Warna Volume Bar

**File**: `main.py` - Cari bagian draw_volume_bar

```python
# Default: Hijau (B, G, R)
color = (0, 255, 0)  # Hijau

# Kustomisasi warna:
color = (255, 0, 0)    # 🔵 Biru
color = (0, 0, 255)    # 🔴 Merah  
color = (255, 0, 255)  # 🟣 Ungu
color = (0, 255, 255)  # 🟡 Kuning
color = (255, 255, 0)  # 🦋 Cyan
```

### ⚙️ Mengubah Sensitivitas Volume

**File**: `main.py` - Cari bagian np.interp

```python
# Default sensitivity
volume = np.interp(distance, [30, 200], [0, 100])

# Lebih sensitif (perubahan volume lebih cepat)
volume = np.interp(distance, [20, 150], [0, 100])

# Kurang sensitif (perubahan volume lebih halus)
volume = np.interp(distance, [50, 250], [0, 100])
```

### 🔧 Advanced Customization

#### Mengubah Gesture Threshold
```python
# File: HandTrackingModule.py
# Adjust gesture detection sensitivity
OK_GESTURE_THRESHOLD = 50    # Default: 60
PEACE_GESTURE_FINGERS = [0,1,1,0,0]  # Finger states
```

#### Menambah Gesture Baru
```python
def detect_custom_gesture(fingers):
    if fingers == [1,1,1,0,0]:  # Three fingers up
        return "Custom Action"
    return None
```

## 🛠️ Troubleshooting

### ❌ Kamera Tidak Aktif
**Gejala**: Frame kosong atau error camera index
**Solusi**:
```python
# Coba ganti camera index
cap = cv2.VideoCapture(0)  # Default camera
cap = cv2.VideoCapture(1)  # External camera

# Test camera availability
if not cap.isOpened():
    print("Error: Camera not accessible")
```

### 🔇 Volume Tidak Berubah
**Gejala**: Gesture terdeteksi tapi volume tidak berubah
**Solusi**:
- **Windows**: Jalankan sebagai Administrator
- **Cek pycaw**: `pip show pycaw`
- **Alternative**: Gunakan fallback volume control

### 🐢 Performa Lagging
**Gejala**: FPS rendah atau response lambat
**Solusi**:
```python
# Kurangi resolusi di main.py
w_cam, h_cam = 640, 480   # Dari 1280x720

# Atau tambahkan frame skipping
frame_skip = 2  # Process setiap 2 frame
```

### ✋ Hand Detection Tidak Akurat
**Gejala**: Tangan tidak terdeteksi atau false positive
**Solusi**:
- Tingkatkan pencahayaan
- Background polos
- Adjust confidence threshold:
```python
detector = HandDetector(detection_confidence=0.7)  # Default: 0.5
```

## ✨ Fitur Tambahan

### 🎯 Enhanced Features

#### 📊 Real-time FPS Display
Indikator FPS di pojok kiri atas untuk monitoring performa

#### 🎨 Smooth Volume Animation
Volume bar dengan animasi transisi yang halus dan gradient colors

#### 🔔 Gesture Feedback Visual
- Color coding untuk setiap gesture
- Visual confirmation untuk aksi yang di-trigger
- Pulse animation untuk interaksi yang engaging

#### ⚡ Performance Optimizations
- Frame skipping untuk kamera low-end
- Efficient hand tracking dengan MediaPipe
- Minimal CPU usage dengan algoritma optimized

### 🔮 Future Enhancements
- [ ] Voice feedback untuk aksi
- [ ] Multiple hand support
- [ ] Custom gesture programming
- [ ] Background blur untuk privacy
- [ ] Cross-platform audio control

## 📁 Struktur Folder

```
gesture_media_control/
├── 📄 main.py                 # Entry point aplikasi
├── 🔧 HandTrackingModule.py   # Modul deteksi tangan
├── 🔊 VolumeController.py     # Kontrol volume sistem  
├── 📦 requirements.txt        # Dependencies
└── 📖 README.md              # Dokumentasi ini
```

### 🗂️ Penjelasan File
- **main.py**: Program utama dengan GUI dan control loop
- **HandTrackingModule.py**: Modular hand detection menggunakan MediaPipe
- **VolumeController.py**: Cross-platform volume control dengan fallback
- **requirements.txt**: Dependencies dan versi yang kompatibel

## 📄 Lisensi

### MIT License

```text
Copyright (c) 2024 Gesture-Controlled Media System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

### 🙏 Kredit & Inspirasi

Proyek ini terinspirasi oleh:
- **MediaPipe Hands** oleh Google Research
- **Computer Vision tutorials** oleh Murtaza Hassan
- **Human-Computer Interaction** research papers

Library yang digunakan:
- OpenCV - Computer vision operations
- MediaPipe - Real-time hand tracking
- Pycaw - Windows audio control

## 👨‍💻 Kontribusi & Kontak

### 🤝 Berkontribusi
Kontribusi sangat diterima! Untuk berkontribusi:

1. Fork repository ini
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

### 📧 Kontak
**Dibuat oleh Asta** - [GitHub Profile](https://github.com/Kazeku-06)


---

<div align="center">

**⭐ Jangan lupa beri bintang jika project ini membantu! ⭐**

*"Technology should work for people, not the other way around."*

</div>