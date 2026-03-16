# Architecture Documentation

## System Architecture

The Health Ops Automation Suite follows a modular, layered architecture designed for healthcare IT operations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web        │  │     CLI      │  │   Mobile     │          │
│  │   Browser    │  │   Terminal   │  │    Apps      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          └────────────────┴────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Web Server (Port 8000)               │  │
│  │                                                          │  │
│  │  Routes:                                                  │  │
│  │  ├── /                     → Dashboard UI (HTML)         │  │
│  │  ├── /docs                 → API Documentation           │  │
│  │  ├── /api/assets           → Asset CRUD                  │  │
│  │  ├── /api/health-status    → Health checks               │  │
│  │  ├── /api/alerts           → Alert management            │  │
│  │  └── /api/stats            → Dashboard statistics        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│   MONITORING    │ │     CLI      │ │   REPOSITORY    │
│    SERVICE      │ │   SERVICE    │ │     LAYER       │
│                 │ │              │ │                 │
│ HealthMonitor   │ │ Commander.js │ │ AssetRepository │
│ AlertManager    │ │ Inquirer     │ │ UserRepository  │
│ ConfigManager   │ │ Chalk/Ora    │ │ NetworkRepo     │
└────────┬────────┘ └──────┬───────┘ └────────┬────────┘
         │                 │                  │
         └─────────────────┴──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 SQLite Database                           │  │
│  │                   (health_ops.db)                         │  │
│  │                                                          │  │
│  │  Tables:                                                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │  assets  │  │  users   │  │health_   │  │  alerts  │ │  │
│  │  │          │──│          │  │ checks   │  │          │ │  │
│  │  │asset_tag │  │employee_ │  │          │  │ severity │ │  │
│  │  │hostname  │  │   id     │  │  status  │  │  message │ │  │
│  │  │department│  │  email   │  │response_ │  │resolved  │ │  │
│  │  │  status  │  │   ...    │  │   time   │  │   ...    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  │                                                          │  │
│  │  ┌──────────┐  ┌──────────┐                             │  │
│  │  │ network_ │  │ software │                             │  │
│  │  │ configs  │  │ versions │                             │  │
│  │  │          │  │          │                             │  │
│  │  │ip_address│  │ software │                             │  │
│  │  │dns_server│  │   name   │                             │  │
│  │  │  domain  │  │ version  │                             │  │
│  │  │   ...    │  │   ...    │                             │  │
│  │  └──────────┘  └──────────┘                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Monitoring Service

