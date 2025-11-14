# PySophosCentralApi - Technical Specification

## 1. API Authentication & Authorization

### 1.1 OAuth2 Client Credentials Flow

Sophos Central uses OAuth2 with client credentials grant for API authentication.

**Authentication Flow:**

```
1. Obtain credentials (Client ID + Client Secret) from Sophos Central
2. Request access token from token endpoint
3. Use access token in Authorization header for API calls
4. Refresh token when expired
```

**Token Endpoint:**
- `POST https://id.sophos.com/api/v2/oauth2/token`

**Required Parameters:**
- `grant_type`: "client_credentials"
- `client_id`: Your client ID
- `client_secret`: Your client secret
- `scope`: "token" (for partner API)

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "optional"
}
```

### 1.2 Whoami Endpoint

After obtaining the access token, determine the appropriate API endpoint:

**Partner API Whoami:**
- `GET https://api.central.sophos.com/whoami/v1`

**Organization API Whoami:**
- `GET https://api.central.sophos.com/whoami/v1`

**Response Structure:**
```json
{
  "id": "organization-id",
  "idType": "tenant|partner|organization",
  "apiHosts": {
    "global": "https://api.central.sophos.com",
    "dataRegion": "https://api-us.central.sophos.com"
  }
}
```

### 1.3 Implementation Classes

**AuthConfig:**
```python
class AuthConfig:
    client_id: str
    client_secret: str
    token_endpoint: str = "https://id.sophos.com/api/v2/oauth2/token"
    scope: str = "token"
```

**Token:**
```python
class Token:
    access_token: str
    token_type: str
    expires_in: int
    expires_at: datetime
    refresh_token: Optional[str] = None
    
    def is_expired(self) -> bool
    def expires_soon(self, threshold_seconds: int = 300) -> bool
```

**AuthProvider:**
```python
class AuthProvider:
    async def get_token(self) -> Token
    async def refresh_token(self) -> Token
    async def get_authorization_header(self) -> dict[str, str]
```

---

## 2. API Client Architecture

### 2.1 Base HTTP Client

**HTTPClient:**
```python
class HTTPClient:
    def __init__(
        self,
        base_url: str,
        auth_provider: AuthProvider,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_retry: bool = True
    )
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None
    ) -> dict
    
    async def get(self, endpoint: str, params: Optional[dict] = None) -> dict
    async def post(self, endpoint: str, json: dict) -> dict
    async def patch(self, endpoint: str, json: dict) -> dict
    async def delete(self, endpoint: str) -> dict
```

**Features:**
- Automatic authentication header injection
- Retry logic with exponential backoff
- Rate limit handling (429 responses)
- Request/response logging
- Timeout handling
- Connection pooling

### 2.2 Pagination Handler

Sophos APIs use cursor-based pagination:

**Request:**
- `pageSize`: Number of items per page (default: 50, max: 1000)
- `pageFromKey`: Cursor for next page

**Response:**
```json
{
  "items": [...],
  "pages": {
    "current": 1,
    "size": 50,
    "total": 10,
    "fromKey": "abc123",
    "nextKey": "def456",
    "maxSize": 1000
  }
}
```

**Paginator:**
```python
class Paginator:
    def __init__(
        self,
        client: HTTPClient,
        endpoint: str,
        page_size: int = 50,
        max_pages: Optional[int] = None
    )
    
    async def iter_pages(self) -> AsyncIterator[dict]
    async def iter_items(self) -> AsyncIterator[dict]
    async def get_all(self) -> list[dict]
```

---

## 3. Endpoint API Specification

Base URL: `{dataRegion}/endpoint/v1`

### 3.1 Endpoints Management

#### List Endpoints
```
GET /endpoints
```

**Query Parameters:**
- `pageSize` (int): Results per page (1-1000, default: 50)
- `pageFromKey` (str): Pagination cursor
- `view` (str): "basic" | "summary" | "full"
- `healthStatus` (str): Filter by health (good|suspicious|bad|unknown)
- `type` (str): Filter by type (computer|server|securityVm)
- `tamperProtectionEnabled` (bool): Filter by tamper protection status
- `lockdownStatus` (str): Filter by lockdown status
- `lastSeenBefore` (datetime): Filter endpoints last seen before
- `lastSeenAfter` (datetime): Filter endpoints last seen after
- `ids` (list[str]): Filter by specific IDs
- `hostnameContains` (str): Filter by hostname substring
- `ipAddresses` (list[str]): Filter by IP addresses
- `macAddresses` (list[str]): Filter by MAC addresses
- `search` (str): Search query
- `searchFields` (list[str]): Fields to search in

