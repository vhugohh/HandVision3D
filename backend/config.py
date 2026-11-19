import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
MODEL_DIR=BASE_DIR/'mediapipe_models'
MODEL_PATH=MODEL_DIR/'hand_landmarker.task'
MODEL_URL=os.getenv('MEDIAPIPE_MODEL_URL','https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task')
MAX_HANDS=int(os.getenv('MAX_HANDS','2'))
