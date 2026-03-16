"""
FastAPI Dashboard for Health Ops Monitoring Service.

Provides:
- REST API endpoints for asset data
- Real-time health status
- Alert management
- Web dashboard UI
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import asyncio
import sys
import os

# Get project root (2 levels up from this file: src -> monitoring-service -> project-root)
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'health_ops.db')

# Add paths
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'database', 'src'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'monitoring-service', 'src'))

# Import models
try:
    from models import Asset, User, HealthCheck, Alert, NetworkConfig, SoftwareVersion
    from models.base import Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create engine pointing to the database
    engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
    Session = sessionmaker(bind=engine)
    
except ImportError as e:
    print(f"Warning: Could not import models: {e}")
    print(f"Database path: {DATABASE_PATH}")
    raise

from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="Health Ops Monitoring Dashboard",
    description="Real-time monitoring dashboard for healthcare IT assets",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class AssetResponse(BaseModel):
    id: int
    asset_tag: str
    asset_type: str
    hostname: str
    department: str
    status: str
    location: str
    user_name: Optional[str] = None

class HealthStatusResponse(BaseModel):
    asset_id: int
    asset_tag: str
    status: str
    response_time_ms: float
    last_checked: Optional[str]
    is_reachable: bool
    error: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    severity: str
    alert_type: str
    message: str
    asset_tag: str
    is_resolved: bool
    created_at: str
    resolved_at: Optional[str] = None

class DashboardStats(BaseModel):
    total_assets: int
    healthy_assets: int
    warning_assets: int
    critical_assets: int
    unresolved_alerts: int
    recent_checks: int

# Helper function to get DB session
def get_db():
    return Session()

# API Routes

@app.get("/api/assets", response_model=List[AssetResponse])
async def get_assets(department: Optional[str] = None, status: Optional[str] = None):
    """Get all assets with optional filtering."""
    session = get_db()
    try:
        query = session.query(Asset)
        
        if department:
            query = query.filter(Asset.department == department)
        if status:
            query = query.filter(Asset.status == status)
        
        assets = query.all()
        
        result = []
        for asset in assets:
            user_name = None
            if asset.user:
                user_name = f"{asset.user.first_name} {asset.user.last_name}"
            
            result.append({
                "id": asset.id,
                "asset_tag": asset.asset_tag,
                "asset_type": asset.asset_type,
                "hostname": asset.hostname or "N/A",
                "department": asset.department or "Unassigned",
                "status": asset.status,
                "location": asset.location or "Unknown",
                "user_name": user_name
            })
        
        return result
    finally:
        session.close()

@app.get("/api/health-status", response_model=List[HealthStatusResponse])
async def get_health_status():
    """Get current health status of all assets."""
    session = get_db()
    try:
        assets = session.query(Asset).filter(Asset.status == 'active').all()
        
        result = []
        for asset in assets:
            latest_check = session.query(HealthCheck).filter(
                HealthCheck.asset_id == asset.id
            ).order_by(HealthCheck.checked_at.desc()).first()
            
            if latest_check:
                result.append({
                    "asset_id": asset.id,
                    "asset_tag": asset.asset_tag,
                    "status": latest_check.status,
                    "response_time_ms": latest_check.response_time_ms,
                    "last_checked": latest_check.checked_at.isoformat() if latest_check.checked_at else None,
                    "is_reachable": latest_check.is_reachable,
                    "error": latest_check.error_message
                })
            else:
                result.append({
                    "asset_id": asset.id,
                    "asset_tag": asset.asset_tag,
                    "status": "unknown",
                    "response_time_ms": 0.0,
                    "last_checked": None,
                    "is_reachable": False,
                    "error": "No health check data"
                })
        
        return result
    finally:
        session.close()

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(unresolved_only: bool = False, limit: int = 50):
    """Get alerts with optional filtering."""
    session = get_db()
    try:
        query = session.query(Alert)
        
        if unresolved_only:
            query = query.filter(Alert.is_resolved == False)
        
        alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
        
        result = []
        for alert in alerts:
            asset_tag = "Unknown"
            if alert.health_check and alert.health_check.asset:
                asset_tag = alert.health_check.asset.asset_tag
            
            result.append({
                "id": alert.id,
                "severity": alert.severity,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "asset_tag": asset_tag,
                "is_resolved": alert.is_resolved,
                "created_at": alert.created_at.isoformat() if alert.created_at else "",
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            })
        
        return result
    finally:
        session.close()

@app.get("/api/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    session = get_db()
    try:
        total_assets = session.query(Asset).filter(Asset.status == 'active').count()
        
        healthy = 0
        warning = 0
        critical = 0
        
        assets = session.query(Asset).filter(Asset.status == 'active').all()
        for asset in assets:
            latest_check = session.query(HealthCheck).filter(
                HealthCheck.asset_id == asset.id
            ).order_by(HealthCheck.checked_at.desc()).first()
            
            if latest_check:
                if latest_check.status == 'healthy':
                    healthy += 1
                elif latest_check.status == 'warning':
                    warning += 1
                elif latest_check.status == 'critical':
                    critical += 1
        
        unresolved = session.query(Alert).filter(Alert.is_resolved == False).count()
        
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_checks = session.query(HealthCheck).filter(
            HealthCheck.checked_at >= one_hour_ago
        ).count()
        
        return {
            "total_assets": total_assets,
            "healthy_assets": healthy,
            "warning_assets": warning,
            "critical_assets": critical,
            "unresolved_alerts": unresolved,
            "recent_checks": recent_checks
        }
    finally:
        session.close()

# HTML Dashboard
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard HTML."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Health Ops Monitoring Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f7fa; color: #333; line-height: 1.6; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
            .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
            .stat-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; }
            .stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
            .stat-card h3 { font-size: 0.875rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
            .stat-value { font-size: 2.5rem; font-weight: 700; color: #333; }
            .stat-card.healthy { border-left: 4px solid #10b981; }
            .stat-card.warning { border-left: 4px solid #f59e0b; }
            .stat-card.critical { border-left: 4px solid #ef4444; }
            .stat-card.info { border-left: 4px solid #3b82f6; }
            .section { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
            .section h2 { font-size: 1.25rem; margin-bottom: 1rem; color: #333; }
            table { width: 100%; border-collapse: collapse; }
            th, td { text-align: left; padding: 0.75rem; border-bottom: 1px solid #e5e7eb; }
            th { font-weight: 600; color: #666; font-size: 0.875rem; text-transform: uppercase; }
            tr:hover { background-color: #f9fafb; }
            .status { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
            .status.healthy { background-color: #d1fae5; color: #065f46; }
            .status.warning { background-color: #fef3c7; color: #92400e; }
            .status.critical { background-color: #fee2e2; color: #991b1b; }
            .status.unknown { background-color: #f3f4f6; color: #6b7280; }
            .refresh-btn { background: #667eea; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-size: 0.875rem; font-weight: 600; }
            .refresh-btn:hover { background: #5568d3; }
            .loading { text-align: center; padding: 2rem; color: #666; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Health Ops Monitoring Dashboard</h1>
            <p>Real-time healthcare IT asset monitoring</p>
        </div>
        <div class="container">
            <div class="stats-grid">
                <div class="stat-card info">
                    <h3>Total Assets</h3>
                    <div class="stat-value" id="totalAssets">-</div>
                </div>
                <div class="stat-card healthy">
                    <h3>Healthy</h3>
                    <div class="stat-value" id="healthyAssets">-</div>
                </div>
                <div class="stat-card warning">
                    <h3>Warning</h3>
                    <div class="stat-value" id="warningAssets">-</div>
                </div>
                <div class="stat-card critical">
                    <h3>Critical</h3>
                    <div class="stat-value" id="criticalAssets">-</div>
                </div>
            </div>
            <div class="section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h2>Asset Health Status</h2>
                    <button class="refresh-btn" onclick="loadData()">Refresh</button>
                </div>
                <div id="assetsTable"><div class="loading">Loading...</div></div>
            </div>
            <div class="section">
                <h2>Recent Alerts</h2>
                <div id="alertsTable"><div class="loading">Loading...</div></div>
            </div>
        </div>
        <script>
            const API_BASE = '';
            async function loadStats() {
                try {
                    const response = await fetch(`${API_BASE}/api/stats`);
                    const stats = await response.json();
                    document.getElementById('totalAssets').textContent = stats.total_assets;
                    document.getElementById('healthyAssets').textContent = stats.healthy_assets;
                    document.getElementById('warningAssets').textContent = stats.warning_assets;
                    document.getElementById('criticalAssets').textContent = stats.critical_assets;
                } catch (error) { console.error('Failed to load stats:', error); }
            }
            async function loadAssets() {
                try {
                    const response = await fetch(`${API_BASE}/api/health-status`);
                    const assets = await response.json();
                    const tableHtml = `<table><thead><tr><th>Asset Tag</th><th>Status</th><th>Response Time</th><th>Last Checked</th></tr></thead><tbody>${assets.map(asset => `<tr><td><strong>${asset.asset_tag}</strong></td><td><span class="status ${asset.status}">${asset.status}</span></td><td>${asset.response_time_ms ? asset.response_time_ms.toFixed(2) + ' ms' : 'N/A'}</td><td>${asset.last_checked ? new Date(asset.last_checked).toLocaleString() : 'Never'}</td></tr>`).join('')}</tbody></table>`;
                    document.getElementById('assetsTable').innerHTML = tableHtml;
                } catch (error) { document.getElementById('assetsTable').innerHTML = `<div class="loading">Error: ${error.message}</div>`; }
            }
            async function loadAlerts() {
                try {
                    const response = await fetch(`${API_BASE}/api/alerts?unresolved_only=true&limit=10`);
                    const alerts = await response.json();
                    if (alerts.length === 0) {
                        document.getElementById('alertsTable').innerHTML = `<p style="color: #666; text-align: center; padding: 2rem;">No unresolved alerts. All systems operational!</p>`;
                        return;
                    }
                    const tableHtml = `<table><thead><tr><th>Severity</th><th>Asset</th><th>Message</th><th>Time</th></tr></thead><tbody>${alerts.map(alert => `<tr><td><span class="status ${alert.severity}">${alert.severity}</span></td><td>${alert.asset_tag}</td><td>${alert.message}</td><td>${new Date(alert.created_at).toLocaleString()}</td></tr>`).join('')}</tbody></table>`;
                    document.getElementById('alertsTable').innerHTML = tableHtml;
                } catch (error) { document.getElementById('alertsTable').innerHTML = `<div class="loading">Error: ${error.message}</div>`; }
            }
            async function loadData() { await Promise.all([loadStats(), loadAssets(), loadAlerts()]); }
            loadData();
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    print(f"Database: {DATABASE_PATH}")
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