**Response:**
```json
{
  "items": [
    {
      "id": "endpoint-id",
      "type": "computer",
      "tenant": {
        "id": "tenant-id"
      },
      "hostname": "DESKTOP-123",
      "health": {
        "overall": "good",
        "threats": {
          "status": "good"
        },
        "services": {
          "status": "good",
          "serviceDetails": []
        }
      },
      "os": {
        "isServer": false,
        "platform": "windows",
        "name": "Windows 10 Pro",
        "majorVersion": 10,
        "minorVersion": 0,
        "build": 19045
      },
      "ipv4Addresses": ["192.168.1.100"],
      "ipv6Addresses": [],
      "macAddresses": ["00:11:22:33:44:55"],
      "associatedPerson": {
        "id": "person-id",
        "name": "John Doe",
        "viaLogin": "john.doe@example.com"
      },
      "tamperProtectionEnabled": true,
      "assignedProducts": [
        {
          "code": "coreAgent",
          "version": "2.2.0",
          "status": "installed"
        }
      ],
      "lastSeenAt": "2025-11-14T10:00:00.000Z"
    }
  ],
  "pages": {
    "current": 1,
    "size": 50,
    "total": 5,
    "nextKey": "next-page-key",
    "maxSize": 1000
  }
}
```

#### Get Endpoint
```
GET /endpoints/{endpointId}
```

**Response:** Single endpoint object (same structure as list item)

### 3.2 Endpoint Actions

#### Scan Endpoint
```
POST /endpoints/{endpointId}/scans
```

**Request Body:**
```json
{
  "enabled": true
}
```

**Response:**
```json
{
  "id": "scan-id",
  "status": "requested"
}
```

#### Isolate Endpoint
```
POST /endpoints/{endpointId}/isolation
```

**Request Body:**
```json
{
  "enabled": true,
  "comment": "Suspected malware infection"
}
```

**Response:**
```json
{
  "id": "isolation-id",
  "status": "requested"
}
```

#### Remove Isolation
```
DELETE /endpoints/{endpointId}/isolation
```

**Request Body:**
```json
{
  "comment": "Threat remediated"
}
```

### 3.3 Tamper Protection

#### Get Tamper Protection Status
```
GET /endpoints/{endpointId}/tamper-protection
```

**Response:**
```json
{
  "enabled": true,
  "globallyEnabled": true,
  "previouslyEnabled": true
}
```

#### Update Tamper Protection
```
POST /endpoints/{endpointId}/tamper-protection
```

**Request Body:**
```json
{
  "enabled": true,
  "regeneratePassword": false
}
```

#### Get Tamper Protection Password
```
GET /endpoints/{endpointId}/tamper-protection/password
```

**Response:**
```json
{
  "password": "xxxxxxxxxx"
}
```

### 3.4 Settings

#### Get Settings
```
GET /settings
```

**Response:**
```json
{
  "allowedItems": {...},
  "blockedItems": {...},
  "webControl": {...},
  "tamperProtection": {...}
}
```

#### Update Settings
```
PATCH /settings/{settingType}
```

Where `settingType` can be:
- `allowed-items`
- `blocked-items`
- `web-control`
- `tamper-protection`

---

## 4. Common API Specification

Base URL: `{dataRegion}/common/v1`

### 4.1 Alerts

#### List Alerts
```
GET /alerts
```

**Query Parameters:**
- `pageSize` (int): Results per page
- `pageFromKey` (str): Pagination cursor
- `product` (list[str]): Filter by product (endpoint, server, mobile, email, etc.)
- `category` (list[str]): Filter by category
- `groupKey` (str): Filter by group
- `severity` (list[str]): Filter by severity (low, medium, high, critical)
- `ids` (list[str]): Specific alert IDs
- `fields` (list[str]): Fields to return
- `from` (datetime): Alerts raised after this time
- `to` (datetime): Alerts raised before this time

