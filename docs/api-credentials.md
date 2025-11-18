# Sophos Central API Credentials: Partner vs Organization

## Overview

Sophos Central provides two types of API credentials, each with different access levels and capabilities. Understanding the difference is crucial for using the correct endpoints.

## Credential Types

### 1. **Organization-Level Credentials**
- **Access Scope**: Single organization only
- **Typical Use Case**: Managing your own organization's endpoints, alerts, and security settings
- **ID Type**: `organization` (shown in `whoami` response)

**Available Endpoints:**
- ✅ Endpoint API (list, manage, scan, isolate endpoints)
- ✅ Alert API (list, view, manage alerts)
- ❌ Tenant management (returns 404)
- ❌ Admin management (returns 404)  
- ❌ Role management (returns 404)

### 2. **Partner-Level Credentials**
- **Access Scope**: Multiple tenants/organizations
- **Typical Use Case**: MSPs managing multiple customer organizations
- **ID Type**: `partner` (shown in `whoami` response)

**Available Endpoints:**
- ✅ All Endpoint API endpoints
- ✅ All Alert API endpoints
- ✅ **Tenant management** (list and manage tenants)
- ✅ **Admin management** (create and manage admins)
- ✅ **Role management** (create and manage roles)

## Checking Your Credential Type

Use the `config test` command to check your credential type:

```bash
pysophos config test
```

**Output for Organization-level credentials:**
```
✓ Whoami request successful
  Organization ID: xxxx-xxxx-xxxx
  ID Type: organization
  
  Access Level: Organization (Limited to own organization data)
    Note: Tenant/Admin/Role endpoints require Partner-level credentials
```

**Output for Partner-level credentials:**
```
✓ Whoami request successful
  Organization ID: xxxx-xxxx-xxxx
  ID Type: partner
  
  Access Level: Partner (Full tenant management available)
```

## Common Errors

### 404 Error on Tenant Commands

**Error:**
```
API error: Unknown error | Status: 404
```

**Cause:** You're using Organization-level credentials to access Partner-only endpoints.

**Solution:** 
1. Verify your credential type: `pysophos config test`
2. If you need Partner-level access, obtain Partner API credentials from Sophos Central
3. Update your configuration with the new credentials

### Which Endpoints Require Partner Credentials?

The following CLI commands require Partner-level credentials:

```bash
# Tenant Management
pysophos tenants list          # ❌ Organization / ✅ Partner
pysophos tenants get <id>      # ❌ Organization / ✅ Partner

# Admin Management  
pysophos admins list           # ❌ Organization / ✅ Partner
pysophos admins create         # ❌ Organization / ✅ Partner
pysophos admins update <id>    # ❌ Organization / ✅ Partner
pysophos admins delete <id>    # ❌ Organization / ✅ Partner

# Role Management
pysophos roles list            # ❌ Organization / ✅ Partner
pysophos roles create          # ❌ Organization / ✅ Partner
pysophos roles update <id>     # ❌ Organization / ✅ Partner
pysophos roles delete <id>     # ❌ Organization / ✅ Partner
```

## Creating API Credentials

### Organization-Level Credentials

1. Log in to Sophos Central
2. Navigate to **Settings & Policies** > **API Credentials**
3. Click **Add Credential**
4. Select appropriate role (e.g., "Service Principal Super Admin")
5. Save the Client ID and Client Secret

### Partner-Level Credentials

1. Log in to Sophos Central **Partner Dashboard**
2. Navigate to **Settings** > **API Credentials Management**
3. Click **Add Credential**
4. Select appropriate partner role
5. Save the Client ID and Client Secret

## API Documentation Reference

For more information, see:
- [Sophos Central APIs Documentation](https://developer.sophos.com/)
- [Sophos Partner API Guide](https://developer.sophos.com/getting-started-partner)
- [Sophos Organization API Guide](https://developer.sophos.com/getting-started-organization)

## Example Configuration

**Organization-level credentials:**
```toml
[auth]
client_id = "org-client-id"
client_secret = "org-client-secret"

[api]
region = "us"
```

**Partner-level credentials:**
```toml
[auth]
client_id = "partner-client-id"  
client_secret = "partner-client-secret"

[api]
region = "us"
```

The credentials look the same in configuration - the difference is in the permissions associated with them in Sophos Central.