```
┌─────────────────────────────────────────────┐
│          MONITORING SERVICE                  │
│          (Python + FastAPI)                  │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │        HealthMonitor                 │   │
│  │  ┌─────────────────────────────┐   │   │
│  │  │   check_asset_health()      │   │   │
│  │  │   - HTTP GET request        │   │   │
│  │  │   - Measure latency         │   │   │
│  │  │   - Classify status         │   │   │
│  │  └─────────────────────────────┘   │   │
│  │                                      │   │
│  │  ┌─────────────────────────────┐   │   │
│  │  │      run_checks()            │   │   │
│  │  │   - Get active assets       │   │   │
│  │  │   - Async parallel checks   │   │   │
│  │  │   - Save results            │   │   │
│  │  └─────────────────────────────┘   │   │
│  │                                      │   │
│  │  ┌─────────────────────────────┐   │   │
│  │  │   start_monitoring()         │   │   │
│  │  │   - Continuous loop         │   │   │
│  │  │   - 30s interval            │   │   │
│  │  └─────────────────────────────┘   │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │        AlertManager                  │   │
│  │  ┌─────────────────────────────┐   │   │
│  │  │     send_alert()             │   │   │
│  │  │   - Console logging         │   │   │
│  │  │   - Database storage        │   │   │
│  │  │   - Webhook support         │   │   │
│  │  └─────────────────────────────┘   │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │      FastAPI Dashboard               │   │
│  │  ┌──────────────┐ ┌──────────────┐ │   │
│  │  │ REST API     │ │ WebSocket    │ │   │
│  │  │ Endpoints    │ │ Real-time    │ │   │
│  │  └──────────────┘ └──────────────┘ │   │
│  └─────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

### 2. CLI Tool

```
┌─────────────────────────────────────────────┐
│              CLI TOOL                        │
│          (Bun + TypeScript)                  │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │      Commander.js Entry              │   │
│  │         (index.ts)                   │   │
│  │                                      │   │
│  │   Commands:                          │   │
│  │   ├── setup                          │   │
│  │   ├── validate                       │   │
│  │   └── report                         │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │         Commands                     │   │
│  │                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   setup     │  │  validate   │  │   │
│  │  │   Command   │  │   Command   │  │   │
│  │  │             │  │             │  │   │
│  │  │ 1. Collect  │  │ 1. Get      │  │   │
│  │  │    user info│  │    assets   │  │   │
│  │  │ 2. Collect  │  │ 2. Validate │  │   │
│  │  │    asset    │  │    security │  │   │
│  │  │    details  │  │ 3. Validate │  │   │
│  │  │ 3. Validate │  │    network  │  │   │
│  │  │    security │  │ 4. Report   │  │   │
│  │  │ 4. Configure│  │    issues   │  │   │
│  │  │    network  │  │             │  │   │
│  │  │ 5. Install  │  │             │  │   │
│  │  │    software │  │             │  │   │
│  │  │ 6. Generate │  │             │  │   │
│  │  │    report   │  │             │  │   │
│  │  └─────────────┘  └─────────────┘  │   │
│  │                                      │   │
│  │  ┌─────────────┐                   │   │
│  │  │   report    │                   │   │
│  │  │   Command   │                   │   │
│  │  │             │                   │   │
│  │  │ 1. Query    │                   │   │
│  │  │    database │                   │   │
│  │  │ 2. Format   │                   │   │
│  │  │    output   │                   │   │
│  │  │ 3. Display  │                   │   │
│  │  │    table    │                   │   │
│  │  └─────────────┘                   │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │          Utilities                   │   │
│  │                                      │   │
│  │  ┌──────────┐ ┌──────────┐         │   │
│  │  │Database  │ │ Security │         │   │
│  │  │ Client   │ │ Checker  │         │   │
│  │  └──────────┘ └──────────┘         │   │
│  │  ┌──────────┐ ┌──────────┐         │   │
│  │  │ Network  │ │ Software │         │   │
│  │  │ Config   │ │ Installer│         │   │
│  │  └──────────┘ └──────────┘         │   │
│  └─────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

### 3. Database Layer