**Response:**
```json
{
  "items": [
    {
      "id": "alert-id",
      "allowedActions": ["acknowledge", "clearThreat"],
      "category": "malware",
      "description": "Malware detected",
      "groupKey": "group-key",
      "managedAgent": {
        "id": "endpoint-id",
        "type": "computer"
      },
      "person": {
        "id": "person-id",
        "name": "John Doe"
      },
      "product": "endpoint",
      "raisedAt": "2025-11-14T10:00:00.000Z",
      "severity": "high",
      "tenant": {
        "id": "tenant-id",
        "name": "Tenant Name"
      },
      "type": "Event::Endpoint::Threat::Detected"
    }
  ],
  "pages": {...}
}
```

#### Get Alert
```
GET /alerts/{alertId}
```

**Response:** Single alert object

#### Update Alert
```
POST /alerts/{alertId}/actions
```

**Request Body:**
```json
{
  "action": "acknowledge",
  "message": "Investigating"
}
```

### 4.2 Tenants

#### List Tenants
```
GET /tenants
```

**Query Parameters:**
- `pageSize` (int)
- `pageFromKey` (str)
- `dataRegion` (str): Filter by data region
- `ids` (list[str]): Specific tenant IDs

**Response:**
```json
{
  "items": [
    {
      "id": "tenant-id",
      "name": "Tenant Name",
      "dataRegion": "us",
      "dataGeography": "US",
      "billingType": "trial|usage|user",
      "partner": {
        "id": "partner-id"
      },
      "apiHost": "https://api-us.central.sophos.com",
      "status": "active"
    }
  ],
  "pages": {...}
}
```

#### Get Tenant
```
GET /tenants/{tenantId}
```

### 4.3 Admins

#### List Admins
```
GET /admins
```

**Response:**
```json
{
  "items": [
    {
      "id": "admin-id",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "role": {
        "id": "role-id",
        "name": "Super Admin"
      },
      "tenants": [
        {
          "id": "tenant-id",
          "name": "Tenant Name"
        }
      ]
    }
  ]
}
```

#### Create Admin
```
POST /admins
```

**Request Body:**
```json
{
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@example.com",
  "roleId": "role-id",
  "tenantIds": ["tenant-id-1", "tenant-id-2"]
}
```

#### Update Admin
```
PATCH /admins/{adminId}
```

#### Delete Admin
```
DELETE /admins/{adminId}
```

### 4.4 Roles

#### List Roles
```
GET /roles
```

**Response:**
```json
{
  "items": [
    {
      "id": "role-id",
      "name": "Super Admin",
      "description": "Full access to all features",
      "permissions": [
        {
          "scope": "tenant",
          "actions": ["read", "create", "update", "delete"]
        }
      ]
    }
  ]
}
```

#### Get Role
```
GET /roles/{roleId}
```

#### Create Role
```
POST /roles
```

**Request Body:**
```json
{
  "name": "Custom Role",
  "description": "Custom role description",
  "permissions": [...]
}
```

---

## 5. Data Models

### 5.1 Core Models

**BaseModel:**
```python
class BaseModel(pydantic.BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )
```

**PaginatedResponse:**
```python
class PageInfo(BaseModel):
    current: int
    size: int
    total: int
    from_key: Optional[str] = Field(None, alias="fromKey")
    next_key: Optional[str] = Field(None, alias="nextKey")
    max_size: int = Field(alias="maxSize")

class PaginatedResponse[T](BaseModel, Generic[T]):
    items: list[T]
    pages: PageInfo
```

### 5.2 Endpoint Models

