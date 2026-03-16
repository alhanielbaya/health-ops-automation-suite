"""
Test the FastAPI Dashboard API endpoints.
"""
import sys
import os

# Setup paths - run from monitoring-service directory
sys.path.insert(0, 'src')
sys.path.insert(0, os.path.join('..', 'database', 'src'))

from fastapi.testclient import TestClient
from dashboard import app

client = TestClient(app)

def test_root():
    """Test the root endpoint returns HTML dashboard."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Health Ops Monitoring Dashboard" in response.text
    print("[OK] Root endpoint returns HTML dashboard")

def test_api_stats():
    """Test the stats API endpoint."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_assets" in data
    assert "healthy_assets" in data
    assert "warning_assets" in data
    assert "critical_assets" in data
    assert "unresolved_alerts" in data
    
    print(f"[OK] Stats API working:")
    print(f"  - Total assets: {data['total_assets']}")
    print(f"  - Healthy: {data['healthy_assets']}")
    print(f"  - Warnings: {data['warning_assets']}")
    print(f"  - Critical: {data['critical_assets']}")

def test_api_assets():
    """Test the assets API endpoint."""
    response = client.get("/api/assets")
    assert response.status_code == 200
    
    assets = response.json()
    assert isinstance(assets, list)
    
    if assets:
        print(f"[OK] Assets API working: {len(assets)} assets found")
        asset = assets[0]
        assert "id" in asset
        assert "asset_tag" in asset
        assert "asset_type" in asset
        print(f"  - First asset: {asset['asset_tag']} ({asset['asset_type']})")
    else:
        print("[OK] Assets API working: 0 assets (database may be empty)")

def test_api_health_status():
    """Test the health status API endpoint."""
    response = client.get("/api/health-status")
    assert response.status_code == 200
    
    statuses = response.json()
    assert isinstance(statuses, list)
    
    print(f"[OK] Health Status API working: {len(statuses)} assets")
    
    if statuses:
        status = statuses[0]
        assert "asset_id" in status
        assert "status" in status
        print(f"  - First status: {status['asset_tag']} is {status['status']}")

def test_api_alerts():
    """Test the alerts API endpoint."""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    
    alerts = response.json()
    assert isinstance(alerts, list)
    
    print(f"[OK] Alerts API working: {len(alerts)} alerts")

def test_api_docs():
    """Test the API documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    print("[OK] API docs endpoint working (Swagger UI)")

if __name__ == "__main__":
    print("Testing FastAPI Dashboard...\n")
    
    try:
        test_root()
        test_api_stats()
        test_api_assets()
        test_api_health_status()
        test_api_alerts()
        test_api_docs()
        
        print("\n" + "="*50)
        print("[SUCCESS] All dashboard tests passed!")
        print("="*50)
        print("\nDashboard is ready to use:")
        print("  1. Start server: python start_dashboard.py")
        print("  2. Open browser: http://localhost:8000")
        print("  3. API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
