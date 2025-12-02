# Save Template From Report - Testing Guide

## Overview
Complete end-to-end testing guide for the "Save as Template" feature that allows users to save filled reports as reusable custom templates.

## Feature Components

### Backend
- **Endpoint**: `POST /api/organizations/{orgShortName}/templates/from-report`
- **File**: `backend/main.py` (lines ~4165-4390)
- **Model**: `CreateTemplateFromReportRequest` (lines ~219-224)

### Frontend
- **Service**: `TemplateService.createTemplateFromReport()` 
  - File: `valuation-frontend/src/app/services/template.service.ts` (lines ~268-323)
  
- **Dialog Component**: `SaveTemplateDialogComponent`
  - File: `valuation-frontend/src/app/components/report-form/save-template-dialog.component.ts`
  - Standalone component with no dependencies (no Angular Material)
  
- **Report Form Integration**:
  - File: `valuation-frontend/src/app/components/report-form/report-form.ts`
  - Methods: `onSaveAsTemplate()`, `saveTemplate()`
  - Button: Added to header right-section

## Test Scenarios

### 1. UI/UX Testing

#### 1.1 Button Visibility
- [ ] **Test**: Navigate to New Report page (select bank, property type, template)
- [ ] **Expected**: "💾 Save as Template" button visible in header (green gradient)
- [ ] **Expected**: Button positioned before the red "Back" button
- [ ] **Expected**: Button disabled when form not ready
- [ ] **Expected**: Button enabled when form is filled

#### 1.2 Dialog Opening
- [ ] **Test**: Click "Save as Template" button
- [ ] **Expected**: Modal dialog opens with semi-transparent overlay
- [ ] **Expected**: Dialog shows:
  - Bank name and property type
  - Template name input (required, 3-100 chars)
  - Description textarea (optional, 0-500 chars)
  - Non-empty field count message
  - Save and Cancel buttons

#### 1.3 Form Validation
- [ ] **Test**: Try to save without template name
- [ ] **Expected**: Save button disabled, validation error shown
- [ ] **Test**: Enter 2 characters in template name
- [ ] **Expected**: Validation error: "Template name must be at least 3 characters"
- [ ] **Test**: Enter 101 characters in template name
- [ ] **Expected**: Validation error: "Template name cannot exceed 100 characters"
- [ ] **Test**: Enter 501 characters in description
- [ ] **Expected**: Validation error: "Description cannot exceed 500 characters"
- [ ] **Test**: Enter valid template name (3-100 chars)
- [ ] **Expected**: Save button enabled

#### 1.4 Dialog Interaction
- [ ] **Test**: Click Cancel button
- [ ] **Expected**: Dialog closes, no API call made
- [ ] **Test**: Click overlay (outside dialog)
- [ ] **Expected**: Dialog closes, no API call made
- [ ] **Test**: Press ESC key
- [ ] **Expected**: Dialog closes, no API call made

### 2. Functional Testing

#### 2.1 Successful Template Creation
- [ ] **Test**: Fill report form with some values, click "Save as Template"
- [ ] **Test**: Enter template name "Test Template 1" and description
- [ ] **Test**: Click Save
- [ ] **Expected**: Save button shows "Saving..." with spinner
- [ ] **Expected**: Success alert shown: "✅ Template 'Test Template 1' saved successfully!"
- [ ] **Expected**: Dialog closes automatically
- [ ] **Expected**: Template visible in Custom Templates Management page

#### 2.2 Field Filtering
- [ ] **Test**: Fill only common fields (valuationReport, bankBranch, etc.)
- [ ] **Test**: Save as template
- [ ] **Expected**: Success (common fields automatically excluded by backend)
- [ ] **Test**: Check saved template in database
- [ ] **Expected**: Template contains zero field_values (only metadata saved)

- [ ] **Test**: Fill bank-specific fields with values
- [ ] **Test**: Leave some fields empty
- [ ] **Test**: Save as template
- [ ] **Expected**: Success
- [ ] **Test**: Check saved template in database
- [ ] **Expected**: Only non-empty bank-specific fields saved in field_values

#### 2.3 Template Limit Enforcement
- [ ] **Test**: Create 3 templates for same bank + property type combination
- [ ] **Expected**: All 3 succeed
- [ ] **Test**: Try to create 4th template for same combination
- [ ] **Expected**: Error 409: "Template name already exists or template limit reached (max 3 per bank/property type)"
- [ ] **Test**: Create template for different bank or property type
- [ ] **Expected**: Success (limit is per bank+property type)

### 3. Permission Testing

#### 3.1 Manager Role
- [ ] **Test**: Login as Manager user
- [ ] **Test**: Navigate to New Report
- [ ] **Expected**: "Save as Template" button visible and enabled
- [ ] **Test**: Save template
- [ ] **Expected**: Success

#### 3.2 Admin Role
- [ ] **Test**: Login as Admin user
- [ ] **Test**: Navigate to New Report
- [ ] **Expected**: "Save as Template" button visible and enabled
- [ ] **Test**: Save template
- [ ] **Expected**: Success

