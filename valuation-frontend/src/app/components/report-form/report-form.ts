import { Component, OnInit, ChangeDetectorRef, inject, computed, ViewChild } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonField, BankBranch, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField, BankSpecificTab, BankSpecificSection, CalculatedFieldConfig, DocumentType } from '../../models';
import { TemplateService } from '../../services/template.service';
import { CustomTemplateService } from '../../services/custom-template.service';
import { TemplateVersioningService } from '../../services/template-versioning.service';
import { CreateReportRequest } from '../../models/template-versioning.models';
import { CalculationService } from '../../services/calculation.service';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { TemplateAutofillModalComponent, AutoFillChoice } from '../custom-templates/template-autofill-modal.component';
import { DynamicTableComponent } from '../dynamic-table/dynamic-table.component';
import { ReportsService } from '../../services/reports.service';
import { NotificationService } from '../../services/notification.service';
import { DropdownValueMappingService } from '../../services/dropdown-value-mapping.service';

@Component({
  selector: 'app-report-form',
  imports: [CommonModule, ReactiveFormsModule, DynamicTableComponent, TemplateAutofillModalComponent],
  templateUrl: './report-form.html',
  styleUrl: './report-form.css',
})
export class ReportForm implements OnInit {
  
  // Dependency Injection
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly dropdownMappingService = inject(DropdownValueMappingService);
  
  // Query parameters from navigation
  selectedBankCode: string = '';
  selectedBankName: string = '';
  selectedTemplateId: string = '';
  selectedTemplateName: string = '';
  selectedPropertyType: string = '';
  customTemplateId: string = '';
  customTemplateName: string = '';
  currentOrgShortName: string = ''; // Track current organization context
  extractedPdfFields: Record<string, any> | null = null; // PDF extracted fields
  
  // Form data - Updated for new structure
  reportForm: FormGroup;
  templateData: ProcessedTemplateData | null = null;
  documentTypes: DocumentType[] = [];
  availableBranches: Array<{value: string, label: string}> = [];
  isLoading = false;
  
  // PDF Generation
  isGeneratingPdf = false;
  
  // Report reference number
  reportReferenceNumber: string | null = null;
  referenceNumberLoading = false;
  referenceNumberError: string | null = null;
  
  // Current report ID (for updates after initial save)
  currentReportId: string | null = null;
  
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
  
  // Report workflow state
  reportStatus: 'draft' | 'saved' | 'submitted' | null = null;
  reportId: string | null = null;
  pendingReportData: any = null;
  
  // View/Edit mode
  isViewMode = false;
  isEditMode = false;
  
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
    private cdr: ChangeDetectorRef,
    private templateVersioningService: TemplateVersioningService,
    private reportsService: ReportsService
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
    this.checkForExistingReport();
    
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
          
          // Extract document types from response
          this.documentTypes = response.documentTypes || [];
          console.log(`📄 Document Types loaded: ${this.documentTypes.length}`, this.documentTypes);
          
          // Process the response into organized field groups
          this.templateData = this.templateService.processTemplateData(response);
          
          console.log('🏗️ Processed template data:', {
            commonFieldGroups: this.templateData.commonFieldGroups.length,
            bankSpecificTabs: this.templateData.bankSpecificTabs.length,
            totalFields: this.templateData.totalFieldCount,
            documentTypes: this.documentTypes.length,
            templateData: this.templateData
          });
          
          this.buildFormControlsWithReportData(this.pendingReportData);
          
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
          
          // If we have pending report data (loading existing report), populate the form
          if (this.pendingReportData) {
            console.log('📝 Template loaded successfully, now populating form with pending report data');
            console.log('📝 Form ready state:', !!this.reportForm);
            console.log('📝 Form controls count:', Object.keys(this.reportForm?.controls || {}).length);
            this.populateFormWithReportData(this.pendingReportData);
            this.pendingReportData = null; // Clear after use
          } else {
            console.log('📝 No pending report data to populate');
          }
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

  /**
   * Determine the base template ID based on property type
   */
  private determineBaseTemplateId(propertyType: string): string {
    // Standard mapping of property types to template IDs
    const templateMapping: { [key: string]: string } = {
      'land': 'land-property',
      'apartment': 'apartment-property',
      'building': 'building-property'
    };
    
    return templateMapping[propertyType.toLowerCase()] || 'land-property';
  }

  checkForExistingReport() {
    // Check if we're loading an existing report by ID
    this.route.params.subscribe(params => {
      const reportId = params['id'];
      if (reportId) {
        console.log('📄 Loading existing report:', reportId);
        this.reportId = reportId;
        this.currentReportId = reportId;
        
        // Check query params for mode
        this.route.queryParams.subscribe(queryParams => {
          const mode = queryParams['mode'];
          this.isViewMode = mode === 'view';
          this.isEditMode = mode === 'edit' || !mode; // Default to edit if no mode specified
          
          console.log('📄 Report mode detection:', { 
            queryParams, 
            mode, 
            isViewMode: this.isViewMode, 
            isEditMode: this.isEditMode 
          });
          console.log('🔍 Mode flags set:', {
            isViewMode: this.isViewMode,
            isEditMode: this.isEditMode
          });
        });
        
        this.loadExistingReport(reportId);
      } else {
        // New report - always edit mode
        this.isViewMode = false;
        this.isEditMode = true;
      }
    });
  }

  loadExistingReport(reportId: string) {
    console.log('📄 Loading existing report data for:', reportId);
    this.isLoading = true;
    
    // Use the reports service to get report details
    this.reportsService.getReportById(reportId).subscribe({
      next: (reportData) => {
        console.log('✅ Existing report loaded:', reportData);
        console.log('📊 Report data structure:', JSON.stringify(reportData, null, 2));
        if (reportData) {
          
          // Extract template information from the report
          this.selectedBankCode = reportData.bankCode || (reportData as any).bank_code || '';
          this.selectedTemplateId = reportData.templateId || (reportData as any).template_id || '';
          this.selectedPropertyType = reportData.propertyType || (reportData as any).property_type || '';
          this.reportReferenceNumber = reportData.referenceNumber || (reportData as any).reference_number || '';
          
          // Fallback: If bankCode is empty, try to derive it from form data or use default
          if (!this.selectedBankCode && (reportData.formData || reportData.form_data)) {
            const formData = reportData.formData || reportData.form_data || {};
            this.selectedBankCode = this.deriveBankCodeFromFormData(formData);
            console.log('📋 Derived bank code from form data:', this.selectedBankCode);
          }
          
          // If still no bank code, use a safe default
          if (!this.selectedBankCode) {
            this.selectedBankCode = 'SBI'; // Default to SBI as most reports are SBI
            console.log('⚠️ No bank code found, defaulting to SBI');
          }
          
          // Load bank branches after setting bank code
          if (this.selectedBankCode) {
            console.log('🏦 Loading branches for loaded report bank:', this.selectedBankCode);
            this.loadBankBranches();
          }
          
          // Set report status (map to form status values)
          const status = reportData.status || 'draft';
          if (status === 'in_progress') {
            this.reportStatus = 'draft';
          } else if (status === 'completed') {
            this.reportStatus = 'saved';
          } else if (status === 'draft' || status === 'submitted') {
            this.reportStatus = status as 'draft' | 'submitted';
          } else {
            this.reportStatus = 'draft';
          }
          
          console.log('📋 Report template info extracted:', {
            bankCode: this.selectedBankCode,
            templateId: this.selectedTemplateId,
            propertyType: this.selectedPropertyType,
            referenceNumber: this.reportReferenceNumber,
            status: this.reportStatus
          });
          
          // Check if report has stored template information from draft (extended data)
          const reportDataAny = reportData as any;
          if (reportDataAny.templateStructure || reportDataAny.report_data?.templateStructure) {
            console.log('📋 Report has stored template structure, using it');
            const templateInfo = reportDataAny.templateStructure || reportDataAny.report_data?.templateStructure;
            this.selectedTemplateId = reportDataAny.templateId || (reportData as any).template_id || 'land-property';
            this.selectedBankCode = reportDataAny.bankCode || (reportData as any).bank_code || this.selectedBankCode;
            this.selectedPropertyType = reportDataAny.propertyType || (reportData as any).property_type || '';
            console.log('📋 Using stored template info:', {
              templateId: this.selectedTemplateId,
              bankCode: this.selectedBankCode,
              propertyType: this.selectedPropertyType
            });
          } else {
            // Fallback: try to determine from available data
            console.log('📋 No stored template structure, inferring from data');
            
            // Use a sensible default that we know works for SBI
            this.selectedTemplateId = 'land-property'; // This should match the create URL
            
            if (this.selectedPropertyType) {
              // Map property type to template ID if available
              const templateMapping: { [key: string]: string } = {
                'residential land': 'land-property',
                'commercial land': 'land-property',
                'agricultural land': 'land-property',
                'land': 'land-property',
                'residential': 'residential',
                'commercial': 'commercial'
              };
              
              const mappedTemplate = templateMapping[this.selectedPropertyType.toLowerCase()];
              if (mappedTemplate) {
                this.selectedTemplateId = mappedTemplate;
                console.log('📋 Mapped property type to template:', this.selectedPropertyType, '->', this.selectedTemplateId);
              }
            }
          }
          
          // Store report data to populate after template loads
          this.pendingReportData = reportData;
          
          // Since the report has an ObjectId template_id, we need to call backend to get available templates
          // and match or use a fallback approach
          console.log('� Template ID is ObjectId, need to determine correct template code');
          console.log('📋 Report has property_address:', reportData.property_address);
          
          // For now, let's try some common SBI templates and see what works
          this.tryLoadingAvailableTemplate(this.selectedBankCode);
        } else {
          console.error('❌ Report not found or invalid data');
          this.isLoading = false;
        }
      },
      error: (error) => {
        console.error('❌ Error loading existing report:', error);
        this.isLoading = false;
        // Could redirect back to reports list or show error message
      }
    });
  }