**Endpoint:**
```python
class HealthStatus(str, Enum):
    GOOD = "good"
    SUSPICIOUS = "suspicious"
    BAD = "bad"
    UNKNOWN = "unknown"

class EndpointType(str, Enum):
    COMPUTER = "computer"
    SERVER = "server"
    SECURITY_VM = "securityVm"

class OSInfo(BaseModel):
    is_server: bool = Field(alias="isServer")
    platform: str
    name: str
    major_version: int = Field(alias="majorVersion")
    minor_version: int = Field(alias="minorVersion")
    build: int

class Health(BaseModel):
    overall: HealthStatus
    threats: dict[str, str]
    services: dict[str, str | list]

class AssignedProduct(BaseModel):
    code: str
    version: str
    status: str

class Endpoint(BaseModel):
    id: str
    type: EndpointType
    tenant_id: str = Field(alias="tenant.id")
    hostname: str
    health: Health
    os: OSInfo
    ipv4_addresses: list[str] = Field(default_factory=list, alias="ipv4Addresses")
    ipv6_addresses: list[str] = Field(default_factory=list, alias="ipv6Addresses")
    mac_addresses: list[str] = Field(default_factory=list, alias="macAddresses")
    tamper_protection_enabled: bool = Field(alias="tamperProtectionEnabled")
    assigned_products: list[AssignedProduct] = Field(alias="assignedProducts")
    last_seen_at: datetime = Field(alias="lastSeenAt")
```

**EndpointFilters:**
```python
class EndpointFilters(BaseModel):
    page_size: int = Field(50, ge=1, le=1000)
    page_from_key: Optional[str] = None
    view: Literal["basic", "summary", "full"] = "summary"
    health_status: Optional[HealthStatus] = None
    type: Optional[EndpointType] = None
    tamper_protection_enabled: Optional[bool] = None
    last_seen_before: Optional[datetime] = None
    last_seen_after: Optional[datetime] = None
    ids: Optional[list[str]] = None
    hostname_contains: Optional[str] = None
    ip_addresses: Optional[list[str]] = None
    mac_addresses: Optional[list[str]] = None
    search: Optional[str] = None
    search_fields: Optional[list[str]] = None
    
    def to_params(self) -> dict[str, str]:
        """Convert filters to API query parameters"""
        # Implementation...
```

### 5.3 Alert Models

**Alert:**
```python
class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertCategory(str, Enum):
    MALWARE = "malware"
    PUA = "pua"
    RANSOMWARE = "ransomware"
    EXPLOIT = "exploit"
    # ... more categories

class Alert(BaseModel):
    id: str
    allowed_actions: list[str] = Field(alias="allowedActions")
    category: AlertCategory
    description: str
    group_key: str = Field(alias="groupKey")
    managed_agent_id: Optional[str] = Field(None, alias="managedAgent.id")
    managed_agent_type: Optional[str] = Field(None, alias="managedAgent.type")
    person_id: Optional[str] = Field(None, alias="person.id")
    person_name: Optional[str] = Field(None, alias="person.name")
    product: str
    raised_at: datetime = Field(alias="raisedAt")
    severity: AlertSeverity
    tenant_id: str = Field(alias="tenant.id")
    tenant_name: str = Field(alias="tenant.name")
    type: str
```

**AlertFilters:**
```python
class AlertFilters(BaseModel):
    page_size: int = Field(50, ge=1, le=1000)
    page_from_key: Optional[str] = None
    product: Optional[list[str]] = None
    category: Optional[list[AlertCategory]] = None
    group_key: Optional[str] = None
    severity: Optional[list[AlertSeverity]] = None
    ids: Optional[list[str]] = None
    from_date: Optional[datetime] = Field(None, alias="from")
    to_date: Optional[datetime] = Field(None, alias="to")
    
    def to_params(self) -> dict[str, str]:
        """Convert filters to API query parameters"""
        # Implementation...
```

---

## 6. Error Handling

### 6.1 API Error Responses

**Standard Error Format:**
```json
{
  "error": "error_code",
  "correlationId": "correlation-id",
  "message": "Human readable error message",
  "requestId": "request-id"
}
```

**HTTP Status Codes:**
- 400: Bad Request - Invalid parameters
- 401: Unauthorized - Invalid/expired token
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource doesn't exist
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Server error
- 503: Service Unavailable - Temporary outage

### 6.2 Exception Mapping

