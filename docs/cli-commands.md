# CLI Commands Reference

Complete reference for the Health Ops CLI Tool.

## Installation

The CLI tool is automatically installed when you run `bun install` in the `cli-tool` directory.

```bash
cd cli-tool
bun install
```

## Global Usage

```bash
bun run src/index.ts [command] [options]
```

## Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output |
| `--dry-run` | Show what would be done without making changes |
| `-V, --version` | Show version number |
| `-h, --help` | Show help |

---

## Commands

### setup - Configure New Workstation

Interactive command to set up a new workstation for an employee.

```bash
bun run src/index.ts setup [options]
```

#### Options

| Option | Description |
|--------|-------------|
| `-u, --user <employeeId>` | Employee ID (skips prompt if provided) |
| `-a, --asset <assetTag>` | Asset tag (skips prompt if provided) |
| `--skip-network` | Skip network configuration |
| `--skip-software` | Skip software installation |

#### Examples

```bash
# Full interactive setup
bun run src/index.ts setup

# Setup with pre-filled values
bun run src/index.ts setup --user EMP001 --asset WS-2024-005

# Setup without network config
bun run src/index.ts setup --skip-network

# Dry run (no changes made)
bun run src/index.ts setup --dry-run
```

#### Output

```
[ Health Ops Workstation Setup ]

Step 1: Creating database records...
[OK] Database records created

Step 2: Validating security settings...
[OK] Security baseline passed

Step 3: Configuring network...
[OK] Network configured

Step 4: Installing required software...
[OK] Epic Hyperspace installed
[OK] Microsoft Office installed
[OK] VPN Client installed
[OK] Antivirus installed

[OK] Workstation setup completed successfully!

Asset: WS-2024-005
User: John Smith
Department: IT
```

---

### validate - Check Compliance

Validate workstation configuration and compliance.

```bash
bun run src/index.ts validate [options]
```

#### Options

| Option | Description |
|--------|-------------|
| `-a, --asset <assetTag>` | Validate specific asset |
| `-d, --department <dept>` | Validate all assets in department |
| `--security-only` | Only check security settings |
| `--network-only` | Only check network settings |

#### Examples

```bash
# Validate all assets
bun run src/index.ts validate

# Validate specific asset
bun run src/index.ts validate --asset WS-2024-001

# Validate department
bun run src/index.ts validate --department IT

# Security only
bun run src/index.ts validate --security-only
```

#### Output

```
[ Health Ops Compliance Validation ]

Validating 3 active assets...

Asset: WS-2024-001 (IT-WS-001)
--------------------------------------------------
[OK] Validation complete
  Hostname: IT-WS-001
  Status: Active

Validation complete!
```

---

### report - Generate Reports

Generate compliance and inventory reports.

```bash
bun run src/index.ts report [options]
```

#### Options

| Option | Description |
|--------|-------------|
| `-t, --type <type>` | Report type: compliance, inventory, alerts (default: compliance) |
| `-f, --format <format>` | Output format: json, csv, table (default: table) |
| `-o, --output <file>` | Output file path |
| `-d, --department <dept>` | Filter by department |

#### Report Types

- **compliance** - Compliance status of assets and software
- **inventory** - Complete asset inventory
- **alerts** - Recent alerts and their status

#### Formats

- **table** - Human-readable table (console)
- **json** - Machine-readable JSON
- **csv** - Comma-separated values

#### Examples

```bash
# Default compliance report
bun run src/index.ts report

# JSON format
bun run src/index.ts report --format json

# Save to file
bun run src/index.ts report --output report.json

# Inventory by department
bun run src/index.ts report --type inventory --department IT

# CSV export
bun run src/index.ts report --format csv --output assets.csv
```

#### Output

```
[ Health Ops Report Generation ]

Report Type: compliance
Format: table
Total Assets: 3

Asset Inventory:
--------------------------------------------------------------------------------
Asset Tag      | Type        | Hostname          | Department
--------------------------------------------------------------------------------
WS-2024-001   | workstation| IT-WS-001        | IT
WS-2024-002   | laptop     | CARD-001         | Cardiology
WS-2024-003   | workstation| ADMIN-001        | Administration
--------------------------------------------------------------------------------

Report generated successfully!
```

---

## Help

Get help for any command:

```bash
# General help
bun run src/index.ts --help

# Command-specific help
bun run src/index.ts setup --help
bun run src/index.ts validate --help
bun run src/index.ts report --help
```

---

## Common Workflows

### New Employee Onboarding

```bash
# Step 1: Set up the workstation
bun run src/index.ts setup

# Step 2: Validate the configuration
bun run src/index.ts validate --asset WS-2024-005

# Step 3: Generate onboarding report
bun run src/index.ts report --type compliance --asset WS-2024-005
```

### Monthly Compliance Audit

```bash
# Generate inventory report
bun run src/index.ts report --type inventory --format csv --output monthly_inventory.csv

# Validate all assets
bun run src/index.ts validate

# Check for non-compliant software
bun run src/index.ts report --type compliance --format json --output compliance_report.json
```

### Department-Specific Tasks

```bash
# Set up workstation for Cardiology
bun run src/index.ts setup
# (select Cardiology when prompted)

# Validate all Cardiology assets
bun run src/index.ts validate --department Cardiology

# Generate Cardiology inventory
bun run src/index.ts report --type inventory --department Cardiology
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Validation failed |
| 3 | Database error |

---

For more information, see the main [README.md](../README.md).