  populateFormWithReportData(reportData: any) {
    console.log('� populateFormWithReportData CALLED');
    console.log('�📝 Populating form with report data:', reportData);
    console.log('📝 Report data type:', typeof reportData);
    console.log('📝 Report data is null/undefined:', reportData === null || reportData === undefined);
    
    // Use formData as single source of truth (contains form values like "mortgage_loan")
    // Check both camelCase and snake_case for backward compatibility
    const actualReportData = reportData.formData || reportData.form_data || reportData.reportData || reportData.report_data;
    
    if (actualReportData) {
      console.log('📝 Found form data:', Object.keys(actualReportData).slice(0, 10));
      console.log('📝 Form data structure (first 500 chars):', JSON.stringify(actualReportData, null, 2).substring(0, 500));
    } else {
      console.log('⚠️ WARNING: No formData, form_data, reportData, or report_data found!');
      console.log('📝 Available keys:', Object.keys(reportData || {}));
    }
    console.log('📝 Available form controls:', Object.keys(this.reportForm?.controls || {}));
    console.log('📝 Form exists:', !!this.reportForm);
    
    if (this.reportForm && reportData) {
      
      // STEP 1: Handle top-level fields that should map to form controls
      console.log('📝 Step 1: Mapping top-level fields...');
      
      // Map top-level referenceNumber (camelCase) or reference_number (snake_case) to report_reference_number form field
      const referenceNumber = reportData.referenceNumber || reportData.reference_number;
      if (referenceNumber) {
        const refControl = this.reportForm.get('report_reference_number');
        if (refControl) {
          refControl.setValue(referenceNumber);
          console.log(`✅ Mapped referenceNumber -> report_reference_number: ${referenceNumber}`);
        } else {
          console.log(`⚠️ No report_reference_number control found for referenceNumber: ${referenceNumber}`);
        }
      }
      
      // Map other top-level fields as needed
      const topLevelFieldMappings = {
        'reference_number': 'report_reference_number',
        'referenceNumber': 'report_reference_number',
        'status': 'status',
        'bank_code': 'bank_code',
        'template_id': 'template_id'
      };
      
      Object.entries(topLevelFieldMappings).forEach(([sourceField, targetField]) => {
        if (reportData[sourceField] && sourceField !== 'reference_number') { // Skip reference_number as it's handled above
          const control = this.reportForm.get(targetField);
          if (control) {
            control.setValue(reportData[sourceField]);
            console.log(`✅ Mapped top-level ${sourceField} -> ${targetField}: ${reportData[sourceField]}`);
          }
        }
      });
      
      // STEP 2: Handle report_data/reportData structure
      if (actualReportData) {
        // Detect format: check if we have nested structure (new format) or flat structure (old format)
        const reportDataObj = actualReportData;
        const hasNestedStructure = this.hasNestedStructure(reportDataObj);
        
        console.log('📝 Step 2: Detected report format:', hasNestedStructure ? 'NESTED (new)' : 'FLAT (old)');
        
        if (hasNestedStructure) {
          // New nested format - map nested data to form controls
          this.populateFromNestedStructure(reportDataObj);
        } else {
          // Old flat format - directly map flat fields to form controls
          this.populateFromFlatStructure(reportDataObj);
        }
      } else {
        console.log('📝 No report_data found, only using top-level fields');
      }
      
      // Apply correct mode state after data population - CRITICAL: This must happen AFTER all data population
      console.log('🔍 About to apply mode state after data population:', {
        isViewMode: this.isViewMode,
        isEditMode: this.isEditMode
      });
      
      if (this.isViewMode) {
        this.applyViewModeState();
      } else if (this.isEditMode) {
        this.applyEditModeState();
      }
      
      // Force change detection to update UI
      this.cdr.detectChanges();
      
      // Double-check view mode is still applied (sometimes change detection can re-enable)
      if (this.isViewMode && this.reportForm.enabled) {
        console.log('⚠️ Form was re-enabled after change detection, re-disabling...');
        this.reportForm.disable();
        Object.keys(this.reportForm.controls).forEach(controlName => {
          const control = this.reportForm.get(controlName);
          if (control && control.enabled) {
            control.disable();
          }
        });
      }
      
      console.log('📝 Form populated with existing report data');
      console.log('🔍 Final form state:', {
        isViewMode: this.isViewMode,
        isEditMode: this.isEditMode,
        formEnabled: this.reportForm.enabled,
        bankBranchControlStatus: this.reportForm.get('bank_branch')?.enabled ? 'enabled' : 'disabled'
      });
      
      // Recalculate all calculated fields after populating with existing data
      this.recalculateAllFields();
      
      // Final step: Ensure reference number is set from the loaded report
      if (this.reportReferenceNumber) {
        const refControl = this.reportForm.get('report_reference_number');
        if (refControl) {
          refControl.setValue(this.reportReferenceNumber);
          console.log(`✅ Final: Set reference number field to: ${this.reportReferenceNumber}`);
        } else {
          console.log(`⚠️ Final: report_reference_number control not found, but value exists: ${this.reportReferenceNumber}`);
        }
      }
    } else {
      console.log('📝 No report_data found or form not ready, fields will remain empty for draft');
    }
    
    this.isLoading = false;
  }

  /**
   * Detect if report data has nested structure (new format) vs flat structure (old format)
   */
  private hasNestedStructure(reportData: any): boolean {
    // Check for new format indicators: common_fields, data, tables
    if (reportData.common_fields || reportData.data || reportData.tables) {
      console.log('📝 Detected new format with common_fields/data/tables structure');
      return true;
    }
    
    // Check for expected tab names in the data
    const expectedTabs = ['property_details', 'valuation', 'building_specification', 'construction_details'];
    
    // If any expected tabs are present as objects, consider it nested
    for (const tab of expectedTabs) {
      if (reportData[tab] && typeof reportData[tab] === 'object' && !Array.isArray(reportData[tab])) {
        return true;
      }
    }
    
    // Also check if most fields are objects (nested) vs primitives (flat)
    let nestedCount = 0;
    let flatCount = 0;
    
    Object.values(reportData).forEach(value => {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        nestedCount++;
      } else {
        flatCount++;
      }
    });
    