```python
class SophosAPIException(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.correlation_id = correlation_id
        self.request_id = request_id

# Specific exceptions
class AuthenticationError(SophosAPIException): pass
class InvalidCredentialsError(AuthenticationError): pass
class TokenExpiredError(AuthenticationError): pass
class RateLimitError(SophosAPIException): pass
class ResourceNotFoundError(SophosAPIException): pass
class ValidationError(SophosAPIException): pass
class PermissionError(SophosAPIException): pass
```

### 6.3 Retry Strategy

```python
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 2,  # Exponential backoff: 2^retry seconds
    "retry_status_codes": [429, 500, 502, 503, 504],
    "retry_methods": ["GET", "PUT", "DELETE", "PATCH"],
}
```

---

## 7. Filter System Design

### 7.1 Filter Builder

```python
class FilterBuilder:
    def __init__(self):
        self._filters: dict[str, Any] = {}
    
    def health_status(self, status: HealthStatus) -> "FilterBuilder":
        self._filters["healthStatus"] = status.value
        return self
    
    def type(self, endpoint_type: EndpointType) -> "FilterBuilder":
        self._filters["type"] = endpoint_type.value
        return self
    
    def hostname_contains(self, hostname: str) -> "FilterBuilder":
        self._filters["hostnameContains"] = hostname
        return self
    
    def last_seen_after(self, dt: datetime) -> "FilterBuilder":
        self._filters["lastSeenAfter"] = dt.isoformat()
        return self
    
    def build(self) -> dict[str, str]:
        return self._filters

# Usage:
filters = (
    FilterBuilder()
    .health_status(HealthStatus.GOOD)
    .type(EndpointType.COMPUTER)
    .hostname_contains("DESKTOP")
    .build()
)
```

### 7.2 Query String Builder

```python
def build_query_string(filters: dict[str, Any]) -> str:
    """Convert filter dict to URL query string"""
    params = []
    for key, value in filters.items():
        if isinstance(value, list):
            for item in value:
                params.append(f"{key}={quote_plus(str(item))}")
        elif value is not None:
            params.append(f"{key}={quote_plus(str(value))}")
    return "&".join(params)
```

---

## 8. Export System Design

### 8.1 Exporter Interface

```python
class Exporter(ABC):
    @abstractmethod
    def export(
        self,
        data: list[dict] | list[BaseModel],
        output: str | Path | None = None,
        **kwargs
    ) -> Optional[str]:
        """
        Export data to specified format.
        
        Args:
            data: Data to export
            output: Output file path or None for stdout
            **kwargs: Format-specific options
            
        Returns:
            String output if output is None, otherwise None
        """
        pass
```

### 8.2 JSON Exporter

```python
class JSONExporter(Exporter):
    def export(
        self,
        data: list[dict] | list[BaseModel],
        output: str | Path | None = None,
        indent: int = 2,
        compact: bool = False,
        **kwargs
    ) -> Optional[str]:
        # Convert Pydantic models to dicts
        if data and isinstance(data[0], BaseModel):
            data = [item.model_dump(by_alias=True) for item in data]
        
        # Set indent
        indent = None if compact else indent
        
        # Serialize
        json_str = json.dumps(data, indent=indent, default=str)
        
        # Write or return
        if output:
            Path(output).write_text(json_str)
            return None
        return json_str
```

### 8.3 CSV Exporter

```python
class CSVExporter(Exporter):
    def export(
        self,
        data: list[dict] | list[BaseModel],
        output: str | Path | None = None,
        delimiter: str = ",",
        flatten: bool = True,
        selected_fields: Optional[list[str]] = None,
        **kwargs
    ) -> Optional[str]:
        # Convert Pydantic models to dicts
        if data and isinstance(data[0], BaseModel):
            data = [item.model_dump(by_alias=True) for item in data]
        
        # Flatten nested structures if needed
        if flatten:
            data = [self._flatten_dict(item) for item in data]
        
        # Filter fields
        if selected_fields:
            data = [
                {k: v for k, v in item.items() if k in selected_fields}
                for item in data
            ]
        
        # Write CSV
        if not data:
            return "" if not output else None
        
        buffer = StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=data[0].keys(),
            delimiter=delimiter
        )
        writer.writeheader()
        writer.writerows(data)
        
        csv_str = buffer.getvalue()
        
        if output:
            Path(output).write_text(csv_str)
            return None
        return csv_str
    
    def _flatten_dict(
        self,
        d: dict,
        parent_key: str = "",
        sep: str = "."
    ) -> dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                # Convert list of dicts to JSON string
                items.append((new_key, json.dumps(v)))
            elif isinstance(v, list):
                # Convert simple lists to comma-separated string
                items.append((new_key, ",".join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)
```

