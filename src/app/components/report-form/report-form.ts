import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonField, BankBranch, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField, BankSpecificTab, BankSpecificSection, DocumentType } from '../../models';
import { TemplateService } from '../../services/template.service';
import { ReportService, ReportRequest } from '../../services/report.service';
import { DynamicTableComponent } from '../dynamic-table/dynamic-table.component';

@Component({
  selector: 'app-report-form',
  imports: [CommonModule, ReactiveFormsModule, DynamicTableComponent],
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
  activeTab = 'template';  // Always default to first tab (Bank-Specific Fields)
  
  // Bank-specific dynamic tabs
  activeBankSpecificTab: string | null = null;

  // Dynamic tables data storage
  dynamicTablesData: { [fieldId: string]: any } = {};

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private http: HttpClient,
    private templateService: TemplateService,
    private reportService: ReportService,
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

    // Setup calculation listeners for fields with calculationMetadata
    this.setupCalculationListeners();
    
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
   * Setup calculation listeners for fields with calculationMetadata
   */
  setupCalculationListeners() {
    if (!this.templateData) return;

    console.log('🧮 Setting up calculation listeners...');
    console.log('📋 Total fields available:', this.templateData.allFields.length);

    // Find all fields with calculation metadata
    this.templateData.allFields.forEach(field => {
      if (field.calculationMetadata?.isCalculatedField && field.formula) {
        console.log(`🧮 Found calculated field: ${field.fieldId} with formula: ${field.formula}`);
        
        // Get dependency fields from the formula or metadata
        const dependencies = field.calculationMetadata.dependencies || this.extractFormulaFields(field.formula);
        console.log(`🔗 Dependencies for ${field.fieldId}:`, dependencies);

        // Set up listeners for each dependency field
        dependencies.forEach(depFieldId => {
          const depControl = this.reportForm.get(depFieldId);
          if (depControl) {
            console.log(`👂 Setting up listener for dependency: ${depFieldId} -> ${field.fieldId}`);
            depControl.valueChanges.subscribe(() => {
              setTimeout(() => {
                const currentValues = this.reportForm.value;
                this.updateCalculatedField(field, currentValues);
              }, 0);
            });
          } else {
            console.warn(`⚠️ Dependency control not found: ${depFieldId}`);
          }
        });

        // Calculate initial value
        const currentValues = this.reportForm.value;
        this.updateCalculatedField(field, currentValues);
      }

      // Handle subfields in groups
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          if (subField.calculationMetadata?.isCalculatedField && subField.formula) {
            console.log(`🧮 Found calculated sub-field: ${subField.fieldId} with formula: ${subField.formula}`);
            
            const dependencies = subField.calculationMetadata.dependencies || this.extractFormulaFields(subField.formula);
            console.log(`🔗 Dependencies for ${subField.fieldId}:`, dependencies);

            dependencies.forEach(depFieldId => {
              const depControl = this.reportForm.get(depFieldId);
              if (depControl) {
                console.log(`👂 Setting up listener for dependency: ${depFieldId} -> ${subField.fieldId}`);
                depControl.valueChanges.subscribe(() => {
                  setTimeout(() => {
                    const currentValues = this.reportForm.value;
                    this.updateCalculatedField(subField, currentValues);
                  }, 0);
                });
              }
            });

            // Calculate initial value
            const currentValues = this.reportForm.value;
            this.updateCalculatedField(subField, currentValues);
          }
        });
      }
    });
  }

  /**
   * Extract field names from a formula string
   */
  extractFormulaFields(formula: string): string[] {
    const fieldPattern = /\b[a-zA-Z_][a-zA-Z0-9_]*\b/g;
    const matches = formula.match(fieldPattern) || [];
    // Filter out mathematical operators and functions
    const operators = ['sin', 'cos', 'tan', 'abs', 'sqrt', 'pow', 'min', 'max', 'Math'];
    return matches.filter(match => !operators.includes(match) && isNaN(Number(match)));
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
    console.log('💾 Saving draft - Form Values:', this.reportForm.value);
    
    // Prepare report data for draft save (no validation required)
    const reportData: ReportRequest = {
      bank_code: this.selectedBankCode,
      template_id: this.selectedTemplateId,
      template_name: this.selectedTemplateName,
      property_type: this.selectedPropertyType,
      form_data: {
        common_fields: this.reportForm.value,
        bank_specific_fields: this.extractBankSpecificData(),
        dynamic_tables: this.dynamicTablesData,
        template_metadata: {
          bank_code: this.selectedBankCode,
          bank_name: this.selectedBankName,
          template_id: this.selectedTemplateId,
          template_name: this.selectedTemplateName,
          property_type: this.selectedPropertyType
        }
      },
      status: 'draft',
      metadata: {
        saved_at: new Date().toISOString(),
        form_completion_percentage: this.calculateFormCompletionPercentage()
      }
    };

    this.reportService.saveDraft(reportData).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ Draft saved successfully:', response.data?.report_id);
          // TODO: Show success toast/notification
          alert('Draft saved successfully!');
        }
      },
      error: (error) => {
        console.error('❌ Failed to save draft:', error);
        alert(`Failed to save draft: ${error.message}`);
      }
    });
  }

  onSubmit() {
    if (this.reportForm.valid) {
      console.log('🚀 Submit - Form Values:', this.reportForm.value);
      
      // Prepare report data
      const reportData: ReportRequest = {
        bank_code: this.selectedBankCode,
        template_id: this.selectedTemplateId,
        template_name: this.selectedTemplateName,
        property_type: this.selectedPropertyType,
        form_data: {
          common_fields: this.reportForm.value,
          bank_specific_fields: this.extractBankSpecificData(),
          dynamic_tables: this.dynamicTablesData,
          template_metadata: {
            bank_code: this.selectedBankCode,
            bank_name: this.selectedBankName,
            template_id: this.selectedTemplateId,
            template_name: this.selectedTemplateName,
            property_type: this.selectedPropertyType
          }
        },
        metadata: {
          submitted_at: new Date().toISOString(),
          form_completion_percentage: this.calculateFormCompletionPercentage()
        }
      };

      // Check user permission and call appropriate service method
      // For now, we'll use a simple save operation
      // TODO: Add role-based logic once auth service is available
      
      this.reportService.saveReport(reportData).subscribe({
        next: (response) => {
          if (response.success) {
            console.log('✅ Report saved successfully:', response.data?.report_id);
            alert('Report saved successfully!');
            // TODO: Navigate to reports list or dashboard
            this.router.navigate(['/dashboard']);
          }
        },
        error: (error) => {
          console.error('❌ Failed to save report:', error);
          alert(`Failed to save report: ${error.message}`);
        }
      });
      
    } else {
      console.log('❌ Form is invalid');
      // Mark all fields as touched to show validation errors
      this.markAllFieldsAsTouched();
      alert('Please fill in all required fields before submitting.');
    }
  }

  /**
   * Mark all form fields as touched to show validation errors
   */
  private markAllFieldsAsTouched() {
    Object.keys(this.reportForm.controls).forEach(key => {
      const control = this.reportForm.get(key);
      if (control) {
        control.markAsTouched();
        
        // If it's a group (for nested fields), mark all nested controls as touched
        if (control instanceof FormGroup) {
          this.markFormGroupAsTouched(control);
        }
      }
    });
  }

  /**
   * Recursively mark all controls in a FormGroup as touched
   */
  private markFormGroupAsTouched(formGroup: FormGroup) {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      if (control) {
        control.markAsTouched();
        if (control instanceof FormGroup) {
          this.markFormGroupAsTouched(control);
        }
      }
    });
  }

  /**
   * Extract bank-specific form data from the form
   */
  private extractBankSpecificData(): any {
    const bankSpecificData: any = {};
    
    if (this.templateData?.bankSpecificTabs) {
      this.templateData.bankSpecificTabs.forEach(tab => {
        tab.sections?.forEach(section => {
          section.fields?.forEach(field => {
            const formValue = this.reportForm.get(field.technicalName || field.fieldId)?.value;
            if (formValue !== null && formValue !== undefined) {
              bankSpecificData[field.technicalName || field.fieldId] = formValue;
            }
          });
        });
      });
    }
    
    return bankSpecificData;
  }

  /**
   * Calculate form completion percentage for progress tracking
   */
  private calculateFormCompletionPercentage(): number {
    const totalFields = this.getTotalFieldCount();
    const filledFields = this.getFilledFieldCount();
    
    if (totalFields === 0) return 0;
    return Math.round((filledFields / totalFields) * 100);
  }

  /**
   * Get number of filled fields in the form
   */
  private getFilledFieldCount(): number {
    let count = 0;
    const formValue = this.reportForm.value;
    
    Object.keys(formValue).forEach(key => {
      const value = formValue[key];
      if (value !== null && value !== undefined && value !== '') {
        count++;
      }
    });
    
    return count;
  }

  onCancel() {
    // Check if form has unsaved changes
    if (this.reportForm.dirty) {
      const confirmLeave = confirm('You have unsaved changes. Are you sure you want to leave without saving?');
      if (!confirmLeave) {
        return;
      }
    }
    
    this.router.navigate(['/dashboard']);
  }

  goBackToSelection() {
    this.router.navigate(['/new-report']);
  }

  /**
   * Get button text based on current implementation
   * TODO: Make this role-based when auth service is integrated
   */
  getSubmitButtonText(): string {
    return 'Save Report';
  }

  /**
   * Get button title/tooltip based on current implementation
   * TODO: Make this role-based when auth service is integrated
   */
  getSubmitButtonTitle(): string {
    return 'Save report (Role-based submission coming soon)';
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
   * Handles form value changes to apply conditional logic and calculations
   */
  handleFormValueChanges(formValues: any): void {
    if (!this.templateData || !this.reportForm) {
      return;
    }

    // Update field visibility and disabled states based on conditional logic
    this.templateData.allFields.forEach(field => {
      this.updateFieldConditionalState(field, formValues);
      
      // Handle calculations for calculated fields (both calculated type and fields with calculationMetadata)
      if ((field.fieldType === 'calculated' && field.formula) || 
          (field.calculationMetadata?.isCalculatedField && field.formula)) {
        this.updateCalculatedField(field, formValues);
      }

      // Handle auto-population for fields with calculationMetadata
      if (field.calculationMetadata?.autoPopulate?.enabled) {
        this.handleAutoPopulation(field, formValues);
      }
      
      // Handle sub-fields for group fields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          this.updateFieldConditionalState(subField, formValues);
          
          // Handle calculations for calculated sub-fields (both calculated type and fields with calculationMetadata)
          if ((subField.fieldType === 'calculated' && subField.formula) || 
              (subField.calculationMetadata?.isCalculatedField && subField.formula)) {
            this.updateCalculatedField(subField, formValues);
          }

          // Handle auto-population for sub-fields
          if (subField.calculationMetadata?.autoPopulate?.enabled) {
            this.handleAutoPopulation(subField, formValues);
          }
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
    if (!field.formula) {
      console.log('⚠️ No formula found for field:', field.fieldId);
      return '';
    }
    
    try {
      // Simple formula evaluation - can be enhanced with a proper expression parser
      let formula = field.formula;
      const formControls = this.reportForm.controls;
      const formValues = this.reportForm.value;
      
      console.log('🧮 Calculating field:', field.fieldId);
      console.log('📋 Original formula:', field.formula);
      console.log('📊 Raw form values:', formValues);
      
      // Replace field references with actual numeric values using word boundaries
      Object.keys(formControls).forEach(fieldId => {
        let value = formControls[fieldId].value || 0;
        
        // Clean currency values - remove currency symbols and commas
        if (typeof value === 'string') {
          value = value.replace(/[₹$£€,\s]/g, '');
          value = parseFloat(value) || 0;
        }
        
        console.log(`🔢 Field ${fieldId}: raw="${formControls[fieldId].value}" cleaned="${value}"`);
        
        // Use word boundaries to prevent partial matches
        formula = formula.replace(new RegExp('\\b' + fieldId + '\\b', 'g'), value.toString());
      });
      
      console.log('🔄 Processed formula:', formula);
      
      // Evaluate simple mathematical expressions
      // Note: In production, use a proper expression parser for security
      const result = Function('"use strict"; return (' + formula + ')')();
      const finalResult = isNaN(result) ? 0 : result;
      
      console.log('✅ Calculation result:', finalResult);
      
      // Format as currency if it's a currency field
      if (field.displayFormat === 'currency' || field.fieldType === 'currency' || field.fieldType === 'calculated' || field.calculationMetadata?.formatting?.currency) {
        const formatted = new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        }).format(finalResult);
        console.log('💰 Formatted result:', formatted);
        return formatted;
      }
      
      return finalResult.toString();
    } catch (error) {
      console.warn('❌ Error calculating formula:', field.formula, error);
      console.warn('❌ Error details:', error instanceof Error ? error.message : 'Unknown error');
      return '';
    }
  }

  /**
   * Update calculated field value in real-time
   */
  private updateCalculatedField(field: any, formValues: any): void {
    console.log(`🔢 updateCalculatedField called for: ${field.fieldId}`, {
      hasFormula: !!field.formula,
      formula: field.formula,
      fieldType: field.fieldType,
      calculationMetadata: field.calculationMetadata
    });
    
    const control = this.reportForm?.get(field.fieldId);
    if (!control || !field.formula) {
      console.warn(`❌ Cannot update calculated field ${field.fieldId}:`, {
        hasControl: !!control,
        hasFormula: !!field.formula
      });
      return;
    }

    try {
      let formula = field.formula;
      
      // Replace field references with actual values from form
      Object.keys(formValues).forEach(fieldId => {
        let value = formValues[fieldId] || 0;
        
        // Clean currency values - remove currency symbols and commas
        if (typeof value === 'string') {
          value = value.replace(/[₹$£€,\s]/g, '');
          value = parseFloat(value) || 0;
        }
        
        console.log(`🔢 Field ${fieldId}: raw="${formValues[fieldId]}" cleaned="${value}"`);
        
        // Use word boundaries to prevent partial matches
        formula = formula.replace(new RegExp('\\b' + fieldId + '\\b', 'g'), value.toString());
      });
      
      console.log('📊 Calculating field:', field.fieldId, 'Formula:', field.formula, 'Processed:', formula);
      
      // Evaluate the mathematical expression
      const result = Function('"use strict"; return (' + formula + ')')();
      const calculatedValue = isNaN(result) ? 0 : result;
      
      // Apply simple numeric formatting (no currency formatting)
      let formattedValue = calculatedValue;
      if (field.calculationMetadata?.formatting) {
        const decimalPlaces = field.calculationMetadata.formatting.decimalPlaces || 2;
        formattedValue = Number(calculatedValue.toFixed(decimalPlaces));
      }
      
      console.log('💰 Calculated result:', calculatedValue, 'Formatted:', formattedValue);
      
      // Temporarily enable the control if it's disabled (for readonly calculated fields)
      const wasDisabled = control.disabled;
      if (wasDisabled) {
        control.enable({ emitEvent: false });
      }
      
      // Update the form control without triggering another value change event
      control.setValue(formattedValue, { emitEvent: false });
      
      // Re-disable the control if it was previously disabled
      if (wasDisabled) {
        control.disable({ emitEvent: false });
      }
      
      // Store the numeric value for further calculations
      (control as any).numericValue = calculatedValue;
      
    } catch (error) {
      console.warn('Error calculating field:', field.fieldId, field.formula, error);
      control.setValue('', { emitEvent: false });
    }
  }

  /**
   * Handle auto-population of fields based on calculation results
   */
  private handleAutoPopulation(field: any, formValues: any): void {
    const metadata = (field as any).calculationMetadata;
    if (!metadata?.autoPopulate?.enabled || !metadata.autoPopulate.targetFields) {
      return;
    }

    const sourceControl = this.reportForm?.get(field.fieldId);
    if (!sourceControl) {
      return;
    }

    const sourceValue = (sourceControl as any).numericValue || sourceControl.value || 0;
    
    // Auto-populate target fields
    metadata.autoPopulate.targetFields.forEach((target: any) => {
      const targetControl = this.reportForm?.get(target.fieldId);
      if (targetControl && (target.condition === 'always' || this.evaluateAutoPopulateCondition(target.condition, formValues))) {
        
        console.log('🔄 Auto-populating field:', target.fieldId, 'with value:', sourceValue);
        
        if (target.mode === 'overwrite' || !targetControl.value) {
          // Format the value if it's a currency field
          let formattedValue = sourceValue;
          if (target.fieldType === 'currency') {
            formattedValue = new Intl.NumberFormat('en-IN', {
              style: 'currency',
              currency: 'INR',
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            }).format(sourceValue);
          }
          
          targetControl.setValue(formattedValue, { emitEvent: false });
          (targetControl as any).isAutoPopulated = true;
        }
      }
    });
  }

  /**
   * Evaluate auto-populate condition
   */
  private evaluateAutoPopulateCondition(condition: string, formValues: any): boolean {
    if (condition === 'always') return true;
    
    // Add more condition evaluation logic here as needed
    try {
      // Simple condition evaluation - enhance as needed
      return Function('"use strict"; return (' + condition + ')')();
    } catch {
      return false;
    }
  }

  /**
   * Manually trigger calculation for testing
   */
  triggerCalculation(): void {
    if (!this.templateData) return;

    const formValues = this.reportForm.value;
    console.log('🔄 Manually triggering calculations with form values:', formValues);
    console.log('📊 Form controls status:', {
      total_extent_plot: this.reportForm.get('total_extent_plot')?.value,
      valuation_rate: this.reportForm.get('valuation_rate')?.value,
      estimated_land_value: this.reportForm.get('estimated_land_value')?.value
    });
    
    // Trigger all calculated fields
    this.templateData.allFields.forEach(field => {
      if (field.calculationMetadata?.isCalculatedField && field.formula) {
        console.log(`🧮 Triggering calculation for: ${field.fieldId}`);
        this.updateCalculatedField(field, formValues);
        
        // Also check for getCalculatedValue method
        const result = this.getCalculatedValue(field);
        console.log(`✅ ${field.fieldId} calculated result:`, result);
      }

      // Handle subfields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          if (subField.calculationMetadata?.isCalculatedField && subField.formula) {
            console.log(`🧮 Triggering calculation for sub-field: ${subField.fieldId}`);
            this.updateCalculatedField(subField, formValues);
          }
        });
      }
    });
    
    this.handleFormValueChanges(formValues);
    this.cdr.detectChanges();
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

}
