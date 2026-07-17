requireAuth();

document.getElementById("save-btn").addEventListener("click", async () => {
  const errorEl = document.getElementById("onboarding-error");
  errorEl.classList.remove("show");
  const age = parseInt(document.getElementById("age").value, 10);
  const gender = document.getElementById("gender").value;
  if (!age || age < 1 || age > 120) {
    errorEl.textContent = "올바른 나이를 입력해주세요";
    errorEl.classList.add("show");
    return;
  }
  try {
    await apiFetch("/api/profile", { method: "PUT", json: { age, gender } });
    window.location.href = "/bodymap.html";
  } catch (e) {
    errorEl.textContent = e.message;
    errorEl.classList.add("show");
  }
});