---

## 9. CLI Implementation Details

### 9.1 Click Command Structure

```python
@click.group()
@click.option("--config", type=click.Path(), help="Config file path")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, config, debug):
    """PySophos - Sophos Central API CLI"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)
    ctx.obj["debug"] = debug
    setup_logging(debug)

@cli.group()
def endpoint():
    """Endpoint API commands"""
    pass

@endpoint.command("list")
@click.option("--health-status", type=click.Choice(["good", "suspicious", "bad", "unknown"]))
@click.option("--type", type=click.Choice(["computer", "server", "securityVm"]))
@click.option("--hostname", help="Filter by hostname (contains)")
@click.option("--output", "-o", type=click.Choice(["table", "json", "csv"]), default="table")
@click.option("--export-file", type=click.Path(), help="Export to file")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all pages")
@click.option("--limit", type=int, help="Limit number of results")
@click.pass_context
async def list_endpoints(ctx, health_status, type, hostname, output, export_file, fetch_all, limit):
    """List endpoints with optional filtering"""
    # Implementation
    pass
```

### 9.2 Output Formatting

**Table Output (using rich):**
```python
def format_table(data: list[dict], columns: list[str]) -> Table:
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="blue"
    )
    
    # Add columns
    for col in columns:
        table.add_column(col, style="white")
    
    # Add rows
    for item in data:
        row = []
        for col in columns:
            value = get_nested_value(item, col)
            # Color code based on value
            if col == "health.overall":
                value = colorize_health(value)
            row.append(str(value))
        table.add_row(*row)
    
    return table
```

**Color Coding:**
```python
def colorize_health(status: str) -> str:
    colors = {
        "good": "green",
        "suspicious": "yellow",
        "bad": "red",
        "unknown": "dim"
    }
    color = colors.get(status, "white")
    return f"[{color}]{status}[/{color}]"

def colorize_severity(severity: str) -> str:
    colors = {
        "low": "blue",
        "medium": "yellow",
        "high": "bright_red",
        "critical": "bold red"
    }
    color = colors.get(severity, "white")
    return f"[{color}]{severity}[/{color}]"
```

---

## 10. Configuration System

### 10.1 Configuration Structure

```python
class APIConfig(BaseModel):
    region: str = "us"
    tenant_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit_retry: bool = True

class AuthConfig(BaseModel):
    client_id: str
    client_secret: str
    credentials_file: Optional[Path] = None

class OutputConfig(BaseModel):
    default_format: Literal["table", "json", "csv"] = "table"
    color_enabled: bool = True
    page_size: int = 50
    table_max_width: Optional[int] = None

class ExportConfig(BaseModel):
    default_directory: Path = Path.home() / "sophos-exports"
    json_indent: int = 2
    csv_delimiter: str = ","
    csv_flatten: bool = True

class Config(BaseModel):
    auth: AuthConfig
    api: APIConfig = APIConfig()
    output: OutputConfig = OutputConfig()
    export: ExportConfig = ExportConfig()
```

### 10.2 Configuration Loading

```python
def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file and environment"""
    # Default path
    if not config_path:
        config_path = get_config_dir() / "config.toml"
    
    # Load from file if exists
    if config_path.exists():
        with open(config_path, "rb") as f:
            config_dict = tomli.load(f)
    else:
        config_dict = {}
    
    # Override with environment variables
    if os.getenv("SOPHOS_CLIENT_ID"):
        config_dict.setdefault("auth", {})["client_id"] = os.getenv("SOPHOS_CLIENT_ID")
    if os.getenv("SOPHOS_CLIENT_SECRET"):
        config_dict.setdefault("auth", {})["client_secret"] = os.getenv("SOPHOS_CLIENT_SECRET")
    # ... more env vars
    
    return Config(**config_dict)
```

---

## 11. Testing Infrastructure

### 11.1 Test Fixtures

