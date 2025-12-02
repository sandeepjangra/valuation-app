import { Component, OnInit, ChangeDetectorRef, inject, computed, ViewChild } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonField, BankBranch, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField, BankSpecificTab, BankSpecificSection, CalculatedFieldConfig } from '../../models';
import { TemplateService } from '../../services/template.service';
import { CustomTemplateService } from '../../services/custom-template.service';
import { CalculationService } from '../../services/calculation.service';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { TemplateAutofillModalComponent, AutoFillChoice } from '../custom-templates/template-autofill-modal.component';
import { SaveTemplateDialogComponent } from './save-template-dialog.component';
import { DynamicTableComponent } from '../dynamic-table/dynamic-table.component';

@Component({
  selector: 'app-report-form',
  imports: [CommonModule, ReactiveFormsModule, DynamicTableComponent, TemplateAutofillModalComponent, SaveTemplateDialogComponent],
  templateUrl: './report-form.html',
  styleUrl: './report-form.css',
})
export class ReportForm implements OnInit {
  
  // Dependency Injection
  private readonly authService = inject(AuthService);
  
  // ViewChild references
  @ViewChild('saveTemplateDialog') saveTemplateDialog!: SaveTemplateDialogComponent;
  
  // Query parameters from navigation
  selectedBankCode: string = '';
  selectedBankName: string = '';
  selectedTemplateId: string = '';
  selectedTemplateName: string = '';
  selectedPropertyType: string = '';
  customTemplateId: string = '';
  customTemplateName: string = '';
  
  // Form data - Updated for new structure
  reportForm: FormGroup;
  templateData: ProcessedTemplateData | null = null;
  availableBranches: Array<{value: string, label: string}> = [];
  isLoading = false;
  
  // Report reference number
  reportReferenceNumber: string | null = null;
  referenceNumberLoading = false;
  referenceNumberError: string | null = null;
  
  // Custom template auto-fill
  showAutoFillModal = false;
  customTemplateValues: Record<string, any> | null = null;
  
  // Current active tab
  activeTab = 'template';  // Always default to first tab (Bank-Specific Fields)
  
  // Bank-specific dynamic tabs
  activeBankSpecificTab: string | null = null;

  // Dynamic tables data storage
  dynamicTablesData: { [fieldId: string]: any } = {};

  // Calculated fields tracking
  calculatedFieldsMap: Map<string, CalculatedFieldConfig> = new Map();
  
