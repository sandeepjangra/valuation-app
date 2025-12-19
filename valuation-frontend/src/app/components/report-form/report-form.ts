import { Component, OnInit, ChangeDetectorRef, inject, computed, ViewChild } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonField, BankBranch, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField, BankSpecificTab, BankSpecificSection, CalculatedFieldConfig } from '../../models';
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
  availableBranches: Array<{value: string, label: string}> = [];
  isLoading = false;
  
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
          
          // Process the response into organized field groups
          this.templateData = this.templateService.processTemplateData(response);
          
          console.log('🏗️ Processed template data:', {
            commonFieldGroups: this.templateData.commonFieldGroups.length,
            bankSpecificTabs: this.templateData.bankSpecificTabs.length,
            totalFields: this.templateData.totalFieldCount,
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
          this.selectedBankCode = reportData.bank_code || '';
          this.selectedTemplateId = reportData.template_id || '';
          this.selectedPropertyType = reportData.property_type || '';
          this.reportReferenceNumber = reportData.reference_number || '';
          
          // Set report status (map to form status values)
          this.reportStatus = reportData.status === 'in_progress' ? 'draft' : 
                             reportData.status === 'completed' ? 'saved' : 
                             reportData.status || 'draft';
          
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
            this.selectedTemplateId = reportDataAny.templateId || reportData.template_id || 'land-property';
            this.selectedBankCode = reportDataAny.bankCode || reportData.bank_code || this.selectedBankCode;
            this.selectedPropertyType = reportDataAny.propertyType || reportData.property_type || '';
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
    console.log('📝 Populating form with report data:', reportData);
    console.log('📝 Report data structure:', JSON.stringify(reportData.report_data, null, 2));
    console.log('📝 Available form controls:', Object.keys(this.reportForm.controls));
    
    if (this.reportForm && reportData.report_data) {
      
      // Detect format: check if we have nested structure (new format) or flat structure (old format)
      const reportDataObj = reportData.report_data;
      const hasNestedStructure = this.hasNestedStructure(reportDataObj);
      
      console.log('📝 Detected report format:', hasNestedStructure ? 'NESTED (new)' : 'FLAT (old)');
      
      if (hasNestedStructure) {
        // New nested format - map nested data to form controls
        this.populateFromNestedStructure(reportDataObj);
      } else {
        // Old flat format - directly map flat fields to form controls
        this.populateFromFlatStructure(reportDataObj);
      }
      
      // Apply readonly state if in view mode - CRITICAL: This must happen AFTER all data population
      console.log('🔍 About to apply view mode state after data population');
      this.applyViewModeState();
      
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
        formEnabled: this.reportForm.enabled
      });
    } else {
      console.log('📝 No report_data found or form not ready, fields will remain empty for draft');
    }
    
    this.isLoading = false;
  }

  /**
   * Detect if report data has nested structure (new format) vs flat structure (old format)
   */
  private hasNestedStructure(reportData: any): boolean {
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
    
    // Handle nested data similar to template loading
    const mapNestedData = (data: any, prefix = '') => {
      Object.keys(data).forEach(key => {
        const value = data[key];
        
        if (value && typeof value === 'object' && !Array.isArray(value)) {
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
              control.setValue(value);
              console.log(`✅ Mapped nested ${prefix ? prefix + '.' + key : key} -> ${controlName} = ${value}`);
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
          control.setValue(value || '');
          console.log(`✅ Mapped flat field ${fieldKey} -> ${controlName} = ${value}`);
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
        this.buildFormControlsWithReportData(this.pendingReportData);
        
        console.log('🔧 Initializing bank specific tabs...');
        this.initializeBankSpecificTabs();
        
        // Force change detection
        this.cdr.detectChanges();
        
        // Now populate with report data if available
        if (this.pendingReportData) {
          console.log('📝 Template loaded, populating with existing report data');
          this.populateFormWithReportData(this.pendingReportData);
          this.pendingReportData = null;
        } else {
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
      // Disable all form controls for view mode
      this.reportForm.disable();
      console.log('🔒 Form disabled for view mode');
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
      this.selectedBankName = params['bankName'] || '';
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
      
      console.log('�🔥 Processed Report Form Params:', {
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
    // In view mode, ALL fields should be disabled
    if (this.isViewMode) {
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
    
    // Get form data without validation - include ALL fields even if empty
    const formData = this.reportForm.getRawValue();
    console.log('💾 Raw form data for draft:', formData);
    
    // Debug current template values
    console.log('🔍 Current template values:', {
      selectedBankCode: this.selectedBankCode,
      selectedBankName: this.selectedBankName,
      selectedTemplateId: this.selectedTemplateId,
      selectedTemplateName: this.selectedTemplateName,
      bankBranch: formData['bank_branch'],
      refNumber: formData['report_reference_number']
    });
    
    // Create comprehensive draft data with template information
    const draftData = {
      // Core template information - essential for re-loading
      bankCode: this.selectedBankCode || this.deriveBankCodeFromFormData(formData),
      bankName: this.selectedBankName || this.deriveBankNameFromFormData(formData),
      templateId: this.selectedTemplateId || 'land-property', // Default template ID
      templateName: this.selectedTemplateName || this.deriveTemplateNameFromFormData(formData),
      propertyType: this.selectedPropertyType,
      customTemplateId: this.customTemplateId,
      customTemplateName: this.customTemplateName,
      referenceNumber: this.reportReferenceNumber,
      
      // Form data - all fields including empty ones
      formData: formData,
      
      // Template structure for future reconstruction
      templateStructure: this.templateData ? {
        totalFieldCount: this.templateData.totalFieldCount,
        // Store basic template info for reconstruction
        templateDataSnapshot: JSON.stringify(this.templateData)
      } : null,
      
      // Status and metadata
      status: 'draft',
      organizationId: this.currentOrgShortName,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    console.log('💾 Comprehensive draft data prepared:', {
      hasTemplateStructure: !!draftData.templateStructure,
      formFieldCount: Object.keys(formData).length,
      templateInfo: {
        bankCode: draftData.bankCode,
        templateId: draftData.templateId,
        propertyType: draftData.propertyType
      }
    });

    console.log('💾 Saving draft data:', draftData);

    // Ensure we have required fields
    const propertyAddress = formData['property_address'] || 
                           formData['Property Address'] || 
                           formData['propertyAddress'] || 
                           'Property Address TBD';
    
    // Validate required fields - derive bank code if not present
    if (!this.selectedBankCode) {
      // Try to derive bank code from form data
      const derivedBankCode = this.deriveBankCodeFromFormData(formData);
      if (derivedBankCode) {
        this.selectedBankCode = derivedBankCode;
        console.log('🏦 Derived bank code:', derivedBankCode);
        
        // Also derive bank name if needed
        if (!this.selectedBankName) {
          this.selectedBankName = this.deriveBankNameFromFormData(formData);
          console.log('🏦 Derived bank name:', this.selectedBankName);
        }
      } else {
        this.isLoading = false;
        this.notificationService.error('Bank code is required to save draft');
        return;
      }
    }
    
    if (!this.selectedTemplateId && !this.customTemplateId) {
      // Try to derive template ID from form data
      const derivedTemplateId = this.deriveTemplateIdFromFormData(formData);
      if (derivedTemplateId) {
        this.selectedTemplateId = derivedTemplateId;
        console.log('📋 Derived template ID:', derivedTemplateId);
        
        // Also derive template name if needed
        if (!this.selectedTemplateName) {
          this.selectedTemplateName = this.deriveTemplateNameFromFormData(formData);
          console.log('📋 Derived template name:', this.selectedTemplateName);
        }
      } else {
        this.isLoading = false;
        this.notificationService.error('Template ID is required to save draft');
        return;
      }
    }

    // Create report request to match backend API with nested structure matching template
    const organizedFormData = this.organizeFormDataForTemplate(formData);
    
    const createRequest = {
      bank_code: this.selectedBankCode,
      template_id: this.selectedTemplateId || this.customTemplateId || '',
      property_address: propertyAddress,
      report_data: {
        ...organizedFormData,
        status: 'draft',
        bankName: this.selectedBankName,
        templateName: this.selectedTemplateName || this.customTemplateName,
        referenceNumber: this.reportReferenceNumber,
        organizationId: this.currentOrgShortName,
        customTemplateId: this.customTemplateId,
        customTemplateName: this.customTemplateName,
        propertyType: this.selectedPropertyType,
        reportType: 'valuation_report',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    };

    console.log('📡 Saving report via API:', createRequest);
    console.log('🔍 Request validation:');
    console.log('  - bank_code:', createRequest.bank_code);
    console.log('  - template_id:', createRequest.template_id);
    console.log('  - property_address:', createRequest.property_address);
    console.log('  - report_data keys:', Object.keys(createRequest.report_data));
    console.log('  - currentReportId:', this.currentReportId);
    console.log('  - isEditMode:', !!this.currentReportId);

    // Call API to create/save draft using HTTP client directly with auth headers
    const token = this.authService.getToken();
    console.log('🔑 Auth token available:', !!token);
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    
    // Determine if we're updating an existing report or creating a new one
    if (this.currentReportId) {
      // UPDATE existing report
      console.log('📝 Updating existing report:', this.currentReportId);
      const updateRequest = {
        report_data: createRequest.report_data,
        status: 'draft'
      };
      
      this.http.put<any>(`http://localhost:8000/api/reports/${this.currentReportId}`, updateRequest, { headers }).subscribe({
        next: (response) => {
          console.log('✅ Report updated successfully:', response);
          this.reportStatus = 'draft';
          this.isLoading = false;
          
          // Show success notification
          this.notificationService.success(`Draft updated successfully! Report ID: ${this.currentReportId}`);
          
          // Refresh form data to prevent blank form after save
          this.refreshFormDataAfterSave();
        },
        error: (error) => {
          console.error('❌ Error updating report - Full error object:', error);
          console.error('❌ Error status:', error.status);
          console.error('❌ Error message:', error.message);
          console.error('❌ Error error property:', JSON.stringify(error.error, null, 2));
          
          this.isLoading = false;
          
          let errorMessage = 'Failed to update report. Please try again.';
          if (error.error) {
            if (typeof error.error === 'string') {
              errorMessage += `\nError: ${error.error}`;
            } else if (error.error.detail) {
              errorMessage += `\nError: ${error.error.detail}`;
            } else {
              errorMessage += `\nError: ${JSON.stringify(error.error)}`;
            }
          }
          
          this.notificationService.error(errorMessage);
        }
      });
    } else {
      // CREATE new report
      console.log('🆕 Creating new report');
      this.http.post<any>('http://localhost:8000/api/reports', createRequest, { headers }).subscribe({
        next: (response) => {
          console.log('✅ Draft saved successfully:', response);
          this.reportStatus = 'draft';
          this.isLoading = false;
          
          // Store report ID for future updates
          if (response.success && response.data && response.data.report_id) {
            this.currentReportId = response.data.report_id;
            console.log('📋 Report ID stored:', this.currentReportId);
            
            // Also store the reference number if available
            if (response.data.reference_number) {
              this.reportReferenceNumber = response.data.reference_number;
              console.log('📋 Reference number updated:', this.reportReferenceNumber);
            }
          }
          
          // Show success notification
          this.notificationService.success(`Draft saved successfully! Report ID: ${this.currentReportId}`);
          
          // Refresh form data to prevent blank form after save
          this.refreshFormDataAfterSave();
        },
        error: (error) => {
          console.error('❌ Error saving draft - Full error object:', error);
          console.error('❌ Error status:', error.status);
          console.error('❌ Error message:', error.message);
          console.error('❌ Error error property:', JSON.stringify(error.error, null, 2));
          
          this.isLoading = false;
          
          let errorMessage = 'Failed to save draft. Please try again.';
          if (error.error) {
            if (typeof error.error === 'string') {
              errorMessage += `\nError: ${error.error}`;
            } else if (error.error.detail) {
              errorMessage += `\nError: ${error.error.detail}`;
            } else {
              errorMessage += `\nError: ${JSON.stringify(error.error)}`;
            }
          }
          
          this.notificationService.error(errorMessage);
        }
      });
    }
  }

  /**
   * Save Report - Save with full validation (mandatory before submit)
   */
  onSaveReport(): void {
    console.log('💾 Save Report clicked');
    
    if (this.isLoading) {
      console.log('⚠️ Already processing, ignoring save report request');
      return;
    }

    // Validate form first
    if (this.reportForm.invalid) {
      console.log('❌ Form validation failed');
      this.markAllFieldsAsTouched();
      console.log('⚠️ Please fix validation errors before saving report');
      // Show validation error notification (will be implemented with notification service)
      return;
    }

    this.isLoading = true;
    
    // Get validated form data
    const formData = this.reportForm.value;
    
    const reportData = {
      ...formData,
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
      const updateRequest = {
        report_data: reportData,
        status: 'saved'
      };
      
      this.http.put<any>(`http://localhost:8000/api/reports/${this.currentReportId}`, updateRequest, { headers }).subscribe({
        next: (response) => {
          console.log('✅ Report saved successfully:', response);
          this.reportStatus = 'saved';
          this.isLoading = false;
          
          // Show success notification
          this.notificationService.success(`Report saved successfully! Report ID: ${this.currentReportId}`);
          
          // Refresh form data to prevent blank form after save
          this.refreshFormDataAfterSave();
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
      const createRequest = {
        bank_code: this.selectedBankCode,
        template_id: this.selectedTemplateId || this.customTemplateId || '',
        property_address: reportData.property_address || 'Property Address TBD',
        report_data: reportData
      };
      
      this.http.post<any>('http://localhost:8000/api/reports', createRequest, { headers }).subscribe({
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
    
    this.http.post<any>(`http://localhost:8000/api/reports/${this.currentReportId}/submit`, {}, { headers }).subscribe({
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

}

