import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import {
  ValuationTemplate,
  BaseField,
  InputField,
  ContainerField,
  TabsField,
  TabField,
  SectionField,
  GroupField,
  TableField,
  AttachmentField,
  FieldTypeDto,
  ContainerTypeDto,
  PropertyTypeDto,
  AggregateTypeDto,
  AttachmentCategoryDto
} from '../../models/valuation-template.model';
import { FormFieldComponent } from './form-fields/form-field';
import { TemplateService } from '../../services/template.service';
import { ReportsService } from '../../services/reports.service';
import { AuthService } from '../../services/auth.service';

// ========================================
// DATA MODELS
// ========================================

interface TemplateSummary {
  bankCode: string;
  bankName: string;
  propertyType: string;
  templateId: string;
}

interface BankWithTemplates {
  bankCode: string;
  bankName: string;
  availableTypes: string[];
}

@Component({
  selector: 'app-new-report-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormFieldComponent],
  templateUrl: './new-report-form.html',
  styleUrl: './new-report-form.css',
})
export class NewReportForm implements OnInit {
  
  // ========================================
  // VIEW STATE
  // ========================================
  currentView: 'selection' | 'template-choice' | 'form' = 'selection';
  isLoading = false;
  isSaving = false;
  errorMessage: string | null = null;
  
  // ========================================
  // SELECTION STATE
  // ========================================
  availableTemplates: TemplateSummary[] = [];
  groupedBanks: BankWithTemplates[] = [];
  
  // ========================================
  // TEMPLATE CHOICE STATE
  // ========================================
  selectedBank: string | null = null;
  selectedBankName: string | null = null;
  selectedPropertyType: string | null = null;
  usePrefilledTemplate = false;
  
  // ========================================
  // FORM STATE
  // ========================================
  template: ValuationTemplate | null = null;
  form = new FormGroup({});
  tableRows: Record<string, Record<string, any>[]> = {};
  collapsedMap: Record<string, boolean> = {};

  constructor(
    private templateService: TemplateService,
    private reportsService: ReportsService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    console.log('🚀 NewReportForm initialized - Clean version');
    
    // Listen to route changes to detect navigation back to create page
    this.route.url.subscribe(() => {
      // Check if there are query parameters
      this.route.queryParams.subscribe(params => {
        const bank = params['bank'];
        const type = params['type'];
        
        if (bank && type) {
          // Restore form state from query parameters
          console.log('📋 Restoring form from query params:', { bank, type });
          this.selectedBank = bank;
          this.selectedPropertyType = type;
          this.currentView = 'form';
          this.loadForm(false);
        } else {
          // No query params - reset to selection view
          console.log('🔄 Resetting to selection view');
          this.resetToSelection();
        }
      });
    });
  }

  /**
   * Reset component to initial selection state
   */
  private resetToSelection() {
    this.currentView = 'selection';
    this.selectedBank = null;
    this.selectedBankName = null;
    this.selectedPropertyType = null;
    this.template = null;
    this.form = new FormGroup({});
    this.tableRows = {};
    this.collapsedMap = {};
    this.fetchAvailableTemplates();
  }

  // ========================================
  // PHASE 1: FETCH & GROUP TEMPLATES
  // ========================================
  
