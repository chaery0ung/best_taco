requireAuth();

const params = new URLSearchParams(window.location.search);
const lesionId = params.get("id");

function urgencyPill(urgency) {
  return urgency === "high" ? '<span class="pill high">긴급</span>' : '<span class="pill low">관찰</span>';
}

async function load() {
  if (!lesionId) {
    window.location.href = "/bodymap.html";
    return;
  }
  try {
    const lesion = await apiFetch(`/api/lesions/${lesionId}`);
    document.getElementById("lesion-title").textContent = `${bodyPartLabel(lesion.body_part)} 히스토리`;

    const timelineEl = document.getElementById("timeline");
    if (lesion.captures.length === 0) {
      timelineEl.innerHTML = '<p class="center-note">아직 촬영 기록이 없습니다. 첫 촬영을 시작해보세요.</p>';
    } else {
      const sorted = [...lesion.captures].reverse();
      timelineEl.innerHTML = sorted
        .map((c, idx) => {
          const prev = sorted[idx + 1];
          const changeText = !prev
            ? "최초 등록"
            : prev.classification === c.classification
            ? "변화 없음 ✅"
            : "변화 감지 ⚠️";
          return `
          <a class="timeline-item" href="/result.html?capture_id=${c.id}" style="text-decoration:none; color:inherit;">
            <img src="${c.image_path}" alt="촬영 사진" />
            <div class="body">
              <div><strong>${c.classification}</strong> ${urgencyPill(c.urgency)}</div>
              <div class="meta">${formatDate(c.created_at)} · 신뢰도 ${Math.round(c.confidence * 100)}%</div>
              <div class="meta">${changeText}</div>
            </div>
          </a>`;
        })
        .join("");
    }

    document.getElementById("retake-btn").addEventListener("click", () => {
      window.location.href = `/capture.html?lesion_id=${lesionId}`;
    });

    document.getElementById("loading").style.display = "none";
    document.getElementById("content").style.display = "block";
  } catch (e) {
    alert(e.message);
    window.location.href = "/bodymap.html";
  }
}

load();
