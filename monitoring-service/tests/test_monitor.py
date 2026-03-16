"""
Test the monitoring service.
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'database', 'src'))

import asyncio
from monitoring.health_monitor import HealthMonitor, CheckResult
from monitoring.config import MonitorConfig

async def test_monitor():
    """Test the health monitor."""
    print("Testing Health Monitor...\n")
    
    # Create monitor with test config
    config = MonitorConfig(
        http_timeout_seconds=5,
        warning_threshold_ms=1000.0,
        critical_threshold_ms=3000.0
    )
    
    monitor = HealthMonitor(config)
    
    # Test single check on google.com (reliable test target)
    print("1. Testing single health check on google.com...")
    
    # Create a mock asset
    class MockAsset:
        def __init__(self):
            self.id = 999
            self.asset_tag = "TEST-001"
            self.hostname = "www.google.com"
            self.status = "active"
    
    mock_asset = MockAsset()
    result = await monitor.check_asset_health(mock_asset)
    
    print(f"   Result: {result.status}")
    print(f"   Response Time: {result.response_time_ms:.2f}ms")
    print(f"   Reachable: {result.is_reachable}")
    if result.error_message:
        print(f"   Error: {result.error_message}")
    
    print("\n2. Testing multiple concurrent checks...")
    
    # Test multiple sites concurrently
    sites = [
        ("Google", "www.google.com"),
        ("GitHub", "www.github.com"),
        ("Example", "www.example.com"),
    ]
    
    class SiteAsset:
        def __init__(self, name, hostname):
            self.id = hash(name) % 10000
            self.asset_tag = f"TEST-{name}"
            self.hostname = hostname
            self.status = "active"
    
    assets = [SiteAsset(name, host) for name, host in sites]
    
    # Run checks concurrently
    tasks = [monitor.check_asset_health(asset) for asset in assets]
    results = await asyncio.gather(*tasks)
    
    print(f"   Checked {len(results)} sites:")
    for i, result in enumerate(results):
        print(f"   - {sites[i][0]}: {result.status} ({result.response_time_ms:.2f}ms)")
    
    print("\n[OK] Monitoring service test completed successfully!")
    print("\nWhat the monitor does:")
    print("  - Performs HTTP health checks on assets")
    print("  - Measures response times")
    print("  - Classifies status: healthy/warning/critical")
    print("  - Can run checks concurrently (async)")
    print("  - Saves results to database")
    print("  - Triggers alerts for failures")

if __name__ == "__main__":
    asyncio.run(test_monitor())
