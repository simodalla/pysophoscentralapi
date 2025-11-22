# CLI Guide

Complete reference for the PySophosCentralApi command-line interface.

## Table of Contents

- [Overview](#overview)
- [Global Options](#global-options)
- [Configuration Commands](#configuration-commands)
- [Endpoint Commands](#endpoint-commands)
- [Alert Commands](#alert-commands)
- [Tenant Commands](#tenant-commands)
- [Admin Commands](#admin-commands)
- [Role Commands](#role-commands)
- [Output Formats](#output-formats)

## Overview

The `pysophos` CLI provides a user-friendly interface to Sophos Central APIs. All commands follow a consistent structure:

```bash
pysophos [GLOBAL_OPTIONS] COMMAND [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

**Example:**
```bash
pysophos --debug endpoint list --health-status bad --output json
```

## Global Options

These options apply to all commands:

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--debug` | Enable debug mode with full tracebacks |
| `--config-file PATH` | Path to configuration file (overrides default locations) |
| `--help` | Show help message |

**Examples:**
```bash
# Use custom config file for any command
pysophos --config-file /path/to/config.toml endpoint list

# Combine with debug mode
pysophos --debug --config-file ./test-config.toml alerts list
```

## Configuration Commands

Manage configuration settings.

### `pysophos config init`

Initialize configuration interactively.

**Options:**
- `--client-id TEXT` - Sophos Central API client ID (prompts if not provided)
- `--client-secret TEXT` - Sophos Central API client secret (prompts if not provided)
- `--region [us|eu|ap|de|ie]` - Data region (default: us)
- `--config-file PATH` - Config file path (default: ~/.config/pysophos/config.toml)

**Examples:**
```bash
# Interactive setup
pysophos config init

# Non-interactive with options
pysophos config init --client-id abc123 --client-secret xyz789 --region eu
```

### `pysophos config show`

Show current configuration (credentials masked).

**Options:**
- `--config-file PATH` - Config file path

**Examples:**
```bash
pysophos config show
pysophos config show --config-file /custom/path/config.toml
```

### `pysophos config test`

Test API connection with current configuration.

**Examples:**
```bash
pysophos config test
```

## Endpoint Commands

Manage and query endpoints.

### `pysophos endpoint list`

List endpoints with optional filtering.

**Filter Options:**
- `--health-status [good|suspicious|bad|unknown]` - Filter by health status
- `--endpoint-type [computer|server|securityVm]` - Filter by endpoint type
- `--lockdown-status [...]` - Filter by lockdown status (creatingWhitelist, installing, locked, notInstalled, registering, starting, stopping, unavailable, uninstalled, unlocked)
- `--tamper-protection / --no-tamper-protection` - Filter by tamper protection status
- `--hostname-contains TEXT` - Filter by hostname substring
- `--last-seen-before TEXT` - Filter endpoints last seen before (ISO 8601: YYYY-MM-DDTHH:MM:SS, assumed UTC)
- `--last-seen-after TEXT` - Filter endpoints last seen after (ISO 8601: YYYY-MM-DDTHH:MM:SS, assumed UTC)
- `--ids TEXT` - Filter by endpoint IDs (comma-separated)
- `--ip-addresses TEXT` - Filter by IP addresses (comma-separated)
- `--mac-addresses TEXT` - Filter by MAC addresses (comma-separated)
- `--search TEXT` - Search query across endpoint fields

**Output Options:**
- `--view [basic|summary|full]` - Detail level for results (default: summary)
- `--page-size INTEGER` - Number of items per page (1-1000, default: 50)
- `--all-pages` - Fetch all pages
- `--output [table|json|csv]` - Output format (default: table)
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
# List all endpoints (table format)
pysophos endpoint list

# Filter by health status
pysophos endpoint list --health-status bad

# Multiple filters
pysophos endpoint list --health-status bad --endpoint-type server

# Filter by hostname
pysophos endpoint list --hostname-contains "web-server"

# Filter by last seen date
pysophos endpoint list --last-seen-after 2024-01-01T00:00:00

# Filter by tamper protection and get full details
pysophos endpoint list --tamper-protection --view full

# Search across all fields
pysophos endpoint list --search "192.168.1"

# Filter by specific endpoint IDs
pysophos endpoint list --ids "id1,id2,id3"

# Export to JSON with multiple filters
pysophos endpoint list --health-status bad --endpoint-type server --output json -f endpoints.json

# Export all pages to CSV
pysophos endpoint list --all-pages --output csv -f all_endpoints.csv
```

### `pysophos endpoint get`

Get details for a specific endpoint.

**Arguments:**
- `ENDPOINT_ID` - The endpoint ID

**Options:**
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos endpoint get abc-123-def
pysophos endpoint get abc-123-def --output json
```

### `pysophos endpoint scan`

Trigger a scan on an endpoint.

**Arguments:**
- `ENDPOINT_ID` - The endpoint ID

**Options:**
- `--comment TEXT` - Comment explaining the scan
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos endpoint scan abc-123-def
pysophos endpoint scan abc-123-def --comment "Routine security scan"
```

### `pysophos endpoint isolate`

Isolate an endpoint from the network.

**Arguments:**
- `ENDPOINT_ID` - The endpoint ID

**Options:**
- `--comment TEXT` - Comment explaining the isolation (required)
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos endpoint isolate abc-123-def --comment "Security incident response"
```

### `pysophos endpoint unisolate`

Remove isolation from an endpoint.

**Arguments:**
- `ENDPOINT_ID` - The endpoint ID

**Options:**
- `--comment TEXT` - Comment explaining the unisolation
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos endpoint unisolate abc-123-def --comment "Threat remediated"
```

### `pysophos endpoint tamper status`

Get tamper protection status for an endpoint.

**Arguments:**
- `ENDPOINT_ID` - The endpoint ID

**Options:**
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos endpoint tamper status abc-123-def
pysophos endpoint tamper status abc-123-def --output json
```

### `pysophos endpoint tamper update`

Update tamper protection for an endpoint.

**Arguments:**
- `ENDPOINT_ID` - The endpoint ID

**Options:**
- `--enable / --disable` - Enable or disable tamper protection
- `--regenerate-password` - Regenerate tamper protection password
- `--sync` - Use synchronous mode

**Examples:**
```bash
# Enable tamper protection
pysophos endpoint tamper update abc-123-def --enable

# Disable tamper protection
pysophos endpoint tamper update abc-123-def --disable

# Enable and regenerate password
pysophos endpoint tamper update abc-123-def --enable --regenerate-password
```

## Alert Commands

Manage alerts.

### `pysophos alerts list`

List alerts with optional filtering.

**Options:**
- `--severity [low|medium|high|critical]` - Filter by severity (can specify multiple)
- `--product [endpoint|server|mobile|email|firewall]` - Filter by product (can specify multiple)
- `--page-size INTEGER` - Number of items per page (default: 50)
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
# List all alerts
pysophos alerts list

# Filter by severity (multiple values)
pysophos alerts list --severity high --severity critical

# Filter by product
pysophos alerts list --product endpoint

# Export to JSON
pysophos alerts list --output json -f alerts.json

# Multiple filters
pysophos alerts list --severity high --product endpoint --output csv
```

### `pysophos alerts get`

Get details for a specific alert.

**Arguments:**
- `ALERT_ID` - The alert ID

**Options:**
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos alerts get alert-123
pysophos alerts get alert-123 --output json
```

### `pysophos alerts action`

Perform an action on an alert.

**Arguments:**
- `ALERT_ID` - The alert ID
- `ACTION` - Action to perform (acknowledge, clearThreat, clearPua)

**Options:**
- `--message TEXT` - Message explaining the action
- `--sync` - Use synchronous mode

**Examples:**
```bash
# Acknowledge alert
pysophos alerts action alert-123 acknowledge

# Clear threat with message
pysophos alerts action alert-123 clearThreat --message "False positive - approved application"
```

## Tenant Commands

Query tenant information.

### `pysophos tenants list`

List tenants.

**Options:**
- `--region [us|eu|ap|de|ie]` - Filter by data region
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos tenants list
pysophos tenants list --region us --output json
```

### `pysophos tenants get`

Get details for a specific tenant.

**Arguments:**
- `TENANT_ID` - The tenant ID

**Options:**
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos tenants get tenant-123
pysophos tenants get tenant-123 --output json
```

## Admin Commands

Manage administrators.

### `pysophos admins list`

List administrators.

**Options:**
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos admins list
pysophos admins list --output json -f admins.json
```

## Role Commands

Manage roles.

### `pysophos roles list`

List roles.

**Options:**
- `--output [table|json|csv]` - Output format
- `-f, --output-file PATH` - Save output to file
- `--no-color` - Disable colored output
- `--sync` - Use synchronous mode

**Examples:**
```bash
pysophos roles list
pysophos roles list --output json
```

## Output Formats

### Table Format (Default)

Rich formatted tables with colored output:

```bash
pysophos endpoint list
```

Output:
```
┌──────────┬──────────────┬────────┬──────────┬─────────────┐
│ ID       │ Hostname     │ Health │ Type     │ OS          │
├──────────┼──────────────┼────────┼──────────┼─────────────┤
│ abc-123  │ DESKTOP-001  │ good   │ computer │ Windows 10  │
│ def-456  │ SERVER-001   │ bad    │ server   │ Win Server  │
└──────────┴──────────────┴────────┴──────────┴─────────────┘
```

### JSON Format

Pretty-printed JSON:

```bash
pysophos endpoint list --output json
```

Output:
```json
{
  "items": [
    {
      "id": "abc-123",
      "hostname": "DESKTOP-001",
      "health": "good",
      "type": "computer",
      "os": "Windows 10"
    }
  ]
}
```

### CSV Format

Standard CSV with headers:

```bash
pysophos endpoint list --output csv -f endpoints.csv
```

Output (endpoints.csv):
```csv
id,hostname,health,type,os
abc-123,DESKTOP-001,good,computer,Windows 10
def-456,SERVER-001,bad,server,Windows Server 2019
```

## Common Workflows

### 1. Daily Security Check

```bash
# Check for bad health endpoints
pysophos endpoint list --health-status bad --output csv -f bad_endpoints.csv

# Check for critical alerts
pysophos alerts list --severity critical --output json -f critical_alerts.json

# Generate report
cat bad_endpoints.csv critical_alerts.json > daily_report.txt
```

### 2. Incident Response

```bash
# Get alert details
pysophos alerts get alert-123 --output json

# Get affected endpoint
pysophos endpoint get endpoint-456 --output json

# Isolate endpoint
pysophos endpoint isolate endpoint-456 --comment "Incident #123 - ransomware detected"

# Acknowledge alert
pysophos alerts action alert-123 acknowledge --message "Endpoint isolated, investigating"
```

### 3. Bulk Export

```bash
# Export all endpoints
pysophos endpoint list --all-pages --output json -f all_endpoints.json

# Export all alerts from last month
pysophos alerts list --all-pages --output csv -f alerts.csv

# Export tenant information
pysophos tenants list --output json -f tenants.json
```

## Tips & Tricks

### 1. Use Shell Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias pys='pysophos'
alias pys-bad='pysophos endpoint list --health-status bad'
alias pys-alerts='pysophos alerts list --severity high --severity critical'
```

### 2. Pipe to jq for JSON Processing

```bash
pysophos endpoint list --output json | jq '.items[] | select(.health == "bad")'
```

### 3. Combine with Other Tools

```bash
# Send to Slack
pysophos alerts list --severity critical --output json | \
  jq -r '.items[0].description' | \
  slack-cli -c '#security' -m "Critical Alert: $(cat)"

# Create ticket
pysophos endpoint list --health-status bad --output csv | \
  python create_ticket.py
```

### 4. Debugging

Use `--debug` for detailed output:

```bash
pysophos --debug endpoint list
```

---

**Need more help?** → [API Reference](../api/index.md) | [Examples](../examples/cli-examples.md)