    // If more than 50% of fields are nested objects, consider it nested format
    return nestedCount > flatCount;
  }

  /**
   * Populate form from nested structure (new format)
   */
  private populateFromNestedStructure(reportData: any) {
    console.log('📝 Using nested structure population strategy');
    console.log('📝 Report data structure for nested population:', {
      hasCommonFields: !!reportData.common_fields,
      hasData: !!reportData.data,
      hasTables: !!reportData.tables,
      commonFieldsKeys: reportData.common_fields ? Object.keys(reportData.common_fields) : [],
      dataKeys: reportData.data ? Object.keys(reportData.data) : [],
      topLevelKeys: Object.keys(reportData)
    });
    
    // First, handle common_fields directly (bank_branch and other common fields)
    if (reportData.common_fields && typeof reportData.common_fields === 'object') {
      console.log('📝 Processing common_fields section:', reportData.common_fields);
      Object.keys(reportData.common_fields).forEach(fieldKey => {
        const value = reportData.common_fields[fieldKey];
        const control = this.reportForm.get(fieldKey);
        if (control) {
          // Find the field definition to check if it's a dropdown
          const fieldDefinition = this.findFieldInTemplate(fieldKey);
          let formValue = value;
          
          if (fieldDefinition) {
            // Convert display label back to form value for dropdown fields
            formValue = this.dropdownMappingService.convertLabelToValue(value, fieldDefinition);
          }
          
          control.setValue(formValue || '');
          console.log(`✅ Mapped common_field ${fieldKey}: "${value}" -> "${formValue}"`);
        } else {
          console.log(`⚠️ No form control found for common field: ${fieldKey}`);
        }
      });
    }
    
    // Handle calculated fields - check for fields in data section that match calculated field patterns
    console.log('📝 Step 3: Processing calculated/readonly fields...');
    if (reportData.data && typeof reportData.data === 'object') {
      const calculatedFields = [
        'estimated_value_of_land',
        'total_land_value', 
        'market_value',
        'final_valuation',
        'total_value',
        'calculated_area',
        'total_cost'
      ];
      
      calculatedFields.forEach(fieldName => {
        // Check in nested data structure
        let value = reportData.data[fieldName];
        
        // Also check in common_fields for calculated fields
        if (!value && reportData.common_fields) {
          value = reportData.common_fields[fieldName];
        }
        
        // Also check deep nested in data section
        if (!value) {
          const deepSearch = (obj: any, searchKey: string): any => {
            if (obj && typeof obj === 'object') {
              if (obj[searchKey] !== undefined) {
                return obj[searchKey];
              }
              for (const key in obj) {
                if (typeof obj[key] === 'object') {
                  const found = deepSearch(obj[key], searchKey);
                  if (found !== undefined) return found;
                }
              }
            }
            return undefined;
          };
          value = deepSearch(reportData.data, fieldName);
        }
        
        if (value !== undefined && value !== null && value !== '') {
          const control = this.reportForm.get(fieldName);
          if (control) {
            // Convert display label back to value if needed (for dropdowns)
            const fieldDefinition = this.findFieldInTemplate(fieldName);
            const valueToSet = this.convertStorageLabelToFormValue(value, fieldDefinition);
            
            control.setValue(valueToSet);
            console.log(`✅ Mapped calculated field ${fieldName}: ${valueToSet}`);
          } else {
            console.log(`⚠️ No form control found for calculated field: ${fieldName}`);
          }
        }
      });
    }

    // Handle tables section specifically
    if (reportData.tables && typeof reportData.tables === 'object') {
      console.log('📝 Processing tables section:', reportData.tables);
      Object.keys(reportData.tables).forEach(tableFieldId => {
        const tableData = reportData.tables[tableFieldId];
        console.log(`🔍 Processing table: ${tableFieldId}`, tableData);
        
        // Extract table data from different possible structures
        let tableStructure = null;
        
        // Check if it has original_data (our new format)
        if (tableData.original_data) {
          tableStructure = tableData.original_data;
          console.log(`📊 Found table original_data for: ${tableFieldId}`);
        }
        // Check if it has direct table structure
        else if (tableData.columns || tableData.rows) {
          tableStructure = tableData;
          console.log(`📊 Found direct table structure for: ${tableFieldId}`);
        }
        // Check if it has structure.rows/columns (definition format)
        else if (tableData.structure && (tableData.structure.columns || tableData.structure.rows)) {
          tableStructure = tableData.structure;
          console.log(`📊 Found table structure definition for: ${tableFieldId}`);
        }
        
        if (tableStructure) {
          // Store in dynamicTablesData for the dynamic table component
          this.dynamicTablesData[tableFieldId] = tableStructure;
          console.log(`✅ Loaded table data for dynamic table: ${tableFieldId}`);
        } else {
          console.log(`⚠️ Could not extract table structure from: ${tableFieldId}`, tableData);
        }
      });
    }
    
    // Also check data section for backward compatibility (existing reports)
    if (reportData.data && typeof reportData.data === 'object') {
      console.log('📝 Checking data section for table fields...');
      Object.keys(reportData.data).forEach(fieldKey => {
        const value = reportData.data[fieldKey];
        
        // Check if this looks like table data
        if (this.isTableData(fieldKey, value)) {
          console.log(`📊 Found table in data section: ${fieldKey}`);
          this.dynamicTablesData[fieldKey] = value;
          console.log(`✅ Loaded table data from data section: ${fieldKey}`);
        }
      });
    }
    
    // Handle nested data similar to template loading
    const mapNestedData = (data: any, prefix = '') => {
      Object.keys(data).forEach(key => {
        const value = data[key];
        
        // Skip common_fields and tables as we handled them above
        if (key === 'common_fields' || key === 'tables') {
          return;
        }
        
        // Skip table fields in data section as we handle them above
        if (key === 'data' && this.isTableData(key, value)) {
          return;
        }
        
        if (value && typeof value === 'object' && !Array.isArray(value)) {
          // Skip table-like objects in data section
          if (this.isTableData(key, value)) {
            return;
          }
          // Recursively handle nested objects
          mapNestedData(value, prefix ? `${prefix}_${key}` : key);
        } else {
          // Direct field mapping
          const possibleControlNames = prefix ? 
            [`${prefix}_${key}`, `${key}`, prefix + key, key.toLowerCase()] : 
            [key, key.toLowerCase()];

          // Try to find a matching form control
          for (const controlName of possibleControlNames) {
            const control = this.reportForm.get(controlName);
            if (control) {
              // Find field definition to check if it's a dropdown
              const fieldDefinition = this.findFieldInTemplate(controlName) || this.findFieldInTemplate(key);
              let formValue = value;
              
              if (fieldDefinition) {
                // Convert display label back to form value for dropdown fields
                formValue = this.dropdownMappingService.convertLabelToValue(value, fieldDefinition);
              }
              
              control.setValue(formValue);
              console.log(`✅ Mapped nested ${prefix ? prefix + '.' + key : key} -> ${controlName}: "${value}" -> "${formValue}"`);
              return; // Found and set, move to next
            }
          }
          console.log(`⚠️ No form control found for nested field: ${key} (tried: ${possibleControlNames.join(', ')})`);
        }
      });
    };
    
    mapNestedData(reportData);
  }

  /**
   * Find field definition in template by field ID
   */
  private findFieldInTemplate(fieldId: string): TemplateField | BankSpecificField | null {
    if (!this.templateData?.allFields) {
      return null;
    }

    // Find field in allFields array
    const field = this.templateData.allFields.find((f: TemplateField | BankSpecificField) => f.fieldId === fieldId);
    return field || null;
  }

  /**
   * Convert form data to storage format (convert dropdown values to labels)
   */
  private convertFormDataForStorage(formData: any): any {
    if (!formData || typeof formData !== 'object') {
      return formData;
    }

    const convertedData: any = {};

    Object.keys(formData).forEach(fieldKey => {
      const fieldValue = formData[fieldKey];
      
      // Find field definition
      const fieldDefinition = this.findFieldInTemplate(fieldKey);
      
      if (fieldDefinition) {
        // Convert form value to display label for dropdown fields
        convertedData[fieldKey] = this.dropdownMappingService.convertFormValueToStorageLabel(fieldValue, fieldDefinition);
      } else {
        // Keep original value if no field definition found
        convertedData[fieldKey] = fieldValue;
      }
    });

    // Also include dynamic table data
    Object.keys(this.dynamicTablesData).forEach(tableKey => {
      convertedData[tableKey] = this.dynamicTablesData[tableKey];
    });

    console.log('🔄 Converted form data for storage:', {
      original: Object.keys(formData).length,
      converted: Object.keys(convertedData).length,
      tables: Object.keys(this.dynamicTablesData).length
    });

    return convertedData;
  }

  /**
   * Convert storage label back to form value (reverse of convertFormDataForStorage)
   * When loading data, we need to convert display labels like "Mortgage Loan" back to values like "mortgage_loan"
   */
  private convertStorageLabelToFormValue(storageValue: any, fieldDefinition: any): any {
    // If no field definition or not a dropdown, return as-is
    if (!fieldDefinition || fieldDefinition.fieldType !== 'select' || !fieldDefinition.options) {
      return storageValue;
    }
    
    // If value is empty/null, return as-is
    if (!storageValue) {
      return storageValue;
    }
    
    // Check if storageValue matches a label (display text)
    const matchingOption = fieldDefinition.options.find((opt: any) => 
      opt.label === storageValue || opt.displayLabel === storageValue
    );
    
    if (matchingOption) {
      console.log(`🔄 Converting label "${storageValue}" to value "${matchingOption.value}"`);
      return matchingOption.value;
    }
    
    // If no match found, assume it's already a value
    return storageValue;
  }

  /**
   * Check if field data looks like table data
   */
  private isTableData(fieldKey: string, value: any): boolean {
    // Check field name for table indicators
    const tableIndicators = ['table', 'list', 'items', 'rows', 'entries', 'specifications', 'valuation_table', '_table'];
    const nameIndicatesTable = tableIndicators.some(indicator => fieldKey.toLowerCase().includes(indicator));
    
    if (!nameIndicatesTable) {
      return false;
    }
    
    // Check if value has table-like structure
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      // Check for dynamic table structure (columns, rows, etc.)
      if (value.columns && value.rows) {
        return true;
      }
      // Check for other table metadata
      if (value.userAddedColumns || value.nextColumnNumber) {
        return true;
      }
    }
    
    return false;
  }

  /**
   * Populate form from flat structure (old format)
   */
  private populateFromFlatStructure(reportData: any) {
    console.log('📝 Using flat structure population strategy');
    
    let populatedCount = 0;
    let skippedCount = 0;
    
    // Direct mapping for flat structure
    Object.keys(reportData).forEach(fieldKey => {
      const value = reportData[fieldKey];
      
      // Skip metadata fields that shouldn't be form fields
      const metadataFields = ['status', 'bankName', 'templateName', 'referenceNumber', 'organizationId', 
                             'customTemplateId', 'customTemplateName', 'propertyType', 'reportType', 
                             'createdAt', 'updatedAt'];
      
      if (metadataFields.includes(fieldKey)) {
        console.log(`📋 Skipping metadata field: ${fieldKey}`);
        return;
      }
      
      // Check if this is a table field (has columns and rows structure)
      if (value && typeof value === 'object' && value.columns && value.rows) {
        console.log(`📊 Found table data for field: ${fieldKey}`);
        
        // Find the field definition in template
        let fieldDefinition: any = null;
        if (this.templateData) {
          fieldDefinition = this.templateData.allFields.find((f: any) => f.fieldId === fieldKey);
        }
        
        if (fieldDefinition) {
          if (fieldDefinition.fieldType === 'table') {
            // Static table - update field.rows directly
            fieldDefinition.rows = value.rows;
            
            // Merge columns: keep template's fieldType, isEditable, isReadonly but allow other properties from saved data
            if (value.columns && fieldDefinition.columns) {
              fieldDefinition.columns = fieldDefinition.columns.map((templateCol: any) => {
                const savedCol = value.columns.find((c: any) => c.columnId === templateCol.columnId);
                return {
                  ...templateCol, // Keep template properties (fieldType, isEditable, isReadonly)
                  ...savedCol,    // Override with saved properties if any
                  fieldType: templateCol.fieldType,       // Force template fieldType
                  isEditable: templateCol.isEditable,     // Force template isEditable
                  isReadonly: templateCol.isReadonly      // Force template isReadonly
                };
              });
            }
            
            console.log(`✅ Loaded STATIC table data for ${fieldKey}: ${value.rows.length} rows`);
          } else if (fieldDefinition.fieldType === 'dynamic_table') {
            // Dynamic table - store in dynamicTablesData
            if (!this.dynamicTablesData) {
              this.dynamicTablesData = {};
            }
            this.dynamicTablesData[fieldKey] = {
              columns: value.columns,
              rows: value.rows,
              userAddedColumns: value.userAddedColumns || [],
              nextColumnNumber: value.nextColumnNumber || 1
            };
            console.log(`✅ Loaded DYNAMIC table data for ${fieldKey}: ${value.rows.length} rows`);
          }
        } else {
          // Field not found in template, try storing as dynamic table
          console.log(`⚠️ Field ${fieldKey} not found in template, storing as dynamic table`);
          if (!this.dynamicTablesData) {
            this.dynamicTablesData = {};
          }
          this.dynamicTablesData[fieldKey] = {
            columns: value.columns,
            rows: value.rows,
            userAddedColumns: value.userAddedColumns || [],
            nextColumnNumber: value.nextColumnNumber || 1
          };
        }
        
        populatedCount++;
        return;
      }
      
      // Try multiple possible form control names
      const possibleControlNames = [
        fieldKey,                           // exact match
        fieldKey.toLowerCase(),             // lowercase
        fieldKey.replace(/_/g, ''),        // without underscores
        fieldKey.replace(/[_-]/g, ''),     // without underscores and dashes
      ];
      
      let controlFound = false;
      for (const controlName of possibleControlNames) {
        const control = this.reportForm.get(controlName);
        if (control) {
          // Find field definition to check if it's a dropdown
          const fieldDefinition = this.findFieldInTemplate(controlName) || this.findFieldInTemplate(fieldKey);
          let formValue = value;
          
          if (fieldDefinition) {
            // Convert display label back to form value for dropdown fields
            formValue = this.dropdownMappingService.convertLabelToValue(value, fieldDefinition);
          }
          
          control.setValue(formValue || '');
          console.log(`✅ Mapped flat field ${fieldKey} -> ${controlName}: "${value}" -> "${formValue}"`);
          populatedCount++;
          controlFound = true;
          break;
        }
      }
      
      if (!controlFound) {
        console.log(`⚠️ No form control found for flat field: ${fieldKey} (tried: ${possibleControlNames.join(', ')})`);
        skippedCount++;
      }
    });
    
    console.log(`📊 Flat structure mapping completed: ${populatedCount} populated, ${skippedCount} skipped`);
  }

  // Try to find a working template for the bank
  tryLoadingAvailableTemplate(bankCode: string) {
    console.log('🔍 Trying to find available templates for bank:', bankCode);
    console.log('🔍 Current report data has property_address:', this.pendingReportData?.property_address);
    
    // First try the exact templates that are known to work for SBI based on the create URL
    const commonTemplates = ['land-property', 'LAND', 'residential', 'commercial', 'agricultural'];
    
    let templateIndex = 0;
    
    const tryNextTemplate = () => {
      if (templateIndex >= commonTemplates.length) {
        console.error('❌ No working templates found for bank:', bankCode);
        console.log('🔄 Creating minimal form structure for report viewing...');
        this.createMinimalFormForViewing();
        return;
      }
      
      const templateToTry = commonTemplates[templateIndex];
      console.log(`🔄 Trying template ${templateIndex + 1}/${commonTemplates.length}: ${templateToTry}`);
      
      this.selectedTemplateId = templateToTry;
      
      // Try to load this template
      const templateCode = templateToTry.toLowerCase();
      this.templateService.getAggregatedTemplateFields(bankCode, templateCode)
        .subscribe({
          next: (response) => {
            console.log(`✅ Found working template: ${templateToTry}`);
            console.log('🔍 Template service response:', response);
            console.log('🔍 About to call handleTemplateResponse...');
            // Process the response like in loadTemplateData
            this.handleTemplateResponse(response);
            console.log('🔍 handleTemplateResponse call completed');
          },
          error: (error) => {
            console.log(`❌ Template ${templateToTry} not available:`, error.error?.detail || error.message);
            templateIndex++;
            tryNextTemplate();
          }
        });
    };
    
    tryNextTemplate();
  }

  // Create a minimal form structure when no template is available
  createMinimalFormForViewing() {
    console.log('📝 Creating minimal form structure for report viewing...');
    
    // Create basic form controls based on the report_data structure
    if (this.pendingReportData?.report_data) {
      const formGroup: any = {};
      
      const addControlsFromObject = (obj: any, prefix = '') => {
        Object.keys(obj).forEach(key => {
          const value = obj[key];
          const controlName = prefix ? `${prefix}_${key}` : key;
          
          if (value && typeof value === 'object' && !Array.isArray(value)) {
            addControlsFromObject(value, controlName);
          } else {
            formGroup[controlName] = [value || ''];
            console.log(`➕ Added control: ${controlName} = ${value}`);
          }
        });
      };
      
      addControlsFromObject(this.pendingReportData.report_data);
      
      // Create the form
      this.reportForm = this.fb.group(formGroup);
      
      console.log('📝 Minimal form created with controls:', Object.keys(formGroup));
      
      // Apply view mode and populate data
      this.applyViewModeState();
      this.populateFormWithMinimalStructure(this.pendingReportData);
      
      this.isLoading = false;
      this.cdr.detectChanges();
    }
  }

  // Handle successful template response
  handleTemplateResponse(response: any) {
    console.log('✅ Template response received:', response);
    console.log('🔍 Current pendingReportData status:', !!this.pendingReportData);
    
    // Check if response has the expected template structure
    if (response && response.templateInfo && response.commonFields) {
      try {
        // Process the raw API response into the expected format
        console.log('🔄 Processing template data...');
        this.templateData = this.templateService.processTemplateData(response);
        console.log('📊 Template data structure processed and loaded:', {
          templateInfo: this.templateData?.templateInfo?.templateName,
          commonFieldGroups: this.templateData?.commonFieldGroups?.length,
          bankSpecificTabs: this.templateData?.bankSpecificTabs?.length,
          totalFields: this.templateData?.totalFieldCount
        });
        
        console.log('🏗️ Building form controls with report data...');
        console.log('🏗️ pendingReportData exists:', !!this.pendingReportData);
        if (this.pendingReportData) {
          console.log('🏗️ pendingReportData keys:', Object.keys(this.pendingReportData));
          console.log('🏗️ pendingReportData.report_data exists:', !!this.pendingReportData.report_data);
        }
        this.buildFormControlsWithReportData(this.pendingReportData);
        
        console.log('🔧 Initializing bank specific tabs...');
        this.initializeBankSpecificTabs();
        
        // Force change detection
        this.cdr.detectChanges();
        
        // Now populate with report data if available
        if (this.pendingReportData) {
          console.log('📝 Template loaded, now calling populateFormWithReportData');
          console.log('📝 Form controls exist:', !!this.reportForm);
          console.log('📝 Form controls count:', Object.keys(this.reportForm?.controls || {}).length);
          console.log('📝 About to call populateFormWithReportData with:', this.pendingReportData);
          this.populateFormWithReportData(this.pendingReportData);
          this.pendingReportData = null;
          console.log('✅ populateFormWithReportData call completed, cleared pendingReportData');
        } else {
          console.log('⚠️ WARNING: No pendingReportData available after template load!');
          console.log('📝 Template loaded for new report');
        }
        
        this.isLoading = false;
        console.log('✅ Template processing completed successfully');
      } catch (error) {
        console.error('❌ Error processing template data:', error);
        this.createMinimalFormForViewing();
      }
    } else {
      console.error('❌ Invalid template response format - missing templateInfo or commonFields');
      console.error('Response keys:', Object.keys(response || {}));
      this.createMinimalFormForViewing();
    }
  }

  // Enhanced form population for full template
  populateFormWithFullTemplate(reportData: any) {
    console.log('📝 Populating full template with report data');
    console.log('📝 Available form controls:', Object.keys(this.reportForm.controls));
    console.log('📝 Report data to populate:', reportData.report_data);
    
    if (this.reportForm && reportData.report_data) {
      // First, try to map the nested structure to form controls
      const mapNestedData = (data: any, prefix = '') => {
        Object.keys(data).forEach(key => {
          const value = data[key];
          
          // Try different control name variations
          const possibleControlNames = [
            key,  // direct key
            prefix ? `${prefix}_${key}` : key,  // prefixed
            prefix ? `${prefix}.${key}` : key,  // dot notation
          ];
          
          if (value && typeof value === 'object' && !Array.isArray(value)) {
            // Recurse into nested objects
            mapNestedData(value, key);
          } else {
            // Try to find a matching form control
            for (const controlName of possibleControlNames) {
              const control = this.reportForm.get(controlName);
              if (control) {
                control.setValue(value);
                console.log(`✅ Mapped ${JSON.stringify(data)} -> ${controlName} = ${value}`);
                return; // Found and set, move to next
              }
            }
            console.log(`⚠️ No form control found for: ${key} (tried: ${possibleControlNames.join(', ')})`);
          }
        });
      };
      
      mapNestedData(reportData.report_data);
      
      // Apply appropriate mode
      if (this.isViewMode) {
        this.applyViewModeState();
      }
      
      this.cdr.detectChanges();
    }
  }

  // Populate form with minimal structure when template isn't available
  populateFormWithMinimalStructure(reportData: any) {
    console.log('📝 Populating minimal form structure');
    
    if (this.reportForm && reportData.report_data) {
      const populateFromObject = (obj: any, prefix = '') => {
        Object.keys(obj).forEach(key => {
          const value = obj[key];
          const controlName = prefix ? `${prefix}_${key}` : key;
          
          if (value && typeof value === 'object' && !Array.isArray(value)) {
            populateFromObject(value, controlName);
          } else {
            const control = this.reportForm.get(controlName);
            if (control) {
              control.setValue(value);
              console.log(`✅ Set ${controlName} = ${value}`);
            }
          }
        });
      };
      
      populateFromObject(reportData.report_data);
      this.cdr.detectChanges();
    }
  }

  // Helper methods for minimal form display
  getFormControlsArray(): Array<{key: string, control: any}> {
    if (!this.reportForm) return [];
    
    return Object.keys(this.reportForm.controls).map(key => ({
      key: key,
      control: this.reportForm.controls[key]
    }));
  }

  formatFieldLabel(fieldKey: string): string {
    // Convert field keys like 'property_details_property_type' to 'Property Type'
    return fieldKey
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  /**
   * Organize flat form data into nested structure matching template expectations
   * This converts flat field keys into nested objects based on template structure
   */
  organizeFormDataForTemplate(flatFormData: any): any {
    console.log('🔄 Organizing form data for template structure...');
    console.log('📊 Input flat data keys:', Object.keys(flatFormData));
    
    if (!this.templateData || !this.templateData.bankSpecificTabs) {
      console.log('⚠️ No template data available, keeping flat structure');
      return flatFormData;
    }

    const organizedData: any = {};
    
    // Process bank-specific tabs to create nested structure
    this.templateData.bankSpecificTabs.forEach(tab => {
      console.log(`📁 Processing tab: ${tab.tabId} (${tab.tabName})`);
      
      if (tab.hasSections && tab.sections) {
        // Tab has sections - create nested structure: tab -> section -> fields
        const tabData: any = {};
        
        tab.sections.forEach(section => {
          console.log(`  📂 Processing section: ${section.sectionId} (${section.sectionName})`);
          const sectionData: any = {};
          
          section.fields.forEach(field => {
            const fieldKey = field.fieldId;
            if (flatFormData.hasOwnProperty(fieldKey)) {
              sectionData[fieldKey] = flatFormData[fieldKey];
              console.log(`    ✅ Mapped ${fieldKey} to ${tab.tabId}.${section.sectionId}.${fieldKey}`);
            }
          });
          
          if (Object.keys(sectionData).length > 0) {
            tabData[section.sectionId] = sectionData;
          }
        });
        
        if (Object.keys(tabData).length > 0) {
          organizedData[tab.tabId] = tabData;
        }
      } else {
        // Tab has direct fields - create simple nested structure: tab -> fields
        const tabData: any = {};
        
        tab.fields.forEach(field => {
          const fieldKey = field.fieldId;
          if (flatFormData.hasOwnProperty(fieldKey)) {
            tabData[fieldKey] = flatFormData[fieldKey];
            console.log(`    ✅ Mapped ${fieldKey} to ${tab.tabId}.${fieldKey}`);
          }
        });
        
        if (Object.keys(tabData).length > 0) {
          organizedData[tab.tabId] = tabData;
        }
      }
    });
    
    // Also include common fields at root level
    if (this.templateData.commonFieldGroups) {
      this.templateData.commonFieldGroups.forEach(group => {
        group.fields.forEach(field => {
          const fieldKey = field.fieldId;
          if (flatFormData.hasOwnProperty(fieldKey)) {
            organizedData[fieldKey] = flatFormData[fieldKey];
            console.log(`✅ Mapped common field ${fieldKey} to root level`);
          }
        });
      });
    }
    
    // Include any unmapped fields at root level (for compatibility)
    Object.keys(flatFormData).forEach(key => {
      let isMapped = false;
      
      // Check if already mapped in nested structure
      const checkNested = (obj: any): boolean => {
        for (const [objKey, objValue] of Object.entries(obj)) {
          if (objKey === key) return true;
          if (typeof objValue === 'object' && objValue !== null) {
            if (checkNested(objValue)) return true;
          }
        }
        return false;
      };
      
      if (!checkNested(organizedData) && !organizedData.hasOwnProperty(key)) {
        organizedData[key] = flatFormData[key];
        console.log(`📋 Included unmapped field ${key} at root level`);
      }
    });

    console.log('✅ Organized data structure:', {
      totalTabs: Object.keys(organizedData).filter(key => typeof organizedData[key] === 'object').length,
      totalFields: Object.keys(organizedData).length,
      organizedKeys: Object.keys(organizedData)
    });
    
    return organizedData;
  }

  // Mode switching methods
  switchToEditMode() {
    console.log('✏️ Switching to Edit Mode');
    this.isViewMode = false;
    this.isEditMode = true;
    this.applyEditModeState();
    
    // Update URL to reflect edit mode
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { mode: 'edit' },
      queryParamsHandling: 'merge'
    });
  }

  switchToViewMode() {
    console.log('👁️ Switching to View Mode');
    this.isViewMode = true;
    this.isEditMode = false;
    this.applyViewModeState();
    
    // Update URL to reflect view mode
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { mode: 'view' },
      queryParamsHandling: 'merge'
    });
  }

  applyViewModeState() {
    console.log('🔍 applyViewModeState called:', {
      hasReportForm: !!this.reportForm,
      isViewMode: this.isViewMode,
      formEnabled: this.reportForm?.enabled
    });
    
    if (this.reportForm && this.isViewMode) {
      // Disable all form controls for view mode EXCEPT bank_branch
      Object.keys(this.reportForm.controls).forEach(controlName => {
        const control = this.reportForm.get(controlName);
        if (control && controlName !== 'bank_branch') {
          control.disable();
        } else if (controlName === 'bank_branch') {
          control?.enable();
          console.log('🔓 Keeping bank_branch enabled in view mode');
        }
      });
      console.log('🔒 Form disabled for view mode (except bank_branch)');
      console.log('🔍 Form status after disable:', {
        formEnabled: this.reportForm.enabled,
        controlCount: Object.keys(this.reportForm.controls).length,
        sampleControlsEnabled: Object.keys(this.reportForm.controls).slice(0, 3).map(key => ({
          name: key,
          enabled: this.reportForm.get(key)?.enabled
        }))
      });
    } else if (!this.isViewMode) {
      console.log('📝 Not in view mode, skipping form disable');
    } else if (!this.reportForm) {
      console.log('⚠️ No report form available to disable');
    }
  }

  applyEditModeState() {
    if (this.reportForm && this.isEditMode) {
      // Enable all form controls for edit mode
      this.reportForm.enable();
      console.log('🔓 Form enabled for edit mode');
      
      // Re-apply readonly logic, but allow bank_branch to be editable
      if (this.templateData && this.templateData.allFields) {
        this.templateData.allFields.forEach(field => {
          // Special case: Allow bank_branch to be editable in edit mode even if marked readonly
          const shouldDisableField = field.isReadonly && field.fieldId !== 'bank_branch';
          
          if (shouldDisableField) {
            const control = this.reportForm.get(field.fieldId);
            if (control) {
              control.disable();
              console.log(`🔒 Re-disabled readonly field in edit mode: ${field.fieldId}`);
            }
          }
          
          // Handle readonly sub-fields
          if (field.fieldType === 'group' && field.subFields) {
            field.subFields.forEach(subField => {
              const shouldDisableSubField = subField.isReadonly && subField.fieldId !== 'bank_branch';
              
              if (shouldDisableSubField) {
                const subControl = this.reportForm.get(subField.fieldId);
                if (subControl) {
                  subControl.disable();
                  console.log(`🔒 Re-disabled readonly sub-field in edit mode: ${subField.fieldId}`);
                }
              }
            });
          }
        });
      }
    }
  }

  loadQueryParams() {
    console.log('🔥 Loading query params...');
    
    // Load route parameters (for organization context)
    this.route.params.subscribe(params => {
      this.currentOrgShortName = params['orgShortName'] || '';
      console.log('🏢 Organization context:', this.currentOrgShortName);
    });
    
    // Load query parameters (for report data)
    this.route.queryParams.subscribe(params => {
      console.log('🔥 Raw query params received:', params);
      this.selectedBankCode = params['bankCode'] || '';
      this.selectedBankName = params['bankName'] || this.getBankFullName(this.selectedBankCode);
      this.selectedTemplateId = params['templateId'] || '';
      this.selectedTemplateName = params['templateName'] || '';
      this.selectedPropertyType = params['propertyType'] || '';
      this.customTemplateId = params['customTemplateId'] || '';
      this.customTemplateName = params['customTemplateName'] || '';
      
      // Process PDF fields if available
      if (params['pdfFields']) {
        try {
          this.extractedPdfFields = JSON.parse(params['pdfFields']);
          console.log('� PDF fields loaded from query params:', this.extractedPdfFields);
        } catch (error) {
          console.error('❌ Error parsing PDF fields:', error);
          this.extractedPdfFields = null;
        }
      }
      
      // If no templateId but we have propertyType, derive templateId from propertyType
      if (!this.selectedTemplateId && this.selectedPropertyType) {
        this.selectedTemplateId = this.selectedPropertyType.toLowerCase();
        console.log('📋 Derived templateId from propertyType:', this.selectedTemplateId);
      }

      console.log('🔥 Processed Report Form Params:', {
        bankCode: this.selectedBankCode,
        bankName: this.selectedBankName,
        templateId: this.selectedTemplateId,
        templateName: this.selectedTemplateName,
        propertyType: this.selectedPropertyType,
        customTemplateId: this.customTemplateId,
        customTemplateName: this.customTemplateName,
        orgShortName: this.currentOrgShortName,
        hasPdfFields: !!this.extractedPdfFields
      });

      // Load template data when query params are available
      if (this.selectedBankCode && (this.selectedTemplateId || this.customTemplateId)) {
        // If we have a custom template but no base templateId, we need to determine it
        if (this.customTemplateId && !this.selectedTemplateId && this.selectedPropertyType) {
          console.log('📝 Custom template without base templateId, determining base template...');
          this.selectedTemplateId = this.determineBaseTemplateId(this.selectedPropertyType);
          console.log('📋 Determined base templateId:', this.selectedTemplateId);
        }
        
        if (this.selectedTemplateId) {
          console.log('🔥 Query params loaded, triggering template data load');
          this.loadTemplateData();
          this.loadReferenceNumber();  // NEW: Load reference number
          
          // Load custom template if specified
          if (this.customTemplateId) {
            console.log('📝 Custom template specified, will load after form build');
          }
        } else {
          console.error('❌ Cannot determine base template for custom template');
        }
      } else {
        console.log('⚠️ Missing required parameters for template loading:', {
          bankCode: this.selectedBankCode,
          templateId: this.selectedTemplateId,
          customTemplateId: this.customTemplateId
        });
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
        console.error('❌ Error: No organization context found. Please select an organization first.');
        this.navigateToReportSelection();
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
          console.error(
            '⚠️ Configuration Required: ' +
            'This organization does not have Report Reference Initials configured. ' +
            'Please contact your administrator to set the "Report Reference Initials" field. ' +
            'Redirecting to report selection page.'
          );
          this.navigateToReportSelection();
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
    
    // Add form controls for document types
    if (this.documentTypes && this.documentTypes.length > 0) {
      console.log(`📄 Adding ${this.documentTypes.length} document type controls`);
      this.documentTypes.forEach(docType => {
        const controlName = `doc_${docType.documentId}`;
        // ⚠️ NO VALIDATION - Allow "NA" or empty values
        formControls[controlName] = ['', []];
        console.log(`  ✅ ${controlName}: ${docType.documentName} (no validation)`);
      });
    }
    
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
    
    // Disable readonly fields (except special cases like bank_branch in edit mode)
    this.templateData.allFields.forEach(field => {
      // Special case: Allow bank_branch to be editable even if marked readonly
      const shouldDisableField = field.isReadonly && !(field.fieldId === 'bank_branch' && this.isEditMode);
      
      if (shouldDisableField) {
        const control = this.reportForm.get(field.fieldId);
        if (control) {
          control.disable();
          console.log(`🔒 Disabled readonly field: ${field.fieldId} (${field.uiDisplayName})`);
        }
      } else if (field.fieldId === 'bank_branch' && this.isEditMode) {
        // Ensure bank_branch is enabled in edit mode
        const control = this.reportForm.get(field.fieldId);
        if (control) {
          control.enable();
          console.log(`🔓 Enabled bank_branch field for edit mode`);
        }
      }
      
      // Handle readonly sub-fields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          const shouldDisableSubField = subField.isReadonly && !(subField.fieldId === 'bank_branch' && this.isEditMode);
          
          if (shouldDisableSubField) {
            const subControl = this.reportForm.get(subField.fieldId);
            if (subControl) {
              subControl.disable();
              console.log(`🔒 Disabled readonly sub-field: ${subField.fieldId}`);
            }
          } else if (subField.fieldId === 'bank_branch' && this.isEditMode) {
            // Ensure bank_branch is enabled in edit mode
            const subControl = this.reportForm.get(subField.fieldId);
            if (subControl) {
              subControl.enable();
              console.log(`🔓 Enabled bank_branch sub-field for edit mode`);
            }
          }
        });
      }
    });

    console.log('✅ Form built with controls:', Object.keys(formControls));
    
    // Set reference number if it was already loaded
    this.setReferenceNumberInForm();
    
    // Apply PDF extracted fields if available
    this.applyExtractedPdfFields();
  }

  /**
   * Enhanced form building that combines template data with saved report data
   * This ensures we have form controls for both template fields and any saved data
   */
  buildFormControlsWithReportData(reportData?: any) {
    console.log('🏗️ Building enhanced form controls with report data support');
    
    const formControls: any = {};
    
    // First, build controls from template data if available
    if (this.templateData) {
      console.log('📋 Adding controls from template data...');
      this.templateData.allFields.forEach(field => {
        const validators = this.buildFieldValidators(field);
        const contextData = {
          bankName: this.selectedBankName,
          bankCode: this.selectedBankCode,
          templateName: this.selectedTemplateName
        };
        
        const defaultValue = this.templateService.getFieldDefaultValue(field, contextData);
        formControls[field.fieldId] = [defaultValue, validators];
        console.log(`  ✅ Template: ${field.fieldId} (${field.fieldType}): ${field.uiDisplayName}`);
        
        // Add sub-field controls for group fields
        if (field.fieldType === 'group' && field.subFields) {
          field.subFields.forEach(subField => {
            const subValidators = this.buildFieldValidators(subField);
            const subDefaultValue = this.templateService.getFieldDefaultValue(subField, contextData);
            formControls[subField.fieldId] = [subDefaultValue, subValidators];
            console.log(`      ✅ Sub-field: ${subField.fieldId} (${subField.fieldType}): ${subField.uiDisplayName}`);
          });
        }
      });
    }
    
    // Second, add controls for any saved report data fields that don't exist in template
    if (reportData?.report_data) {
      console.log('💾 Adding controls from saved report data...');
      
      const addControlsForSavedData = (obj: any, prefix = '') => {
        Object.keys(obj).forEach(key => {
          const value = obj[key];
          const controlName = prefix ? `${prefix}_${key}` : key;
          
          // Skip metadata fields
          const metadataFields = ['status', 'bankName', 'templateName', 'referenceNumber', 'organizationId', 
                                 'customTemplateId', 'customTemplateName', 'propertyType', 'reportType', 
                                 'createdAt', 'updatedAt'];
          
          if (metadataFields.includes(controlName)) {
            return;
          }
          
          if (value && typeof value === 'object' && !Array.isArray(value)) {
            // Recursively add controls for nested objects
            addControlsForSavedData(value, controlName);
          } else {
            // Only add control if it doesn't exist from template
            if (!formControls[controlName] && !formControls[key]) {
              formControls[controlName] = [value || ''];
              console.log(`  ➕ Saved data: ${controlName} = ${value}`);
            }
          }
        });
      };
      
      addControlsForSavedData(reportData.report_data);
    }
    
    // Create the form
    this.reportForm = this.fb.group(formControls);
    
    // Initialize calculated fields tracking if template data exists
    if (this.templateData) {
      this.initializeCalculatedFields();
      // TODO: Implement setupCalculationListeners method for calculated fields
      // this.setupCalculationListeners();
    }
    
    // Log summary
    const controlCount = Object.keys(formControls).length;
    console.log(`🎯 Enhanced form building complete: ${controlCount} controls created`);
    
    // Apply view mode disabling - disable all fields if in view mode
    if (this.isViewMode) {
      console.log('👁️ View mode: disabling all form controls');
      console.log('🔍 Form state before disable:', {
        formEnabled: this.reportForm.enabled,
        controlCount: Object.keys(formControls).length
      });
      
      // Disable the entire form
      this.reportForm.disable();
      
      // Also explicitly disable each individual control to be extra sure
      Object.keys(this.reportForm.controls).forEach(controlName => {
        const control = this.reportForm.get(controlName);
        if (control && control.enabled) {
          control.disable();
          console.log(`🔒 Explicitly disabled control: ${controlName}`);
        }
      });
      
      console.log('🔍 Form state after disable:', {
        formEnabled: this.reportForm.enabled,
        sampleControls: Object.keys(this.reportForm.controls).slice(0, 3).map(key => ({
          name: key,
          enabled: this.reportForm.get(key)?.enabled
        }))
      });
    } else {
      // Only apply readonly states in edit mode
      if (this.templateData) {
        this.templateData.allFields.forEach(field => {
          if (field.isReadonly) {
            const control = this.reportForm.get(field.fieldId);
            if (control) {
              control.disable();
              console.log(`🔒 Disabled readonly field: ${field.fieldId}`);
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
      }
    }
    
    // Force change detection
    setTimeout(() => {
      this.cdr.detectChanges();
    }, 0);
    
    // Subscribe to form value changes
    this.reportForm.valueChanges.subscribe(values => {
      this.handleFormValueChanges(values);
    });
    
    // Set reference number if it was already loaded
    this.setReferenceNumberInForm();
    
    // Apply PDF extracted fields if available
    this.applyExtractedPdfFields();
    
    console.log('✅ Enhanced form built with controls:', Object.keys(formControls));
  }

  /**
   * Set the reference number in the form field (called after form is built)
   * NOTE: Reference numbers are now generated server-side only to avoid duplication
   */
  setReferenceNumberInForm() {
    // NO LONGER SETTING REFERENCE NUMBER IN FORM 
    // The backend will generate reference_number automatically
    // This prevents duplicate reference fields in the database
    console.log('📋 Reference number will be generated server-side:', this.reportReferenceNumber);
  }

  /**
   * Apply extracted PDF fields to the form (called after form is built)
   */
  applyExtractedPdfFields() {
    if (this.extractedPdfFields && this.reportForm && Object.keys(this.extractedPdfFields).length > 0) {
      console.log('📄 Applying PDF extracted fields to form:', this.extractedPdfFields);
      
      let appliedCount = 0;
      const availableControls = Object.keys(this.reportForm.controls);
      
      // Match PDF fields to form controls and apply values
      Object.keys(this.extractedPdfFields).forEach(pdfFieldKey => {
        const pdfValue = this.extractedPdfFields![pdfFieldKey];
        let matchingControl: string | undefined;
        
        // Strategy 1: Direct case-insensitive match
        matchingControl = availableControls.find(controlKey => 
          controlKey.toLowerCase() === pdfFieldKey.toLowerCase()
        );
        
        // Strategy 2: Convert camelCase to snake_case and match
        if (!matchingControl) {
          const snakeCaseKey = pdfFieldKey.replace(/([A-Z])/g, '_$1').toLowerCase();
          matchingControl = availableControls.find(controlKey => 
            controlKey.toLowerCase() === snakeCaseKey
          );
          if (matchingControl) {
            console.log(`🔄 Mapped camelCase to snake_case: ${pdfFieldKey} -> ${snakeCaseKey} -> ${matchingControl}`);
          }
        }
        
        // Strategy 3: Remove underscores and match
        if (!matchingControl) {
          const noUnderscoreKey = pdfFieldKey.replace(/_/g, '');
          matchingControl = availableControls.find(controlKey => 
            controlKey.replace(/_/g, '').toLowerCase() === noUnderscoreKey.toLowerCase()
          );
          if (matchingControl) {
            console.log(`🔄 Mapped by removing underscores: ${pdfFieldKey} -> ${matchingControl}`);
          }
        }
        
        if (matchingControl && pdfValue !== null && pdfValue !== undefined && pdfValue !== '') {
          const control = this.reportForm.get(matchingControl);
          if (control && !control.disabled) {
            control.setValue(pdfValue);
            appliedCount++;
            console.log(`📄 Applied PDF field: ${pdfFieldKey} -> ${matchingControl} = "${pdfValue}"`);
          } else {
            console.log(`⚠️ Control ${matchingControl} is disabled, skipping PDF field: ${pdfFieldKey}`);
          }
        } else {
          console.log(`⚠️ No matching form control found for PDF field: ${pdfFieldKey}`);
        }
      });
      
      console.log(`✅ Applied ${appliedCount} of ${Object.keys(this.extractedPdfFields).length} PDF fields to form`);
      
      // Trigger change detection to update UI
      this.cdr.detectChanges();
    } else {
      console.log('ℹ️ No PDF fields to apply:', {
        hasPdfFields: !!this.extractedPdfFields,
        hasForm: !!this.reportForm,
        pdfFieldsCount: this.extractedPdfFields ? Object.keys(this.extractedPdfFields).length : 0
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
    // ⚠️ NO VALIDATION - Allow drafts to be saved with any data
    // Users can enter "NA", leave fields empty, or use very long text
    // Backend draft endpoints handle incomplete data
    return [];
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
    if (!this.selectedBankCode) {
      console.log('⚠️ No bank code selected, skipping branch loading');
      return;
    }

    // Load bank branches dynamically from dedicated API endpoint
    const bankBranchesUrl = `http://localhost:8000/api/banks/${this.selectedBankCode}/branches`;
    console.log('🏦 Loading branches from:', bankBranchesUrl);
    
    this.http.get<any[]>(bankBranchesUrl)
      .subscribe({
        next: (branches) => {
          console.log(`🏦 Loaded ${branches.length} branches for ${this.selectedBankCode}:`, branches);
          
          // Transform branches data for dropdown
          this.availableBranches = branches
            .filter((branch: any) => branch.isActive !== false) // Include branches that don't have isActive or are true
            .map((branch: any) => ({
              value: branch.branchId || branch.branchCode,
              label: `${branch.branchName}${branch.branchAddress?.city ? ' - ' + branch.branchAddress.city : ''}`,
              ifscCode: branch.ifscCode,
              address: branch.branchAddress
            }));
            
          console.log(`✅ Processed ${this.availableBranches.length} active branches for dropdown`);
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
    const commonGroups = this.getCommonFieldGroups();
    console.log('🔍 hasCommonFields():', {
      hasFields,
      commonFieldGroups: commonGroups.length,
      templateData: !!this.templateData,
      firstGroup: commonGroups.length > 0 ? {
        name: commonGroups[0].groupName,
        displayName: commonGroups[0].displayName,
        fieldsCount: commonGroups[0].fields.length,
        firstField: commonGroups[0].fields[0] ? {
          fieldId: commonGroups[0].fields[0].fieldId,
          fieldType: commonGroups[0].fields[0].fieldType,
          uiDisplayName: commonGroups[0].fields[0].uiDisplayName
        } : null
      } : null
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

  // Legacy onSubmit method for form submission - will be replaced by workflow methods
  onSubmit() {
    // ⚠️ NO VALIDATION - Allow draft submissions with incomplete data
    console.log('Submit - Form Values:', this.reportForm.value);
    // TODO: Implement submit functionality
  }

  /**
   * Helper method to get current organization context for navigation
   */
  private getCurrentOrgContext(): string {
    if (this.currentOrgShortName) {
      return this.currentOrgShortName;
    }
    
    // Fallback: try to extract from current URL or use system-administration as default
    const urlSegments = this.router.url.split('/');
    const orgIndex = urlSegments.findIndex(segment => segment === 'org');
    return orgIndex >= 0 && orgIndex + 1 < urlSegments.length 
      ? urlSegments[orgIndex + 1] 
      : 'system-administration';
  }

  /**
   * Navigate to the new report selection page within current organization context
   */
  private navigateToReportSelection() {
    const orgShortName = this.getCurrentOrgContext();
    this.router.navigate(['/org', orgShortName, 'reports', 'new']);
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
      
      // Handle calculated fields with formulas (deferred to avoid ExpressionChangedAfterItHasBeenCheckedError)
      if (field.formula) {
        setTimeout(() => this.updateCalculatedField(field), 0);
      }
      
      // Handle sub-fields for group fields
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          this.updateFieldConditionalState(subField, formValues);
          
          // Handle calculated sub-fields (deferred)
          if (subField.formula) {
            setTimeout(() => this.updateCalculatedField(subField), 0);
          }
        });
      }
    });
  }

  /**
   * Update calculated field value based on formula
   */
  private updateCalculatedField(field: any): void {
    const control = this.reportForm?.get(field.fieldId);
    if (!control) {
      return;
    }

    // Calculate new value
    const calculatedValue = this.getCalculatedValue(field);
    
    // Get current value (works even if control is disabled)
    const currentValue = control.value;
    
    // Only update if value changed to avoid infinite loops
    if (currentValue !== calculatedValue) {
      // Use patchValue instead of setValue to avoid triggering validation
      // and set emitEvent to false to prevent circular updates
      if (control.disabled) {
        // For disabled controls, we need to enable temporarily
        control.enable({ emitEvent: false });
        control.patchValue(calculatedValue, { emitEvent: false, onlySelf: true });
        control.disable({ emitEvent: false });
      } else {
        control.patchValue(calculatedValue, { emitEvent: false, onlySelf: true });
      }
      
      console.log(`📊 Calculated field '${field.fieldId}' updated:`, calculatedValue);
    }
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
    // In view mode, ALL fields should be disabled
    if (this.isViewMode) {
      return true;
    }
    
    // Formula fields should always be disabled (readonly)
    if (field.formula || field.isReadonly) {
      return true;
    }
    
    // In edit mode, check if field has conditional logic that makes it disabled
    if (!field.conditionalLogic) {
      return false;
    }
    
    // If conditional logic evaluates to false, disable the field
    return !this.evaluateConditionalLogic(field.conditionalLogic);
  }

  /**
   * Extract field dependencies from formula string
   */
  private extractFormulaDependencies(formula: string): string[] {
    // Extract all field IDs (alphanumeric + underscore) from formula
    const matches = formula.match(/[a-zA-Z_][a-zA-Z0-9_]*/g) || [];
    // Filter out JavaScript keywords and operators
    const jsKeywords = ['return', 'function', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'true', 'false', 'null', 'undefined'];
    return matches.filter(match => !jsKeywords.includes(match));
  }

  /**
   * Get calculated value for calculated fields with enhanced logic
   */
  getCalculatedValue(field: any): string {
    if (!field.formula) return '';
    
    try {
      const formula = field.formula;
      const formControls = this.reportForm?.controls;
      
      if (!formControls) {
        console.warn('No form controls available for calculation');
        return '';
      }
      
      // Extract dependencies from formula
      const dependencies = this.extractFormulaDependencies(formula);
      
      console.log(`🧮 Calculating field '${field.fieldId}' with formula: ${formula}`);
      console.log(`🧮 Dependencies:`, dependencies);
      
      // Get values for all dependencies
      const values: { [key: string]: any } = {};
      const hasValue: { [key: string]: boolean } = {};
      let filledCount = 0;
      let totalDependencies = dependencies.length;
      
      dependencies.forEach(fieldId => {
        const control = formControls[fieldId];
        const rawValue = control ? control.value : null;
        
        // Check if field has a value (not empty, not null, not undefined)
        hasValue[fieldId] = rawValue !== null && rawValue !== '' && rawValue !== undefined;
        
        if (hasValue[fieldId]) {
          values[fieldId] = parseFloat(rawValue) || 0;
          filledCount++;
        } else {
          values[fieldId] = 0;
        }
        
        console.log(`  📊 ${fieldId}: raw=${rawValue}, parsed=${values[fieldId]}, hasValue=${hasValue[fieldId]}`);
      });
      
      console.log(`  📊 Filled count: ${filledCount}/${totalDependencies}`);
      
      // Apply default logic:
      // - If no values filled → return 0
      // - If some values filled → use 1 for empty fields
      // - If all values filled → use actual formula
      let calculationFormula = formula;
      
      if (filledCount === 0) {
        // No values filled - return 0
        console.log(`  ✅ No values filled, returning 0`);
        return '0';
      } else if (filledCount < totalDependencies) {
        // Partial values - replace empty fields with 1, filled fields with actual values
        dependencies.forEach(fieldId => {
          const value = hasValue[fieldId] ? values[fieldId] : 1;
          calculationFormula = calculationFormula.replace(new RegExp(`\\b${fieldId}\\b`, 'g'), value.toString());
        });
        console.log(`  ✅ Partial values, using formula with defaults: ${calculationFormula}`);
      } else {
        // All values filled - use actual values
        dependencies.forEach(fieldId => {
          calculationFormula = calculationFormula.replace(new RegExp(`\\b${fieldId}\\b`, 'g'), values[fieldId].toString());
        });
        console.log(`  ✅ All values filled, using formula: ${calculationFormula}`);
      }
      
      // Evaluate the formula
      // Note: Using Function() for evaluation - in production consider using a safer expression parser
      const result = Function('"use strict"; return (' + calculationFormula + ')')();
      
      console.log(`  ✅ Result: ${result}`);
      
      // Handle special cases
      if (!isFinite(result)) {
        // Division by zero or other infinity
        console.warn('Formula resulted in infinity or NaN:', field.formula);
        return '0';
      }
      
      if (isNaN(result)) {
        return '';
      }
      
      // Round to 2 decimal places for currency fields
      if (field.fieldType === 'currency' || field.displayFormat === 'currency') {
        return result.toFixed(2);
      }
      
      return result.toString();
    } catch (error) {
      console.warn('Error calculating formula:', field.formula, error);
      return '';
    }
  }

  /**
   * Debug: Log subField properties (temporary for debugging)
   */
  debugSubField(subField: any): void {
    if (subField.fieldType === 'currency') {
      console.log('🔍 Currency SubField Debug:', {
        fieldId: subField.fieldId,
        uiDisplayName: subField.uiDisplayName,
        fieldType: subField.fieldType,
        formula: subField.formula,
        hasFormula: !!subField.formula,
        allProperties: Object.keys(subField)
      });
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
   * Load custom template data and auto-apply with fill_empty strategy
   * Since user already selected to use custom template, we default to fill empty fields
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
        
        // Auto-apply with fill_empty strategy (requirement 2)
        // Since user already selected to use custom template, we automatically fill empty fields
        console.log('🎯 Auto-applying custom template with fill_empty strategy (user already chose to use template)');
        
        // Get current form values
        const currentValues = this.reportForm.value;
        
        // Apply template values with fill_empty strategy
        const mergedValues = this.customTemplateService.applyTemplateToFormData(
          currentValues,
          this.customTemplateValues,
          'fill_empty'
        );

        // Update form with merged values
        this.reportForm.patchValue(mergedValues);
        
        console.log('✅ Form auto-filled with custom template values (empty fields only)');
        this.cdr.detectChanges();
        
        // Template applied silently - no popup needed since user already selected to use it
      },
      error: (error) => {
        console.error('❌ Failed to load custom template:', error);
        console.log('⚠️ Failed to load custom template. Proceeding with empty form.');
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
    
    // Log success message
    const message = choice.strategy === 'fill_empty'
      ? 'Empty fields have been filled with template values'
      : 'All fields have been replaced with template values';
    
    console.log('✅', message);
  }

  /**
   * Handle Save as Template button click
   * Opens the save template dialog and handles the save operation
   */


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
    console.log('🧮 Total allFields:', this.templateData.allFields.length);

    // Find all fields with formulas and set them as readonly
    const formulaFields: any[] = [];
    
    this.templateData.allFields.forEach(field => {
      // Log all group fields to see their structure
      if (field.fieldType === 'group') {
        console.log(`🔍 Group field: ${field.fieldId}`, {
          hasSubFields: !!field.subFields,
          subFieldsCount: field.subFields?.length || 0,
          subFields: field.subFields?.map(sf => ({
            fieldId: sf.fieldId,
            fieldType: sf.fieldType,
            hasFormula: !!sf.formula,
            formula: sf.formula
          }))
        });
      }
      
      if (field.formula) {
        formulaFields.push(field);
        console.log(`✅ Top-level formula field: ${field.fieldId}`);
        
        // Set field as readonly
        const control = this.reportForm.get(field.fieldId);
        if (control) {
          control.disable({ emitEvent: false });
        }
      }
      
      // Check subFields in groups
      if (field.fieldType === 'group' && field.subFields) {
        field.subFields.forEach(subField => {
          if (subField.formula) {
            formulaFields.push(subField);
            console.log(`✅ SubField formula field: ${subField.fieldId} (formula: ${subField.formula})`);
            
            // Set field as readonly
            const control = this.reportForm.get(subField.fieldId);
            if (control) {
              control.disable({ emitEvent: false });
            }
          }
        });
      }
    });

    console.log(`🧮 Found ${formulaFields.length} formula-based calculated fields:`, 
      formulaFields.map(f => ({ id: f.fieldId, formula: f.formula }))
    );

    // Extract all calculated fields from template data (old calculation service)
    this.calculatedFieldsMap = this.calculationService.getCalculatedFields(this.templateData.allFields);
    
    console.log(`🧮 Found ${this.calculatedFieldsMap.size} calculation service fields:`, 
      Array.from(this.calculatedFieldsMap.keys())
    );

    // Set up listeners for each calculated field (old system)
    this.calculatedFieldsMap.forEach((config, fieldId) => {
      this.setupCalculatedFieldListener(fieldId, config);
    });

    // Perform initial calculation for all calculated fields
    this.recalculateAllFields();
    
    // Perform initial calculation for formula fields
    formulaFields.forEach(field => {
      this.updateCalculatedField(field);
    });
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
      
      // Format currency fields with ₹ symbol and proper formatting
      let displayValue: string | number = calculatedValue;
      if (config.outputFormat === 'currency' || fieldId.toLowerCase().includes('value') || fieldId.toLowerCase().includes('amount')) {
        displayValue = this.calculationService.formatCurrency(calculatedValue);
      }
      
      control.setValue(displayValue, { emitEvent: false });
      
      if (wasDisabled) {
        control.disable({ emitEvent: false });
      }

      console.log(`🧮 Calculated ${fieldId} = ${displayValue} (raw: ${calculatedValue})`);
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

  // ================================
  // NEW WORKFLOW ACTIONS
  // ================================

  /**
   * Cancel - Discard changes and go back
   */
  onCancel(): void {
    console.log('❌ Cancel clicked - discarding changes');
    
    // For better UX, directly navigate back - user can use browser back if they want to stay
    console.log('🔙 Navigating back to selection page');
    this.goBackToSelection();
  }

  /**
   * Save Draft - Save without validation (optional step)
   */
  onSaveDraft(): void {
    console.log('💾 Save Draft clicked');
    
    if (this.isLoading) {
      console.log('⚠️ Already processing, ignoring save draft request');
      return;
    }

    this.isLoading = true;
    
    // Get form data without validation - accept any data
    const rawFormData = this.reportForm.getRawValue();
    console.log('💾 Raw form data for draft:', rawFormData);
    
    // Convert dropdown values to display labels
    const processedFormData = this.convertFormDataForStorage(rawFormData);
    
    // Format table data for storage (both dynamic and static tables)
    const formattedTableData: any = {};
    
    // 1. Extract dynamic table data
    if (this.dynamicTablesData) {
      Object.keys(this.dynamicTablesData).forEach(fieldId => {
        const tableData = this.dynamicTablesData[fieldId];
        formattedTableData[fieldId] = {
          columns: tableData.columns,
          rows: tableData.rows
        };
        console.log(`📊 Formatted DYNAMIC table data for ${fieldId}:`, formattedTableData[fieldId]);
      });
    }
    
    // 2. Extract static table data from template fields
    if (this.templateData && this.templateData.allFields) {
      this.templateData.allFields.forEach((field: any) => {
        if (field.fieldType === 'table' && field.rows && field.rows.length > 0) {
          formattedTableData[field.fieldId] = {
            columns: field.columns,
            rows: field.rows
          };
          console.log(`📊 Formatted STATIC table data for ${field.fieldId}:`, formattedTableData[field.fieldId]);
        }
      });
    }
    
    // Merge formatted table data with form data
    const completeFormData = {
      ...processedFormData,
      ...formattedTableData
    };
    
    console.log('📊 Complete form data (with tables):', completeFormData);
    
    // Prepare formData with raw values + table data (single source of truth)
    const formDataWithTables = {
      ...rawFormData,
      ...formattedTableData
    };
    
    // Prepare draft payload for backend
    const draftPayload = {
      bankCode: this.selectedBankCode || '',
      bank_code: this.selectedBankCode || '',
      propertyType: this.selectedPropertyType || '',
      property_type: this.selectedPropertyType || '',
      applicantName: completeFormData['applicant_name'] || completeFormData['Applicant Name'] || '',
      applicant_name: completeFormData['applicant_name'] || completeFormData['Applicant Name'] || '',
      templateId: this.selectedTemplateId || this.customTemplateId || '',
      template_id: this.selectedTemplateId || this.customTemplateId || '',
      reportData: completeFormData,  // Keep for backward compatibility
      report_data: completeFormData,
      formData: formDataWithTables,  // Single source of truth with raw form values + tables
      form_data: formDataWithTables
    };

    console.log('📤 Draft payload:', draftPayload);
    
    // Use ReportsService to save/update draft
    if (this.currentReportId) {
      // UPDATE existing draft
      console.log('🔄 Updating existing draft:', this.currentReportId);
      this.reportsService.updateDraft(this.currentReportId, draftPayload).subscribe({
        next: (response) => {
          console.log('✅ Draft updated successfully:', response);
          this.isLoading = false;
          this.reportStatus = 'draft';
          
          if (response.success) {
            this.notificationService.success(`Draft updated successfully!`);
          }
        },
        error: (error) => {
          console.error('❌ Error updating draft:', error);
          this.isLoading = false;
          this.notificationService.error('Failed to update draft. Please try again.');
        }
      });
    } else {
      // CREATE new draft
      console.log('🆕 Creating new draft');
      this.reportsService.saveDraft(draftPayload).subscribe({
        next: (response) => {
          console.log('✅ Draft saved successfully:', response);
          this.isLoading = false;
          this.reportStatus = 'draft';
          
          // Store report ID for future updates
          if (response.success && response.data && response.data.report_id) {
            this.currentReportId = response.data.report_id;
            console.log('📋 Report ID stored:', this.currentReportId);
          }
          
          this.notificationService.success(`Draft saved successfully! Report ID: ${this.currentReportId}`);
        },
        error: (error) => {
          console.error('❌ Error saving draft:', error);
          this.isLoading = false;
          this.notificationService.error('Failed to save draft. Please try again.');
        }
      });
    }
  }
    
  onSaveReport(): void {
    console.log('💾 Save Report clicked');
    
    if (this.isLoading) {
      console.log('⚠️ Already processing, ignoring save report request');
      return;
    }

    // ⚠️ NO VALIDATION - Allow saving incomplete drafts
    // Users can save with empty fields, "NA" text, or any data

    this.isLoading = true;
    
    // Get form data and convert dropdown values to display labels
    const rawFormData = this.reportForm.value;
    const processedFormData = this.convertFormDataForStorage(rawFormData);
    
    // Format table data for storage (both dynamic and static tables)
    const formattedTableData: any = {};
    
    // 1. Extract dynamic table data
    if (this.dynamicTablesData) {
      Object.keys(this.dynamicTablesData).forEach(fieldId => {
        const tableData = this.dynamicTablesData[fieldId];
        formattedTableData[fieldId] = {
          columns: tableData.columns,
          rows: tableData.rows
        };
      });
    }
    
    // 2. Extract static table data from template fields
    if (this.templateData && this.templateData.allFields) {
      this.templateData.allFields.forEach((field: any) => {
        if (field.fieldType === 'table' && field.rows && field.rows.length > 0) {
          formattedTableData[field.fieldId] = {
            columns: field.columns,
            rows: field.rows
          };
        }
      });
    }
    
    // Prepare formData with raw values + table data
    const formDataWithTables = {
      ...rawFormData,
      ...formattedTableData
    };
    
    const reportData = {
      ...processedFormData,
      ...formattedTableData,
      bankCode: this.selectedBankCode,
      bankName: this.selectedBankName,
      templateId: this.selectedTemplateId,
      templateName: this.selectedTemplateName,
      propertyType: this.selectedPropertyType,
      customTemplateId: this.customTemplateId,
      customTemplateName: this.customTemplateName,
      referenceNumber: this.reportReferenceNumber,
      status: 'saved',
      organizationId: this.currentOrgShortName,
      validatedAt: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    console.log('💾 Saving validated report data:', reportData);

    // Call API to save report with validation status
    const token = this.authService.getToken();
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    
    if (this.currentReportId) {
      // UPDATE existing report with saved status
      console.log('📝 Updating existing report with saved status:', this.currentReportId);
      
      // Get current org short name
      const orgShortName = this.route.snapshot.paramMap.get('orgShortName') || 'system-administration';
      
      const updateRequest = {
        report_data: reportData,
        form_data: formDataWithTables,  // Include formData with tables
        status: 'saved'
      };
      
      const updateUrl = `http://localhost:8000/api/org/${orgShortName}/reports/draft/${this.currentReportId}`;
      console.log('📝 Update URL:', updateUrl);
      
      this.http.put<any>(updateUrl, updateRequest, { headers }).subscribe({
        next: (response) => {
          console.log('✅ Report saved successfully:', response);
          this.reportStatus = 'saved';
          this.isLoading = false;
          
          // Show success notification
          this.notificationService.success(`Report saved successfully! Report ID: ${this.currentReportId}`);
          
          // Don't reload - just update the status
          console.log('✅ Report saved, staying on current page');
        },
        error: (error) => {
          console.error('❌ Error saving report:', error);
          this.isLoading = false;
          
          let errorMessage = 'Failed to save report. Please try again.';
          if (error.error?.detail) {
            errorMessage += `\nError: ${error.error.detail}`;
          }
          
          this.notificationService.error(errorMessage);
        }
      });
    } else {
      // CREATE new report with saved status
      console.log('🆕 Creating new report with saved status');
      
      // Get current org short name
      const orgShortName = this.route.snapshot.paramMap.get('orgShortName') || 'system-administration';
      
      const createRequest = {
        bank_code: this.selectedBankCode,
        template_id: this.selectedTemplateId || this.customTemplateId || '',
        property_address: reportData.property_address || 'Property Address TBD',
        report_data: reportData
      };
      
      const createUrl = `http://localhost:8000/api/org/${orgShortName}/reports`;
      console.log('📝 Create URL:', createUrl);
      
      this.http.post<any>(createUrl, createRequest, { headers }).subscribe({
        next: (response) => {
          console.log('✅ Report created and saved successfully:', response);
          this.reportStatus = 'saved';
          this.isLoading = false;
          
          // Store report ID for future updates
          if (response.success && response.data && response.data.report_id) {
            this.currentReportId = response.data.report_id;
            console.log('📋 Report ID stored:', this.currentReportId);
            
            if (response.data.reference_number) {
              this.reportReferenceNumber = response.data.reference_number;
              console.log('📋 Reference number updated:', this.reportReferenceNumber);
            }
          }
          
          // Show success notification
          this.notificationService.success(`Report saved successfully! Report ID: ${this.currentReportId}`);
          
          // Refresh form data to prevent blank form after save
          this.refreshFormDataAfterSave();
        },
        error: (error) => {
          console.error('❌ Error creating report:', error);
          this.isLoading = false;
          
          let errorMessage = 'Failed to create report. Please try again.';
          if (error.error?.detail) {
            errorMessage += `\nError: ${error.error.detail}`;
          }
          
          this.notificationService.error(errorMessage);
        }
      });
    }
  }

  /**
   * Submit Report - Manager only action (requires saved report)
   */
  onSubmitReport(): void {
    console.log('🚀 Submit Report clicked');
    
    if (this.isLoading) {
      console.log('⚠️ Already processing, ignoring submit request');
      return;
    }

    if (!this.isManager()) {
      console.log('❌ Only managers can submit reports');
      // Show error notification (will be implemented with notification service)
      return;
    }

    if (this.reportStatus !== 'saved') {
      console.log('❌ Report must be saved and validated before submission');
      // Show error notification (will be implemented with notification service)
      return;
    }

    // For now, proceed without confirmation dialog - will be replaced with better UX
    console.log('🚀 Proceeding with report submission...');

    this.isLoading = true;
    
    console.log('🚀 Submitting report for final approval...');

    // Call API to submit report
    const token = this.authService.getToken();
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    
    if (!this.currentReportId) {
      console.error('❌ No report ID available for submission');
      this.notificationService.error('Report ID is required for submission');
      this.isLoading = false;
      return;
    }
    
    // Get current org short name
    const orgShortName = this.route.snapshot.paramMap.get('orgShortName') || 'system-administration';
    const submitUrl = `http://localhost:8000/api/org/${orgShortName}/reports/${this.currentReportId}/submit`;
    console.log('📝 Submit URL:', submitUrl);
    
    this.http.post<any>(submitUrl, {}, { headers }).subscribe({
      next: (response) => {
        console.log('✅ Report submitted successfully:', response);
        this.reportStatus = 'submitted';
        this.isLoading = false;
        
        // Show success notification
        this.notificationService.success(`Report submitted successfully! Report ID: ${this.currentReportId}`);
        
        // Refresh form data to prevent blank form after submit
        this.refreshFormDataAfterSave();
        
        // Optionally redirect to reports list after submission
        // this.router.navigate(['/org', this.currentOrgShortName, 'reports']);
      },
      error: (error) => {
        console.error('❌ Error submitting report:', error);
        this.isLoading = false;
        
        let errorMessage = 'Failed to submit report. Please try again.';
        if (error.error?.detail) {
          errorMessage += `\nError: ${error.error.detail}`;
        }
        
        this.notificationService.error(errorMessage);
      }
    });
  }

  /**
   * Mark all form fields as touched to show validation errors
   */
  private markAllFieldsAsTouched(): void {
    Object.keys(this.reportForm.controls).forEach(key => {
      const control = this.reportForm.get(key);
      if (control) {
        control.markAsTouched();
      }
    });
  }

  /**
   * Derive bank code from form data when not available from report metadata
   */
  private deriveBankCodeFromFormData(formData: any): string {
    // Check bank branch field to determine bank code
    const bankBranch = formData['bank_branch'] || '';
    
    if (bankBranch.includes('sbi_')) {
      return 'SBI';
    } else if (bankBranch.includes('hdfc_')) {
      return 'HDFC';
    } else if (bankBranch.includes('icici_')) {
      return 'ICICI';
    } else if (bankBranch.includes('axis_')) {
      return 'AXIS';
    } else if (bankBranch.includes('pnb_')) {
      return 'PNB';
    }
    
    // Check reference number pattern
    const refNumber = formData['report_reference_number'] || '';
    if (refNumber.startsWith('CEV')) {
      return 'SBI'; // Common pattern for SBI reports
    }
    
    // Default fallback
    return 'SBI';
  }

  /**
   * Derive bank name from form data when not available from report metadata
   */
  private deriveBankNameFromFormData(formData: any): string {
    const bankCode = this.deriveBankCodeFromFormData(formData);
    
    switch (bankCode) {
      case 'SBI': return 'State Bank of India';
      case 'HDFC': return 'HDFC Bank';
      case 'ICICI': return 'ICICI Bank';
      case 'AXIS': return 'Axis Bank';
      case 'PNB': return 'Punjab National Bank';
      default: return 'State Bank of India';
    }
  }

  /**
   * Derive template name from form data when not available from report metadata
   */
  private deriveTemplateNameFromFormData(formData: any): string {
    const bankCode = this.deriveBankCodeFromFormData(formData);
    
    // Check if building exists to determine template type
    const buildingConstructed = formData['building_constructed'] || '';
    if (buildingConstructed === 'yes') {
      return `${bankCode} Property & Building Valuation`;
    } else {
      return `${bankCode} Land Property Valuation`;
    }
  }

  /**
   * Derive template ID from form data when not available from report metadata
   */
  private deriveTemplateIdFromFormData(formData: any): string {
    const bankCode = this.deriveBankCodeFromFormData(formData);
    
    // Strategy 1: Check for specific property type fields
    const buildingConstructed = formData['building_constructed'] || '';
    const propertyType = formData['property_type'] || formData['propertyType'] || '';
    
    // Strategy 2: Use bank code to construct template ID pattern
    if (bankCode) {
      if (buildingConstructed === 'yes' || propertyType.toLowerCase().includes('apartment') || propertyType.toLowerCase().includes('building')) {
        return `${bankCode.toLowerCase()}-apartment`;
      } else {
        return `${bankCode.toLowerCase()}-land-property`;
      }
    }
    
    // Strategy 3: Fallback based on reference number pattern (CEV suggests SBI)
    const referenceNumber = formData['reference_number'] || this.reportReferenceNumber || '';
    if (referenceNumber.includes('CEV')) {
      return 'sbi-land-property'; // Default to land property for SBI
    }
    
    // Strategy 4: Safe fallback
    console.warn('🔄 Could not derive template ID, using safe fallback');
    return 'sbi-land-property';
  }

  /**
   * Refresh form data after successful save operations to prevent blank form
   */
  private refreshFormDataAfterSave(): void {
    if (!this.currentReportId) {
      console.log('🔄 No current report ID, skipping refresh');
      return;
    }
    
    console.log('🔄 Refreshing form data after save for report:', this.currentReportId);
    
    // Reload the report data from backend to refresh the form
    this.reportsService.getReportById(this.currentReportId).subscribe({
      next: (reportData) => {
        console.log('✅ Form data refreshed successfully:', reportData);
        if (reportData && reportData.report_data) {
          // Repopulate the form with fresh data from backend
          this.populateFormWithReportData(reportData);
          console.log('📝 Form repopulated with fresh data');
        }
      },
      error: (error) => {
        console.error('❌ Error refreshing form data:', error);
        // Don't show error to user as save was successful, just log it
      }
    });
  }

  /**
   * Go back to reports page
   */
  goBackToReports(): void {
    console.log('🔙 Navigating back to reports page');
    this.router.navigate(['/org', this.currentOrgShortName, 'reports']);
  }

  /**
   * Go back to report selection (legacy method - kept for compatibility)
   */
  goBackToSelection(): void {
    console.log('🔙 Navigating back to report selection');
    this.router.navigate(['/org', this.currentOrgShortName, 'reports', 'new']);
  }

  /**
   * Gets the full bank name from bank code
   */
  getBankFullName(bankCode: string): string {
    const bankNameMap: { [key: string]: string } = {
      'SBI': 'State Bank of India',
      'HDFC': 'HDFC Bank',
      'ICICI': 'ICICI Bank',
      'BOI': 'Bank of India',
      'PNB': 'Punjab National Bank',
      'BOB': 'Bank of Baroda',
      'UBI': 'Union Bank of India',
      'UCO': 'UCO Bank',
      'CBI': 'Central Bank of India'
    };
    return bankNameMap[bankCode] || bankCode;
  }

  /**
   * Gets the formatted template display name
   */
  getFormattedTemplateName(): string {
    if (!this.selectedBankCode && !this.selectedTemplateName) {
      return 'Property Valuation Report';
    }

    const bankFullName = this.getBankFullName(this.selectedBankCode);
    
    if (this.selectedTemplateName) {
      return `${bankFullName} - ${this.selectedTemplateName}`;
    }
    
    // Fallback: construct from property type if available
    if (this.selectedPropertyType) {
      const propertyTypeFormatted = this.selectedPropertyType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      return `${bankFullName} - ${propertyTypeFormatted} Property Valuation`;
    }
    
    return `${bankFullName} - Property Valuation`;
  }

  /**
   * Generate PDF report
   */
  async generatePDF(): Promise<void> {
    if (!this.reportId) {
      this.notificationService.error('No report selected for PDF generation');
      return;
    }

    this.isGeneratingPdf = true;

    try {
      // Prepare report data
      const reportData = {
        reportId: this.reportId,
        bankCode: this.selectedBankCode,
        propertyType: this.selectedPropertyType,
        templateData: this.templateData,
        formValues: this.reportForm.value,
        reportReferenceNumber: this.reportReferenceNumber,
        organizationShortName: this.currentOrgShortName
      };

      // Call the backend PDF generation endpoint
      const response = await this.http.post(`/api/reports/${this.reportId}/generate-pdf`, reportData, {
        responseType: 'blob'
      }).toPromise();

      if (!response) {
        throw new Error('No response received from PDF generation service');
      }

      // Create download link
      const blob = new Blob([response], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename
      const bankName = this.getBankFullName(this.selectedBankCode).replace(/\s+/g, '_');
      const propertyType = this.selectedPropertyType?.replace('_', ' ').replace(/\s+/g, '_') || 'Property';
      const refNumber = this.reportReferenceNumber || 'Report';
      const timestamp = new Date().toISOString().split('T')[0];
      
      link.download = `${bankName}_${propertyType}_Valuation_${refNumber}_${timestamp}.pdf`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      this.notificationService.success('PDF report generated successfully');
    } catch (error) {
      console.error('Error generating PDF:', error);
      this.notificationService.error('Failed to generate PDF report. Please try again.');
    } finally {
      this.isGeneratingPdf = false;
    }
  }

}

