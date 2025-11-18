# Examples

Code examples and tutorials for PySophosCentralApi.

## Quick Links

- **[Basic Examples](#basic-examples)** - Simple, common use cases
- **[Advanced Examples](#advanced-examples)** - Complex scenarios
- **[CLI Examples](#cli-examples)** - Command-line usage
- **[Integration Examples](#integration-examples)** - Integration with other tools

## Basic Examples

### 1. List All Endpoints

**Async:**
```python
import asyncio
from pysophoscentralapi.core import Config
from pysophoscentralapi.api.endpoint import EndpointAPI

async def list_endpoints():
    config = Config.from_file()
    
    async with EndpointAPI(config) as api:
        endpoints = await api.list()
        
        for endpoint in endpoints:
            print(f"{endpoint.hostname}: {endpoint.health}")

asyncio.run(list_endpoints())
```

**Sync:**
```python
from pysophoscentralapi.core import Config
from pysophoscentralapi.sync.endpoint import EndpointAPISync

config = Config.from_file()

with EndpointAPISync(config) as api:
    endpoints = api.list()
    
    for endpoint in endpoints:
        print(f"{endpoint.hostname}: {endpoint.health}")
```

### 2. Filter Endpoints by Health

```python
from pysophoscentralapi.api.endpoint.models import EndpointFilters, HealthStatus

async with EndpointAPI(config) as api:
    # Create filter for bad health
    filters = EndpointFilters(
        health_status=[HealthStatus.BAD, HealthStatus.SUSPICIOUS]
    )
    
    bad_endpoints = await api.list(filters=filters)
    print(f"Found {len(bad_endpoints)} unhealthy endpoints")
```

### 3. Get High-Severity Alerts

```python
from pysophoscentralapi.api.common import CommonAPI
from pysophoscentralapi.api.common.models import AlertFilters, Severity

async with CommonAPI(config) as api:
    filters = AlertFilters(
        severity=[Severity.HIGH, Severity.CRITICAL]
    )
    
    alerts = await api.alerts.list(filters=filters)
    
    for alert in alerts:
        print(f"[{alert.severity}] {alert.description}")
```

### 4. Scan an Endpoint

```python
async with EndpointAPI(config) as api:
    # Trigger scan
    await api.scan(
        endpoint_id="abc-123-def-456",
        comment="Weekly security scan"
    )
    print("Scan triggered successfully")
```

### 5. Export Data to JSON

```python
from pysophoscentralapi.exporters import JSONExporter
from pathlib import Path

# Get data
async with EndpointAPI(config) as api:
    endpoints = await api.list()

# Export to JSON file
exporter = JSONExporter(
    output_file=Path("endpoints.json"),
    indent=2,
    sort_keys=True
)
exporter.export(endpoints)
print("Data exported to endpoints.json")
```

### 6. Export Data to CSV

```python
from pysophoscentralapi.exporters import CSVExporter
from pathlib import Path

# Get data
async with EndpointAPI(config) as api:
    endpoints = await api.list()

# Export to CSV
exporter = CSVExporter(
    output_file=Path("endpoints.csv"),
    flatten_nested=True,
    custom_headers={
        "id": "Endpoint ID",
        "hostname": "Hostname",
        "health": "Health Status"
    }
)
exporter.export(endpoints)
```

## Advanced Examples

### 1. Complex Filtering with QueryBuilder

```python
from pysophoscentralapi.filters import QueryBuilder
from datetime import datetime, timezone, timedelta

# Build complex query
query = QueryBuilder()

# Add filters
query.filter().equals("status", "active")
query.filter().contains("hostname", "SERVER")
query.filter().date_range(
    "last_seen",
    start=datetime.now(timezone.utc) - timedelta(days=7)
)

# Add sorting
query.sort_ascending("hostname")
query.sort_descending("last_seen")

# Add pagination and field selection
query.page_size(100)
query.fields("id", "hostname", "health", "last_seen")

# Build parameters
params = query.build()
print(f"Query parameters: {params}")
```

### 2. Batch Processing with Progress

```python
from pysophoscentralapi.exporters import JSONExporter

async with EndpointAPI(config) as api:
    # Get all endpoints (large dataset)
    all_endpoints = []
    
    async for endpoint in api.paginate(page_size=100):
        all_endpoints.append(endpoint)

# Export with progress indicator
exporter = JSONExporter(output_file=Path("all_endpoints.json"))
exporter.export_batch(
    all_endpoints,
    batch_size=500,
    show_progress=True
)
```

### 3. Incident Response Workflow

```python
async def respond_to_incident(alert_id: str, endpoint_id: str):
    """Complete incident response workflow."""
    config = Config.from_file()
    
    # Get alert details
    async with CommonAPI(config) as api:
        alert = await api.alerts.get(alert_id)
        print(f"Alert: {alert.description}")
        print(f"Severity: {alert.severity}")
    
    # Get endpoint details
    async with EndpointAPI(config) as api:
        endpoint = await api.get(endpoint_id)
        print(f"Endpoint: {endpoint.hostname}")
        print(f"Health: {endpoint.health}")
        
        # Isolate endpoint
        print("Isolating endpoint...")
        await api.isolate(
            endpoint_id=endpoint_id,
            comment=f"Incident response for alert {alert_id}"
        )
        
        # Trigger scan
        print("Triggering security scan...")
        await api.scan(
            endpoint_id=endpoint_id,
            comment="Post-isolation security scan"
        )
    
    # Acknowledge alert
    async with CommonAPI(config) as api:
        await api.alerts.perform_action(
            alert_id=alert_id,
            action="acknowledge",
            message="Endpoint isolated and scan initiated"
        )
    
    print("Incident response completed")

# Run
asyncio.run(respond_to_incident("alert-123", "endpoint-456"))
```

### 4. Health Status Report Generator

```python
from collections import Counter
from pysophoscentralapi.exporters import CSVExporter

async def generate_health_report():
    """Generate endpoint health status report."""
    config = Config.from_file()
    
    async with EndpointAPI(config) as api:
        # Get all endpoints
        all_endpoints = []
        async for endpoint in api.paginate():
            all_endpoints.append(endpoint)
        
        # Count by health status
        health_counts = Counter(e.health for e in all_endpoints)
        
        # Count by type
        type_counts = Counter(e.type for e in all_endpoints)
        
        # Print summary
        print("=== Endpoint Health Report ===")
        print(f"Total Endpoints: {len(all_endpoints)}")
        print("\nBy Health Status:")
        for status, count in health_counts.items():
            print(f"  {status}: {count}")
        print("\nBy Type:")
        for type_, count in type_counts.items():
            print(f"  {type_}: {count}")
        
        # Export detailed report
        report_data = []
        for endpoint in all_endpoints:
            report_data.append({
                "hostname": endpoint.hostname,
                "health": endpoint.health,
                "type": endpoint.type,
                "os": endpoint.os.name if endpoint.os else "Unknown",
                "last_seen": endpoint.last_seen_at
            })
        
        exporter = CSVExporter(output_file=Path("health_report.csv"))
        exporter.export(report_data)
        print("\nDetailed report exported to health_report.csv")

asyncio.run(generate_health_report())
```

### 5. Multi-Tenant Operations

```python
async def process_all_tenants():
    """Process data across multiple tenants."""
    config = Config.from_file()
    
    async with CommonAPI(config) as api:
        # Get all tenants
        tenants = await api.tenants.list()
        
        for tenant in tenants:
            print(f"\nProcessing tenant: {tenant.name}")
            
            # Switch to tenant (update config)
            tenant_config = Config(
                auth=config.auth,
                api=APIConfig(
                    region=tenant.data_region,
                    tenant_id=tenant.id
                )
            )
            
            # Get endpoint count for this tenant
            async with EndpointAPI(tenant_config) as endpoint_api:
                endpoints = await endpoint_api.list(page_size=1)
                print(f"  Endpoints: {len(endpoints)}")
            
            # Get alert count
            async with CommonAPI(tenant_config) as tenant_api:
                alerts = await tenant_api.alerts.list(page_size=1)
                print(f"  Alerts: {len(alerts)}")

asyncio.run(process_all_tenants())
```

## CLI Examples

### Basic Commands

```bash
# List all endpoints
pysophos endpoint list

# Filter by health
pysophos endpoint list --health-status bad

# Export to JSON
pysophos endpoint list --output json -f endpoints.json

# Get alerts
pysophos alerts list --severity high --severity critical
```

### Scripting Examples

**Daily Security Check:**
```bash
#!/bin/bash

# Get critical alerts
pysophos alerts list --severity critical --output json > critical_alerts.json

# Get bad health endpoints
pysophos endpoint list --health-status bad --output csv > bad_endpoints.csv

# Send notification if issues found
ALERT_COUNT=$(jq '.items | length' critical_alerts.json)
if [ $ALERT_COUNT -gt 0 ]; then
    echo "Found $ALERT_COUNT critical alerts!"
    # Send to Slack/email
fi
```

**Bulk Endpoint Scan:**
```bash
#!/bin/bash

# Get all endpoint IDs with bad health
IDS=$(pysophos endpoint list --health-status bad --output json | \
      jq -r '.items[].id')

# Scan each endpoint
for ID in $IDS; do
    echo "Scanning $ID..."
    pysophos endpoint scan "$ID" --comment "Automated security scan"
    sleep 5  # Rate limiting
done
```

## Integration Examples

### 1. Integration with Pandas

```python
import pandas as pd
from pysophoscentralapi.core import Config
from pysophoscentralapi.api.endpoint import EndpointAPI

async def create_dataframe():
    config = Config.from_file()
    
    async with EndpointAPI(config) as api:
        endpoints = await api.list()
    
    # Convert to dict list
    data = [e.model_dump() for e in endpoints]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Analysis
    print(df.groupby('health')['id'].count())
    print(df.groupby('type')['id'].count())
    
    # Save to Excel
    df.to_excel("endpoints.xlsx", index=False)

asyncio.run(create_dataframe())
```

### 2. Integration with Elasticsearch

```python
from elasticsearch import Elasticsearch

async def sync_to_elasticsearch():
    config = Config.from_file()
    es = Elasticsearch(['localhost:9200'])
    
    async with EndpointAPI(config) as api:
        async for endpoint in api.paginate():
            # Index in Elasticsearch
            es.index(
                index='sophos-endpoints',
                id=endpoint.id,
                document=endpoint.model_dump()
            )
            print(f"Indexed {endpoint.hostname}")

asyncio.run(sync_to_elasticsearch())
```

### 3. Integration with Slack

```python
from slack_sdk import WebClient

async def send_critical_alerts_to_slack():
    config = Config.from_file()
    slack = WebClient(token="your-slack-token")
    
    async with CommonAPI(config) as api:
        filters = AlertFilters(severity=[Severity.CRITICAL])
        alerts = await api.alerts.list(filters=filters)
        
        for alert in alerts:
            slack.chat_postMessage(
                channel='#security',
                text=f"🚨 Critical Alert: {alert.description}"
            )

asyncio.run(send_critical_alerts_to_slack())
```

---

**More Examples:** Check the `/examples` directory in the repository for additional code samples.

