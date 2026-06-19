/**
 * app.js — SEMS Frontend Logic
 * ────────────────────────────
 * Handles:
 *  - Login / logout (simple role-based)
 *  - Page navigation (single-page app feel)
 *  - Prediction form submission → Flask API
 *  - Analytics charts using Chart.js
 *  - Buildings table population
 */

const API_BASE = "http://localhost:5000";

// ── Simple user store (in a real app this would use JWT tokens) ──────────────
const USERS = {
  "admin":  { password: "admin123",  role: "Admin",  name: "Admin User" },
  "prachi": { password: "sems2026",  role: "Student", name: "Prachi Pimpalkar" },
  "user":   { password: "user123",   role: "User",   name: "Demo User" }
};

let currentUser = null;
let charts = {};   // Stores Chart.js instances so we can destroy & recreate


// ════════════════════════════════════════════════════════════════════════════
//  AUTH
// ════════════════════════════════════════════════════════════════════════════

function login() {
  const username = document.getElementById("loginUsername").value.trim().toLowerCase();
  const password = document.getElementById("loginPassword").value;
  const errBox   = document.getElementById("loginError");

  errBox.style.display = "none";

  if (!username || !password) {
    showLoginError("Please enter username and password.");
    return;
  }

  const user = USERS[username];
  if (!user || user.password !== password) {
    showLoginError("Invalid username or password. Try: admin / admin123");
    return;
  }

  currentUser = { username, ...user };
  document.getElementById("loginPage").style.display   = "none";
  document.getElementById("dashboardApp").style.display = "flex";

  document.getElementById("topbarTitle").textContent = `Welcome, ${user.name}`;
  document.getElementById("userAvatar").textContent  = user.name[0].toUpperCase();
  document.getElementById("userName").textContent    = user.name;
  document.getElementById("userRole").textContent    = user.role;

  // Show admin-only nav item
  if (user.role === "Admin") {
    document.getElementById("adminNav").style.display = "flex";
  }

  navigateTo("dashboard");
}

function logout() {
  currentUser = null;
  document.getElementById("dashboardApp").style.display = "none";
  document.getElementById("loginPage").style.display     = "flex";
  document.getElementById("loginUsername").value = "";
  document.getElementById("loginPassword").value = "";
  // Destroy charts to avoid canvas reuse errors
  Object.values(charts).forEach(c => c && c.destroy());
  charts = {};
}

function showLoginError(msg) {
  const errBox = document.getElementById("loginError");
  errBox.textContent = msg;
  errBox.style.display = "block";
}

// Allow Enter key on login form
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && document.getElementById("loginPage").style.display !== "none") {
    login();
  }
});


// ════════════════════════════════════════════════════════════════════════════
//  NAVIGATION
// ════════════════════════════════════════════════════════════════════════════

function navigateTo(pageId) {
  // Hide all pages
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));

  // Show target page
  const target = document.getElementById("page-" + pageId);
  if (target) target.classList.add("active");

  // Mark nav item active
  const navItem = document.querySelector(`[data-page="${pageId}"]`);
  if (navItem) navItem.classList.add("active");

  // Update topbar title
  const titles = {
    dashboard: "Dashboard Overview",
    predict:   "Energy Prediction",
    analytics: "Analytics & Charts",
    buildings: "Buildings Report",
    admin:     "Admin Panel"
  };
  document.getElementById("topbarTitle").textContent = titles[pageId] || "SEMS";

  // Load page-specific data
  if (pageId === "dashboard")  loadDashboard();
  if (pageId === "analytics")  loadAnalytics();
  if (pageId === "buildings")  loadBuildings();
  if (pageId === "predict")    loadPredictOptions();
}


// ════════════════════════════════════════════════════════════════════════════
//  DASHBOARD
// ════════════════════════════════════════════════════════════════════════════

