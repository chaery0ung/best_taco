requireAuth();

let lesionsByPart = {};
let selectedPart = null;

document.getElementById("logout-btn").addEventListener("click", () => {
  clearToken();
  window.location.href = "/";
});

document.getElementById("tab-front").addEventListener("click", () => showView("front"));
document.getElementById("tab-back").addEventListener("click", () => showView("back"));

function showView(view) {
  document.getElementById("svg-front").style.display = view === "front" ? "block" : "none";
  document.getElementById("svg-back").style.display = view === "back" ? "block" : "none";
}

function selectPart(part) {
  selectedPart = part;
  document.getElementById("empty-hint").style.display = "none";
  const panel = document.getElementById("part-panel");
  panel.style.display = "block";
  document.getElementById("part-title").textContent = bodyPartLabel(part);
}

function applyMapColors() {
  document.querySelectorAll(".body-part").forEach((el) => {
    const part = el.dataset.part;
    const lesions = lesionsByPart[part] || [];
    el.classList.remove("has-lesion", "has-high");
    if (lesions.some((l) => l.latest_urgency === "high")) {
      el.classList.add("has-high");
    } else if (lesions.length > 0) {
      el.classList.add("has-lesion");
    }
  });
}

async function loadLesions() {
  const lesions = await apiFetch("/api/lesions");
  lesionsByPart = {};
  lesions.forEach((l) => {
    if (!lesionsByPart[l.body_part]) lesionsByPart[l.body_part] = [];
    lesionsByPart[l.body_part].push(l);
  });
  applyMapColors();
}

document.querySelectorAll(".body-part").forEach((el) => {
  el.addEventListener("click", () => selectPart(el.dataset.part));
});

document.getElementById("take-photo-btn").addEventListener("click", async () => {
  if (!selectedPart) return;
  const btn = document.getElementById("take-photo-btn");
  btn.disabled = true;
  try {
    const lesion = await apiFetch("/api/lesions", { method: "POST", json: { body_part: selectedPart } });
    window.location.href = `/capture.html?lesion_id=${lesion.id}`;
  } catch (e) {
    alert(e.message);
    btn.disabled = false;
  }
});

loadLesions();
