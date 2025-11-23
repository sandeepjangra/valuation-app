# Database Restructure Plan

## Current Situation Analysis

### Current Database Names:
- `valuation_admin` - Stores old organization schema
- `valuation_001` - Currently stores NEW organization schema (confusing name!)
- `sk_tindwal_001` - Organization-specific database
- `shared_resources` - Shared templates, banks, etc.

### Problem:
1. **Confusing naming**: `valuation_001` sounds like an org database but actually holds the central organizations collection
2. **Two organization collections exist**:
   - `valuation_admin.organizations` (OLD schema with organization_id)
   - `valuation_001.organizations` (NEW schema with org_short_name)
3. **UI creates orgs differently**: Frontend sends to `/api/admin/organizations` which saves to `valuation_admin.organizations`

## Proposed Solution

### New Database Structure:

```
valuation_app_central     → Replaces valuation_001 (Central management database)
├── organizations         → Master organizations list (NEW schema)
├── users_settings       → User profiles and preferences
└── system_config        → Application-wide settings

valuation_admin          → Keep for backward compatibility
└── organizations        → OLD organizations (to be migrated/deprecated)

shared_resources         → Keep as-is
├── banks
├── common_fields
└── templates

{org_short_name}         → Organization-specific databases
├── reports
├── activity_logs
├── users (org-specific)
└── org_data
```

### Organization Schema Unification:

**Current UI sends (CreateOrganizationRequest)**:
```typescript
{
  name: string
  type: 'valuation_company' | 'enterprise'
  description?: string
  contact_email?: string
  phone_number?: string
  address?: {street, city, state, country, postal_code}
  subscription_plan?: 'basic' | 'premium' | 'enterprise'
  max_users?: number
  max_reports?: number
}
```

**Current backend creates in valuation_admin.organizations**:
```javascript
{
  organization_id: "company_name_001",  // Generated
  name: string,
  status: "active",
  contact_info: {email, phone, address},
  settings: {max_users, s3_prefix, features_enabled, timezone, date_format},
  subscription: {plan, max_reports_per_month, storage_limit_gb},
  created_by, created_at, updated_at,
  isActive: true
}
```

**NEW unified schema (valuation_app_central.organizations)**:
```javascript
{
  _id: ObjectId,
  
  // Core identity
  org_name: string,              // From UI: name
  org_short_name: string,        // Generated from name (URL-safe)
  org_display_name: string,      // From UI: name
  organization_type: string,     // From UI: type
  description: string,           // From UI: description
  
  // System flags
  is_system_org: boolean,        // false for normal orgs
  is_active: boolean,            // From UI: status = "active"
  
  // Contact information
  contact_info: {
    email: string,               // From UI: contact_email
    phone: string,               // From UI: phone_number
    address: {                   // From UI: address
      street, city, state, country, postal_code
    }
  },
  
  // Settings & Limits
  settings: {
    s3_prefix: string,           // org_short_name or organization_id
    subscription_plan: string,   // From UI: subscription_plan
    max_users: number,           // From UI: max_users
    max_reports_per_month: number, // From UI: max_reports
    max_storage_gb: number,      // Based on plan
    features_enabled: [],
    timezone: "UTC",
    date_format: "DD/MM/YYYY"
  },
  
  // Backward compatibility
  metadata: {
    original_organization_id: string,  // "company_name_001" for old orgs
    database_name: string,             // org_short_name
    migrated_from: string,
    migration_date: datetime
  },
  
  // Audit fields
  created_by: string,
  created_at: datetime,
  updated_at: datetime
}
```

## Implementation Steps

### Step 1: Rename valuation_001 → valuation_app_central
- MongoDB doesn't support direct rename
- Strategy: Create new database, copy data, update all references

### Step 2: Update Backend Organization Creation
- Modify `/api/admin/organizations` endpoint
- Save to `valuation_app_central.organizations` (NEW schema)
- Generate `org_short_name` from `name`
- Map UI fields to new schema
- Create org database using `org_short_name`

### Step 3: Update Backend Organization API
- Point to `valuation_app_central.organizations`
- Update all database references from `valuation_001` to `valuation_app_central`

### Step 4: Migrate Existing Organizations
- Run migration script
- Copy from `valuation_admin.organizations` to `valuation_app_central.organizations`
- Transform OLD schema → NEW schema
- Preserve all data in metadata for backward compatibility

### Step 5: Update Frontend
- Keep `CreateOrganizationRequest` interface (no changes needed)
- Backend will map these fields to new schema automatically

### Step 6: Deprecate valuation_admin.organizations
- Mark as read-only
- Keep for audit trail
- All new operations use valuation_app_central

## Questions for User:

1. **Database naming**: Do you approve `valuation_app_central` or prefer a different name?
   - Alternatives: `valuation_core`, `valuation_master`, `central_db`

2. **Organization type**: UI sends `type: 'valuation_company' | 'enterprise'`
   - Should we keep this field in new schema as `organization_type`?
   - Or merge it into something else?

3. **Migration timing**: Should we:
   - A. Do it now (rename valuation_001 → valuation_app_central)
   - B. Keep valuation_001 for now, just update references
   - C. Different approach?

4. **Backward compatibility**: Should we keep old organization_id generation logic?
   - Current: `company_name_001`, `company_name_002`
   - New: Use `org_short_name` as primary identifier

## Recommendation:

I recommend:
1. Rename `valuation_001` → `valuation_app_central`
2. Update `/api/admin/organizations` to save to new database with unified schema
3. Keep backward compatibility by storing `organization_id` in `metadata`
4. Update organization API to read from `valuation_app_central.organizations`
5. Keep `valuation_admin.organizations` as archived/legacy data

This gives us a clean, meaningful database structure while preserving all existing functionality.

**What would you like to do?**
