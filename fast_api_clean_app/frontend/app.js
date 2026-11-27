const API = "";

// --- Storage ---
function getTokens() {
    return {
        access: localStorage.getItem("access_token"),
        refresh: localStorage.getItem("refresh_token"),
    };
}
function setTokens(access, refresh) {
    localStorage.setItem("access_token", access);
    if (refresh) localStorage.setItem("refresh_token", refresh);
}
function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
}

// --- HTTP with auto-refresh ---
async function api(path, options = {}) {
    const { access, refresh } = getTokens();
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    if (access) headers["Authorization"] = `Bearer ${access}`;

    let res = await fetch(API + path, { ...options, headers });

    if (res.status === 401 && refresh) {
        const refreshed = await tryRefresh(refresh);
        if (refreshed) {
            headers["Authorization"] = `Bearer ${refreshed.access_token}`;
            res = await fetch(API + path, { ...options, headers });
        } else {
            clearTokens();
            showAuth();
            throw new Error("Session expired");
        }
    }
    return res;
}

async function tryRefresh(refresh) {
    const res = await fetch(API + "/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data;
}

// --- Views ---
function showAuth() {
    document.getElementById("auth-view").classList.remove("hidden");
    document.getElementById("dashboard-view").classList.add("hidden");
}

function showDashboard() {
    document.getElementById("auth-view").classList.add("hidden");
    document.getElementById("dashboard-view").classList.remove("hidden");
    loadDashboard();
}

function showError(msg) {
    const el = document.getElementById("auth-error");
    el.textContent = msg;
    el.classList.remove("hidden");
    setTimeout(() => el.classList.add("hidden"), 4000);
}

// --- Auth ---
async function doLogin() {
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const res = await fetch(API + "/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Ошибка" }));
        showError(err.detail || "Ошибка входа");
        return;
    }
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    showDashboard();
}

async function doRegister() {
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const display_name = document.getElementById("reg-name").value.trim();
    const res = await fetch(API + "/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, display_name }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Ошибка" }));
        showError(err.detail || "Ошибка регистрации");
        return;
    }
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    showDashboard();
}

async function doLogout() {
    const { refresh } = getTokens();
    if (refresh) {
        try {
            await api("/auth/logout", {
                method: "POST",
                body: JSON.stringify({ refresh_token: refresh }),
            });
        } catch {}
    }
    clearTokens();
    showAuth();
}

function steamLogin() {
    window.location.href = "/auth/steam/login";
}

// --- Dashboard ---
async function loadDashboard() {
    await Promise.all([loadProfile(), loadPlatforms(), loadGameState()]);
}

async function loadProfile() {
    const res = await api("/auth/me");
    if (!res.ok) return;
    const p = await res.json();
    const el = document.getElementById("profile-info");
    el.innerHTML = `
        <span class="label">Имя:</span><span class="value">${escapeHtml(p.display_name)}</span>
        <span class="label">Email:</span><span class="value">${escapeHtml(p.email || "—")}</span>
        <span class="label">ID:</span><span class="value">${p.id}</span>
        <span class="label">Статус:</span><span class="value">${p.status}</span>
    `;
}

async function loadPlatforms() {
    const res = await api("/auth/me/platforms");
    if (!res.ok) return;
    const links = await res.json();
    const el = document.getElementById("platforms-list");
    if (!links.length) {
        el.innerHTML = '<p class="empty">Платформы не привязаны</p>';
        return;
    }
    el.innerHTML = links.map(l => `
        <div class="platform-row">
            <span class="platform-name">${escapeHtml(l.platform)}</span>
            <span class="platform-id">${escapeHtml(l.platform_user_id)}</span>
        </div>
    `).join("");
}

async function loadGameState() {
    const res = await api("/auth/me/game-state");
    if (!res.ok) return;
    const { data } = await res.json();
    document.getElementById("click-count").textContent = data.clicks || 0;
}

async function doClick() {
    const btn = document.getElementById("click-btn");
    btn.disabled = true;
    try {
        const res = await api("/auth/me/game-state/counters/clicks/increment", {
            method: "POST",
        });
        if (res.ok) {
            const { data } = await res.json();
            document.getElementById("click-count").textContent = data.clicks || 0;
        } else {
            const err = await res.json().catch(() => ({}));
            console.error("click failed:", res.status, err);
        }
    } finally {
        btn.disabled = false;
    }
}

// --- Steam ---
async function linkSteam() {
    const res = await api("/auth/steam/link");
    if (!res.ok) {
        alert("Не удалось инициировать привязку");
        return;
    }
    const data = await res.json();
    window.location.href = data.redirect_url;
}

function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
}

// --- Steam callback handling ---
function handleRedirectFragment() {
    const hash = window.location.hash.substring(1);
    if (!hash) return;
    const params = new URLSearchParams(hash);
    const access = params.get("access_token");
    const refresh = params.get("refresh_token");
    const linked = params.get("steam_linked");

    if (access && refresh) {
        setTokens(access, refresh);
        history.replaceState(null, "", "/"); // чистим URL от токенов
        showDashboard();
    } else if (linked) {
        history.replaceState(null, "", "/");
        showDashboard();
    }
}

// --- Bootstrap ---
window.addEventListener("DOMContentLoaded", () => {
    handleRedirectFragment();
    const { access } = getTokens();
    if (access) showDashboard();
    else showAuth();
});