#### 3.3 Employee Role
- [ ] **Test**: Login as Employee user
- [ ] **Test**: Navigate to New Report
- [ ] **Expected**: "Save as Template" button visible but disabled
- [ ] **Test**: Try to save template (via API directly)
- [ ] **Expected**: Error 403: "You do not have permission to create templates"

### 4. Error Handling

#### 4.1 Validation Errors
- [ ] **Test**: Send invalid template name (< 3 chars) via API
- [ ] **Expected**: Error 400 with validation details
- [ ] **Expected**: Dialog shows error message

#### 4.2 Duplicate Template Name
- [ ] **Test**: Create template named "My Template"
- [ ] **Test**: Try to create another template with same name for same org
- [ ] **Expected**: Error 409: "Template name already exists..."
- [ ] **Expected**: Dialog shows error message

#### 4.3 Bank/Template Not Found
- [ ] **Test**: Send request with invalid bank code
- [ ] **Expected**: Error 404: "Bank or template not found"
- [ ] **Expected**: Dialog shows error message

#### 4.4 Network Errors
- [ ] **Test**: Stop backend server
- [ ] **Test**: Try to save template
- [ ] **Expected**: Dialog shows error: "Failed to save template"
- [ ] **Expected**: Save button re-enabled for retry

### 5. Integration Testing

#### 5.1 Template Reuse
- [ ] **Test**: Create custom template from report with specific values
- [ ] **Test**: Navigate back to New Report
- [ ] **Test**: Select same bank + property type
- [ ] **Expected**: Template available in auto-fill modal
- [ ] **Test**: Apply template
- [ ] **Expected**: Form filled with saved values

#### 5.2 Activity Logging
- [ ] **Test**: Save a template
- [ ] **Test**: Check Activity Logs page
- [ ] **Expected**: Activity logged with:
  - Action: "created_custom_template"
  - Entity type: "custom_template"
  - Details: template name, bank, property type

#### 5.3 Database Verification
- [ ] **Test**: Save template and check MongoDB
- [ ] **Expected**: Document in `<org>_custom_templates` collection with:
  - `template_name`: as entered
  - `description`: as entered or null
  - `bank_code`: from selected bank
  - `template_code`: from selected template
  - `property_type`: from selected property type
  - `field_values`: only non-empty bank-specific fields
  - `is_active`: true
  - `created_at`: current timestamp
  - `created_by`: current user email

### 6. Browser Compatibility
- [ ] **Test**: Chrome/Edge (latest)
- [ ] **Test**: Firefox (latest)
- [ ] **Test**: Safari (latest)
- [ ] **Expected**: All features work consistently

### 7. Responsive Design
- [ ] **Test**: Desktop (1920x1080)
- [ ] **Test**: Laptop (1366x768)
- [ ] **Test**: Tablet (768x1024)
- [ ] **Expected**: Dialog properly centered and readable
- [ ] **Expected**: Button visible and accessible

## Manual Testing Steps

### Happy Path Test
1. **Login** as Manager/Admin
2. **Navigate** to New Report
3. **Select** Bank: SBI, Property Type: Land, Template: SBI Land Valuation
4. **Fill** some bank-specific fields with values
5. **Click** "💾 Save as Template" button
6. **Verify** dialog opens with correct bank/property info
7. **Enter** template name: "SBI Land Template Test"
8. **Enter** description: "Test template for SBI land valuations"
9. **Click** Save
10. **Verify** success alert shown
11. **Navigate** to Custom Templates Management
12. **Verify** new template listed

### Error Handling Test
1. **Follow** steps 1-8 from Happy Path
2. **Create** 2 more templates (total 3)
3. **Try** to create 4th template
4. **Verify** error shown: "template limit reached"
5. **Click** Cancel
6. **Try** with duplicate name
7. **Verify** error shown: "Template name already exists"

## Automated Testing Checklist

### Unit Tests Needed
- [ ] `onSaveAsTemplate()` - dialog opening logic
- [ ] `saveTemplate()` - API call with correct parameters
- [ ] `SaveTemplateDialogComponent` - form validation
- [ ] `SaveTemplateDialogComponent` - event emissions
- [ ] `TemplateService.createTemplateFromReport()` - HTTP request

### Integration Tests Needed
- [ ] Full flow from button click to API call
- [ ] Error handling flow
- [ ] Permission checking flow

## Known Issues/Limitations
- CSS budget warning (non-blocking, can be addressed later)
- No undo functionality (templates can be deleted from management page)
- Maximum 3 templates per bank+property type combination

## Success Criteria
✅ All test scenarios pass
✅ No console errors
✅ Backend validation works correctly
✅ Frontend validation matches backend rules
✅ Error messages are user-friendly
✅ Activity logging works
✅ Database records correct
✅ Build succeeds (warnings acceptable)

## Related Documentation
- API Documentation: `docs/api/CREATE_TEMPLATE_FROM_REPORT_ENDPOINT.md`
- Business Requirements: Original conversation about custom template feature