```python
@pytest.fixture
def mock_http_client():
    """Mock HTTP client with predefined responses"""
    client = Mock(spec=HTTPClient)
    # Setup responses
    return client

@pytest.fixture
def sample_endpoint():
    """Sample endpoint data"""
    return {
        "id": "endpoint-123",
        "type": "computer",
        "hostname": "DESKTOP-TEST",
        "health": {"overall": "good"},
        # ... more fields
    }

@pytest.fixture
async def api_client(mock_http_client):
    """Create API client with mock HTTP client"""
    auth = Mock(spec=AuthProvider)
    return SophosAPIClient(mock_http_client, auth)
```

### 11.2 Response Mocking

```python
def mock_response(status_code: int, json_data: dict) -> Mock:
    """Create mock response"""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.headers = {}
    return response

@pytest.mark.asyncio
async def test_list_endpoints(api_client, sample_endpoint):
    """Test listing endpoints"""
    # Setup mock response
    api_client.http_client.get.return_value = {
        "items": [sample_endpoint],
        "pages": {"current": 1, "size": 1, "total": 1}
    }
    
    # Call method
    result = await api_client.endpoint.list_endpoints()
    
    # Assertions
    assert len(result.items) == 1
    assert result.items[0].id == "endpoint-123"
    api_client.http_client.get.assert_called_once()
```

---

## 12. Performance Considerations

### 12.1 Connection Pooling

```python
# httpx supports connection pooling by default
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=30.0
    )
)
```

### 12.2 Response Caching

```python
class CachedResponse:
    def __init__(self, data: dict, expires_at: datetime):
        self.data = data
        self.expires_at = expires_at
    
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at

class ResponseCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, CachedResponse] = {}
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[dict]:
        if key in self._cache:
            cached = self._cache[key]
            if not cached.is_expired():
                return cached.data
            del self._cache[key]
        return None
    
    def set(self, key: str, data: dict, ttl: Optional[int] = None):
        ttl = ttl or self._default_ttl
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl)
        self._cache[key] = CachedResponse(data, expires_at)
```

### 12.3 Concurrent Requests

```python
async def fetch_multiple_endpoints(
    client: HTTPClient,
    endpoint_ids: list[str]
) -> list[Endpoint]:
    """Fetch multiple endpoints concurrently"""
    tasks = [
        client.get(f"/endpoints/{endpoint_id}")
        for endpoint_id in endpoint_ids
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    endpoints = []
    for response in responses:
        if isinstance(response, Exception):
            logger.error(f"Failed to fetch endpoint: {response}")
            continue
        endpoints.append(Endpoint(**response))
    
    return endpoints
```

---

## 13. Security Implementation

### 13.1 Credential Storage

```python
class SecureCredentialStore:
    """Store credentials securely"""
    
    def __init__(self, config_dir: Path):
        self.credentials_file = config_dir / "credentials.json"
        self.credentials_file.chmod(0o600)  # Owner read/write only
    
    def save(self, credentials: dict):
        """Save credentials (consider encryption)"""
        # In production, consider using keyring library
        # or encrypting the credentials file
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)
        self.credentials_file.chmod(0o600)
    
    def load(self) -> dict:
        """Load credentials"""
        if not self.credentials_file.exists():
            raise FileNotFoundError("Credentials file not found")
        return json.loads(self.credentials_file.read_text())
```

### 13.2 Sensitive Data Filtering

```python
class SensitiveDataFilter:
    """Filter sensitive data from logs"""
    
    SENSITIVE_FIELDS = [
        "client_secret",
        "access_token",
        "refresh_token",
        "password",
        "authorization"
    ]
    
    @classmethod
    def filter_dict(cls, data: dict) -> dict:
        """Recursively filter sensitive fields"""
        filtered = {}
        for key, value in data.items():
            if key.lower() in cls.SENSITIVE_FIELDS:
                filtered[key] = "***REDACTED***"
            elif isinstance(value, dict):
                filtered[key] = cls.filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    cls.filter_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        return filtered
```

---

This technical specification provides detailed implementation guidance for the PySophosCentralApi project. It should be used in conjunction with the main project plan to ensure consistent and high-quality implementation.