```
┌─────────────────────────────────────────────┐
│           DATABASE LAYER                     │
│         (SQLite + SQLAlchemy)                │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │         SQLAlchemy ORM               │   │
│  │                                      │   │
│  │  Models:                             │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ Asset                          │  │   │
│  │  │ ├── id (PK)                    │  │   │
│  │  │ ├── asset_tag (unique)         │  │   │
│  │  │ ├── asset_type                 │  │   │
│  │  │ ├── hostname                   │  │   │
│  │  │ ├── department                 │  │   │
│  │  │ ├── status                     │  │   │
│  │  │ └── user_id (FK)               │  │   │
│  │  └───────────────────────────────┘  │   │
│  │                                      │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ User                           │  │   │
│  │  │ ├── id (PK)                    │  │   │
│  │  │ ├── employee_id (unique)       │  │   │
│  │  │ ├── first_name                 │  │   │
│  │  │ ├── last_name                  │  │   │
│  │  │ ├── email (unique)             │  │   │
│  │  │ └── department                 │  │   │
│  │  └───────────────────────────────┘  │   │
│  │                                      │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ HealthCheck                    │  │   │
│  │  │ ├── id (PK)                    │  │   │
│  │  │ ├── asset_id (FK)              │  │   │
│  │  │ ├── status                     │  │   │
│  │  │ ├── response_time_ms           │  │   │
│  │  │ └── checked_at                 │  │   │
│  │  └───────────────────────────────┘  │   │
│  │                                      │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ Alert                          │  │   │
│  │  │ ├── id (PK)                    │  │   │
│  │  │ ├── health_check_id (FK)       │  │   │
│  │  │ ├── severity                   │  │   │
│  │  │ ├── message                    │  │   │
│  │  │ └── is_resolved                │  │   │
│  │  └───────────────────────────────┘  │   │
│  │                                      │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ NetworkConfig                  │  │   │
│  │  │ ├── id (PK)                    │  │   │
│  │  │ ├── asset_id (FK)              │  │   │
│  │  │ ├── ip_address                 │  │   │
│  │  │ ├── dns_primary                │  │   │
│  │  │ └── domain                     │  │   │
│  │  └───────────────────────────────┘  │   │
│  │                                      │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ SoftwareVersion                │  │   │
│  │  │ ├── id (PK)                    │  │   │
│  │  │ ├── asset_id (FK)              │  │   │
│  │  │ ├── software_name              │  │   │
│  │  │ ├── version                    │  │   │
│  │  │ └── is_compliant               │  │   │
│  │  └───────────────────────────────┘  │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │         Repository Pattern           │   │
│  │                                      │   │
│  │  AssetRepository                     │   │
│  │  ├── create()                        │   │
│  │  ├── get_by_id()                     │   │
│  │  ├── get_by_tag()                    │   │
│  │  ├── get_all()                       │   │
│  │  ├── update()                        │   │
│  │  └── delete()                        │   │
│  │                                      │   │
│  │  UserRepository                      │   │
│  │  NetworkConfigRepository             │   │
│  │  SoftwareVersionRepository           │   │
│  └─────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Monitoring Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  Asset   │────▶│ HealthMonitor│────▶│ HealthCheck  │
│  (DB)    │     │              │     │  (DB Record) │
└──────────┘     └──────────────┘     └──────────────┘
                        │
                        ▼
               ┌──────────────┐
               │    Status    │
               │   Healthy?   │
               └──────────────┘
                        │
           ┌────────────┼────────────┐
           │            │            │
           ▼            ▼            ▼
      ┌────────┐  ┌────────┐  ┌────────┐
      │Healthy │  │Warning │  │Critical│
      │Continue│  │  Log   │  │  Alert │
      └────────┘  └────────┘  └────────┘
                                     │
                                     ▼
                            ┌──────────────┐
                            │ AlertManager │
                            │              │
                            │ 1. Console   │
                            │ 2. Database  │
                            │ 3. Webhook   │
                            └──────────────┘
```

### New Hire Setup Flow

```
┌──────────┐
│   CLI    │
│  setup   │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ 1. Collect Info  │
│    - User data   │
│    - Asset data  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. Save to DB    │
│    - User record │
│    - Asset record│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. Validate      │
│    Security      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. Configure     │
│    Network       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. Install       │
│    Software      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. Generate      │
│    Report        │
└──────────────────┘
```

## Technology Stack Details

