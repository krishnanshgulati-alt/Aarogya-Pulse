const API_BASE = ""; // Same server hosts the frontend and backend.

const byId = (id) => document.getElementById(id);
const connectionPill = byId("connection-pill");
const toast = byId("toast");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 3200);
}

function formatNumber(value, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(digits);
}

function formatTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {"Content-Type": "application/json", ...(options.headers || {})},
    ...options
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = body.detail || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return body;
}

async function checkBackend() {
  try {
    await api("/api/health");
    connectionPill.textContent = "Backend connected";
    connectionPill.className = "pill pill-ok";
  } catch {
    connectionPill.textContent = "Backend offline";
    connectionPill.className = "pill pill-error";
  }
}

function renderReading(reading) {
  if (!reading) return;
  byId("heart-rate").textContent = formatNumber(reading.heart_rate);
  byId("spo2").textContent = formatNumber(reading.spo2);
  byId("temperature").textContent = formatNumber(reading.skin_temperature, 1);
  byId("motion").textContent = reading.motion_detected ? "Movement" : "Still / unknown";
}

function renderHistory(readings) {
  const tbody = byId("history-body");
  tbody.replaceChildren();
  if (!readings || readings.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty-cell";
    cell.textContent = "No readings yet. Generate demo data or send a sensor reading.";
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }
  [...readings].reverse().forEach((reading) => {
    const row = document.createElement("tr");
    const values = [
      formatTime(reading.created_at),
      reading.heart_rate == null ? "—" : `${formatNumber(reading.heart_rate)} BPM`,
      reading.spo2 == null ? "—" : `${formatNumber(reading.spo2)}%`,
      reading.source || "unknown"
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    });
    tbody.appendChild(row);
  });
}

async function refreshDashboard() {
  try {
    const [latestData, historyData] = await Promise.all([
      api("/api/readings/latest"),
      api("/api/readings/history?limit=30")
    ]);
    renderReading(latestData.reading);
    renderHistory(historyData.readings);
    await checkBackend();
  } catch (error) {
    await checkBackend();
    showToast(`Could not load readings: ${error.message}`);
  }
}

async function generateDemoReading() {
  // These are made-up demo values for testing the UI, not a person's health data.
  const sample = {
    heart_rate: Math.round(68 + Math.random() * 35),
    spo2: Math.round(95 + Math.random() * 5),
    skin_temperature: Number((31 + Math.random() * 4).toFixed(1)),
    pulse_feature: Number((0.35 + Math.random() * 0.55).toFixed(2)),
    motion_detected: Math.random() > 0.72,
    source: "demo"
  };
  try {
    await api("/api/readings", {method: "POST", body: JSON.stringify(sample)});
    await refreshDashboard();
    showToast("Demo reading saved. This is simulated data, not a real measurement.");
  } catch (error) {
    showToast(`Could not save demo reading: ${error.message}`);
  }
}

async function checkModelStatus() {
  try {
    const result = await api("/api/predict", {method: "POST", body: "{}"});
    byId("assessment-title").textContent =
      result.mode === "demo_placeholder" ? "ML model not connected" : "Model response received";
    byId("assessment-message").textContent = result.message ||
      "Model returned a response. Confirm its meaning with your ML teammate.";
    showToast("Backend responded. The current project uses a placeholder, not a medical model.");
  } catch (error) {
    byId("assessment-title").textContent = "Unable to check model";
    byId("assessment-message").textContent = error.message;
    showToast(error.message);
  }
}

async function clearDemoData() {
  const confirmed = window.confirm("Delete all saved local demo readings?");
  if (!confirmed) return;
  try {
    await api("/api/readings", {method: "DELETE"});
    await refreshDashboard();
    byId("assessment-title").textContent = "Model not connected";
    byId("assessment-message").textContent = "Demo readings were cleared. The ML model is still a placeholder.";
    showToast("Demo readings cleared.");
  } catch (error) {
    showToast(`Could not clear readings: ${error.message}`);
  }
}

byId("demo-button").addEventListener("click", generateDemoReading);
byId("refresh-button").addEventListener("click", refreshDashboard);
byId("predict-button").addEventListener("click", checkModelStatus);
byId("clear-button").addEventListener("click", clearDemoData);

checkBackend();
refreshDashboard();
