document.getElementById("show-signup").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("login-form").style.display = "none";
  document.getElementById("signup-form").style.display = "block";
});
document.getElementById("show-login").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("signup-form").style.display = "none";
  document.getElementById("login-form").style.display = "block";
});

async function afterAuth() {
  try {
    const me = await apiFetch("/api/auth/me");
    if (me.age) {
      window.location.href = "/bodymap.html";
    } else {
      window.location.href = "/onboarding.html";
    }
  } catch (e) {
    window.location.href = "/onboarding.html";
  }
}

document.getElementById("login-btn").addEventListener("click", async () => {
  const errorEl = document.getElementById("login-error");
  errorEl.classList.remove("show");
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  if (!email || !password) {
    errorEl.textContent = "Please enter your email and password";
    errorEl.classList.add("show");
    return;
  }
  try {
    const res = await apiFetch("/api/auth/login", { method: "POST", json: { email, password } });
    setToken(res.access_token);
    await afterAuth();
  } catch (e) {
    errorEl.textContent = e.message;
    errorEl.classList.add("show");
  }
});

document.getElementById("signup-btn").addEventListener("click", async () => {
  const errorEl = document.getElementById("signup-error");
  errorEl.classList.remove("show");
  const name = document.getElementById("signup-name").value.trim();
  const email = document.getElementById("signup-email").value.trim();
  const password = document.getElementById("signup-password").value;
  if (!name || !email || !password) {
    errorEl.textContent = "Please fill in all fields";
    errorEl.classList.add("show");
    return;
  }
  try {
    const res = await apiFetch("/api/auth/signup", { method: "POST", json: { name, email, password } });
    setToken(res.access_token);
    window.location.href = "/onboarding.html";
  } catch (e) {
    errorEl.textContent = e.message;
    errorEl.classList.add("show");
  }
});