  // Role-based permissions (NEW!)
  protected readonly canSubmitReports = computed(() => this.authService.canSubmitReports());
  protected readonly canDeleteReports = computed(() => this.authService.hasPermission('reports', 'delete'));
  protected readonly isManager = computed(() => this.authService.isManager());
  protected readonly isEmployee = computed(() => this.authService.isEmployee() && !this.authService.isManager());
  protected readonly currentUserRole = computed(() => this.authService.getCurrentRole());

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private http: HttpClient,
    private templateService: TemplateService,
    private customTemplateService: CustomTemplateService,
    private calculationService: CalculationService,
    private organizationService: OrganizationService,
    private cdr: ChangeDetectorRef
  ) {
    this.reportForm = this.fb.group({});
  }

  ngOnInit() {
    console.log('🔥 ReportForm ngOnInit called');
    
    // Always reset to first tab on init/reload
    this.activeTab = 'template';
    this.activeBankSpecificTab = null;
    console.log('🔄 Reset to first tab (template) on page load');
    
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
          
          // Load custom template values if specified
          if (this.customTemplateId) {
            this.loadCustomTemplate();
          }
          
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
      this.customTemplateId = params['customTemplateId'] || '';
      this.customTemplateName = params['customTemplateName'] || '';
      
      console.log('🔥 Processed Report Form Params:', {
        bankCode: this.selectedBankCode,
        bankName: this.selectedBankName,
        templateId: this.selectedTemplateId,
        templateName: this.selectedTemplateName,
        propertyType: this.selectedPropertyType,
        customTemplateId: this.customTemplateId,
        customTemplateName: this.customTemplateName
      });

      // Load template data when query params are available
      if (this.selectedBankCode && this.selectedTemplateId) {
        console.log('🔥 Query params loaded, triggering template data load');
        this.loadTemplateData();
        this.loadReferenceNumber();  // NEW: Load reference number
        
        // Load custom template if specified
        if (this.customTemplateId) {
          console.log('📝 Custom template specified, will load after form build');
        }
      }
    });
  }

  /**
   * Load the next report reference number for this organization
   * Blocks form loading if organization doesn't have reference initials configured
   */
  loadReferenceNumber() {
    // Get organization short name from route params
    this.route.params.subscribe(params => {
      const orgShortName = params['orgShortName'];
      if (!orgShortName) {
        console.warn('⚠️ No organization context found in route');
        alert('Error: No organization context found. Please select an organization first.');
        this.router.navigate(['/new-report']);
        return;
      }

      this.referenceNumberLoading = true;
      this.referenceNumberError = null;

      this.organizationService.getNextReferenceNumber(orgShortName).subscribe({
        next: (data) => {
          this.reportReferenceNumber = data.reference_number;
          console.log('📋 Report reference number loaded:', this.reportReferenceNumber);
          this.referenceNumberLoading = false;
          
          // Set the reference number in form (if form is already built)
          this.setReferenceNumberInForm();
        },
        error: (error) => {
          console.error('❌ Failed to load reference number:', error);
          this.referenceNumberError = 'Organization reference number not configured';
          this.referenceNumberLoading = false;
          
          // Block the form - show error and redirect
          alert(
            '⚠️ Configuration Required\n\n' +
            'This organization does not have Report Reference Initials configured.\n\n' +
            'Please contact your administrator to:\n' +
            '1. Go to Admin → Organizations\n' +
            '2. Edit this organization\n' +
            '3. Set the "Report Reference Initials" field (e.g., CEV/RVO)\n\n' +
            'You will be redirected to the report selection page.'
          );
          this.router.navigate(['/new-report']);
        }
      });
    }).unsubscribe();
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
    console.log('🏗️ Creating form controls for fields:');
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
      console.log(`  ✅ ${field.fieldId} (${field.fieldType}): ${field.uiDisplayName}`);
      
      // Add sub-field controls for group fields
      if (field.fieldType === 'group' && field.subFields) {
        console.log(`    🔸 Group has ${field.subFields.length} sub-fields:`);
        field.subFields.forEach(subField => {
          const subValidators = this.buildFieldValidators(subField);
          const subDefaultValue = this.templateService.getFieldDefaultValue(subField, contextData);
          formControls[subField.fieldId] = [subDefaultValue, subValidators];
          console.log(`      ✅ ${subField.fieldId} (${subField.fieldType}): ${subField.uiDisplayName}`);
        });
      }
    });
    
    this.reportForm = this.fb.group(formControls);
    
    // Initialize calculated fields tracking
    this.initializeCalculatedFields();
    
    // Log summary of form controls created
    const controlCount = Object.keys(formControls).length;
    const textareaControls = Object.keys(formControls).filter(key => {
      if (!this.templateData) return false;
      const field = this.templateData.allFields.find(f => f.fieldId === key || (f.fieldType === 'group' && f.subFields?.some(sf => sf.fieldId === key)));
      if (field && field.fieldType === 'group' && field.subFields) {
        const subField = field.subFields.find(sf => sf.fieldId === key);
        return subField?.fieldType === 'textarea';
      }
      return field?.fieldType === 'textarea';
    });
    
    console.log(`🎯 Form building complete:`, {
      totalControls: controlCount,
      textareaControls: textareaControls.length,
      textareaFieldIds: textareaControls
    });
    
    // Force change detection after form is built
    setTimeout(() => {
      this.cdr.detectChanges();
    }, 0);
    
    // Subscribe to form value changes for conditional logic
    this.reportForm.valueChanges.subscribe(values => {
      this.handleFormValueChanges(values);
    });
    
    // Disable readonly fields
    this.templateData.allFields.forEach(field => {
      if (field.isReadonly) {
        const control = this.reportForm.get(field.fieldId);
        if (control) {
          control.disable();
          console.log(`🔒 Disabled readonly field: ${field.fieldId} (${field.uiDisplayName})`);
        }
      }
      
      // Handle readonly sub-fields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          if (subField.isReadonly) {
            const subControl = this.reportForm.get(subField.fieldId);
            if (subControl) {
              subControl.disable();
              console.log(`🔒 Disabled readonly sub-field: ${subField.fieldId}`);
            }
          }
        });
      }
    });

    console.log('✅ Form built with controls:', Object.keys(formControls));
    
    // Set reference number if it was already loaded
    this.setReferenceNumberInForm();
  }

  /**
   * Set the reference number in the form field (called after form is built)
   */
  setReferenceNumberInForm() {
    if (this.reportReferenceNumber && this.reportForm) {
      const refControl = this.reportForm.get('report_reference_number');
      if (refControl) {
        refControl.setValue(this.reportReferenceNumber);
        refControl.disable();
        console.log('📋 Reference number set in form and DISABLED:', {
          value: this.reportReferenceNumber,
          disabled: refControl.disabled,
          status: refControl.status
        });
      } else {
        console.log('⚠️ Reference number field not found in form yet');
      }
    } else {
      console.log('⚠️ Cannot set reference number:', {
        hasReferenceNumber: !!this.reportReferenceNumber,
        hasForm: !!this.reportForm
      });
    }
  }

  /**
   * Initialize bank-specific tabs - set first tab as active
   */
  initializeBankSpecificTabs() {
    const bankSpecificTabs = this.getBankSpecificTabs();
    if (bankSpecificTabs.length > 0) {
      // Always start with the first bank-specific tab on page load
      this.activeBankSpecificTab = bankSpecificTabs[0].tabId;
      console.log('🔧 Initialized first bank-specific tab:', this.activeBankSpecificTab);
    }
  }

  buildFieldValidators(field: TemplateField | BankSpecificField): any[] {
    const validators: any[] = [];
    
    // Skip validation for readonly/auto-generated fields (they're disabled anyway)
    if (field.isReadonly || (field as any).isAutoGenerated) {
      return validators;
    }
    
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
    // Load bank branches dynamically from API instead of hardcoded data
    this.http.get<any[]>('http://localhost:8000/api/banks')
      .subscribe({
        next: (banks) => {
          console.log('🏦 Loaded banks data:', banks);
          
          // Find the selected bank and populate branches
          const selectedBank = banks.find((bank: any) => bank.bankCode === this.selectedBankCode);
          if (selectedBank && selectedBank.branches) {
            this.availableBranches = selectedBank.branches
              .filter((branch: any) => branch.isActive)
              .map((branch: any) => ({
                value: branch.branchId,
                label: branch.branchName
              }));
            
            console.log(`🔧 Loaded ${this.availableBranches.length} branches for ${this.selectedBankCode}:`, 
              this.availableBranches.map((b: any) => b.label));
          } else {
            console.warn(`⚠️ No branches found for bank: ${this.selectedBankCode}`);
            this.availableBranches = [];
          }
        },
        error: (error) => {
          console.error('❌ Error loading bank branches:', error);
          
          // Fallback to hardcoded data if API fails
          this.loadBankBranchesFallback();
        }
      });
  }

  private loadBankBranchesFallback() {
    console.log('🔄 Using fallback hardcoded branch data');
    
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
    const selectedBank = banksData.documents.find((bank: any) => bank.bankCode === this.selectedBankCode);
    if (selectedBank && selectedBank.branches) {
      this.availableBranches = selectedBank.branches
        .filter((branch: any) => branch.isActive)
        .map((branch: any) => ({
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

  isFieldEmpty(fieldId: string): boolean {
    const control = this.reportForm.get(fieldId);
    return !control || !control.value || control.value === '';
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
    
    // Trigger recalculation when switching tabs
    this.recalculateAllFields();
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

  /**
   * Evaluates conditional logic for a field or field group
   */
  evaluateConditionalLogic(conditionalLogic: any): boolean {
    if (!conditionalLogic || !conditionalLogic.field) {
      return true; // Show field if no conditional logic
    }

    const fieldValue = this.reportForm.get(conditionalLogic.field)?.value;
    const targetValue = conditionalLogic.value;
    const operator = conditionalLogic.operator || '==';

    switch (operator) {
      case '==':
      case 'equals':
        return fieldValue === targetValue;
      case '!=':
      case 'not_equals':
        return fieldValue !== targetValue;
      case 'in':
        return Array.isArray(targetValue) && targetValue.includes(fieldValue);
      case 'not_in':
        return Array.isArray(targetValue) && !targetValue.includes(fieldValue);
      case 'empty':
        return !fieldValue || fieldValue === '';
      case 'not_empty':
        return fieldValue && fieldValue !== '';
      default:
        console.warn(`Unknown conditional operator: ${operator}`);
        return true;
    }
  }

  /**
   * Checks if a field should be visible based on conditional logic
   */
  shouldShowField(field: any): boolean {
    if (!field.conditionalLogic) {
      return true;
    }
    return this.evaluateConditionalLogic(field.conditionalLogic);
  }

  /**
   * Checks if a field group should be visible based on conditional logic
   */
  shouldShowFieldGroup(fieldGroup: any): boolean {
    if (!fieldGroup.conditionalLogic) {
      return true;
    }
    return this.evaluateConditionalLogic(fieldGroup.conditionalLogic);
  }

  /**
   * Checks if a section should be visible based on conditional logic
   */
  shouldShowSection(section: any): boolean {
    if (!section.conditionalLogic) {
      return true;
    }
    return this.evaluateConditionalLogic(section.conditionalLogic);
  }

  /**
   * Handles form value changes to apply conditional logic
   */
  handleFormValueChanges(formValues: any): void {
    if (!this.templateData || !this.reportForm) {
      return;
    }

    // Update field visibility and disabled states based on conditional logic
    this.templateData.allFields.forEach(field => {
      this.updateFieldConditionalState(field, formValues);
      
      // Handle sub-fields for group fields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          this.updateFieldConditionalState(subField, formValues);
        });
      }
    });
  }

  /**
   * Updates a field's conditional state (visibility and disabled status)
   */
  private updateFieldConditionalState(field: any, formValues: any): void {
    const control = this.reportForm?.get(field.fieldId);
    if (!control) {
      return;
    }

    // Check if field should be disabled based on conditional logic
    const shouldDisable = this.isFieldDisabled(field);
    
    if (shouldDisable && !control.disabled) {
      control.disable({ emitEvent: false });
    } else if (!shouldDisable && control.disabled && !field.isReadonly) {
      control.enable({ emitEvent: false });
    }
  }

  /**
   * Gets the disabled state of a field based on conditional logic
   */
  isFieldDisabled(field: any): boolean {
    if (!field.conditionalLogic) {
      return false;
    }
    
    // If conditional logic evaluates to false, disable the field
    return !this.evaluateConditionalLogic(field.conditionalLogic);
  }

  /**
   * Get calculated value for calculated fields
   */
  getCalculatedValue(field: any): string {
    if (!field.formula) return '';
    
    try {
      // Simple formula evaluation - can be enhanced with a proper expression parser
      let formula = field.formula;
      const formControls = this.reportForm.controls;
      
      // Replace field references with actual values
      Object.keys(formControls).forEach(fieldId => {
        const value = formControls[fieldId].value || 0;
        formula = formula.replace(new RegExp(fieldId, 'g'), value.toString());
      });
      
      // Evaluate simple mathematical expressions
      // Note: In production, use a proper expression parser for security
      const result = Function('"use strict"; return (' + formula + ')')();
      return isNaN(result) ? '' : result.toString();
    } catch (error) {
      console.warn('Error calculating formula:', field.formula, error);
      return '';
    }
  }

  /**
   * Get input type for table cells
   */
  getTableCellInputType(fieldType: string): string {
    switch (fieldType) {
      case 'number':
      case 'currency':
      case 'decimal':
        return 'number';
      case 'date':
        return 'date';
      case 'email':
        return 'email';
      default:
        return 'text';
    }
  }

  /**
   * Update table cell value
   */
  updateTableCell(tableFieldId: string, rowIndex: number, columnId: string, event: any): void {
    const value = event.target.value;
    
    // Find the table field in template data
    let tableField: any = null;
    
    // Search in all fields
    if (this.templateData) {
      for (const field of this.templateData.allFields) {
        if (field.fieldId === tableFieldId) {
          tableField = field;
          break;
        }
      }
    }
    
    if (tableField && tableField.rows && tableField.rows[rowIndex]) {
      tableField.rows[rowIndex][columnId] = value;
      
      // Trigger change detection
      this.cdr.detectChanges();
      
      // Optionally update form control if needed
      console.log(`Updated table ${tableFieldId} row ${rowIndex} column ${columnId} to:`, value);
    }
  }

  /**
   * Handle dynamic table data changes
   */
  onDynamicTableDataChange(tableData: any): void {
    console.log('🔄 Dynamic table data changed:', tableData);
    
    // Store the dynamic table data in form state or component state
    // This will be used when submitting the form
    if (!this.dynamicTablesData) {
      this.dynamicTablesData = {};
    }
    
    this.dynamicTablesData[tableData.fieldId] = {
      columns: tableData.columns,
      rows: tableData.rows,
      userAddedColumns: tableData.userAddedColumns,
      nextColumnNumber: tableData.nextColumnNumber,
      lastUpdated: new Date().toISOString()
    };
    
    // Trigger change detection
    this.cdr.detectChanges();
    
    console.log('📊 Updated dynamic tables data:', this.dynamicTablesData);
  }

  /**
   * Get dynamic table initial data
   */
  getDynamicTableInitialData(fieldId: string): any {
    return this.dynamicTablesData?.[fieldId] || null;
  }

  /**
   * Check if field is dynamic table type
   */
  isDynamicTable(field: any): boolean {
    return field.fieldType === 'dynamic_table' && field.tableConfig;
  }

  /**
   * Load custom template data and show auto-fill modal
   */
  loadCustomTemplate(): void {
    if (!this.customTemplateId) {
      console.warn('⚠️ No custom template ID provided');
      return;
    }

    console.log('📝 Loading custom template:', this.customTemplateId);
    
    this.customTemplateService.getTemplate(this.customTemplateId).subscribe({
      next: (template) => {
        console.log('✅ Custom template loaded:', template.templateName);
        this.customTemplateValues = template.fieldValues;
        
        // Show auto-fill modal to let user choose strategy
        this.showAutoFillModal = true;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('❌ Failed to load custom template:', error);
        alert('Failed to load custom template. Proceeding with empty form.');
      }
    });
  }

  /**
   * Handle auto-fill modal choice
   */
  onAutoFillChoice(choice: AutoFillChoice): void {
    this.showAutoFillModal = false;

    if (!choice.confirmed || choice.strategy === 'cancel' || !this.customTemplateValues) {
      console.log('❌ Auto-fill cancelled by user');
      this.customTemplateValues = null;
      return;
    }

    console.log(`✅ Applying custom template with strategy: ${choice.strategy}`);
    
    // Get current form values
    const currentValues = this.reportForm.value;
    
    // Apply template values with selected strategy
    const mergedValues = this.customTemplateService.applyTemplateToFormData(
      currentValues,
      this.customTemplateValues,
      choice.strategy
    );

    // Update form with merged values
    this.reportForm.patchValue(mergedValues);
    
    console.log('✅ Form updated with custom template values');
    this.cdr.detectChanges();
    
    // Show success message
    const message = choice.strategy === 'fill_empty'
      ? 'Empty fields have been filled with template values'
      : 'All fields have been replaced with template values';
    
    alert(message);
  }

  /**
   * Handle Save as Template button click
   * Opens the save template dialog and handles the save operation
   */
  onSaveAsTemplate(): void {
    if (!this.saveTemplateDialog) {
      console.error('❌ Save template dialog not found');
      alert('Error: Dialog component not available');
      return;
    }

    // Get current form values
    const formValues = this.reportForm.value;
    
    // Set dialog data with current report context
    this.saveTemplateDialog.data = {
      bankCode: this.selectedBankCode,
      bankName: this.selectedBankName,
      templateCode: this.selectedTemplateId,
      propertyType: this.selectedPropertyType,
      fieldValues: formValues
    };

    // Open the dialog
    this.saveTemplateDialog.open();

    // Subscribe to save event
    const saveSubscription = this.saveTemplateDialog.save.subscribe((templateData: { templateName: string; description: string }) => {
      this.saveTemplate(templateData.templateName, templateData.description, formValues);
      saveSubscription.unsubscribe();
    });

    // Subscribe to cancel event
    const cancelSubscription = this.saveTemplateDialog.cancel.subscribe(() => {
      console.log('❌ Save template cancelled by user');
      cancelSubscription.unsubscribe();
    });
  }

  /**
   * Save the current form as a custom template
   */
  private saveTemplate(templateName: string, description: string, formValues: any): void {
    // Get target org from route params (where user is working)
    let targetOrgShortName = '';
    this.route.params.subscribe(params => {
      targetOrgShortName = params['orgShortName'] || '';
    }).unsubscribe();
    
    if (!targetOrgShortName) {
      console.error('❌ No organization context found in route');
      this.saveTemplateDialog.setError('No organization context found');
      return;
    }

    if (!this.selectedBankCode || !this.selectedTemplateId) {
      console.error('❌ Missing bank or template information');
      this.saveTemplateDialog.setError('Missing bank or template information');
      return;
    }

    console.log('💾 Saving template:', {
      templateName,
      targetOrg: targetOrgShortName,  // Organization from URL
      bank: this.selectedBankCode,
      template: this.selectedTemplateId
    });

    this.saveTemplateDialog.setSaving(true);

    this.templateService.createTemplateFromReport(
      targetOrgShortName,  // Use target org from route
      templateName,
      description,
      this.selectedBankCode,
      this.selectedTemplateId,
      formValues
    ).subscribe({
      next: (response) => {
        console.log('✅ Template saved successfully:', response);
        this.saveTemplateDialog.setSaving(false);
        this.saveTemplateDialog.close();
        
        // Show success message
        alert(`✅ Template "${templateName}" saved successfully!\n\nYou can now use this template when creating new reports.`);
      },
      error: (error) => {
        console.error('❌ Failed to save template:', error);
        this.saveTemplateDialog.setSaving(false);
        
        // Log detailed error information for debugging
        console.error('Error details:', {
          status: error.status,
          statusText: error.statusText,
          error: error.error,
          message: error.message
        });
        
        let errorMessage = 'Failed to save template';
        
        if (error.status === 401) {
          errorMessage = 'Not authenticated. Please log in again.';
          // Optionally redirect to login after a delay
          setTimeout(() => this.router.navigate(['/login']), 2000);
        } else if (error.status === 400) {
          errorMessage = error.error?.detail || error.error?.error || 'Invalid template data';
        } else if (error.status === 403) {
          errorMessage = error.error?.detail || error.error?.error || 'You do not have permission to create templates';
        } else if (error.status === 409) {
          errorMessage = 'Template name already exists or template limit reached (max 3 per bank/property type)';
        } else if (error.status === 404) {
          errorMessage = 'Bank or template not found';
        }
        
        this.saveTemplateDialog.setError(errorMessage);
      }
    });
  }

  /**
   * Initialize calculated fields system
   * - Extracts all calculated fields from template
   * - Sets up real-time listeners for source field changes
   * - Calculates initial values
   */
  private initializeCalculatedFields(): void {
    if (!this.templateData) {
      return;
    }

    console.log('🧮 Initializing calculated fields system...');

    // Extract all calculated fields from template data
    this.calculatedFieldsMap = this.calculationService.getCalculatedFields(this.templateData.allFields);
    
    console.log(`🧮 Found ${this.calculatedFieldsMap.size} calculated fields:`, 
      Array.from(this.calculatedFieldsMap.keys())
    );

    // Set up listeners for each calculated field
    this.calculatedFieldsMap.forEach((config, fieldId) => {
      this.setupCalculatedFieldListener(fieldId, config);
    });

    // Perform initial calculation for all calculated fields
    this.recalculateAllFields();
  }

  /**
   * Sets up a listener for a calculated field
   * Triggers recalculation whenever any source field changes
   */
  private setupCalculatedFieldListener(fieldId: string, config: CalculatedFieldConfig): void {
    // Get all dependencies (fields that trigger recalculation)
    const dependencies = this.calculationService.getFieldDependencies(config);

    console.log(`🧮 Setting up listener for ${fieldId}, dependencies:`, dependencies);

    // Subscribe to value changes of each dependency
    dependencies.forEach(depFieldId => {
      const control = this.reportForm.get(depFieldId);
      
      if (control) {
        control.valueChanges.subscribe(() => {
          this.calculateField(fieldId, config);
        });
      } else {
        console.warn(`⚠️ Dependency control not found: ${depFieldId}`);
      }
    });
  }

  /**
   * Calculates the value for a specific calculated field
   */
  private calculateField(fieldId: string, config: CalculatedFieldConfig): void {
    const calculatedValue = this.calculationService.evaluateCalculatedField(config, this.reportForm);
    
    // Update the field value (enable temporarily if readonly)
    const control = this.reportForm.get(fieldId);
    if (control) {
      const wasDisabled = control.disabled;
      
      if (wasDisabled) {
        control.enable({ emitEvent: false });
      }
      
      control.setValue(calculatedValue, { emitEvent: false });
      
      if (wasDisabled) {
        control.disable({ emitEvent: false });
      }

      console.log(`🧮 Calculated ${fieldId} = ${calculatedValue}`);
    }
  }

  /**
   * Recalculates all calculated fields
   * Called on initialization and when switching tabs
   */
  private recalculateAllFields(): void {
    console.log('🧮 Recalculating all calculated fields...');
    
    this.calculatedFieldsMap.forEach((config, fieldId) => {
      this.calculateField(fieldId, config);
    });
  }

}

