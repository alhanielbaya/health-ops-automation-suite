const API_BASE = "";

async function loadStats() {
  try {
    const response = await fetch(`${API_BASE}/api/stats`);
    const stats = await response.json();
    document.getElementById("totalAssets").textContent = stats.total_assets;
    document.getElementById("healthyAssets").textContent = stats.healthy_assets;
    document.getElementById("warningAssets").textContent = stats.warning_assets;
    document.getElementById("criticalAssets").textContent =
      stats.critical_assets;
  } catch (error) {
    console.error("Failed to load stats:", error);
  }
}

async function loadAssets() {
  try {
    const response = await fetch(`${API_BASE}/api/health-status`);
    const assets = await response.json();
    const tableHtml = `<table><thead><tr><th>Asset Tag</th><th>Status</th><th>Response Time</th><th>Last Checked</th></tr></thead><tbody>${assets.map((asset) => `<tr><td><strong>${asset.asset_tag}</strong></td><td><span class="status ${asset.status}">${asset.status}</span></td><td>${asset.response_time_ms ? asset.response_time_ms.toFixed(2) + " ms" : "N/A"}</td><td>${asset.last_checked ? new Date(asset.last_checked).toLocaleString() : "Never"}</td></tr>`).join("")}</tbody></table>`;
    document.getElementById("assetsTable").innerHTML = tableHtml;
  } catch (error) {
    document.getElementById("assetsTable").innerHTML =
      `<div class="loading">Error: ${error.message}</div>`;
  }
}

async function loadAlerts() {
  try {
    const response = await fetch(
      `${API_BASE}/api/alerts?unresolved_only=true&limit=10`,
    );
    const alerts = await response.json();
    if (alerts.length === 0) {
      document.getElementById("alertsTable").innerHTML =
        `<p style="color: #666; text-align: center; padding: 2rem;">No unresolved alerts. All systems operational!</p>`;
      return;
    }
    const tableHtml = `<table><thead><tr><th>Severity</th><th>Asset</th><th>Message</th><th>Time</th></tr></thead><tbody>${alerts.map((alert) => `<tr><td><span class="status ${alert.severity}">${alert.severity}</span></td><td>${alert.asset_tag}</td><td>${alert.message}</td><td>${new Date(alert.created_at).toLocaleString()}</td></tr>`).join("")}</tbody></table>`;
    document.getElementById("alertsTable").innerHTML = tableHtml;
  } catch (error) {
    document.getElementById("alertsTable").innerHTML =
      `<div class="loading">Error: ${error.message}</div>`;
  }
}

async function loadData() {
  await Promise.all([loadStats(), loadAssets(), loadAlerts()]);
}

loadData();
setInterval(loadData, 30000);
