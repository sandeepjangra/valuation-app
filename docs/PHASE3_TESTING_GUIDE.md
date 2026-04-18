# Phase 3 Testing Guide: Manager vs Employee Permissions

## 🎯 Overview

This guide will help you test the new manager-only approve/reject/delete functionality for reports.

## 🚀 Prerequisites

✅ Backend running on `http://localhost:8000`  
✅ Frontend running on `http://localhost:4200`  
✅ MongoDB running with test data

## 👥 Test Users

You'll need at least **two users** in the same organization:

### User 1: Manager
- **Email**: `manager@example.com`
- **Role**: `manager`
- **Organization**: Any (e.g., `acme-corp`)

### User 2: Employee
- **Email**: `employee@example.com`
- **Role**: `employee`
- **Organization**: Same as manager (e.g., `acme-corp`)

### System Admin (Optional)
- **Email**: `admin@example.com`
- **Organization**: `system-administration`
- **Can**: Access any organization and perform any action

## 📝 Test Scenarios

### Test 1: Employee Creates and Submits Report ✅

**As Employee:**

1. Login as `employee@example.com`
2. Navigate to Reports page
3. Click "Create New Report"
4. Fill in report details:
   - Report Title: "Test Property Valuation"
   - Report Type: "Property Valuation"
   - Description: "Test report for approval workflow"
   - Property Address: "123 Main St"
5. Submit the report
6. **Expected**: Report status changes to "submitted"
7. **Expected**: Report appears in reports list with "Submitted" badge (purple)
8. **Expected**: NO approve/reject buttons visible (employee cannot approve)

---

### Test 2: Manager Approves Submitted Report ✅

**As Manager:**

1. Login as `manager@example.com`
2. Navigate to Reports page
3. Find the submitted report from Test 1
4. **Expected**: See "✅ Approve" (green) and "❌ Reject" (red) buttons
5. Click "✅ Approve" button
6. Confirm the approval in the dialog
7. **Expected**: Success message appears
8. **Expected**: Report status changes to "✅ Approved" (green badge)
9. **Expected**: Approve/Reject buttons disappear (already approved)
10. Refresh the page to verify persistence

---

### Test 3: Manager Rejects Submitted Report ❌

**As Manager:**

1. Create another report as employee (or ask employee to create one)
2. Submit the report (status: "submitted")
3. Login as `manager@example.com`
4. Navigate to Reports page
5. Find the submitted report
6. Click "❌ Reject" button
7. **Expected**: Modal opens with rejection reason textarea
8. Enter rejection reason: "Missing property valuation details"
9. Click "Reject Report" button
10. **Expected**: Success message appears
11. **Expected**: Report status changes to "❌ Rejected" (red badge)
12. **Expected**: Approve/Reject buttons disappear

**Backend Verification:**
```bash
# Check MongoDB to verify rejection reason was saved
mongo valuation_admin
db.acme-corp.reports.findOne({ status: "rejected" })
# Should show: workflow.RejectionReason: "Missing property valuation details"
```

---

### Test 4: Employee Cannot Approve Reports 🚫

**As Employee:**

1. Login as `employee@example.com`
2. Navigate to Reports page
3. Look at submitted reports
4. **Expected**: NO approve/reject buttons visible
5. **Expected**: Only "View" and "Edit" buttons visible

**Manual API Test (Optional):**
```bash
# Try to approve as employee (should fail with 403)
curl -X POST http://localhost:8000/api/org/acme-corp/reports/{REPORT_ID}/approve \
  -H "Authorization: Bearer {EMPLOYEE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"approvedBy": "employee@example.com"}'

# Expected Response:
{
  "success": false,
  "message": "Only managers can approve reports",
  "data": null
}
```

---

### Test 5: Employee Cannot Delete Reports 🚫

**As Employee:**

1. Login as `employee@example.com`
2. Navigate to Reports page
3. **Expected**: Delete button is commented out/disabled
4. **Expected**: Cannot delete any reports through UI

**Manual API Test (Optional):**
```bash
# Try to delete as employee (should fail with 403)
curl -X DELETE http://localhost:8000/api/org/acme-corp/reports/{REPORT_ID} \
  -H "Authorization: Bearer {EMPLOYEE_TOKEN}"

# Expected Response:
{
  "success": false,
  "message": "Only managers can delete reports",
  "data": null
}
```

