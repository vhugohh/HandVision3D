from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
MODEL_DIR = BASE_DIR / "mediapipe_models"
MODEL_PATH = MODEL_DIR / "hand_landmarker.task"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
MAX_HANDS = int(os.getenv("MAX_HANDS", "2"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "65"))
MAX_FRAME_BYTES = int(os.getenv("MAX_FRAME_BYTES", str(2 * 1024 * 1024)))