async function loadDashboard() {
  try {
    const res  = await fetch(`${API_BASE}/api/analytics`);
    const data = await res.json();
    if (!data.success) return;

    // Compute summary stats
    const totalVals    = Object.values(data.building_totals);
    const totalEnergy  = totalVals.reduce((a, b) => a + b, 0).toFixed(0);
    const avgMonthly   = (Object.values(data.monthly_avg).reduce((a, b) => a + b, 0) / 12).toFixed(0);
    const highCount    = data.usage_counts["High"] || 0;

    document.getElementById("stat-total").textContent    = `${Number(totalEnergy).toLocaleString()} kWh`;
    document.getElementById("stat-monthly").textContent  = `${Number(avgMonthly).toLocaleString()} kWh`;
    document.getElementById("stat-buildings").textContent = Object.keys(data.building_totals).length;
    document.getElementById("stat-high").textContent     = `${highCount} days`;

    // Monthly trend mini chart
    renderMiniChart("chartDashMonthly", data.monthly_avg,
      ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
      "Monthly Avg (kWh)", "#1a73e8");

    // Building pie chart
    renderDonut("chartDashBuilding", data.building_totals);

    // Populate top5 table
    populateTop5(data.top5_high_consumption);

  } catch (err) {
    console.error("Dashboard load error:", err);
  }
}

function renderMiniChart(canvasId, monthlyData, labels, label, color) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  charts[canvasId] = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label,
        data: labels.map((_, i) => monthlyData[i + 1] || 0),
        borderColor: color,
        backgroundColor: color + "22",
        fill: true,
        tension: 0.4,
        pointRadius: 3
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: false } }
    }
  });
}

function renderDonut(canvasId, buildingData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  const COLORS = ["#1a73e8","#34a853","#ea4335","#fbbc04","#9c27b0","#00bcd4","#ff5722","#607d8b"];

  charts[canvasId] = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(buildingData),
      datasets: [{ data: Object.values(buildingData), backgroundColor: COLORS, borderWidth: 2 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "right", labels: { font: { size: 11 } } } }
    }
  });
}

function populateTop5(rows) {
  const tbody = document.getElementById("top5Body");
  if (!tbody) return;
  tbody.innerHTML = rows.map(r => `
    <tr>
      <td>${r.Date}</td>
      <td>${r.Building_Name}</td>
      <td><strong>${r.Energy_Consumption_kWh}</strong></td>
      <td><span class="badge badge-${r.Usage_Level.toLowerCase()}">${r.Usage_Level}</span></td>
    </tr>
  `).join("");
}


// ════════════════════════════════════════════════════════════════════════════
//  PREDICTION
// ════════════════════════════════════════════════════════════════════════════

async function loadPredictOptions() {
  try {
    const res  = await fetch(`${API_BASE}/api/options`);
    const data = await res.json();
    if (!data.success) return;

    const bSel = document.getElementById("predBuilding");
    const uSel = document.getElementById("predUsage");
    bSel.innerHTML = data.data.buildings.map(b => `<option value="${b}">${b}</option>`).join("");
    uSel.innerHTML = data.data.usage_levels.map(u => `<option value="${u}">${u}</option>`).join("");
  } catch {
    console.warn("Could not load prediction options — using defaults.");
  }
}

