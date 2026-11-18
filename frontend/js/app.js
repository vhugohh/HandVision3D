const video = document.getElementById("cameraVideo");
const startButton = document.getElementById("startButton");
const stopButton = document.getElementById("stopButton");
const cameraPlaceholder = document.getElementById("cameraPlaceholder");
const statusDot = document.getElementById("statusDot");
const connectionText = document.getElementById("connectionText");
const cameraState = document.getElementById("cameraState");
const systemMessage = document.getElementById("systemMessage");

let mediaStream = null;
let socket = null;
let captureTimer = null;
let captureCanvas = document.createElement("canvas");
let sending = false;
let sentFrames = 0;
let fpsWindowStart = performance.now();
let fpsCount = 0;
let lastSentAt = 0;

const CAPTURE_FPS = 12;
const CAPTURE_WIDTH = 640;
const JPEG_QUALITY = 0.62;

function setConnection(connected) {
  statusDot.classList.toggle("online", connected);
  connectionText.textContent = connected ? "Servidor conectado" : "Sistema desconectado";
}

function websocketUrl() {
  const scheme = location.protocol === "https:" ? "wss:" : "ws:";
  return `${scheme}//${location.host}/ws`;
}

function connectSocket() {
  return new Promise((resolve, reject) => {
    socket = new WebSocket(websocketUrl());
    socket.onopen = () => { setConnection(true); resolve(); };
    socket.onerror = () => reject(new Error("No fue posible conectar con el servidor."));
    socket.onclose = () => {
      sending = false;
      setConnection(false);
      if (mediaStream) systemMessage.textContent = "Se perdió la conexión con el servidor.";
    };
    socket.onmessage = (event) => {
      sending = false;
      const data = JSON.parse(event.data);
      if (data.type === "hand_data") updateTelemetry(data);
      if (data.type === "error") systemMessage.textContent = data.message;
    };
  });
}

function updateTelemetry(data) {
  document.getElementById("handCount").textContent = `${data.hand_count} / 2`;
  const labels = data.hands.map(hand => hand.label.toLowerCase());
  document.getElementById("leftState").textContent = labels.includes("left") ? "Detectada" : "No detectada";
  document.getElementById("rightState").textContent = labels.includes("right") ? "Detectada" : "No detectada";
  document.getElementById("resolutionValue").textContent = `${data.width} × ${data.height}`;
  document.getElementById("latencyValue").textContent = `${Math.max(0, Math.round(performance.now() - lastSentAt))} ms`;

  fpsCount++;
  const now = performance.now();
  if (now - fpsWindowStart >= 1000) {
    document.getElementById("fpsValue").textContent = fpsCount;
    fpsCount = 0;
    fpsWindowStart = now;
  }
  systemMessage.textContent = data.hand_count
    ? `${data.hand_count} mano(s) detectada(s). Los datos articulares están listos para el motor 3D.`
    : "Buscando manos. Coloca las manos frente a la cámara.";
}

async function startCamera() {
  try {
    startButton.disabled = true;
    systemMessage.textContent = "Solicitando acceso a la cámara...";
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 24, max: 30 } }
    });
    video.srcObject = mediaStream;
    await video.play();
    video.classList.add("active");
    cameraPlaceholder.style.display = "none";

    await connectSocket();
    cameraState.textContent = "ACTIVA";
    cameraState.style.color = "#59d7a0";
    startButton.textContent = "Cámara activa";
    stopButton.disabled = false;
    systemMessage.textContent = "Cámara conectada. Detectando manos...";

    captureTimer = setInterval(sendFrame, 1000 / CAPTURE_FPS);
  } catch (error) {
    systemMessage.textContent = error.message || "No se pudo iniciar la cámara.";
    stopCamera();
  } finally {
    startButton.disabled = false;
  }
}

function sendFrame() {
  if (!mediaStream || !socket || socket.readyState !== WebSocket.OPEN || sending) return;
  if (!video.videoWidth || !video.videoHeight) return;

  sending = true;
  const scale = Math.min(1, CAPTURE_WIDTH / video.videoWidth);
  captureCanvas.width = Math.round(video.videoWidth * scale);
  captureCanvas.height = Math.round(video.videoHeight * scale);
  const context = captureCanvas.getContext("2d", { alpha: false });
  context.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
  const image = captureCanvas.toDataURL("image/jpeg", JPEG_QUALITY);
  lastSentAt = performance.now();

  try {
    socket.send(JSON.stringify({
      type: "frame",
      timestamp_ms: Date.now(),
      image
    }));
    sentFrames++;
  } catch (error) {
    sending = false;
    systemMessage.textContent = "No se pudo enviar el fotograma.";
  }
}

function stopCamera() {
  if (captureTimer) clearInterval(captureTimer);
  captureTimer = null;
  if (socket) { socket.close(); socket = null; }
  if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
  mediaStream = null;
  video.srcObject = null;
  video.classList.remove("active");
  cameraPlaceholder.style.display = "block";
  cameraState.textContent = "INACTIVA";
  cameraState.style.color = "#f0b86c";
  startButton.textContent = "Iniciar cámara";
  stopButton.disabled = true;
  document.getElementById("handCount").textContent = "0 / 2";
  document.getElementById("leftState").textContent = "No detectada";
  document.getElementById("rightState").textContent = "No detectada";
  document.getElementById("fpsValue").textContent = "0";
  document.getElementById("resolutionValue").textContent = "—";
  document.getElementById("latencyValue").textContent = "—";
  systemMessage.textContent = "Cámara detenida.";
  setConnection(false);
}

startButton.addEventListener("click", startCamera);
stopButton.addEventListener("click", stopCamera);
window.addEventListener("beforeunload", stopCamera);

fetch("/api/status").then(response => response.json()).then(data => {
  systemMessage.textContent = data.status === "ready"
    ? "Motor de detección listo. Inicia la cámara."
    : "El servidor está iniciando el modelo de detección.";
}).catch(() => {
  systemMessage.textContent = "No se pudo consultar el estado del servidor.";
});
