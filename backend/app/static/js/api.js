const TOKEN_KEY = "dermalyze_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
function requireAuth() {
  if (!getToken()) {
    window.location.href = "/";
  }
}

async function apiFetch(path, options = {}) {
  const headers = options.headers ? { ...options.headers } : {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (options.json !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.json);
  }
  const res = await fetch(path, { ...options, headers });
  if (res.status === 401) {
    clearToken();
    window.location.href = "/";
    throw new Error("인증이 만료되었습니다");
  }
  if (!res.ok) {
    let detail = "요청 처리 중 오류가 발생했습니다";
    try {
      const body = await res.json();
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail)) {
        detail = body.detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
      }
    } catch (e) {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res;
}

const BODY_PART_LABELS = {
  head: "머리",
  neck: "목",
  chest: "가슴",
  abdomen: "복부",
  back: "등",
  left_upper_arm: "왼쪽 위팔",
  left_forearm: "왼쪽 아래팔",
  right_upper_arm: "오른쪽 위팔",
  right_forearm: "오른쪽 아래팔",
  left_thigh: "왼쪽 허벅지",
  left_lower_leg: "왼쪽 종아리",
  right_thigh: "오른쪽 허벅지",
  right_lower_leg: "오른쪽 종아리",
};

function bodyPartLabel(key) {
  return BODY_PART_LABELS[key] || key;
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("ko-KR", { year: "numeric", month: "long", day: "numeric" });
}
