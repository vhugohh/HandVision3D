"""Adaptador MediaPipe Tasks: detecta hasta dos manos sin dibujar landmarks."""

import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from .config import MODEL_PATH, MODEL_URL, MAX_HANDS
from .hand_kinematics import calculate_finger_angles


class HandDetector:
    def __init__(self):
        self.landmarker = None
        self.last_timestamp_ms = 0

    @staticmethod
    def ensure_model():
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
            return
        temporary = MODEL_PATH.with_suffix(".download")
        request = urllib.request.Request(
            MODEL_URL, headers={"User-Agent": "HandVision3D/0.1"}
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            temporary.write_bytes(response.read())
        temporary.replace(MODEL_PATH)

    def start(self):
        self.ensure_model()
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=MAX_HANDS,
            min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.50,
            min_tracking_confidence=0.50,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def close(self):
        if self.landmarker is not None:
            self.landmarker.close()
            self.landmarker = None

    def process_jpeg(self, jpeg_bytes: bytes, timestamp_ms: int):
        if self.landmarker is None:
            raise RuntimeError("El detector MediaPipe no está inicializado.")

        array = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("No fue posible decodificar el fotograma.")

        height, width = frame.shape[:2]
        # MediaPipe handedness assumes mirrored selfie input.
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # MediaPipe exige marcas de tiempo crecientes.
        timestamp_ms = max(int(timestamp_ms), self.last_timestamp_ms + 1)
        self.last_timestamp_ms = timestamp_ms

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        hands = []

        for index, hand_landmarks in enumerate(result.hand_landmarks or []):
            handedness = "Unknown"
            confidence = 0.0
            if result.handedness and index < len(result.handedness):
                category = result.handedness[index][0]
                handedness = category.category_name
                confidence = float(category.score)

            points = [
                {
                    "x": round(float(point.x), 6),
                    "y": round(float(point.y), 6),
                    "z": round(float(point.z), 6),
                }
                for point in hand_landmarks
            ]

            hands.append({
                "label": handedness,
                "confidence": round(confidence, 4),
                "landmarks": points,
                "angles": calculate_finger_angles(hand_landmarks),
            })

        return {
            "type": "hand_data",
            "width": width,
            "height": height,
            "hand_count": len(hands),
            "hands": hands,
            "timestamp_ms": timestamp_ms,
        }
