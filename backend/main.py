import asyncio,json,logging
from contextlib import asynccontextmanager
from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .hand_detector import HandDetector,decode_frame
logging.basicConfig(level=logging.INFO);log=logging.getLogger('handvision');detector=None
@asynccontextmanager
async def lifespan(app):
 global detector;detector=HandDetector();yield
 if detector:detector.close()
app=FastAPI(title='HandVision 3D',version='1.0.0',lifespan=lifespan)
app.mount('/static',StaticFiles(directory='frontend'),name='static')
@app.get('/',response_class=HTMLResponse)
async def home():
 with open('frontend/index.html',encoding='utf-8') as f:return f.read()
@app.get('/health')
async def health():return {'status':'ok','application':'HandVision 3D'}
@app.websocket('/ws')
async def ws_endpoint(ws:WebSocket):
 await ws.accept()
 try:
  while True:
   msg=json.loads(await ws.receive_text())
   if msg.get('type')!='frame':continue
   try:
    frame=decode_frame(msg['image']);result=await asyncio.to_thread(detector.process,frame);await ws.send_json({'type':'pose',**result})
   except Exception as e:log.exception('frame error');await ws.send_json({'type':'error','message':str(e)})
 except WebSocketDisconnect:pass
