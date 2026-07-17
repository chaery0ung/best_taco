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
    throw new Error("Your session has expired");
  }
  if (!res.ok) {
    let detail = "An error occurred while processing the request";
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
  head: "Head",
  neck: "Neck",
  chest: "Chest",
  abdomen: "Abdomen",
  back: "Back",
  left_upper_arm: "Left Upper Arm",
  left_forearm: "Left Forearm",
  right_upper_arm: "Right Upper Arm",
  right_forearm: "Right Forearm",
  left_thigh: "Left Thigh",
  left_lower_leg: "Left Lower Leg",
  right_thigh: "Right Thigh",
  right_lower_leg: "Right Lower Leg",
};

function bodyPartLabel(key) {
  return BODY_PART_LABELS[key] || key;
}
