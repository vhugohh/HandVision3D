# HandVision 3D — Etapa 1

Aplicación web para detectar hasta dos manos mediante Python, OpenCV y MediaPipe, y transmitir los datos articulares al navegador. La interfaz no dibuja ni muestra los landmarks. En esta etapa se prepara el flujo de captura y datos; el renderizado anatómico con Three.js y los modelos GLB se incorporarán en la Etapa 3.

## Requisitos

- Python 3.11
- Cámara web
- Google Chrome, Edge o Firefox actualizado
- Conexión a Internet durante la primera ejecución para descargar el modelo de MediaPipe

## Ejecutar localmente en Windows

Abre PowerShell en la carpeta del proyecto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Si PowerShell bloquea la activación del entorno, ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Abre `http://127.0.0.1:8000`. Acepta el permiso de cámara y pulsa **Iniciar cámara**.

## Ejecutar localmente en macOS o Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

## Endpoints

- `GET /` — interfaz web.
- `GET /health` — health check para Render.
- `GET /api/status` — estado del detector.
- `WS /ws` — recibe fotogramas JPEG codificados en base64 y devuelve detecciones.

## Publicar en GitHub

Crea un repositorio vacío llamado `HandVision3D`. Desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "HandVision 3D - Etapa 1"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/HandVision3D.git
git push -u origin main
```

Sustituye `TU_USUARIO` por tu usuario real de GitHub. No subas el entorno `.venv` ni el modelo descargado.

## Desplegar en Render

1. Sube el repositorio a GitHub.
2. En Render selecciona **New + > Blueprint** o crea un Web Service conectado al repositorio.
3. Si usas Blueprint, Render leerá `render.yaml`.
4. Si creas el servicio manualmente:
   - Runtime: Docker (recomendado; usa el `Dockerfile` incluido)
   - Dockerfile path: `./Dockerfile`
   - Docker context: `.`
5. Espera a que termine el despliegue y abre la URL HTTPS asignada.
6. Acepta el permiso de cámara del navegador.

La cámara se captura en el navegador del visitante. Los fotogramas se envían por WebSocket al backend Python. El navegador debe usar HTTPS en producción para permitir el acceso a la cámara.

## Comprobar el servicio

Abre `/health` y verifica una respuesta similar a:

```json
{"status":"ok","application":"HandVision 3D","version":"0.1.0"}
```

Abre `/api/status`; cuando el modelo termine de iniciar, `status` debe ser `ready`.

## Consideraciones de esta etapa

- Se procesan como máximo dos manos.
- Cada mano produce 21 puntos internos y ángulos articulares aproximados.
- No se dibujan landmarks sobre la vista de cámara ni sobre el área 3D.
- La vista previa de cámara sí se muestra en un panel pequeño.
- La etapa 1 no incluye todavía modelos anatómicos ni animación 3D.
- Se instala `opencv-contrib-python` porque MediaPipe 0.10.21 declara la variante contrib como dependencia; no mezcles paquetes OpenCV distintos en el mismo entorno.
- El plan gratuito de Render puede tener recursos limitados y suspender servicios inactivos; la primera petición puede tardar mientras el servicio despierta.
- El modelo MediaPipe se descarga al iniciar el backend. El servicio necesita acceso saliente a Internet durante esa descarga.

## Tecnologías

Python · OpenCV · MediaPipe Tasks · FastAPI · WebSocket · HTML · CSS · JavaScript
