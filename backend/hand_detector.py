import base64,urllib.request
import cv2,numpy as np,mediapipe as mp
from .config import MODEL_DIR,MODEL_PATH,MODEL_URL,MAX_HANDS
from .hand_kinematics import calculate_pose,PoseSmoother
class HandDetector:
 def __init__(self):
  MODEL_DIR.mkdir(exist_ok=True,parents=True)
  if not MODEL_PATH.exists():urllib.request.urlretrieve(MODEL_URL,MODEL_PATH)
  opts=mp.tasks.vision.HandLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),running_mode=mp.tasks.vision.RunningMode.VIDEO,num_hands=MAX_HANDS,min_hand_detection_confidence=.55,min_hand_presence_confidence=.55,min_tracking_confidence=.5)
  self.detector=mp.tasks.vision.HandLandmarker.create_from_options(opts);self.smoother=PoseSmoother();self.frame=0
 def process(self,image):
  self.frame+=1;rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);res=self.detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb),self.frame*33);hands=[]
  for i,lms in enumerate(res.hand_landmarks or []):
   cat=res.handedness[i][0] if res.handedness and res.handedness[i] else None;label=cat.category_name if cat else 'Unknown';score=cat.score if cat else 0
   pose=self.smoother.apply(label,calculate_pose(lms,label,score));hands.append({'id':label.lower(),'label':label,'pose':pose})
  return {'hands':hands,'hand_count':len(hands),'frame':self.frame}
 def close(self):self.detector.close()
def decode_frame(data):
 raw=base64.b64decode(data.split(',',1)[-1]);img=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
 if img is None:raise ValueError('Fotograma JPEG inválido')
 return img
