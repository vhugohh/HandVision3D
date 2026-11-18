import base64
import binascii
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIR, MAX_FRAME_BYTES
from .hand_detector import HandDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("handvision3d")

detector = HandDetector()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando HandVision 3D...")
    detector.start()
    logger.info("MediaPipe Hand Landmarker listo.")
    yield
    detector.close()
    logger.info("Detector cerrado.")


app = FastAPI(
    title="HandVision 3D",
    version="0.1.0",
    description="Detección de manos para animación tridimensional.",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok", "application": "HandVision 3D", "version": "0.1.0"}


@app.get("/api/status")
async def api_status():
    return {
        "status": "ready" if detector.landmarker is not None else "starting",
        "max_hands": 2,
        "landmarks_per_hand": 21,
        "rendering_3d": False,
        "stage": 1,
    }


@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.websocket("/ws")
async def hand_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("Cliente WebSocket conectado.")
    last_frame_time = 0.0

    try:
        while True:
            message = await websocket.receive_json()

            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if message.get("type") != "frame":
                await websocket.send_json({
                    "type": "error",
                    "message": "Tipo de mensaje no reconocido."
                })
                continue

            data_url = message.get("image", "")
            if not isinstance(data_url, str) or "," not in data_url:
                await websocket.send_json({
                    "type": "error", "message": "Formato de imagen inválido."
                })
                continue

            encoded = data_url.split(",", 1)[1]
            if len(encoded) > (MAX_FRAME_BYTES * 4 // 3 + 16):
                await websocket.send_json({
                    "type": "error", "message": "Fotograma demasiado grande."
                })
                continue

            try:
                jpeg_bytes = base64.b64decode(encoded, validate=True)
                if len(jpeg_bytes) > MAX_FRAME_BYTES:
                    raise ValueError("Fotograma demasiado grande.")
                client_timestamp = int(message.get("timestamp_ms", time.time() * 1000))
                result = detector.process_jpeg(jpeg_bytes, client_timestamp)
                now = time.monotonic()
                result["server_processing_fps_window"] = (
                    round(1.0 / (now - last_frame_time), 1) if last_frame_time else 0
                )
                last_frame_time = now
                await websocket.send_json(result)
            except (ValueError, binascii.Error) as exc:
                await websocket.send_json({"type": "error", "message": str(exc)})
            except Exception:
                logger.exception("Error procesando fotograma.")
                await websocket.send_json({
                    "type": "error",
                    "message": "Error interno al procesar el fotograma."
                })

    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado.")
    except Exception:
        logger.exception("Conexión WebSocket finalizada por error.")
