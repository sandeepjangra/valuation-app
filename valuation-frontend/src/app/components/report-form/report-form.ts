import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonField, BankBranch, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField, BankSpecificTab, BankSpecificSection } from '../../models';
import { TemplateService } from '../../services/template.service';

@Component({
  selector: 'app-report-form',
  imports: [CommonModule, ReactiveFormsModule],
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
  
  // Form data - Updated for new structure
  reportForm: FormGroup;
  templateData: ProcessedTemplateData | null = null;
  availableBranches: Array<{value: string, label: string}> = [];
  isLoading = false;
  
  // Current active tab
  activeTab = 'template';  // Default to template tab instead of common
  
  // Bank-specific dynamic tabs
  activeBankSpecificTab: string | null = null;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private http: HttpClient,
    private templateService: TemplateService,
    private cdr: ChangeDetectorRef
  ) {
    this.reportForm = this.fb.group({});
  }

  ngOnInit() {
    console.log('🔥 ReportForm ngOnInit called');
    this.loadQueryParams();
    this.loadBankBranches();
    
    // Load template data after query params are loaded
    if (this.selectedBankCode && this.selectedTemplateId) {
      console.log('🔥 Query params available, loading template data:', {
        bankCode: this.selectedBankCode,
        templateId: this.selectedTemplateId
      });
      this.loadTemplateData();
    } else {
      console.log('🔥 No query params yet, waiting...');
      // Retry after a short delay to ensure query params are loaded
      setTimeout(() => {
        if (this.selectedBankCode && this.selectedTemplateId) {
          console.log('🔥 Retrying template data load after delay');
          this.loadTemplateData();
        }
      }, 100);
    }
    
    // Log current timestamp for debugging - Updated to trigger hot reload
    console.log('🕒 ReportForm component initialized at:', new Date().toISOString());
  }

  // Method to manually refresh data (for debugging)
  refreshTemplateData() {
    console.log('🔄 Manual refresh triggered');
    this.loadTemplateData();
  }

  loadTemplateData() {
    if (!this.selectedBankCode || !this.selectedTemplateId) {
      console.warn('⚠️ Missing bank code or template ID for loading template data');
      return;
    }

    this.isLoading = true;
    
    // Convert templateId to templateCode (uppercase LAND -> lowercase land)
    const templateCode = this.selectedTemplateId.toLowerCase();
    console.log(`🔄 Loading template data for: ${this.selectedBankCode}/${templateCode} (converted from ${this.selectedTemplateId})`);
    
    this.templateService.getAggregatedTemplateFields(this.selectedBankCode, templateCode)
      .subscribe({
        next: (response) => {
          console.log('✅ Raw aggregated API Response:', response);
          console.log('✅ API Response type:', typeof response);
          console.log('✅ API Response keys:', Object.keys(response));
          
          // Process the response into organized field groups
          this.templateData = this.templateService.processTemplateData(response);
          
          console.log('🏗️ Processed template data:', {
            commonFieldGroups: this.templateData.commonFieldGroups.length,
            bankSpecificTabs: this.templateData.bankSpecificTabs.length,
            totalFields: this.templateData.totalFieldCount,
            templateData: this.templateData
          });
          
          this.buildFormControls();
          
          // Initialize first bank-specific tab if available
          this.initializeBankSpecificTabs();
          
          this.isLoading = false;
          
          // Force change detection to ensure template updates
          this.cdr.detectChanges();
          console.log('🔄 Change detection triggered after template data load');
        },
        error: (error) => {
          console.error('❌ Error loading template data:', error);
          console.log('🔄 Falling back to legacy common fields loading...');
          
          // Fallback to old method for common fields only
          this.loadCommonFieldsFallback();
          this.isLoading = false;
        }
      });
  }

  loadQueryParams() {
    console.log('🔥 Loading query params...');
    this.route.queryParams.subscribe(params => {
      console.log('🔥 Raw query params received:', params);
      this.selectedBankCode = params['bankCode'] || '';
      this.selectedBankName = params['bankName'] || '';
      this.selectedTemplateId = params['templateId'] || '';
      this.selectedTemplateName = params['templateName'] || '';
      this.selectedPropertyType = params['propertyType'] || '';
      
      console.log('🔥 Processed Report Form Params:', {
        bankCode: this.selectedBankCode,
        bankName: this.selectedBankName,
        templateId: this.selectedTemplateId,
        templateName: this.selectedTemplateName,
        propertyType: this.selectedPropertyType
      });

      // Load template data when query params are available
      if (this.selectedBankCode && this.selectedTemplateId) {
        console.log('🔥 Query params loaded, triggering template data load');
        this.loadTemplateData();
      }
    });
  }

  buildFormControls() {
    if (!this.templateData) {
      console.warn('⚠️ No template data available for form building');
      return;
    }

    const formControls: any = {};
    
    // Debug log the fields being used for form building
    console.log('🏗️ Building form with template data:', {
      commonFields: this.templateData.commonFieldGroups.length,
      bankSpecificTabs: this.templateData.bankSpecificTabs.length,
      totalFields: this.templateData.totalFieldCount
    });
    
    // Process all fields from template data
    this.templateData.allFields.forEach(field => {
      const validators = this.buildFieldValidators(field);
      
      // Set default value with context
      const contextData = {
        bankName: this.selectedBankName,
        bankCode: this.selectedBankCode,
        templateName: this.selectedTemplateName
      };
      
      const defaultValue = this.templateService.getFieldDefaultValue(field, contextData);
      
      formControls[field.fieldId] = [defaultValue, validators];
      
      // Add sub-field controls for group fields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          const subValidators = this.buildFieldValidators(subField);
          const subDefaultValue = this.templateService.getFieldDefaultValue(subField, contextData);
          formControls[subField.fieldId] = [subDefaultValue, subValidators];
        });
      }
    });
    
    this.reportForm = this.fb.group(formControls);
    
    // Disable readonly fields
    this.templateData.allFields.forEach(field => {
      if (field.isReadonly) {
        const control = this.reportForm.get(field.fieldId);
        if (control) {
          control.disable();
        }
      }
      
      // Handle readonly sub-fields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          if (subField.isReadonly) {
            const subControl = this.reportForm.get(subField.fieldId);
            if (subControl) {
              subControl.disable();
            }
          }
        });
      }
    });

    console.log('✅ Form built with controls:', Object.keys(formControls));
  }

  /**
   * Initialize bank-specific tabs - set first tab as active
   */
  initializeBankSpecificTabs() {
    const bankSpecificTabs = this.getBankSpecificTabs();
    if (bankSpecificTabs.length > 0) {
      this.activeBankSpecificTab = bankSpecificTabs[0].tabId;
      console.log('🔧 Initialized bank-specific tab:', this.activeBankSpecificTab);
    }
  }

  buildFieldValidators(field: TemplateField | BankSpecificField): any[] {
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
    
    // Numeric validations
    if (field.validation?.min !== undefined) {
      validators.push(Validators.min(field.validation.min));
    }
    if (field.validation?.max !== undefined) {
      validators.push(Validators.max(field.validation.max));
    }
    
    return validators;
  }

  // Legacy fallback method (simplified)
  loadCommonFieldsFallback() {
    console.log('📦 Using fallback method - loading basic common fields only');
    
    // Fetch common fields data dynamically from backend API as fallback
    const timestamp = new Date().getTime();
    const apiUrl = `http://localhost:8000/api/common-fields?t=${timestamp}`;
    
    this.http.get<CommonField[]>(apiUrl)
      .subscribe({
        next: (fields) => {
          console.log('✅ Fallback - Raw API Response:', fields);
          
          // Create a basic template data structure for compatibility
          this.templateData = {
            templateInfo: {
              templateId: this.selectedTemplateId,
              templateName: this.selectedTemplateName,
              propertyType: this.selectedPropertyType,
              bankCode: this.selectedBankCode,
              bankName: this.selectedBankName,
              version: '1.0'
            },
            commonFieldGroups: [{
              groupName: 'default',
              displayName: 'Common Fields',
              fields: fields.filter(field => field.isActive).sort((a, b) => a.sortOrder - b.sortOrder)
            }],
            bankSpecificTabs: [],
            allFields: fields.filter(field => field.isActive).sort((a, b) => a.sortOrder - b.sortOrder),
            totalFieldCount: fields.filter(field => field.isActive).length
          };

          console.log('📋 Fallback template data created:', this.templateData);
          this.buildFormControls();
        },
        error: (error) => {
          console.error('❌ Fallback also failed:', error);
          // Create minimal empty structure
          this.templateData = {
            templateInfo: {
              templateId: this.selectedTemplateId,
              templateName: this.selectedTemplateName,
              propertyType: this.selectedPropertyType,
              bankCode: this.selectedBankCode,
              bankName: this.selectedBankName,
              version: '1.0'
            },
            commonFieldGroups: [],
            bankSpecificTabs: [],
            allFields: [],
            totalFieldCount: 0
          };
        }
      });
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

  // Helper methods for template access
  getCommonFieldGroups(): FieldGroup[] {
    return this.templateData?.commonFieldGroups || [];
  }

  getBankSpecificTabs(): BankSpecificTab[] {
    const tabs = this.templateData?.bankSpecificTabs || [];
    console.log('🔍 getBankSpecificTabs() called:', {
      tabsCount: tabs.length,
      tabs: tabs.map(t => ({ 
        id: t.tabId, 
        name: t.tabName, 
        fieldsCount: t.fields.length,
        hasSections: t.hasSections,
        sectionsCount: t.sections?.length || 0 
      }))
    });
    return tabs;
  }

  hasCommonFields(): boolean {
    if (!this.templateData) {
      console.log('🔍 hasCommonFields(): No template data yet');
      return false;
    }
    const hasFields = this.getCommonFieldGroups().length > 0;
    console.log('🔍 hasCommonFields():', {
      hasFields,
      commonFieldGroups: this.getCommonFieldGroups().length,
      templateData: !!this.templateData
    });
    return hasFields;
  }

  hasBankSpecificFields(): boolean {
    if (!this.templateData) {
      console.log('🔍 hasBankSpecificFields(): No template data yet');
      return false;
    }
    const hasFields = this.getBankSpecificTabs().length > 0;
    console.log('🔍 hasBankSpecificFields():', {
      hasFields,
      bankSpecificTabs: this.getBankSpecificTabs().length,
      templateData: !!this.templateData
    });
    return hasFields;
  }

  getTotalFieldCount(): number {
    return this.templateData?.totalFieldCount || 0;
  }

  // Check if form is ready with controls
  isFormReady(): boolean {
    const hasControls = this.reportForm && Object.keys(this.reportForm.controls).length > 0;
    console.log('🔍 isFormReady():', {
      hasControls,
      controlsCount: Object.keys(this.reportForm?.controls || {}).length,
      templateData: !!this.templateData
    });
    return hasControls;
  }

  // Tab navigation
  switchTab(tab: string) {
    this.activeTab = tab;
  }

  // Bank-specific tab navigation
  switchBankSpecificTab(tabId: string) {
    this.activeBankSpecificTab = tabId;
    console.log('🔄 Switched to bank-specific tab:', tabId);
  }

  // Get active bank-specific tab data
  getActiveBankSpecificTab(): BankSpecificTab | null {
    if (!this.activeBankSpecificTab) return null;
    const activeTab = this.getBankSpecificTabs().find(tab => tab.tabId === this.activeBankSpecificTab) || null;
    
    // Debug logging
    if (activeTab) {
      console.log('🔍 Active tab details:', {
        tabId: activeTab.tabId,
        tabName: activeTab.tabName,
        fieldsCount: activeTab.fields.length,
        hasSections: activeTab.hasSections,
        sectionsCount: activeTab.sections?.length || 0,
        fields: activeTab.fields.map(f => ({ id: f.fieldId, name: f.uiDisplayName, type: f.fieldType }))
      });
    }
    
    return activeTab;
  }

  // Check if a tab has sections
  tabHasSections(tab: BankSpecificTab): boolean {
    return tab.hasSections && (tab.sections?.length || 0) > 0;
  }

  // Get sections for a tab
  getTabSections(tab: BankSpecificTab): BankSpecificSection[] {
    return tab.sections || [];
  }

  // Get fields for a specific section within a tab
  getSectionFields(tab: BankSpecificTab, sectionId: string): BankSpecificField[] {
    const section = tab.sections?.find(s => s.sectionId === sectionId);
    return section?.fields || [];
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
