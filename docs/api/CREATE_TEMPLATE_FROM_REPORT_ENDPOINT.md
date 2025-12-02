# Create Template From Report - API Endpoint Documentation

## Endpoint Information

**URL:** `POST /api/organizations/{org_short_name}/templates/from-report`

**Purpose:** Create a custom template from a filled report form, saving only bank-specific fields with non-empty values.

**Created:** November 30, 2025

---

## Authentication

- **Required:** Yes
- **Type:** Bearer Token (JWT)
- **Roles Allowed:** Manager, Admin only

---

## Request

### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_short_name` | string | Yes | Organization short name (must match authenticated user's org) |

### Request Body

```json
{
  "templateName": "string (required, max 100 chars)",
  "description": "string (optional, max 500 chars)",
  "bankCode": "string (required, e.g., 'SBI', 'HDFC')",
  "templateCode": "string (required, e.g., 'land-property', 'apartment-property')",
  "fieldValues": {
    "field_id_1": "value1",
    "field_id_2": 123,
    "field_id_3": true,
    ...
  }
}
```

### Request Model (Pydantic)

```python
class CreateTemplateFromReportRequest(BaseModel):
    templateName: str
    description: Optional[str] = None
    bankCode: str
    templateCode: str  # e.g., "land-property"
    fieldValues: Dict[str, Any]  # All field values from the report form
```

---

## Business Rules

### 1. **Template Limit**
- Maximum **3 custom templates** per organization + bank + property type combination
- Returns `400 Bad Request` if limit exceeded
- User must delete an existing template before creating a new one

### 2. **Field Filtering**
- **Only bank-specific fields** are saved (common fields are excluded)
- **Only non-empty values** are saved
  - Null values excluded
  - Empty strings excluded
  - Empty arrays excluded
  - Empty objects excluded
  - Whitespace-only strings excluded

### 3. **Template Name Uniqueness**
- Template name must be unique within organization + bank + property type
- Returns `400 Bad Request` if duplicate name exists

### 4. **Permissions**
- Only users with **Manager** or **Admin** roles can create templates
- Returns `403 Forbidden` for other roles

### 5. **Organization Context**
- `org_short_name` in URL must match authenticated user's organization
- Returns `403 Forbidden` on mismatch

---

## Response

### Success Response (201 Created)

```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "templateName": "My Custom Template",
    "bankCode": "SBI",
    "propertyType": "land",
    "fieldCount": 15
  },
  "message": "Custom template created successfully with 15 field values"
}
```

### Error Responses

#### 400 - Template Limit Exceeded
```json
{
  "success": false,
  "error": "Maximum 3 templates allowed for SBI - land. Please delete an existing template first."
}
```

#### 400 - Duplicate Template Name
```json
{
  "success": false,
  "error": "Template name 'My Template' already exists for SBI - land"
}
```

#### 400 - No Fields to Save
```json
{
  "success": false,
  "error": "No bank-specific field values to save. Please fill in at least one bank-specific field."
}
```

#### 403 - Insufficient Permissions
```json
{
  "success": false,
  "error": "Only Manager or Admin can create custom templates"
}
```

#### 403 - Organization Mismatch
```json
{
  "success": false,
  "error": "Organization mismatch"
}
```

#### 404 - Bank Not Found
```json
{
  "success": false,
  "error": "Bank SBI not found"
}
```

#### 404 - Template Not Found
```json
{
  "success": false,
  "error": "Template land-property not found for bank SBI"
}
```

---

## Processing Logic

### Step 1: Authentication & Authorization
1. Verify JWT token
2. Extract organization context
3. Verify `org_short_name` matches user's organization
4. Check user role (must be Manager or Admin)

### Step 2: Validation
1. Check template count limit (max 3 per org + bank + property type)
2. Check for duplicate template name
3. Validate bank exists in system
4. Validate template configuration exists for bank

### Step 3: Field Filtering
1. Get list of common field IDs from `common_form_fields` collection
2. Filter out common fields from `fieldValues`
3. Filter out empty values (null, "", [], {}, whitespace-only)
4. Count remaining bank-specific fields
5. Reject if no fields remain after filtering

### Step 4: Template Creation
1. Parse property type from `templateCode` (e.g., "land-property" → "land")
2. Get bank name from banks configuration
3. Build template document with metadata:
   - Template name, description
   - Bank code, bank name, property type
   - Filtered field values
   - Created by, modified by (current user)
   - Organization ID
   - Timestamps
   - Version (starts at 1)
   - `createdFrom: "report_form"` marker
4. Insert into `custom_templates` collection in organization database

### Step 5: Activity Logging
Log activity with:
- Action: `custom_template_created_from_report`
- Resource type: `custom_template`
- Resource ID: New template ID
- Details: Template name, bank, property type, field count
- User info, timestamp, IP address

---

## Database Schema

### Collection: `{org_database}.custom_templates`