async function runPrediction() {
  const building   = document.getElementById("predBuilding").value;
  const usage      = document.getElementById("predUsage").value;
  const month      = parseInt(document.getElementById("predMonth").value);
  const dayOfWeek  = parseInt(document.getElementById("predDay").value);

  const btn      = document.getElementById("predictBtn");
  const resultBox = document.getElementById("resultBox");

  btn.innerHTML = `<span class="spinner"></span> Predicting...`;
  btn.disabled  = true;

  try {
    const res  = await fetch(`${API_BASE}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ building_name: building, usage_level: usage, month, day_of_week: dayOfWeek })
    });
    const data = await res.json();

    if (!data.success) {
      alert("Prediction error: " + data.error);
      return;
    }

    const p = data.prediction;
    document.getElementById("resultValue").textContent = p.random_forest_kwh;
    document.getElementById("resultRF").textContent    = p.random_forest_kwh + " kWh";
    document.getElementById("resultLR").textContent    = p.linear_regression_kwh + " kWh";
    document.getElementById("resultBuilding").textContent = building;
    document.getElementById("resultMonth").textContent = monthName(month);
    document.getElementById("resultUsage").textContent = usage;

    const sugg = document.getElementById("resultSuggestions");
    sugg.innerHTML = data.suggestions.map(s => `<div class="suggestion-item">${s}</div>`).join("");

    resultBox.classList.add("show");

  } catch (err) {
    alert("Network error — make sure the Flask server is running on port 5000.\n\nError: " + err.message);
  } finally {
    btn.innerHTML = "⚡ Predict Energy";
    btn.disabled  = false;
  }
}

function monthName(m) {
  return ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][m];
}


// ════════════════════════════════════════════════════════════════════════════
//  ANALYTICS
// ════════════════════════════════════════════════════════════════════════════

async function loadAnalytics() {
  try {
    const res  = await fetch(`${API_BASE}/api/analytics`);
    const data = await res.json();
    if (!data.success) return;

    const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

    // Monthly trend bar chart
    renderBarChart("chartMonthly", months,
      months.map((_, i) => data.monthly_avg[i + 1] || 0),
      "Avg Energy (kWh)", "#1a73e8");

    // Building totals horizontal bar
    renderHorizBar("chartBuilding",
      Object.keys(data.building_totals),
      Object.values(data.building_totals));

    // Usage level doughnut
    renderUsageDoughnut("chartUsage", data.usage_counts);

  } catch (err) {
    console.error("Analytics error:", err);
  }
}

function renderBarChart(canvasId, labels, dataVals, label, color) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  charts[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label, data: dataVals,
        backgroundColor: color + "cc",
        borderColor: color,
        borderWidth: 1, borderRadius: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

function renderHorizBar(canvasId, labels, dataVals) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  const COLORS = ["#1a73e8","#34a853","#ea4335","#fbbc04","#9c27b0","#00bcd4","#ff5722","#607d8b"];
  charts[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Total kWh",
        data: dataVals,
        backgroundColor: COLORS,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true } }
    }
  });
}

function renderUsageDoughnut(canvasId, usageCounts) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();

  charts[canvasId] = new Chart(ctx, {
    type: "pie",
    data: {
      labels: Object.keys(usageCounts),
      datasets: [{
        data: Object.values(usageCounts),
        backgroundColor: ["#ea4335","#fbbc04","#34a853"],
        borderWidth: 2
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}


// ════════════════════════════════════════════════════════════════════════════
//  BUILDINGS
// ════════════════════════════════════════════════════════════════════════════

async function loadBuildings() {
  try {
    const res  = await fetch(`${API_BASE}/api/buildings`);
    const data = await res.json();
    if (!data.success) return;

    const tbody = document.getElementById("buildingsBody");
    tbody.innerHTML = data.data.map((b, i) => {
      const effBadge = b.avg_kwh > 250 ? "badge-high" : b.avg_kwh > 150 ? "badge-medium" : "badge-low";
      const effLabel = b.avg_kwh > 250 ? "High" : b.avg_kwh > 150 ? "Medium" : "Low";
      return `
        <tr>
          <td>${i+1}</td>
          <td><strong>${b.building}</strong></td>
          <td>${b.avg_kwh.toLocaleString()}</td>
          <td>${b.max_kwh.toLocaleString()}</td>
          <td>${b.min_kwh.toLocaleString()}</td>
          <td>${b.total_kwh.toLocaleString()}</td>
          <td><span class="badge ${effBadge}">${effLabel}</span></td>
        </tr>`;
    }).join("");

  } catch (err) {
    console.error("Buildings load error:", err);
  }
}