---

### Test 6: System Admin Can Approve Any Report 🔓

**As System Admin:**

1. Login as system admin (`system-administration` org)
2. Navigate to any organization's reports (e.g., `/org/acme-corp/reports`)
3. Find a submitted report
4. **Expected**: See approve/reject buttons (system admin has full access)
5. Approve or reject a report
6. **Expected**: Operation succeeds
7. **Expected**: System admin can manage reports across all organizations

---

### Test 7: Cannot Approve Draft Reports ⚠️

**As Manager:**

1. Login as `manager@example.com`
2. Navigate to Reports page
3. Look at draft reports (status: "draft")
4. **Expected**: NO approve/reject buttons (only submitted reports can be approved)
5. Create a new draft report
6. **Expected**: Draft report shows "View" and "Edit" buttons only

**Manual API Test (Optional):**
```bash
# Try to approve a draft report (should fail with 400)
curl -X POST http://localhost:8000/api/org/acme-corp/reports/{DRAFT_REPORT_ID}/approve \
  -H "Authorization: Bearer {MANAGER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"approvedBy": "manager@example.com"}'

# Expected Response:
{
  "success": false,
  "message": "Report must be in 'submitted' status to be approved. Current status: draft",
  "data": null
}
```

---

### Test 8: Rejection Reason Validation ✍️

**As Manager:**

1. Login as `manager@example.com`
2. Find a submitted report
3. Click "❌ Reject" button
4. **Expected**: Modal opens
5. Try to click "Reject Report" without entering reason
6. **Expected**: Button is disabled (no rejection reason provided)
7. Enter a single character: "x"
8. **Expected**: Button becomes enabled
9. Clear the textarea
10. **Expected**: Button becomes disabled again
11. Enter proper reason: "Missing documents"
12. Click "Reject Report"
13. **Expected**: Report rejected successfully

---

### Test 9: Status Badge Display 🏷️

**Verify all status badges render correctly:**

1. **Draft** - Yellow badge (🟡)
2. **In Progress** - Blue badge (🔵)
3. **Submitted** - Purple badge (🟣)
4. **Approved** - Green badge (🟢) with checkmark "✅ Approved"
5. **Rejected** - Red badge (🔴) with X "❌ Rejected"
6. **Completed** - Green badge (🟢)

---

### Test 10: Button Visibility Matrix 📊

**Test button visibility based on role and status:**

| Report Status | Employee Actions | Manager Actions |
|--------------|------------------|-----------------|
| Draft | View, Edit | View, Edit |
| In Progress | View, Edit | View, Edit |
| Submitted | View | View, Approve, Reject |
| Approved | View | View |
| Rejected | View, Edit | View, Edit |
| Completed | View | View |

---

## 🐛 Common Issues & Solutions

### Issue 1: Buttons Not Showing for Manager

**Symptoms:** Manager logged in but approve/reject buttons don't appear

**Check:**
```typescript
// Verify JWT token includes correct role
localStorage.getItem('token')
// Decode JWT at jwt.io and verify:
// - role: "manager"
// - org_short_name matches current org
```

**Solution:** Re-login or check user role in database

---

### Issue 2: 403 Forbidden Error

**Symptoms:** Manager gets 403 when approving

**Check:**
- JWT token is valid and not expired
- User's role is "manager" in database
- Organization short name matches URL

**Solution:** Check backend logs for authorization failure reason

---

### Issue 3: Report Status Not Updating

**Symptoms:** Approve/reject succeeds but status doesn't change

**Check:**
- Browser console for errors
- Network tab for API response
- MongoDB to verify status changed

**Solution:** Refresh page or check database directly

---

### Issue 4: Modal Not Closing

**Symptoms:** Rejection modal stays open after submission

**Check:**
- Browser console for errors
- Check if `isProcessingAction` signal is stuck

**Solution:** Manually close with X button or refresh page

---

## 🔍 Backend Log Verification

Monitor backend logs during testing:

```bash
# Backend should log:
✅ Report approved successfully by manager@example.com
✅ Report rejected by manager@example.com. Reason: Missing property valuation details
⚠️ User employee@example.com with role employee attempted to approve report 12345
⚠️ User employee@example.com with role employee attempted to delete report 12345
```

---

## 📊 Database Verification

After each test, verify database changes:

```javascript
// MongoDB queries

// Check approved report
db['acme-corp'].reports.findOne({ status: "approved" })
// Should show:
// - status: "approved"
// - workflow.Status: "APPROVED"
// - workflow.ApprovedBy: "manager@example.com"
// - workflow.ApprovedAt: ISODate("...")

// Check rejected report
db['acme-corp'].reports.findOne({ status: "rejected" })
// Should show:
// - status: "rejected"
// - workflow.Status: "REJECTED"
// - workflow.ReviewedBy: "manager@example.com"
// - workflow.RejectionReason: "Missing property valuation details"
// - workflow.ReviewedAt: ISODate("...")
```

---

## ✅ Success Criteria

All tests pass if:

✅ Employees can create and submit reports  
✅ Employees CANNOT approve or reject reports  
✅ Employees CANNOT delete reports  
✅ Managers can approve submitted reports  
✅ Managers can reject submitted reports with reason  
✅ Managers can delete reports  
✅ System admins can perform all actions  
✅ Only submitted reports show approve/reject buttons  
✅ Status badges display correctly  
✅ Rejection reason is required and saved  
✅ All actions are logged in backend  
✅ Database reflects correct status changes  

---

## 🎥 Demo Script

**5-Minute Quick Demo:**

1. **Setup** (30 sec)
   - Show login page
   - Login as employee
   
2. **Employee Workflow** (1 min)
   - Create report
   - Submit report
   - Show no approve/reject buttons
   
3. **Manager Workflow** (2 min)
   - Logout and login as manager
   - Show approve/reject buttons on submitted report
   - Approve one report
   - Show success and status change
   
4. **Rejection Workflow** (1.5 min)
   - Find another submitted report
   - Click reject
   - Show modal with reason textarea
   - Enter rejection reason
   - Submit rejection
   - Show status change to rejected

---

## 📸 Expected UI Screenshots

### Employee View (Submitted Report)
```
┌─────────────────────────────────────────┐
│ Report: Test Property Valuation         │
│ Status: 🟣 Submitted                     │
│                                         │
│ [👁️ View]  [✏️ Edit]                    │
└─────────────────────────────────────────┘
```

### Manager View (Submitted Report)
```
┌─────────────────────────────────────────┐
│ Report: Test Property Valuation         │
│ Status: 🟣 Submitted                     │
│                                         │
│ [👁️ View]  [✏️ Edit]                    │
│ [✅ Approve]  [❌ Reject]                │
└─────────────────────────────────────────┘
```

### Manager View (Approved Report)
```
┌─────────────────────────────────────────┐
│ Report: Test Property Valuation         │
│ Status: 🟢 ✅ Approved                   │
│                                         │
│ [👁️ View]                               │
└─────────────────────────────────────────┘
```

### Rejection Modal
```
┌─────────────────────────────────────────┐
│ ❌ Reject Report                    [×] │
├─────────────────────────────────────────┤
│ ⚠️ Warning: This will reject report     │
│ Test Property Valuation                 │
│                                         │
│ Rejection Reason *                      │
│ ┌─────────────────────────────────────┐ │
│ │ Missing property valuation details  │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│ Provide clear feedback...               │
│                                         │
│ [Cancel]  [Reject Report]               │
└─────────────────────────────────────────┘
```

---

## 🔗 API Endpoints Reference

### Approve Report
```
POST /api/org/{orgShortName}/reports/{reportId}/approve
Authorization: Bearer {token}
Content-Type: application/json

{
  "approvedBy": "manager@example.com"
}
```

### Reject Report
```
POST /api/org/{orgShortName}/reports/{reportId}/reject
Authorization: Bearer {token}
Content-Type: application/json

{
  "rejectedBy": "manager@example.com",
  "rejectionReason": "Missing property valuation details"
}
```

### Delete Report (Manager Only)
```
DELETE /api/org/{orgShortName}/reports/{reportId}
Authorization: Bearer {token}
```

---

## 🎉 Conclusion

Once all tests pass, Phase 3 is complete! The system now properly enforces:
- ✅ Manager-only approve/reject/delete permissions
- ✅ Employee can create/submit but not approve
- ✅ Clear UI feedback with status badges
- ✅ Comprehensive rejection reason tracking
- ✅ System admin override capabilities

Happy Testing! 🚀
