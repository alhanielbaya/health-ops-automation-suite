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
from fastapi.responses import HTMLResponse, FileResponse
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

# Get the directory containing this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(CURRENT_DIR, '..', '..'))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "monitoring-service", "static")), name="static")

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
@app.get("/")
async def get_dashboard():
    """Serve the main dashboard HTML."""
    template_path = os.path.join(PROJECT_ROOT, "monitoring-service", "templates", "index.html")
    return FileResponse(template_path)

if __name__ == "__main__":
    import uvicorn
    print(f"Database: {DATABASE_PATH}")
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
