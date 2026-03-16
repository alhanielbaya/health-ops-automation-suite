"""
Main entry point for the monitoring service.
Provides both command-line interface and FastAPI dashboard.
"""
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring.health_monitor import HealthMonitor
from monitoring.config import MonitorConfig


async def main():
    """Main entry point for CLI monitoring."""
    print("Starting Health Ops Monitoring Service...")
    print("Press Ctrl+C to stop\n")
    
    # Initialize monitor with default config
    config = MonitorConfig()
    monitor = HealthMonitor(config)
    
    try:
        # Start continuous monitoring
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nStopping monitoring service...")
        monitor.stop_monitoring()
        print("Goodbye!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