```javascript
{
  "_id": ObjectId("..."),
  "templateName": "My Custom Template",
  "description": "Template for standard land valuations",
  "bankCode": "SBI",
  "bankName": "State Bank of India",
  "propertyType": "land",
  "templateCode": "land-property",
  "fieldValues": {
    "property_address": "123 Main St",
    "land_area_sqft": 5000,
    "valuation_amount": 2500000,
    ...
  },
  "createdBy": ObjectId("..."),
  "createdByName": "John Doe",
  "modifiedBy": ObjectId("..."),
  "modifiedByName": "John Doe",
  "organizationId": ObjectId("..."),
  "isActive": true,
  "version": 1,
  "createdFrom": "report_form",  // Indicates created from report vs. scratch
  "createdAt": ISODate("2025-11-30T10:30:00Z"),
  "modifiedAt": ISODate("2025-11-30T10:30:00Z")
}
```

### Indexes

```javascript
// Unique constraint on template name per org + bank + property type
{
  "organizationId": 1,
  "bankCode": 1,
  "propertyType": 1,
  "templateName": 1,
  "isActive": 1
}

// Query optimization for listing templates
{
  "organizationId": 1,
  "bankCode": 1,
  "propertyType": 1,
  "isActive": 1
}

// Query optimization for user's templates
{
  "organizationId": 1,
  "createdBy": 1,
  "isActive": 1
}
```

---

## Example Usage

### cURL Example

```bash
curl -X POST "https://api.example.com/api/organizations/acme-corp/templates/from-report" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "templateName": "Standard Land Valuation Template",
    "description": "Default template for land property valuations with typical values",
    "bankCode": "SBI",
    "templateCode": "land-property",
    "fieldValues": {
      "borrower_name": "",
      "valuation_date": "",
      "property_address": "Sector 5, HSR Layout",
      "land_area_sqft": 2400,
      "land_rate_per_sqft": 5000,
      "total_land_value": 12000000,
      "construction_type": "RCC",
      "age_of_construction": 5,
      "market_value": 15000000
    }
  }'
```

### TypeScript/Angular Example

```typescript
async createTemplateFromReport(
  orgShortName: string,
  templateName: string,
  description: string,
  bankCode: string,
  templateCode: string,
  formValues: Record<string, any>
): Promise<any> {
  const url = `/api/organizations/${orgShortName}/templates/from-report`;
  
  const payload = {
    templateName,
    description,
    bankCode,
    templateCode,
    fieldValues: formValues
  };
  
  return this.http.post(url, payload).toPromise();
}
```

---

## Activity Log Entry

```json
{
  "organizationId": ObjectId("..."),
  "userId": ObjectId("..."),
  "userEmail": "john.doe@acme.com",
  "action": "custom_template_created_from_report",
  "resourceType": "custom_template",
  "resourceId": "507f1f77bcf86cd799439011",
  "details": {
    "templateName": "Standard Land Valuation Template",
    "bankCode": "SBI",
    "propertyType": "land",
    "templateCode": "land-property",
    "fieldCount": 15
  },
  "ipAddress": "192.168.1.100",
  "timestamp": "2025-11-30T10:30:00.000Z"
}
```

---

## Related Endpoints

- `GET /api/custom-templates` - List all custom templates
- `GET /api/custom-templates/{template_id}` - Get template details
- `PUT /api/custom-templates/{template_id}` - Update template
- `DELETE /api/custom-templates/{template_id}` - Delete template
- `POST /api/custom-templates/{template_id}/clone` - Clone template
- `GET /api/templates/{bank_code}/{template_id}/aggregated-fields` - Get template structure

---

## Notes

1. **Field Filtering is Automatic**: Frontend doesn't need to filter fields - the backend automatically:
   - Excludes common fields (borrower name, date, etc.)
   - Excludes empty values
   - Only saves meaningful bank-specific data

2. **Property Type Parsing**: Property type is extracted from `templateCode`:
   - `"land-property"` → `propertyType: "land"`
   - `"apartment-property"` → `propertyType: "apartment"`

3. **Version Tracking**: Each template starts at version 1. Future updates will increment the version.

4. **Audit Trail**: The `createdFrom: "report_form"` field distinguishes templates created from reports vs. created from scratch.

5. **Soft Deletes**: Templates use `isActive: false` for soft deletion rather than hard deletes.

---

## Implementation Location

**File:** `/backend/main.py`
**Lines:** ~4165-4390
**Model Definition:** Lines ~219-224

---

## Testing Checklist

- [ ] Create template with valid data → 201 Created
- [ ] Create 4th template when limit is 3 → 400 Bad Request
- [ ] Create template with duplicate name → 400 Bad Request
- [ ] Create template with empty field values → 400 Bad Request (no fields to save)
- [ ] Create template as Viewer role → 403 Forbidden
- [ ] Create template with wrong org → 403 Forbidden
- [ ] Create template with invalid bank → 404 Not Found
- [ ] Verify common fields are filtered out
- [ ] Verify empty values are filtered out
- [ ] Verify activity log is created
- [ ] Verify template count is correct

---

**Last Updated:** November 30, 2025
**Endpoint Version:** 1.0
