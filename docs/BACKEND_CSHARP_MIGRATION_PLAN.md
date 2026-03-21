# Backend C# Migration Plan

**Date**: March 15, 2026  
**Status**: Planning Phase

---

## 📋 Current Backend Analysis

### Controllers & Endpoints

#### 1. **TemplatesController** (`/api/templates`)
**Current Endpoints:**
- `GET /{bankCode}/{templateCode}/aggregated-fields` - Get aggregated template (common fields + bank-specific)
- `GET /health` - Health check

**Status**: ⚠️ **NEEDS MAJOR UPDATE**
- Currently reads from: `common_form_fields`, `{bank}_{propertyType}_property_details` collections
- Needs to read from: `valuation_templates.templates` collection (new C# structure)

---

#### 2. **BanksController** (`/api/banks`)
**Current Endpoints:**
- `GET /` - Get all active banks
- `GET /{bankCode}` - Get bank by code
- `GET /all` - Get all banks (including inactive)
- `GET /{bankCode}/branches` - Get branches for a bank
- `GET /health` - Health check

**Status**: ⚠️ **NEEDS UPDATE**
- Currently reads from: `valuation_admin.banks` collection (multiple documents)
- Needs to read from: `valuation_templates.banks` collection (single document with Banks array)

---

#### 3. **OrganizationsController** (`/api/organizations`)
**Current Endpoints:**
- `GET /` - Get all active organizations
- `GET /{orgShortName}` - Get organization by short name
- `PATCH /{orgShortName}` - Update organization

**Status**: ⚠️ **NEEDS UPDATE**
- Currently reads from: `valuation_admin.organizations` collection (multiple documents)
- Needs to read from: `valuation_templates.organizations` collection (single document with Organizations array)

---

#### 4. **ReportsController** (Not reviewed yet)
**Status**: 🔍 Needs analysis

---

## 🎯 Migration Strategy

### Phase 1: Update Entity Models (Core Layer)
**Priority**: HIGH
**Estimated Time**: 2-3 hours

1. **Create New Template Entity** (`Template.cs`)
   - Map to new C# structure with PascalCase
   - Support Elements[] array with $type discriminator
   - Support CalculationRules[] array
   - Collection: `valuation_templates.templates`

2. **Update Bank Entity** (`Bank.cs`)
   - Update to read from single document with Banks[] array
   - Change BsonElement names to PascalCase
   - Collection: `valuation_templates.banks`

3. **Update Organization Entity** (`Organization.cs`)
   - Update to read from single document with Organizations[] array
   - Change BsonElement names to PascalCase
   - Collection: `valuation_templates.organizations`

---

### Phase 2: Update Repository Layer (Infrastructure)
**Priority**: HIGH
**Estimated Time**: 3-4 hours

1. **TemplateRepository**
   - Switch database from `valuation_admin` to `valuation_templates`
   - Update queries for new template structure
   - Implement template fetching by TemplateId
   - Implement bank/property type lookup

2. **BankRepository**
   - Switch to single document query
   - Implement Banks[] array filtering
   - Update branch queries

3. **OrganizationRepository**
   - Switch to single document query
   - Implement Organizations[] array filtering
   - Update reference number increment logic

---

### Phase 3: Update Service Layer (Core)
**Priority**: HIGH
**Estimated Time**: 2-3 hours

1. **TemplateService**
   - Remove aggregation logic (templates are now complete)
   - Update GetAggregatedTemplateAsync to fetch from new collection
   - Transform response to match frontend expectations

2. **BankService**
   - Update to work with Banks[] array
   - Maintain existing API contracts

3. **OrganizationService**
   - Update to work with Organizations[] array
   - Maintain reference number logic

---

### Phase 4: Update Controller Layer (API)
**Priority**: MEDIUM
**Estimated Time**: 1-2 hours

1. **TemplatesController**
   - Update response transformation
   - Ensure backward compatibility with frontend

2. **BanksController**
   - Update response format if needed
   - Maintain existing endpoints

3. **OrganizationsController**
   - Update response format if needed
   - Maintain existing endpoints

---

### Phase 5: Frontend Integration
**Priority**: MEDIUM
**Estimated Time**: 2-3 hours

1. **Update API Services** (Angular)
   - Verify existing endpoints still work
   - Update TypeScript models if needed
   - Test template loading
   - Test bank selection
   - Test organization switching

---

## 🔍 Key Questions to Address

### 1. Template Structure
**Q**: Should we maintain the old "aggregated" response format, or update frontend to handle new structure?
**Options**:
- A) Keep transformation in backend (backward compatible)
- B) Update frontend to use new structure directly (cleaner)
- **Recommendation**: Start with A, migrate to B later