  fetchAvailableTemplates() {
    console.log('📡 Fetching available templates from MongoDB...');
    this.isLoading = true;
    this.errorMessage = null;
    this.cdr.markForCheck(); // Trigger change detection for zoneless mode

    // Fetch templates dynamically from backend API
    // getAllTemplatesFromAllBanks now fetches banks from /api/banks endpoint
    this.templateService.getAllTemplatesFromAllBanks().subscribe({
      next: (templates) => {
        console.log('✅ Received templates from API:', templates);
        console.log('📊 First template raw data:', templates[0]);
        
        // Transform backend template format to TemplateSummary
        this.availableTemplates = templates.map((t: any) => {
          const bankCode = t.bankDetails?.bankCode || t.BankDetails?.BankCode || t.bankCode || 'UNKNOWN';
          const bankName = t.bankDetails?.bankName || t.BankDetails?.BankName || t.bankName || bankCode;
          
          const transformed = {
            bankCode: bankCode,
            bankName: bankName,
            propertyType: (t.propertyType || t.PropertyType || 'unknown').toLowerCase(),
            templateId: t.templateId || t.TemplateId || t.id || t._id
          };
          console.log('🔄 Transformed:', { 
            original: { code: bankCode, name: bankName }, 
            transformed: { code: transformed.bankCode, name: transformed.bankName } 
          });
          return transformed;
        });
        
        console.log('📊 All transformed templates:', this.availableTemplates);
        
        // Group by bank
        this.groupedBanks = this.groupTemplatesByBank(this.availableTemplates);
        this.isLoading = false;
        this.cdr.markForCheck(); // Trigger change detection for zoneless mode
        
        console.log('✅ Templates grouped by bank:', this.groupedBanks);
      },
      error: (error) => {
        console.error('❌ Failed to fetch templates:', error);
        this.errorMessage = 'Failed to load templates. Please check if the backend is running.';
        this.isLoading = false;
        this.cdr.markForCheck(); // Trigger change detection for zoneless mode
      }
    });
  }

  groupTemplatesByBank(templates: TemplateSummary[]): BankWithTemplates[] {
    const bankMap = new Map<string, Set<string>>();
    const bankNames = new Map<string, string>();

    templates.forEach(t => {
      if (!bankMap.has(t.bankCode)) {
        bankMap.set(t.bankCode, new Set());
        bankNames.set(t.bankCode, t.bankName);
      }
      bankMap.get(t.bankCode)!.add(t.propertyType);
    });

    return Array.from(bankMap.entries()).map(([code, types]) => ({
      bankCode: code,
      bankName: bankNames.get(code)!,
      availableTypes: Array.from(types).sort()
    }));
  }

  // ========================================
  // PHASE 2: TEMPLATE SELECTION
  // ========================================
  
