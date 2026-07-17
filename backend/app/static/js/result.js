requireAuth();

const params = new URLSearchParams(window.location.search);
const captureId = params.get("capture_id");

async function load() {
  if (!captureId) {
    window.location.href = "/bodymap.html";
    return;
  }
  try {
    const capture = await apiFetch(`/api/captures/${captureId}`);

    document.getElementById("orig-img").src = capture.image_path;
    document.getElementById("heatmap-img").src = capture.heatmap_path || capture.image_path;
    document.getElementById("classification").textContent = capture.classification;
    document.getElementById("confidence").textContent = `Confidence ${Math.round(capture.confidence * 100)}% · ${bodyPartLabel(
      capture.body_part
    )}`;

    const pill = document.getElementById("urgency-pill");
    if (capture.urgency === "high") {
      pill.textContent = "High Urgency";
      pill.classList.add("high");
      document.getElementById("high-urgency-block").style.display = "block";
    } else {
      pill.textContent = "Low Urgency";
      pill.classList.add("low");
      document.getElementById("low-urgency-block").style.display = "block";
    }

    document.getElementById("gemini-report").textContent = capture.gemini_report || "";

    document.getElementById("pdf-btn")?.addEventListener("click", () => downloadPdf());
    document.getElementById("pdf-btn-low")?.addEventListener("click", () => downloadPdf());

    document.getElementById("loading").style.display = "none";
    document.getElementById("content").style.display = "block";
  } catch (e) {
    alert(e.message);
    window.location.href = "/bodymap.html";
  }
}

async function downloadPdf() {
  try {
    const res = await fetch(`/api/reports/${captureId}/pdf`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error("Failed to generate PDF");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `skin_report_${captureId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert(e.message);
  }
}

load();
