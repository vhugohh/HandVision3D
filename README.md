# HandVision 3D

Aplicación web de seguimiento bilateral de manos con Python, FastAPI, MediaPipe Tasks y Three.js. La cámara se captura en el navegador; los fotogramas JPEG se envían por WebSocket al backend y la pose estimada anima dos modelos 3D en el navegador.

## Funciones
- Detección de hasta dos manos.
- Flexión estimada de articulaciones MCP/PIP/DIP (pulgar: MCP/IP).
- Orientación de palma mediante quaternion y ángulos Euler.
- Gestos geométricos: palma abierta, puño, pinza y señalar.
- Suavizado temporal de pose.
- Modelos 3D procedurales con palma, dedos, volumen de articulaciones y uñas; sin landmarks ni esqueletos visibles.
- Indicadores de cámara, FPS, resolución, latencia aproximada y telemetría por dedo.
- Evento `handvision:pose` y `window.handVisionLatestPose` para integraciones adicionales.

## Requisitos y ejecución local
Python 3.11, pip y navegador moderno. Se requiere internet la primera vez para descargar el modelo MediaPipe y para cargar Three.js desde CDN.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Abre http://127.0.0.1:8000 y concede permiso de cámara. Los navegadores permiten cámara en localhost o en un sitio HTTPS.

## Render + GitHub
1. Sube el contenido del repositorio a GitHub.
2. Crea un Web Service en Render conectado al repositorio.
3. Render utilizará el Dockerfile y `render.yaml`.
4. Espera el despliegue y abre la URL HTTPS para conceder permiso de cámara.
5. El modelo `hand_landmarker.task` se descarga automáticamente al iniciar el backend y se almacena en `mediapipe_models/`.

Se recomienda un plan de Render con memoria suficiente para MediaPipe. Los planes gratuitos pueden suspender servicios y limitar la fluidez. Si el sistema de archivos es efímero, el modelo se volverá a descargar en cada arranque.

## Endpoints y datos
- `GET /health`: estado del servicio.
- `WS /ws`: recibe JSON `{ "type": "frame", "image": "data:image/jpeg;base64,..." }` y devuelve mensajes `type: pose` con `hands[]`.
- Cada mano contiene `label`, `confidence`, `position`, `orientation.quaternion`, `orientation.euler`, `fingers`, `pinch_ratio` y `gesture`.

```javascript
window.addEventListener('handvision:pose', (event) => {
  const { hands, hand_count } = event.detail;
  // Integrar datos en otros componentes Three.js.
});
```

## Limitaciones técnicas
Los ángulos y gestos son estimaciones basadas en los landmarks de MediaPipe, no mediciones clínicas. Los modelos 3D son mallas procedurales estilizadas con volumen y materiales de apariencia cutánea; no son escaneos anatómicos hiperrealistas ni modelos médicos. La orientación de mano depende de la perspectiva y visibilidad. La latencia varía según equipo, conexión y recursos del servidor. El vídeo no se almacena: se procesa como flujo de fotogramas.