  selectTemplate(bankCode: string, bankName: string, propertyType: string) {
    console.log('🏦 Template selected:', { bankCode, propertyType });
    this.selectedBank = bankCode;
    this.selectedBankName = bankName;
    this.selectedPropertyType = propertyType;
    
    // Update URL with query parameters
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { bank: bankCode, type: propertyType },
      queryParamsHandling: 'merge'
    });
    
    this.cdr.markForCheck(); // Trigger change detection for zoneless mode
    
    // Skip template choice view, load blank form directly
    console.log('⏭️ Skipping choice view, loading blank form directly...');
    this.loadForm(false); // false = blank form
  }

  goBackToSelection() {
    console.log('⬅️ Going back to selection');
    this.currentView = 'selection';
    this.selectedBank = null;
    this.selectedBankName = null;
    this.selectedPropertyType = null;
  }

  // ========================================
  // PHASE 3: LOAD FORM
  // ========================================
  
  loadForm(usePrefilled: boolean) {
    console.log('📄 Loading form:', { usePrefilled, bank: this.selectedBank, type: this.selectedPropertyType });
    
    this.usePrefilledTemplate = usePrefilled;
    this.currentView = 'form';
    this.isLoading = true;
    this.errorMessage = null;
    this.cdr.markForCheck(); // Trigger change detection for zoneless mode

    // Call API to get full template
    this.templateService
      .getAggregatedTemplateFields(this.selectedBank!, this.selectedPropertyType!)
      .subscribe({
        next: (response) => {
          console.log('✅ Template data received from API:', response);
          
          // Convert API response
          this.template = this.convertApiResponseToTemplate(response);
          console.log('✅ Template converted:', this.template);
          console.log('✅ Template elements count:', this.template.elements.length);
          console.log('✅ Template elements:', this.template.elements.map(e => ({ 
            $type: e.$type, 
            fieldId: e.fieldId, 
            label: e.label,
            container: (e as any).container 
          })));
          
          // Build form
          this.buildFormControls(this.template.elements);
          console.log('✅ Form controls built');
          
          // Prefill if requested
          if (usePrefilled) {
            this.prefillFormWithDefaults(this.template);
            console.log('✅ Form prefilled');
          }
          
          // Collect tables & initialize state
          this.collectTables(this.template.elements);
          this.initCollapsedState(this.template.elements);
          
          this.isLoading = false;
          this.cdr.markForCheck(); // Trigger change detection for zoneless mode
          console.log('🎉 Form ready!');
        },
        error: (error) => {
          console.error('❌ Failed to load template:', error);
          this.errorMessage = `Failed to load template: ${error.statusText || error.message}`;
          this.isLoading = false;
          this.cdr.markForCheck(); // Trigger change detection for zoneless mode
        }
      });
  }

  // ========================================
  // CONVERSION & FORM BUILDING
  // ========================================
  
  private convertApiResponseToTemplate(apiResponse: any): ValuationTemplate {
    console.log('🔄 Converting API response to template:', apiResponse);
    console.log('🔍 API Response structure:', {
      hasCommonFields: !!apiResponse.commonFields,
      commonFieldsCount: apiResponse.commonFields?.length || 0,
      hasBankSpecificTabs: !!apiResponse.bankSpecificTabs,
      bankSpecificTabsCount: apiResponse.bankSpecificTabs?.length || 0
    });
    const elements: BaseField[] = [];

    // Add common fields
    if (apiResponse.commonFields && apiResponse.commonFields.length > 0) {
      console.log(`✅ Found ${apiResponse.commonFields.length} common fields`);
      apiResponse.commonFields.forEach((field: any) => {
        elements.push(this.convertFieldToBaseField(field));
      });
    }

    // Add bank-specific tabs
    if (apiResponse.bankSpecificTabs && apiResponse.bankSpecificTabs.length > 0) {
      console.log(`✅ Found ${apiResponse.bankSpecificTabs.length} bank-specific tabs`);
      const tabGroupChildren: TabField[] = apiResponse.bankSpecificTabs.map((tab: any) => 
        this.convertTabToTabField(tab)
      );

      const tabGroup: TabsField = {
        $type: 'container',
        fieldId: 'tabs_main',
        label: 'Report Sections',
        displayOrder: elements.length,
        fieldType: FieldTypeDto.Container,
        isVisible: true,
        container: ContainerTypeDto.TabGroup,
        children: tabGroupChildren
      };

      elements.push(tabGroup);
      console.log('✅ TabGroup added to elements');
    } else {
      console.warn('⚠️ No bank-specific tabs found in API response');
    }

    console.log(`✅ Total elements: ${elements.length}`, elements);

    return {
      templateId: apiResponse.templateInfo.templateId,
      templateName: apiResponse.templateInfo.templateName,
      templateDescription: apiResponse.templateInfo.description || '',
      bankDetails: {
        bankCode: apiResponse.templateInfo.bankCode,
        bankName: apiResponse.templateInfo.bankName
      },
      propertyType: this.mapPropertyType(apiResponse.templateInfo.propertyType),
      isActive: true,
      createdAt: new Date().toISOString(),
      calculationRules: [],
      elements
    };
  }

  private convertFieldToBaseField(field: any): BaseField {
    // Check if it has subFields - means it's a Group container
    if (field.subFields && field.subFields.length > 0) {
      console.log(`📦 Converting Group field: ${field.fieldId} with ${field.subFields.length} children`);
      return this.convertGroupFromTemplateField(field);
    } else if (field.fieldType === 'table' || field.type === 'table') {
      return this.convertTableToField(field);
    } else {
      return this.convertInputToField(field);
    }
  }

  private convertGroupFromTemplateField(field: any): GroupField {
    return {
      $type: 'container',
      fieldId: field.fieldId,
      label: field.uiDisplayName || field.label || field.fieldId,
      displayOrder: field.sortOrder || field.displayOrder || 0,
      fieldType: FieldTypeDto.Container,
      isVisible: field.isActive !== false,
      container: ContainerTypeDto.Group,
      isCollapsible: true,  // Make groups collapsible
      isCollapsed: false,   // Start expanded
      children: (field.subFields || []).map((child: any) => this.convertSubFieldToBaseField(child))
    };
  }

  private convertSubFieldToBaseField(field: any): InputField {
    return {
      $type: 'input',
      fieldId: field.fieldId,
      label: field.uiDisplayName || field.label || field.fieldId,
      displayOrder: field.sortOrder || field.displayOrder || 0,
      fieldType: this.mapFieldType(field.fieldType),
      isVisible: field.isActive !== false,
      specificType: this.mapFieldType(field.fieldType),
      isRequired: field.isRequired || false,
      isReadonly: field.isReadonly || false,
      placeholderText: field.placeholder || '',
      defaultValue: field.defaultValue,
      options: field.options?.map((opt: any) => opt.label || opt.value || opt) || undefined,
      validationRules: field.validation || undefined,
      helpText: field.helpText || ''
    } as InputField;
  }

  private convertGroupToBaseField(group: any): GroupField {
    return {
      $type: 'container',
      fieldId: group.fieldId,
      label: group.label,
      displayOrder: group.displayOrder || 0,
      fieldType: FieldTypeDto.Container,
      isVisible: group.isVisible !== false,
      container: ContainerTypeDto.Group,
      isCollapsible: false,
      isCollapsed: false,
      children: (group.children || []).map((child: any) => this.convertChildFieldToBaseField(child))
    };
  }

  private convertChildFieldToBaseField(field: any): BaseField {
    if (field.$type === 'input') {
      return {
        $type: 'input',
        fieldId: field.fieldId,
        label: field.label,
        displayOrder: field.displayOrder || 0,
        fieldType: this.mapBackendFieldTypeToFrontend(field.specificType),
        isVisible: field.isVisible !== false,
        specificType: this.mapBackendFieldTypeToFrontend(field.specificType),
        isRequired: field.isRequired || false,
        isReadonly: field.isReadonly || false,
        placeholderText: field.placeholderText || '',
        defaultValue: field.defaultValue,
        options: field.options?.map((opt: any) => opt.label || opt.value || opt) || undefined,
        validationRules: field.validationRules || undefined,
        helpText: field.helpText || ''
      } as InputField;
    } else if (field.$type === 'table') {
      return this.convertTableToField(field);
    } else {
      // Fallback to input field
      return this.convertInputToField(field);
    }
  }

  private mapBackendFieldTypeToFrontend(specificType: string): FieldTypeDto {
    const typeMap: Record<string, FieldTypeDto> = {
      'Text': FieldTypeDto.Text,
      'Number': FieldTypeDto.Number,
      'Date': FieldTypeDto.Date,
      'Dropdown': FieldTypeDto.Dropdown,
      'Textarea': FieldTypeDto.Textarea,
      'Currency': FieldTypeDto.Currency,
      'Checkbox': FieldTypeDto.Checkbox,
      'Radio': FieldTypeDto.Radio,
      'Email': FieldTypeDto.Text,
      'Phone': FieldTypeDto.Text
    };
    return typeMap[specificType] || FieldTypeDto.Text;
  }

  private convertInputToField(field: any): InputField {
    return {
      $type: 'input',
      fieldId: field.fieldId,
      label: field.uiDisplayName || field.label || field.fieldId,
      displayOrder: field.sortOrder || 0,
      fieldType: this.mapFieldType(field.type || field.fieldType),
      isVisible: true,
      specificType: this.mapFieldType(field.type || field.fieldType),
      isRequired: field.isRequired || false,
      isReadonly: field.isReadonly || false,
      placeholderText: field.placeholder || '',
      defaultValue: field.defaultValue,
      options: field.options?.map((opt: any) => opt.label || opt.value || opt) || undefined,
      validationRules: field.validation || undefined,
      helpText: field.helpText || ''
    } as InputField;
  }

  private convertTableToField(field: any): TableField {
    return {
      $type: 'table',
      fieldId: field.fieldId,
      label: field.uiDisplayName || field.label || field.fieldId,
      displayOrder: field.sortOrder || 0,
      fieldType: FieldTypeDto.Table,
      isVisible: true,
      columns: field.columns || [],
      rows: field.rows || [],
      summaries: field.summaries || [],
      minRows: field.minRows || 1,
      maxRows: field.maxRows || 10,
      allowAddRows: field.allowAddRows !== false,
      allowDeleteRows: field.allowDeleteRows !== false,
      showFooter: field.showFooter || false
    };
  }

  private convertTabToTabField(tab: any): TabField {
    const tabChildren: BaseField[] = [];

    // Add direct fields
    if (tab.fields && tab.fields.length > 0) {
      tab.fields.forEach((field: any) => {
        tabChildren.push(this.convertFieldToBaseField(field));
      });
    }

    // Add sections
    if (tab.sections && tab.sections.length > 0) {
      tab.sections.forEach((section: any) => {
        tabChildren.push(this.convertSectionToBaseField(section));
      });
    }

    return {
      $type: 'container',
      fieldId: tab.tabId,
      label: tab.tabName,
      displayOrder: tab.sortOrder || 0,
      fieldType: FieldTypeDto.Tab,
      isVisible: true,
      container: ContainerTypeDto.Tab,
      children: tabChildren
    };
  }

  private convertSectionToBaseField(section: any): SectionField {
    return {
      $type: 'container',
      fieldId: section.sectionId,
      label: section.sectionName,
      displayOrder: section.sortOrder || 0,
      fieldType: FieldTypeDto.Container,
      isVisible: true,
      container: ContainerTypeDto.Section,
      isCollapsible: true,
      isCollapsed: false,
      children: (section.fields || []).map((field: any) => this.convertFieldToBaseField(field))
    };
  }

  private mapFieldType(type: string): FieldTypeDto {
    const typeMap: Record<string, FieldTypeDto> = {
      'text': FieldTypeDto.Text,
      'number': FieldTypeDto.Number,
      'date': FieldTypeDto.Date,
      'select': FieldTypeDto.Dropdown,
      'textarea': FieldTypeDto.Textarea,
      'currency': FieldTypeDto.Currency,
      'checkbox': FieldTypeDto.Checkbox,
      'radio': FieldTypeDto.Radio,
      'email': FieldTypeDto.Text,
      'phone': FieldTypeDto.Text,
      'table': FieldTypeDto.Table
    };
    return typeMap[type] || FieldTypeDto.Text;
  }

  private mapPropertyType(type: string): PropertyTypeDto {
    const typeMap: Record<string, PropertyTypeDto> = {
      'land': PropertyTypeDto.Land,
      'apartment': PropertyTypeDto.Apartment,
      'house': PropertyTypeDto.House,
      'commercial': PropertyTypeDto.Commercial
    };
    return typeMap[type.toLowerCase()] || PropertyTypeDto.Land;
  }

  private buildFormControls(fields: BaseField[]) {
    for (const field of fields) {
      if (field.$type === 'input') {
        const inputField = field as InputField;
        const validators = [];
        if (inputField.isRequired) validators.push(Validators.required);
        this.form.addControl(inputField.fieldId, new FormControl(inputField.defaultValue || '', validators));
      } else if (field.$type === 'container') {
        const container = field as TabsField | TabField | SectionField | GroupField;
        if ('children' in container && container.children) {
          this.buildFormControls(container.children);
        }
      }
    }
  }

  private prefillFormWithDefaults(template: ValuationTemplate) {
    this.setDefaultValues(template.elements);
  }

  private setDefaultValues(elements: BaseField[]) {
    elements.forEach(field => {
      if (field.$type === 'input') {
        const inputField = field as InputField;
        if (inputField.defaultValue) {
          this.form.get(inputField.fieldId)?.setValue(inputField.defaultValue);
        }
      } else if (field.$type === 'container') {
        const container = field as TabsField | TabField | SectionField | GroupField;
        if ('children' in container && container.children) {
          this.setDefaultValues(container.children);
        }
      }
    });
  }

  private collectTables(elements: BaseField[]) {
    for (const element of elements) {
      if (element.$type === 'table') {
        const tableField = element as TableField;
        if (tableField.rows && tableField.rows.length > 0) {
          this.tableRows[tableField.fieldId] = tableField.rows;
          console.log(`📊 Table ${tableField.fieldId}: Using ${tableField.rows.length} rows from API`);
        } else {
          this.tableRows[tableField.fieldId] = [];
        }
      } else if (element.$type === 'container') {
        const container = element as TabsField | TabField | SectionField | GroupField;
        if ('children' in container && container.children) {
          this.collectTables(container.children);
        }
      }
    }
  }

  private initCollapsedState(elements: BaseField[]) {
    for (const element of elements) {
      if (element.$type === 'container') {
        const container = element as TabsField | TabField | SectionField | GroupField;
        // Initialize collapsed state for Sections
        if (container.container === ContainerTypeDto.Section) {
          const section = container as SectionField;
          this.collapsedMap[section.fieldId] = section.isCollapsed || false;
        }
        // Initialize collapsed state for Groups
        if (container.container === ContainerTypeDto.Group) {
          const group = container as GroupField;
          this.collapsedMap[group.fieldId] = group.isCollapsed || false;
        }
        if ('children' in container && container.children) {
          this.initCollapsedState(container.children);
        }
      }
    }
  }

  onSubmit() {
    console.log('📤 Form submitted:', this.form.value);
    // Default submit behavior - save as draft
    this.onSaveAsDraft();
  }

  /**
   * Save report as draft (can be incomplete)
   */
  onSaveAsDraft() {
    if (this.isSaving) return;
    
    this.isSaving = true;
    this.errorMessage = null;

    const reportData = this.prepareReportData();
    
    console.log('💾 Saving as draft...', reportData);

    this.reportsService.saveDraft(reportData).subscribe({
      next: (response) => {
        console.log('✅ Draft saved successfully:', response);
        this.isSaving = false;
        
        // Show success message
        alert('✅ Report saved as draft successfully!');
        
        // Navigate to reports list
        const user = this.authService.currentUser();
        const orgShortName = user?.org_short_name || 'system-administration';
        this.router.navigate([`/org/${orgShortName}/reports`]);
      },
      error: (error) => {
        console.error('❌ Error saving draft:', error);
        this.isSaving = false;
        this.errorMessage = error.error?.message || 'Failed to save draft';
        alert('❌ Failed to save draft: ' + this.errorMessage);
      }
    });
  }

  /**
   * Submit report for review (requires complete/valid form)
   */
  onSubmitForReview() {
    if (this.isSaving || this.form.invalid) return;
    
    this.isSaving = true;
    this.errorMessage = null;

    const reportData = this.prepareReportData();
    
    console.log('📤 Submitting for review...', reportData);

    // First save as draft, then submit
    this.reportsService.saveDraft(reportData).subscribe({
      next: (draftResponse) => {
        console.log('✅ Draft saved, now submitting...', draftResponse);
        
        const reportId = draftResponse.data?.id || draftResponse.data?.reportId;
        
        if (!reportId) {
          this.isSaving = false;
          this.errorMessage = 'Could not get report ID from draft response';
          alert('❌ Error: ' + this.errorMessage);
          return;
        }

        // Now submit the report
        this.reportsService.submitReport(reportId, reportData).subscribe({
          next: (submitResponse) => {
            console.log('✅ Report submitted successfully:', submitResponse);
            this.isSaving = false;
            
            // Show success message
            alert('✅ Report submitted for review successfully!');
            
            // Navigate to reports list
            const user = this.authService.currentUser();
            const orgShortName = user?.org_short_name || 'system-administration';
            this.router.navigate([`/org/${orgShortName}/reports`]);
          },
          error: (error) => {
            console.error('❌ Error submitting report:', error);
            this.isSaving = false;
            this.errorMessage = error.error?.message || 'Failed to submit report';
            alert('❌ Failed to submit report: ' + this.errorMessage);
          }
        });
      },
      error: (error) => {
        console.error('❌ Error saving draft before submit:', error);
        this.isSaving = false;
        this.errorMessage = error.error?.message || 'Failed to save draft';
        alert('❌ Failed to save draft: ' + this.errorMessage);
      }
    });
  }

  /**
   * Prepare report data from form values
   */
  private prepareReportData(): any {
    return {
      bankCode: this.selectedBank,
      propertyType: this.selectedPropertyType,
      templateId: this.template?.templateId,
      reportData: this.form.value,
      formData: this.form.value,
      tableRows: this.tableRows
    };
  }
}
