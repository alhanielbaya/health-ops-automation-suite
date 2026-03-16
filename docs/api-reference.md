# API Reference

Complete reference for the Health Ops Monitoring Dashboard API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production, add API key authentication.

## Content Type

All requests and responses use JSON format:

```
Content-Type: application/json
```

---

## Endpoints

### Dashboard

#### Get Dashboard UI
```
GET /
```

Returns the HTML dashboard interface.

**Response**: `text/html`

---

### Assets

#### List All Assets
```
GET /api/assets
```

Retrieve a list of all IT assets.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| department | string | No | Filter by department (e.g., "IT", "Cardiology") |
| status | string | No | Filter by status ("active", "maintenance", "retired") |

**Response**:
```json
[
  {
    "id": 1,
    "asset_tag": "WS-2024-001",
    "asset_type": "workstation",
    "hostname": "IT-WS-001",
    "department": "IT",
    "status": "active",
    "location": "Floor 2",
    "user_name": "John Smith"
  }
]
```

**Example**:
```bash
curl http://localhost:8000/api/assets

curl "http://localhost:8000/api/assets?department=IT&status=active"
```

---

#### Get Asset Details
```
GET /api/assets/{asset_id}
```

Retrieve detailed information about a specific asset.

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asset_id | integer | Yes | Asset ID |

**Response**:
```json
{
  "asset": {
    "id": 1,
    "asset_tag": "WS-2024-001",
    "asset_type": "workstation",
    "hostname": "IT-WS-001",
    "serial_number": "SN123456",
    "manufacturer": "Dell",
    "model": "OptiPlex 7090",
    "status": "active",
    "location": "Floor 2",
    "department": "IT"
  },
  "user": {
    "id": 1,
    "name": "John Smith",
    "email": "john.smith@hospital.com",
    "department": "IT"
  },
  "health": {
    "status": "healthy",
    "response_time_ms": 45.2,
    "last_checked": "2024-03-16T14:30:00",
    "is_reachable": true
  },
  "network": {
    "ip_address": "192.168.1.100",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "gateway": "192.168.1.1",
    "dns_primary": "8.8.8.8",
    "domain": "hospital.local"
  },
  "software": [
    {
      "name": "Epic Hyperspace",
      "version": "2023.1.2",
      "vendor": "Epic Systems",
      "is_required": true,
      "is_compliant": true
    }
  ]
}
```

**Example**:
```bash
curl http://localhost:8000/api/assets/1
```

---

### Health Status

#### Get Health Status
```
GET /api/health-status
```

Retrieve current health status for all active assets.

**Response**:
```json
[
  {
    "asset_id": 1,
    "asset_tag": "WS-2024-001",
    "status": "healthy",
    "response_time_ms": 45.23,
    "last_checked": "2024-03-16T14:30:00",
    "is_reachable": true,
    "error": null
  },
  {
    "asset_id": 2,
    "asset_tag": "WS-2024-002",
    "status": "warning",
    "response_time_ms": 1200.50,
    "last_checked": "2024-03-16T14:30:00",
    "is_reachable": true,
    "error": null
  }
]
```

**Status Values**:
- `healthy` - Response time < 1000ms
- `warning` - Response time between 1000ms and 5000ms
- `critical` - Response time > 5000ms or unreachable
- `unknown` - No health check data available

**Example**:
```bash
curl http://localhost:8000/api/health-status
```

---

#### Get Health History
```
GET /api/health-history/{asset_id}
```

Retrieve health check history for a specific asset.

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| asset_id | integer | Yes | Asset ID |

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| hours | integer | No | Hours of history to retrieve (default: 24) |

**Response**:
```json
[
  {
    "timestamp": "2024-03-16T14:30:00",
    "status": "healthy",
    "response_time_ms": 45.23,
    "is_reachable": true
  },
  {
    "timestamp": "2024-03-16T14:00:00",
    "status": "healthy",
    "response_time_ms": 52.10,
    "is_reachable": true
  }
]
```

**Example**:
```bash
curl http://localhost:8000/api/health-history/1?hours=12
```

---

### Alerts

#### List Alerts
```
GET /api/alerts
```

Retrieve alerts with optional filtering.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| unresolved_only | boolean | No | Show only unresolved alerts (default: false) |
| limit | integer | No | Maximum number of alerts (default: 50) |

**Response**:
```json
[
  {
    "id": 1,
    "severity": "critical",
    "alert_type": "health_check",
    "message": "Asset WS-2024-002 is not responding",
    "asset_tag": "WS-2024-002",
    "is_resolved": false,
    "created_at": "2024-03-16T14:30:00",
    "resolved_at": null
  }
]
```

**Severity Values**:
- `info` - Informational
- `warning` - Warning condition
- `critical` - Critical condition requiring attention