### Python Stack
```
┌─────────────────────────────────────┐
│        Application Layer             │
│  ┌───────────────────────────────┐  │
│  │      FastAPI                   │  │
│  │   - REST API endpoints         │  │
│  │   - WebSocket support          │  │
│  │   - Auto-generated docs        │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│        Business Logic Layer          │
│  ┌───────────────────────────────┐  │
│  │   HealthMonitor                │  │
│  │   - aiohttp (async HTTP)       │  │
│  │   - asyncio (concurrency)      │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   AlertManager                 │  │
│  │   - Logging                    │  │
│  │   - Notification               │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│        Data Access Layer             │
│  ┌───────────────────────────────┐  │
│  │      SQLAlchemy                │  │
│  │   - ORM models                 │  │
│  │   - Query builder              │  │
│  │   - Relationship mapping       │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│        Database Layer                │
│  ┌───────────────────────────────┐  │
│  │       SQLite                   │  │
│  │   - File-based storage         │  │
│  │   - ACID compliance            │  │
│  │   - Zero configuration         │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### TypeScript/Bun Stack
```
┌─────────────────────────────────────┐
│        CLI Interface                 │
│  ┌───────────────────────────────┐  │
│  │      Commander.js              │  │
│  │   - Command routing            │  │
│  │   - Option parsing             │  │
│  │   - Help generation            │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│        User Interaction              │
│  ┌───────────────────────────────┐  │
│  │       Inquirer                 │  │
│  │   - Interactive prompts        │  │
│  │   - Input validation           │  │
│  │   - List selection             │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │     Chalk + Ora                │  │
│  │   - Colored output             │  │
│  │   - Loading spinners           │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│        Runtime Environment           │
│  ┌───────────────────────────────┐  │
│  │         Bun                    │  │
│  │   - TypeScript execution       │  │
│  │   - Package management         │  │
│  │   - Built-in test runner       │  │
│  │   - Fast startup               │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────┐
│           SECURITY LAYERS                    │
├─────────────────────────────────────────────┤
│                                              │
│  Layer 1: Input Validation                   │
│  ├─ Pydantic models (API)                    │
│  ├─ Type checking (TypeScript)               │
│  └─ SQL injection prevention (ORM)           │
│                                              │
│  Layer 2: Authentication                     │
│  ├─ API key support (configurable)           │
│  ├─ Session management (future)              │
│  └─ JWT tokens (future)                      │
│                                              │
│  Layer 3: Authorization                      │
│  ├─ Role-based access (future)               │
│  ├─ Resource permissions                     │
│  └─ Audit logging                            │
│                                              │
│  Layer 4: Data Protection                    │
│  ├─ Database encryption (SQLite)             │
│  ├─ HTTPS for API (production)               │
│  └─ Sensitive data masking                   │
│                                              │
└─────────────────────────────────────────────┘
```

## Scalability Considerations

### Current Architecture (Single Server)
```
┌─────────────────────────────────────┐
│  Single Server Deployment           │
│  ├─ SQLite database                 │
│  ├─ Python + FastAPI                │
│  ├─ Bun CLI                         │
│  └─ Suitable for: 100-1000 assets   │
└─────────────────────────────────────┘
```

### Future Scalability (Distributed)
```
┌─────────────────────────────────────┐
│  Distributed Architecture           │
│                                     │
│  ┌──────────┐      ┌──────────┐    │
│  │   API    │◄────►│   API    │    │
│  │ Server 1 │      │ Server 2 │    │
│  └────┬─────┘      └────┬─────┘    │
│       │                 │           │
│       └────────┬────────┘           │
│                ▼                     │
│         ┌──────────┐                │
│         │  Load    │                │
│         │ Balancer │                │
│         └────┬─────┘                │
│              │                       │
│       ┌──────┴──────┐               │
│       ▼             ▼               │
│  ┌──────────┐ ┌──────────┐          │
│  │PostgreSQL│ │   Redis  │          │
│  │  Cluster │ │   Cache  │          │
│  └──────────┘ └──────────┘          │
│                                     │
│  Suitable for: 1000+ assets         │
└─────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment
```
Developer Machine
├── Python 3.10+
├── Bun runtime
├── SQLite database
└── All services local
```

### Production Environment (Recommended)
```
Production Server
├── Docker containers
│   ├── API service
│   ├── Monitoring service
│   └── CLI (maintenance)
├── PostgreSQL database
├── Redis (caching)
├── Nginx (reverse proxy)
└── SSL certificates
```

---

## Key Design Decisions

1. **Async Programming**: Using asyncio for concurrent health checks
2. **Repository Pattern**: Clean separation between business logic and data access
3. **Separation of Concerns**: Three distinct components with clear responsibilities
4. **SQLite for Development**: Simple, portable, zero-configuration
5. **TypeScript for CLI**: Type safety, modern JavaScript features
6. **FastAPI for Dashboard**: Auto-generated docs, async support, modern Python

---

For more details, see the API Reference and CLI Commands documentation.
