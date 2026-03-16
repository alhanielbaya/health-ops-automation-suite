# Health Ops Automation Suite

A complete healthcare IT automation system for monitoring, asset management, and workstation configuration.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Bun](https://img.shields.io/badge/Bun-1.0+-black.svg)](https://bun.sh)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

This suite provides three integrated components for healthcare IT operations:

1. **Monitoring Service** (Python + FastAPI) - Real-time health monitoring of IT assets
2. **CLI Tool** (Bun + TypeScript) - Automated workstation configuration
3. **Database** (SQLite + SQLAlchemy) - Centralized asset and monitoring data

## Features

### Mission-Critical Monitoring
- Async health checks with configurable intervals
- Latency measurement with threshold-based alerting
- Real-time web dashboard
- Alert management and notification system
- Health check history and reporting

### Infrastructure Automation
- Interactive workstation setup for new hires
- Security baseline validation
- Network configuration automation
- Software compliance tracking
- Compliance reporting (JSON/CSV/Table)

### Database Management
- SQLite database with SQLAlchemy ORM
- Asset tracking (computers, servers, devices)
- User management (employees, departments)
- Network configuration storage
- Software version inventory
- Health check and alert history

## Quick Start

### Prerequisites

- **Python 3.10+** - [Download](https://python.org/downloads)
- **Bun 1.0+** - [Install](https://bun.sh/docs/installation)
- **Git** - [Download](https://git-scm.com)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd health-ops-automation-suite
```

2. **Set up Python environment**
```bash
# Create virtual environment
cd monitoring-service
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Initialize the database**
```bash
cd ../database
pip install -r requirements.txt
python init_db.py
```

4. **Set up Bun CLI tool**
```bash
cd ../cli-tool
bun install
```

## Usage

### Start the Monitoring Dashboard

```bash
cd monitoring-service
source venv/Scripts/activate  # On Windows
python start_dashboard.py
```

Open your browser:
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Run Health Checks

```bash
cd monitoring-service
source venv/Scripts/activate
python tests/test_monitor.py
```

### Configure a New Workstation

```bash
cd cli-tool
bun run src/index.ts setup
```

Follow the interactive prompts to:
1. Enter employee information
2. Configure asset details
3. Set up network configuration
4. Install required software

### Generate Reports

```bash
cd cli-tool
bun run src/index.ts report
```

### Validate Compliance

```bash
cd cli-tool
bun run src/index.ts validate
```

## Project Structure

```
health-ops-automation-suite/
├── monitoring-service/          # Python monitoring service
│   ├── src/
│   │   ├── monitoring/         # Core monitoring logic
│   │   │   ├── health_monitor.py
│   │   │   ├── alert_manager.py
│   │   │   └── config.py
│   │   └── dashboard.py        # FastAPI dashboard
│   ├── tests/
│   │   ├── test_monitor.py
│   │   └── test_dashboard.py
│   ├── requirements.txt
│   └── start_dashboard.py
│
├── cli-tool/                   # Bun + TypeScript CLI
│   ├── src/
│   │   ├── commands/          # CLI commands
│   │   │   ├── setup.ts
│   │   │   ├── validate.ts
│   │   │   └── report.ts
│   │   └── utils/             # Utility functions
│   │       ├── db.ts
│   │       ├── security.ts
│   │       ├── network.ts
│   │       └── software.ts
│   ├── tests/
│   │   └── cli.test.ts
│   ├── package.json
│   └── tsconfig.json
│
├── database/                  # SQLite database module
│   ├── src/
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── asset.py
│   │   │   ├── user.py
│   │   │   ├── network_config.py
│   │   │   ├── software_version.py
│   │   │   └── health_check.py
│   │   └── repositories/     # Data access layer
│   │       └── asset_repo.py
│   ├── migrations/
│   ├── requirements.txt
│   └── init_db.py
│
└── docs/                     # Documentation
    ├── architecture.md
    ├── api-reference.md
    └── cli-commands.md
```

## Technology Stack

### Python Components
- **FastAPI** - Modern web framework for the dashboard API
- **SQLAlchemy** - ORM for database operations
- **aiohttp** - Async HTTP client for health checks
- **Pydantic** - Data validation and serialization
- **pytest** - Testing framework
- **Uvicorn** - ASGI server

### TypeScript/Bun Components
- **Bun** - JavaScript runtime and package manager
- **Commander.js** - CLI framework
- **Inquirer** - Interactive prompts
- **Chalk** - Terminal styling
- **Ora** - Loading spinners

### Database
- **SQLite** - Serverless database
- **SQLAlchemy** - Python ORM
- **Alembic** - Database migrations (optional)

## Configuration

### Environment Variables

Create a `.env` file in `monitoring-service/`:

```env
# Monitoring Configuration
MONITOR_HTTP_TIMEOUT=10
MONITOR_WARNING_THRESHOLD=1000
MONITOR_CRITICAL_THRESHOLD=5000
MONITOR_CHECK_INTERVAL=30

# Database
DATABASE_URL=sqlite:///../../database/health_ops.db

# Alert Settings
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook
```

### Monitoring Thresholds

Edit `monitoring-service/src/monitoring/config.py`:

```python
@dataclass
class MonitorConfig:
    http_timeout_seconds: int = 10
    warning_threshold_ms: float = 1000.0    # 1 second
    critical_threshold_ms: float = 5000.0   # 5 seconds
    check_interval_seconds: int = 30
```

## API Reference

See [docs/api-reference.md](docs/api-reference.md) for complete API documentation.

### Quick API Examples

```bash
# Get all assets
curl http://localhost:8000/api/assets

# Get health status
curl http://localhost:8000/api/health-status

# Get dashboard stats
curl http://localhost:8000/api/stats

# Get alerts
curl http://localhost:8000/api/alerts
```

## CLI Commands

See [docs/cli-commands.md](docs/cli-commands.md) for complete CLI documentation.

### Quick CLI Examples

```bash
# Setup new workstation
bun run src/index.ts setup

# Validate compliance
bun run src/index.ts validate --asset WS-2024-001

# Generate report
bun run src/index.ts report --type compliance --format json

# Get help
bun run src/index.ts --help
```

## Testing

### Python Tests
```bash
cd monitoring-service
source venv/Scripts/activate

# Run monitoring tests
python tests/test_monitor.py

# Run dashboard tests
python tests/test_dashboard.py

# Run all tests with pytest
pytest tests/
```

### Bun Tests
```bash
cd cli-tool

# Run all tests
bun test

# Run specific test file
bun test tests/cli.test.ts
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed architecture diagrams and explanations.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
├─────────────────────────────────────────────────────────┤
│  Web Dashboard (http://localhost:8000)                  │
│  CLI Tool (bun run src/index.ts)                        │
│  API Clients                                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    API LAYER                             │
├─────────────────────────────────────────────────────────┤
│  FastAPI REST Endpoints                                  │
│  - /api/assets                                           │
│  - /api/health-status                                    │
│  - /api/alerts                                           │
│  - /api/stats                                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC                        │
├─────────────────────────────────────────────────────────┤
│  HealthMonitor (async checks)                           │
│  AlertManager (notifications)                           │
│  Repository Pattern (data access)                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                            │
├─────────────────────────────────────────────────────────┤
│  SQLite Database (health_ops.db)                        │
│  - Assets, Users, HealthChecks                          │
│  - Alerts, NetworkConfig                                │
│  - SoftwareVersion                                      │
└─────────────────────────────────────────────────────────┘
```

## Deployment

### Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Add authentication to dashboard
- [ ] Configure HTTPS
- [ ] Set up environment variables
- [ ] Configure log rotation
- [ ] Set up monitoring/metrics
- [ ] Database backups
- [ ] Security audit

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY monitoring-service/requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start server
CMD ["python", "monitoring-service/start_dashboard.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@healthops.local or open an issue on GitHub.

## Acknowledgments

- FastAPI team for the excellent web framework
- SQLAlchemy team for the powerful ORM
- Bun team for the fast JavaScript runtime
- Healthcare IT community for best practices

---

**Built with care for healthcare IT operations** 🏥