**Example**:
```bash
# Get all alerts
curl http://localhost:8000/api/alerts

# Get only unresolved alerts
curl "http://localhost:8000/api/alerts?unresolved_only=true&limit=10"
```

---

#### Resolve Alert
```
POST /api/alerts/{alert_id}/resolve
```

Mark an alert as resolved.

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| alert_id | integer | Yes | Alert ID |

**Request Body**:
```json
{
  "resolved_by": "john.smith",
  "notes": "Rebooted server, now responding normally"
}
```

**Response**:
```json
{
  "message": "Alert resolved successfully",
  "alert_id": 1
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/alerts/1/resolve \
  -H "Content-Type: application/json" \
  -d '{"resolved_by": "john.smith", "notes": "Fixed the issue"}'
```

---

### Statistics

#### Get Dashboard Statistics
```
GET /api/stats
```

Retrieve dashboard statistics and summary information.

**Response**:
```json
{
  "total_assets": 50,
  "healthy_assets": 45,
  "warning_assets": 3,
  "critical_assets": 2,
  "unresolved_alerts": 5,
  "recent_checks": 150
}
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| total_assets | integer | Total number of active assets |
| healthy_assets | integer | Assets with healthy status |
| warning_assets | integer | Assets with warning status |
| critical_assets | integer | Assets with critical status |
| unresolved_alerts | integer | Number of unresolved alerts |
| recent_checks | integer | Health checks in last hour |

**Example**:
```bash
curl http://localhost:8000/api/stats
```

---

## WebSocket

### Real-time Updates

Connect to WebSocket for real-time dashboard updates:

```
WS /ws
```

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Message Format**:
```json
{
  "type": "stats",
  "data": {
    "total_assets": 50,
    "healthy_assets": 45,
    "warning_assets": 3,
    "critical_assets": 2,
    "unresolved_alerts": 5,
    "recent_checks": 150
  }
}
```

Updates are sent every 5 seconds.

---

## Error Responses

### HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 404 | Resource not found |
| 422 | Validation error |
| 500 | Internal server error |

### Error Format

```json
{
  "detail": "Asset not found"
}
```

---

## API Documentation (Swagger)

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

Features:
- Try out API endpoints directly
- View request/response schemas
- Download OpenAPI specification

---

## Rate Limiting

Currently, no rate limiting is implemented. For production, implement rate limiting:

```python
# Example: 100 requests per minute per IP
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    # Implementation here
    pass
```

---

## Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Get all assets
response = requests.get(f"{BASE_URL}/api/assets")
assets = response.json()

# Get health status
response = requests.get(f"{BASE_URL}/api/health-status")
health_data = response.json()

# Resolve an alert
response = requests.post(
    f"{BASE_URL}/api/alerts/1/resolve",
    json={"resolved_by": "admin", "notes": "Fixed"}
)
```

### JavaScript Client

```javascript
const BASE_URL = 'http://localhost:8000';

// Get all assets
fetch(`${BASE_URL}/api/assets`)
  .then(res => res.json())
  .then(data => console.log(data));

// Get health status
fetch(`${BASE_URL}/api/health-status`)
  .then(res => res.json())
  .then(data => console.log(data));

// Resolve alert
fetch(`${BASE_URL}/api/alerts/1/resolve`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ resolved_by: 'admin', notes: 'Fixed' })
});
```

### cURL Examples

```bash
# Get stats
curl http://localhost:8000/api/stats

# Get assets with filters
curl "http://localhost:8000/api/assets?department=IT&status=active"

# Get health history
curl http://localhost:8000/api/health-history/1?hours=24

# Resolve alert
curl -X POST http://localhost:8000/api/alerts/1/resolve \
  -H "Content-Type: application/json" \
  -d '{"resolved_by":"admin","notes":"Resolved"}'
```

---

## Data Models

### Asset

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| asset_tag | string | Asset tag (e.g., "WS-2024-001") |
| asset_type | string | Type: workstation, laptop, server |
| hostname | string | Network hostname |
| department | string | Department name |
| status | string | active, maintenance, retired |
| location | string | Physical location |

### Health Status

| Field | Type | Description |
|-------|------|-------------|
| asset_id | integer | Asset ID |
| asset_tag | string | Asset tag |
| status | string | healthy, warning, critical, unknown |
| response_time_ms | float | Response time in milliseconds |
| last_checked | string | ISO 8601 timestamp |
| is_reachable | boolean | Whether asset is reachable |
| error | string | Error message if any |

### Alert

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| severity | string | info, warning, critical |
| alert_type | string | Type of alert |
| message | string | Alert message |
| asset_tag | string | Related asset |
| is_resolved | boolean | Resolution status |
| created_at | string | Creation timestamp |
| resolved_at | string | Resolution timestamp |

---

For more information, see the main [README.md](../README.md).
