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

function changeBadge(status) {
  if (status === "changed") return '<span class="pill high">변화 감지 ⚠️</span>';
  if (status === "no_change") return '<span class="pill low">변화 없음 ✅</span>';
  return '<span class="pill neutral">신규 등록</span>';
}

function renderPartPanel(part) {
  selectedPart = part;
  document.getElementById("empty-hint").style.display = "none";
  const panel = document.getElementById("part-panel");
  panel.style.display = "block";
  document.getElementById("part-title").textContent = bodyPartLabel(part);

  const lesions = lesionsByPart[part] || [];
  const listEl = document.getElementById("part-lesions");
  if (lesions.length === 0) {
    listEl.innerHTML = '<p class="center-note" style="padding:6px 0;">등록된 병변이 없습니다</p>';
  } else {
    listEl.innerHTML = lesions
      .map(
        (l) => `
      <a class="lesion-item" href="/lesion.html?id=${l.id}">
        <div>
          <div>${l.label || "병변 #" + l.id}</div>
          <div class="meta">${l.latest_classification || "촬영 기록 없음"}</div>
        </div>
        ${changeBadge(l.change_status)}
      </a>`
      )
      .join("");
  }
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
  el.addEventListener("click", () => renderPartPanel(el.dataset.part));
});

document.getElementById("add-lesion-btn").addEventListener("click", async () => {
  if (!selectedPart) return;
  const btn = document.getElementById("add-lesion-btn");
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
