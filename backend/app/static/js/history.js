requireAuth();

function changeBadge(status) {
  if (status === "changed") return '<span class="pill high">변화 감지 ⚠️</span>';
  if (status === "no_change") return '<span class="pill low">변화 없음 ✅</span>';
  return '<span class="pill neutral">신규 등록</span>';
}

async function load() {
  const listEl = document.getElementById("list");
  try {
    const lesions = await apiFetch("/api/lesions");
    if (lesions.length === 0) {
      listEl.innerHTML = '<p class="center-note">아직 등록된 병변이 없습니다. 신체 지도에서 부위를 선택해 등록해보세요.</p>';
      return;
    }
    listEl.innerHTML = lesions
      .map(
        (l) => `
      <a class="lesion-item" href="/lesion.html?id=${l.id}">
        <div>
          <div>${bodyPartLabel(l.body_part)}${l.label ? " · " + l.label : ""}</div>
          <div class="meta">${l.latest_classification || "촬영 기록 없음"}${
          l.latest_created_at ? " · " + formatDate(l.latest_created_at) : ""
        }</div>
        </div>
        ${changeBadge(l.change_status)}
      </a>`
      )
      .join("");
  } catch (e) {
    listEl.innerHTML = `<p class="center-note">${e.message}</p>`;
  }
}

load();
