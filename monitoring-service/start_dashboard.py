#!/usr/bin/env python
"""
Start the FastAPI Dashboard.

Usage:
    python start_dashboard.py
    
Then open: http://localhost:8000
"""
import sys
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add paths
sys.path.insert(0, os.path.join(project_root, 'monitoring-service', 'src'))
sys.path.insert(0, os.path.join(project_root, 'database', 'src'))

print("Starting Health Ops Dashboard...")
print(f"Project root: {project_root}")
print()

# Import and start the dashboard
from dashboard import app
import uvicorn

if __name__ == "__main__":
    print("Dashboard URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    uvicorn.run(
        "dashboard:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
