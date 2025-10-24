import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonField, BankBranch } from '../../models';

@Component({
  selector: 'app-report-form',
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './report-form.html',
  styleUrl: './report-form.css',
})
export class ReportForm implements OnInit {
  
  // Query parameters from navigation
  selectedBankCode: string = '';
  selectedBankName: string = '';
  selectedTemplateId: string = '';
  selectedTemplateName: string = '';
  selectedPropertyType: string = '';
  
  // Form data
  reportForm: FormGroup;
  commonFields: CommonField[] = [];
  availableBranches: Array<{value: string, label: string}> = [];
  isLoading = false;
  
  // Current active tab
  activeTab = 'common';

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private http: HttpClient
  ) {
    this.reportForm = this.fb.group({});
  }

  ngOnInit() {
    this.loadQueryParams();
    this.loadCommonFields();
    this.loadBankBranches();
    
    // Log current timestamp for debugging - Updated to trigger hot reload
    console.log('🕒 ReportForm component initialized at:', new Date().toISOString());
  }

  // Method to manually refresh data (for debugging)
  refreshCommonFields() {
    console.log('🔄 Manual refresh triggered');
    this.loadCommonFields();
  }

  loadQueryParams() {
    this.route.queryParams.subscribe(params => {
      this.selectedBankCode = params['bankCode'] || '';
      this.selectedBankName = params['bankName'] || '';
      this.selectedTemplateId = params['templateId'] || '';
      this.selectedTemplateName = params['templateName'] || '';
      this.selectedPropertyType = params['propertyType'] || '';
      
      console.log('Report Form Params:', {
        bankCode: this.selectedBankCode,
        bankName: this.selectedBankName,
        templateId: this.selectedTemplateId,
        templateName: this.selectedTemplateName,
        propertyType: this.selectedPropertyType
      });
    });
  }

  loadCommonFields() {
    // Fetch common fields data dynamically from backend API
    this.isLoading = true;
    
    // Add cache-busting parameter to ensure fresh data
    const timestamp = new Date().getTime();
    const apiUrl = `http://localhost:8000/api/common-fields?t=${timestamp}`;
    
    console.log('🔄 Fetching common fields from API with cache-busting:', apiUrl);
    
    this.http.get<CommonField[]>(apiUrl)
      .subscribe({
        next: (fields) => {
          console.log('✅ Raw API Response:', fields);
          console.log('📊 GridSize values from API:');
          fields.forEach(field => {
            console.log(`  ${field.uiDisplayName}: gridSize=${field.gridSize} (CSS class: grid-${field.gridSize})`);
          });
          
          // Filter active fields and sort by sortOrder
          this.commonFields = fields
            .filter(field => field.isActive)
            .sort((a, b) => a.sortOrder - b.sortOrder);

          console.log('📋 Processed common fields:', this.commonFields);
          this.buildFormControls();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('❌ Error loading common fields:', error);
          console.log('🔄 Falling back to embedded data...');
          
          // Fallback to embedded data if API fails
          this.loadCommonFieldsFallback();
          this.isLoading = false;
        }
      });
  }

  loadCommonFieldsFallback() {
    // Fallback embedded data (in case API is not available)
    console.log('📦 Using fallback embedded common fields data');
    
    const fallbackFields: CommonField[] = [
      {
        "_id": "68fa41fa7cb7c7ce7f3f8bd1",
        "fieldId": "report_reference_number",
        "technicalName": "report_reference_number",
        "uiDisplayName": "Report Reference Number",
        "fieldType": "text" as const,
        "isRequired": true,
        "placeholder": "Enter report reference number",
        "helpText": "Unique reference number for this valuation report",
        "validation": {
          "pattern": "^[A-Z]{2,4}[0-9]{4,8}$",
          "maxLength": 20
        },
        "gridSize": 4,
        "sortOrder": 1,
        "isActive": true
      },
      {
        "_id": "68fa41fa7cb7c7ce7f3f8bd2",
        "fieldId": "valuation_date",
        "technicalName": "valuation_date",
        "uiDisplayName": "Valuation Date",
        "fieldType": "date" as const,
        "isRequired": true,
        "defaultValue": "today",
        "placeholder": "Select valuation date",
        "helpText": "Date when the property valuation was conducted",
        "validation": {
          "maxDate": "today",
          "minDate": "2020-01-01"
        },
        "gridSize": 4,
        "sortOrder": 2,
        "isActive": true
      },
      {
        "_id": "68fa41fa7cb7c7ce7f3f8bd3",
        "fieldId": "inspection_date",
        "technicalName": "inspection_date",
        "uiDisplayName": "Inspection Date",
        "fieldType": "date" as const,
        "isRequired": true,
        "placeholder": "Select inspection date",
        "helpText": "Date when the property was physically inspected",
        "validation": {
          "maxDate": "today",
          "minDate": "2020-01-01"
        },
        "gridSize": 4,
        "sortOrder": 3,
        "isActive": true
      },
      {
        "_id": "68fa41fa7cb7c7ce7f3f8bd4",
        "fieldId": "valuation_purpose",
        "technicalName": "valuation_purpose",
        "uiDisplayName": "Valuation Purpose",
        "fieldType": "select" as const,
        "isRequired": true,
        "options": [
          { "value": "home_loan", "label": "Home Loan" },
          { "value": "mortgage_loan", "label": "Mortgage Loan" },
          { "value": "insurance", "label": "Insurance Purpose" },
          { "value": "legal_settlement", "label": "Legal Settlement" },
          { "value": "sale_purchase", "label": "Sale/Purchase" },
          { "value": "stamp_duty", "label": "Stamp Duty Assessment" },
          { "value": "other", "label": "Other" }
        ],
        "placeholder": "Select valuation purpose",
        "helpText": "Reason for conducting this property valuation",
        "gridSize": 4,
        "sortOrder": 4,
        "isActive": true
      },
      {
        "_id": "68fa41fa7cb7c7ce7f3f8bd5",
        "fieldId": "applicant_name",
        "technicalName": "applicant_name",
        "uiDisplayName": "Applicant Name",
        "fieldType": "text" as const,
        "isRequired": true,
        "placeholder": "Enter applicant's full name",
        "helpText": "Full name of the loan applicant/property owner",
        "validation": {
          "minLength": 3,
          "maxLength": 100,
          "pattern": "^[a-zA-Z\\s\\.]+$"
        },
        "gridSize": 4,
        "sortOrder": 5,
        "isActive": true
      },
      {
        "_id": "68fa41fa7cb7c7ce7f3f8bd6",
        "fieldId": "bank_name",
        "technicalName": "bank_name",
        "uiDisplayName": "Bank Name",
        "fieldType": "text" as const,
        "isRequired": true,
        "isReadonly": true,
        "placeholder": "Bank name (selected from previous page)",
        "helpText": "Name of the lending bank/financial institution (auto-populated from selection)",
        "gridSize": 4,
        "sortOrder": 6,
        "isActive": true
      },
      {
        "_id": "68fa41fa7cb7c7ce7f3f8bd7",
        "fieldId": "bank_branch",
        "technicalName": "bank_branch",
        "uiDisplayName": "Bank Branch",
        "fieldType": "select" as const,
        "isRequired": true,
        "placeholder": "Select branch",
        "helpText": "Choose the specific bank branch for this application",
        "gridSize": 4,
        "sortOrder": 7,
        "isActive": true
      }
    ];

    // Filter active fields and sort by sortOrder
    this.commonFields = fallbackFields
      .filter(field => field.isActive)
      .sort((a, b) => a.sortOrder - b.sortOrder);

    this.buildFormControls();
  }

  buildFormControls() {
    const formControls: any = {};
    
    // Debug log the fields being used for form building
    console.log('🏗️ Building form with fields:', this.commonFields.map(f => ({
      name: f.uiDisplayName,
      gridSize: f.gridSize,
      cssClass: `grid-${f.gridSize}`
    })));
    
    this.commonFields.forEach(field => {
      const validators = [];
      
      // Required validation
      if (field.isRequired) {
        validators.push(Validators.required);
      }
      
      // Pattern validation
      if (field.validation?.pattern) {
        validators.push(Validators.pattern(field.validation.pattern));
      }
      
      // Length validations
      if (field.validation?.minLength) {
        validators.push(Validators.minLength(field.validation.minLength));
      }
      if (field.validation?.maxLength) {
        validators.push(Validators.maxLength(field.validation.maxLength));
      }
      
      // Set default value
      let defaultValue = '';
      if (field.fieldId === 'bank_name') {
        defaultValue = this.selectedBankName;
      } else if (field.fieldId === 'valuation_date' && field.defaultValue === 'today') {
        defaultValue = new Date().toISOString().split('T')[0];
      }
      
      formControls[field.fieldId] = [defaultValue, validators];
    });
    
    this.reportForm = this.fb.group(formControls);
    
    // Disable bank_name field
    const bankNameControl = this.reportForm.get('bank_name');
    if (bankNameControl) {
      bankNameControl.disable();
    }
  }

  loadBankBranches() {
    // Load bank branches from the same banks data used in New Report
    const banksData = {
      documents: [
        {
          bankCode: "SBI",
          bankName: "State Bank of India",
          branches: [
            { branchId: "SBI_DEL_CP_001", branchName: "Connaught Place", isActive: true },
            { branchId: "SBI_MUM_BKC_002", branchName: "Bandra Kurla Complex", isActive: true },
            { branchId: "SBI_BLR_MGB_003", branchName: "MG Road", isActive: true }
          ]
        },
        {
          bankCode: "HDFC",
          bankName: "HDFC Bank Limited",
          branches: [
            { branchId: "HDFC_MUM_BND_001", branchName: "Bandra West", isActive: true },
            { branchId: "HDFC_GUR_CYB_002", branchName: "Cyber City", isActive: true }
          ]
        },
        {
          bankCode: "PNB",
          bankName: "Punjab National Bank",
          branches: [
            { branchId: "PNB_DEL_KP_001", branchName: "Karol Bagh", isActive: true },
            { branchId: "PNB_CHD_SC_002", branchName: "Sector 17", isActive: true }
          ]
        },
        {
          bankCode: "UNION",
          bankName: "Union Bank of India",
          branches: [
            { branchId: "UNION_MUM_FC_001", branchName: "Fort Circle", isActive: true }
          ]
        },
        {
          bankCode: "BOB",
          bankName: "Bank of Baroda",
          branches: [
            { branchId: "BOB_MUM_OP_001", branchName: "Opera House", isActive: true }
          ]
        },
        {
          bankCode: "UCO",
          bankName: "UCO Bank",
          branches: [
            { branchId: "UCO_KOL_BBD_001", branchName: "BBD Bagh", isActive: true }
          ]
        },
        {
          bankCode: "CBI",
          bankName: "Central Bank of India",
          branches: [
            { branchId: "CBI_MUM_NC_001", branchName: "Nariman Point", isActive: true }
          ]
        }
      ]
    };

    // Find the selected bank and populate branches
    const selectedBank = banksData.documents.find(bank => bank.bankCode === this.selectedBankCode);
    if (selectedBank && selectedBank.branches) {
      this.availableBranches = selectedBank.branches
        .filter(branch => branch.isActive)
        .map(branch => ({
          value: branch.branchId,
          label: branch.branchName
        }));
    }
  }

  // Form validation helpers
  getFieldError(fieldId: string): string {
    const control = this.reportForm.get(fieldId);
    if (control && control.errors && control.touched) {
      if (control.errors['required']) return 'This field is required';
      if (control.errors['pattern']) return 'Invalid format';
      if (control.errors['minlength']) return `Minimum ${control.errors['minlength'].requiredLength} characters required`;
      if (control.errors['maxlength']) return `Maximum ${control.errors['maxlength'].requiredLength} characters allowed`;
    }
    return '';
  }

  isFieldInvalid(fieldId: string): boolean {
    const control = this.reportForm.get(fieldId);
    return !!(control && control.invalid && control.touched);
  }

  // Tab navigation
  switchTab(tab: string) {
    this.activeTab = tab;
  }

  // Actions
  onSaveDraft() {
    console.log('Save Draft - Form Values:', this.reportForm.value);
    console.log('Form Valid:', this.reportForm.valid);
    // TODO: Implement save draft functionality
  }

  onSubmit() {
    if (this.reportForm.valid) {
      console.log('Submit - Form Values:', this.reportForm.value);
      // TODO: Implement submit functionality
    } else {
      console.log('Form is invalid');
      // Mark all fields as touched to show validation errors
      Object.keys(this.reportForm.controls).forEach(key => {
        this.reportForm.get(key)?.markAsTouched();
      });
    }
  }

  onCancel() {
    this.router.navigate(['/dashboard']);
  }

  goBackToSelection() {
    this.router.navigate(['/new-report']);
  }
}
