requireAuth();

const params = new URLSearchParams(window.location.search);
const lesionId = params.get("lesion_id");
if (!lesionId) window.location.href = "/bodymap.html";

const video = document.getElementById("video");
const filePreview = document.getElementById("file-preview");
const overlay = document.getElementById("overlay");
const ctx = overlay.getContext("2d");
const cameraWrap = document.querySelector(".camera-wrap");

let mode = null; // "camera" | "file"
let selectedFile = null;

function resizeOverlay() {
  const rect = cameraWrap.getBoundingClientRect();
  overlay.width = rect.width;
  overlay.height = rect.height;
  drawGuides();
}
window.addEventListener("resize", resizeOverlay);

function drawGuides() {
  const w = overlay.width;
  const h = overlay.height;
  ctx.clearRect(0, 0, w, h);

  // Center distance-guide circle: frame the lesion here.
  const cx = w / 2;
  const cy = h / 2;
  const r = Math.min(w, h) * 0.28;
  ctx.strokeStyle = "rgba(255,255,255,0.9)";
  ctx.lineWidth = 2;
  ctx.setLineDash([8, 6]);
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.stroke();

  // Coin reference circle (~24mm coin) in the corner for scale calibration.
  const coinR = Math.min(w, h) * 0.06;
  const coinX = coinR + 16;
  const coinY = h - coinR - 16;
  ctx.strokeStyle = "rgba(242,193,78,0.95)";
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.arc(coinX, coinY, coinR, 0, Math.PI * 2);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "rgba(242,193,78,0.95)";
  ctx.font = "10px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("Coin", coinX, coinY + coinR + 14);

  ctx.fillStyle = "rgba(255,255,255,0.9)";
  ctx.font = "11px sans-serif";
  ctx.fillText("Center lesion here", cx, cy - r - 10);
}

async function loadLesionTitle() {
  try {
    const lesion = await apiFetch(`/api/lesions/${lesionId}`);
    document.getElementById("capture-title").textContent = `${bodyPartLabel(lesion.body_part)} Capture`;
  } catch (e) {
    /* non-fatal */
  }
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
      audio: false,
    });
    video.srcObject = stream;
    video.style.display = "block";
    mode = "camera";
    resizeOverlay();
  } catch (e) {
    document.getElementById("camera-error").textContent =
      "Camera unavailable. Please use the 'Upload / Take Photo' button below.";
    document.getElementById("camera-error").classList.add("show");
    document.getElementById("shutter-btn").disabled = true;
  }
}

document.getElementById("file-btn").addEventListener("click", () => {
  document.getElementById("file-input").click();
});

document.getElementById("file-input").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  selectedFile = file;
  mode = "file";
  video.style.display = "none";
  filePreview.style.display = "block";
  filePreview.src = URL.createObjectURL(file);
  filePreview.onload = resizeOverlay;
});

document.getElementById("shutter-btn").addEventListener("click", async () => {
  if (mode === "camera") {
    const off = document.createElement("canvas");
    off.width = video.videoWidth;
    off.height = video.videoHeight;
    off.getContext("2d").drawImage(video, 0, 0);
    off.toBlob((blob) => uploadCapture(blob), "image/png");
  } else if (mode === "file" && selectedFile) {
    uploadCapture(selectedFile);
  } else {
    alert("Please select a photo first");
  }
});

async function uploadCapture(blob) {
  document.getElementById("uploading").style.display = "block";
  document.getElementById("shutter-btn").disabled = true;
  document.getElementById("file-btn").disabled = true;
  try {
    const formData = new FormData();
    formData.append("file", blob, "capture.png");
    const res = await fetch(`/api/lesions/${lesionId}/captures`, {
      method: "POST",
      headers: { Authorization: `Bearer ${getToken()}` },
      body: formData,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "Upload failed");
    }
    const capture = await res.json();
    window.location.href = `/result.html?capture_id=${capture.id}`;
  } catch (e) {
    alert(e.message);
    document.getElementById("uploading").style.display = "none";
    document.getElementById("shutter-btn").disabled = false;
    document.getElementById("file-btn").disabled = false;
  }
}

loadLesionTitle();
startCamera();
resizeOverlay();