### 2. Database Connection
**Q**: Should we keep both databases (old & new) for rollback capability?
**Options**:
- A) Switch completely to new database
- B) Keep both, with fallback logic
- **Recommendation**: B for first release, then remove old

### 3. Common Fields
**Q**: How to handle common fields in new structure?
**Current**: Separate `common_form_fields` collection
**New**: Templates have all fields included
**Recommendation**: Remove common fields fetch, use template directly

### 4. Document Types
**Q**: How to handle document types in new structure?
**Current**: Separate document_types collection with nested valuation tab
**New**: Part of template structure
**Recommendation**: Extract from template Elements[]

---

## 📝 Implementation Checklist

### Step 1: Create New Entity Models
- [ ] Create `Template.cs` with PascalCase properties
- [ ] Create `TemplateElement.cs` for Elements[] array
- [ ] Create `CalculationRule.cs` for formulas
- [ ] Update `Bank.cs` for new structure
- [ ] Update `BankBranch.cs` for PascalCase
- [ ] Update `Organization.cs` for new structure
- [ ] Create `BanksCollection.cs` wrapper
- [ ] Create `OrganizationsCollection.cs` wrapper

### Step 2: Update Repositories
- [ ] Update `ITemplateRepository` interface
- [ ] Implement `TemplateRepository` for new collection
- [ ] Update `IBankRepository` interface
- [ ] Implement `BankRepository` for new structure
- [ ] Update `IOrganizationRepository` interface
- [ ] Implement `OrganizationRepository` for new structure

### Step 3: Update Services
- [ ] Update `ITemplateService` interface
- [ ] Implement `TemplateService` with new logic
- [ ] Update `IBankService` interface
- [ ] Implement `BankService` with array filtering
- [ ] Update `IOrganizationService` interface
- [ ] Implement `OrganizationService` with array filtering

### Step 4: Update Controllers
- [ ] Test `TemplatesController` with new data
- [ ] Test `BanksController` with new data
- [ ] Test `OrganizationsController` with new data
- [ ] Update error handling
- [ ] Update logging

### Step 5: Frontend Integration
- [ ] Test template loading in UI
- [ ] Test bank selection in UI
- [ ] Test organization switching in UI
- [ ] Test report creation with new templates
- [ ] Test formula calculations

---

## 🚨 Critical Considerations

### 1. Backward Compatibility
- Ensure existing reports still load correctly
- Maintain API response format
- Don't break existing frontend code

### 2. Data Migration
- Verify all 12 templates are accessible
- Verify all 8 banks are accessible
- Verify organization is accessible
- Test edge cases (missing templates, inactive banks)

### 3. Performance
- New structure should be faster (less aggregation)
- Monitor query performance
- Check index usage

### 4. Testing
- Unit tests for repositories
- Integration tests for services
- End-to-end tests for controllers
- Frontend integration tests

---

## 📊 Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|---------------|-------------|
| Entity Models | 2-3 hours | None |
| Repositories | 3-4 hours | Entity Models |
| Services | 2-3 hours | Repositories |
| Controllers | 1-2 hours | Services |
| Frontend Testing | 2-3 hours | Controllers |
| **Total** | **10-15 hours** | Sequential |

---

## 🎯 Next Actions

1. **Review this plan** - Confirm approach
2. **Answer key questions** - Make architectural decisions
3. **Start Phase 1** - Create entity models
4. **Iterate** - Update and test incrementally

**Ready to proceed?** Let me know your decisions on the key questions and I'll start with Phase 1!
