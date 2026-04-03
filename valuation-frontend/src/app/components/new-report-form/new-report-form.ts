import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
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

@Component({
  selector: 'app-new-report-form',
  imports: [CommonModule, ReactiveFormsModule, FormFieldComponent],
  templateUrl: './new-report-form.html',
  styleUrl: './new-report-form.css',
})
export class NewReportForm implements OnInit {

  collapsedMap: Record<string, boolean> = {};
  form = new FormGroup({});
  tableRows: Record<string, Record<string, any>[]> = {};
  isLoading = true;
  errorMessage: string | null = null;

  // Template will be loaded from API
  template: ValuationTemplate | null = null;
  
  // Mock template for fallback (same as before)
  private mockTemplate: ValuationTemplate = {
    templateId: 'SBI_LAND_001',
    templateName: 'SBI Land Property Valuation',
    templateDescription: 'Standard land property valuation template for SBI',
    bankDetails: { bankName: 'State Bank of India', bankCode: 'SBI' },
    propertyType: PropertyTypeDto.Land,
    isActive: true,
    createdAt: new Date().toISOString(),
    calculationRules: [
      {
        ruleId: 'calc_total',
        triggerFieldIds: ['land_area', 'rate_per_sqft'],
        formula: 'land_area * rate_per_sqft',
        targetFieldId: 'estimated_value'
      }
    ],
    elements: [

      {
        $type: 'input',
        fieldId: 'applicant_name',
        label: 'Applicant Name',
        displayOrder: 0,
        fieldType: FieldTypeDto.Text,
        isVisible: true,
        specificType: FieldTypeDto.Text,
        isRequired: true,
        isReadonly: false,
        placeholderText: 'Enter applicant full name',
        validationRules: { minLength: 3, maxLength: 100 }
      } as InputField,

      {
        $type: 'container',
        fieldId: 'tabs_main',
        label: 'Main Tabs',
        displayOrder: 1,
        fieldType: FieldTypeDto.Container,
        isVisible: true,
        container: ContainerTypeDto.TabGroup,
        children: [

          {
            $type: 'container',
            fieldId: 'tab_property_details',
            label: 'Property Details',
            displayOrder: 0,
            fieldType: FieldTypeDto.Tab,
            isVisible: true,
            container: ContainerTypeDto.Tab,
            children: [

              {
                $type: 'container',
                fieldId: 'section_location',
                label: 'Location Information',
                displayOrder: 0,
                fieldType: FieldTypeDto.Container,
                isVisible: true,
                container: ContainerTypeDto.Section,
                isCollapsible: true,
                isCollapsed: false,
                children: [
                  { $type: 'input', fieldId: 'property_address', label: 'Property Address', displayOrder: 0, fieldType: FieldTypeDto.Textarea, isVisible: true, specificType: FieldTypeDto.Textarea, isRequired: true, isReadonly: false, placeholderText: 'Enter full property address' } as InputField,
                  { $type: 'input', fieldId: 'city', label: 'City / Town', displayOrder: 1, fieldType: FieldTypeDto.Text, isVisible: true, specificType: FieldTypeDto.Text, isRequired: true, isReadonly: false, placeholderText: 'City or town name' } as InputField,
                  { $type: 'input', fieldId: 'state', label: 'State', displayOrder: 2, fieldType: FieldTypeDto.Dropdown, isVisible: true, specificType: FieldTypeDto.Dropdown, isRequired: true, isReadonly: false, options: ['Andhra Pradesh', 'Delhi', 'Gujarat', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal'] } as InputField,
                  { $type: 'input', fieldId: 'pin_code', label: 'PIN Code', displayOrder: 3, fieldType: FieldTypeDto.Text, isVisible: true, specificType: FieldTypeDto.Text, isRequired: true, isReadonly: false, placeholderText: '6-digit PIN code', validationRules: { pattern: '^[1-9][0-9]{5}$', errorMessage: 'Enter a valid 6-digit PIN code' } } as InputField
                ]
              } as SectionField,

              {
                $type: 'container',
                fieldId: 'group_land_details',
                label: 'Land Measurements',
                displayOrder: 1,
                fieldType: FieldTypeDto.Container,
                isVisible: true,
                container: ContainerTypeDto.Group,
                isCollapsible: false,
                isCollapsed: false,
                children: [
                  { $type: 'input', fieldId: 'land_area', label: 'Land Area (sq ft)', displayOrder: 0, fieldType: FieldTypeDto.Number, isVisible: true, specificType: FieldTypeDto.Number, isRequired: true, isReadonly: false, validationRules: { min: 1 } } as InputField,
                  { $type: 'input', fieldId: 'land_shape', label: 'Land Shape', displayOrder: 1, fieldType: FieldTypeDto.Dropdown, isVisible: true, specificType: FieldTypeDto.Dropdown, isRequired: false, isReadonly: false, options: ['Regular', 'Irregular', 'Corner Plot', 'L-Shaped'] } as InputField,
                  { $type: 'input', fieldId: 'road_width', label: 'Road Width (ft)', displayOrder: 2, fieldType: FieldTypeDto.Number, isVisible: true, specificType: FieldTypeDto.Number, isRequired: false, isReadonly: false } as InputField,
                  { $type: 'input', fieldId: 'is_corner_plot', label: 'Corner Plot?', displayOrder: 3, fieldType: FieldTypeDto.Checkbox, isVisible: true, specificType: FieldTypeDto.Checkbox, isRequired: false, isReadonly: false } as InputField
                ]
              } as GroupField,

              {
                $type: 'table', fieldId: 'boundaries_table', label: 'Boundary Details',
                displayOrder: 2, fieldType: FieldTypeDto.Table, isVisible: true,
                minRows: 4, allowAddRows: false, allowDeleteRows: false, showFooter: false, summaries: [],
                columns: [
                  { fieldId: 'direction', label: 'Direction', fieldType: FieldTypeDto.Dropdown, isReadonly: false, options: ['North', 'South', 'East', 'West'] },
                  { fieldId: 'boundary_by', label: 'Bounded By', fieldType: FieldTypeDto.Text, isReadonly: false },
                  { fieldId: 'dimension_ft', label: 'Dimension (ft)', fieldType: FieldTypeDto.Number, isReadonly: false }
                ]
              } as TableField

            ]
          } as TabField,

          {
            $type: 'container',
            fieldId: 'tab_valuation',
            label: 'Valuation',
            displayOrder: 1,
            fieldType: FieldTypeDto.Tab,
            isVisible: true,
            container: ContainerTypeDto.Tab,
            children: [
              { $type: 'input', fieldId: 'valuation_date', label: 'Valuation Date', displayOrder: 0, fieldType: FieldTypeDto.Date, isVisible: true, specificType: FieldTypeDto.Date, isRequired: true, isReadonly: false } as InputField,
              { $type: 'input', fieldId: 'rate_per_sqft', label: 'Market Rate (₹/sq ft)', displayOrder: 1, fieldType: FieldTypeDto.Currency, isVisible: true, specificType: FieldTypeDto.Currency, isRequired: true, isReadonly: false, validationRules: { min: 0 } } as InputField,
              { $type: 'input', fieldId: 'estimated_value', label: 'Estimated Value (₹)', displayOrder: 2, fieldType: FieldTypeDto.Currency, isVisible: true, specificType: FieldTypeDto.Currency, isRequired: false, isReadonly: true, helpText: 'Auto-calculated: Land Area × Market Rate' } as InputField,
              { $type: 'input', fieldId: 'valuation_purpose', label: 'Purpose of Valuation', displayOrder: 3, fieldType: FieldTypeDto.Dropdown, isVisible: true, specificType: FieldTypeDto.Dropdown, isRequired: true, isReadonly: false, options: ['Home Loan', 'Mortgage', 'Sale', 'Insurance', 'Legal', 'Other'] } as InputField,
              { $type: 'input', fieldId: 'valuation_remarks', label: 'Remarks', displayOrder: 4, fieldType: FieldTypeDto.Textarea, isVisible: true, specificType: FieldTypeDto.Textarea, isRequired: false, isReadonly: false, placeholderText: 'Any additional remarks...' } as InputField,
              {
                $type: 'table', fieldId: 'floorwise_table', label: 'Floor-wise Valuation',
                displayOrder: 5, fieldType: FieldTypeDto.Table, isVisible: true,
                minRows: 1, allowAddRows: true, allowDeleteRows: true, showFooter: true,
                summaries: [{ columnFieldId: 'floor_value', operation: AggregateTypeDto.Sum, label: 'Total Value', summaryFieldId: 'total_floor_value' }],
                columns: [
                  { fieldId: 'floor_name', label: 'Floor', fieldType: FieldTypeDto.Text, isReadonly: false },
                  { fieldId: 'built_area', label: 'Built-up Area (sq ft)', fieldType: FieldTypeDto.Number, isReadonly: false },
                  { fieldId: 'rate', label: 'Rate (₹/sq ft)', fieldType: FieldTypeDto.Currency, isReadonly: false },
                  { fieldId: 'floor_value', label: 'Value (₹)', fieldType: FieldTypeDto.Currency, isReadonly: true }
                ]
              } as TableField
            ]
          } as TabField,

          {
            $type: 'container',
            fieldId: 'tab_documents',
            label: 'Documents',
            displayOrder: 2,
            fieldType: FieldTypeDto.Tab,
            isVisible: true,
            container: ContainerTypeDto.Tab,
            children: [
              { $type: 'attachment', fieldId: 'title_deed', label: 'Title Deed', displayOrder: 0, fieldType: FieldTypeDto.FileUpload, isVisible: true, allowedExtensions: ['.pdf', '.jpg', '.png'], maxFileSize: 5242880, allowMultiple: false, category: AttachmentCategoryDto.LegalDocument } as AttachmentField,
              { $type: 'attachment', fieldId: 'property_photos', label: 'Property Photos', displayOrder: 1, fieldType: FieldTypeDto.FileUpload, isVisible: true, allowedExtensions: ['.jpg', '.jpeg', '.png'], maxFileSize: 10485760, allowMultiple: true, category: AttachmentCategoryDto.PropertyPhoto } as AttachmentField,
              { $type: 'attachment', fieldId: 'site_map', label: 'Site Map / Sketch', displayOrder: 2, fieldType: FieldTypeDto.FileUpload, isVisible: true, allowedExtensions: ['.pdf', '.jpg', '.png'], maxFileSize: 5242880, allowMultiple: false, category: AttachmentCategoryDto.MapOrSketch } as AttachmentField
            ]
          } as TabField

        ]
      } as TabsField

    ]
  };

  constructor(
    private templateService: TemplateService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    // Get bank code and property type from query params
    this.route.queryParams.subscribe(params => {
      const bankCode = params['bankCode'] || 'SBI';
      const propertyType = params['propertyType'] || 'land';
      
      console.log('🔄 NewReportForm: Loading template', { bankCode, propertyType });
      this.loadTemplate(bankCode, propertyType);
    });
  }

  private loadTemplate(bankCode: string, propertyType: string) {
    this.isLoading = true;
    this.errorMessage = null;

    this.templateService.getAggregatedTemplateFields(bankCode, propertyType).subscribe({
      next: (response) => {
        console.log('✅ Template loaded successfully', response);
        // Convert the API response to ValuationTemplate format
        this.template = this.convertApiResponseToTemplate(response);
        this.buildFormControls(this.template.elements);
        this.collectTables(this.template.elements);
        this.initCollapsedState(this.template.elements);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('❌ Failed to load template', error);
        this.errorMessage = 'Failed to load template. Please try again.';
        // Fallback to mock template
        this.template = this.mockTemplate;
        this.buildFormControls(this.template.elements);
        this.collectTables(this.template.elements);
        this.initCollapsedState(this.template.elements);
        this.isLoading = false;
      }
    });
  }

  /**
   * Convert TemplateService API response to ValuationTemplate format
   * This bridges the old AggregatedTemplateResponse format to the new container-based format
   */
  private convertApiResponseToTemplate(apiResponse: any): ValuationTemplate {
    const elements: BaseField[] = [];

    // Add common fields as root-level input elements
    if (apiResponse.commonFields && apiResponse.commonFields.length > 0) {
      apiResponse.commonFields.forEach((field: any) => {
        elements.push(this.convertFieldToBaseField(field));
      });
    }

    // Add bank-specific tabs as TabGroup container
    if (apiResponse.bankSpecificTabs && apiResponse.bankSpecificTabs.length > 0) {
      const tabGroupChildren: TabField[] = [];
      
      apiResponse.bankSpecificTabs.forEach((tab: any) => {
        const tabChildren: BaseField[] = [];
        
        // Add tab-level fields
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
        
        // Create Tab container
        const tabField: TabField = {
          $type: 'container',
          fieldId: tab.tabId,
          label: tab.tabName,
          displayOrder: tab.sortOrder || 0,
          fieldType: FieldTypeDto.Tab,
          isVisible: true,
          container: ContainerTypeDto.Tab,
          children: tabChildren
        };
        
        tabGroupChildren.push(tabField);
      });
      
      // Create TabGroup container
      const tabGroup: TabsField = {
        $type: 'container',
        fieldId: 'bank_specific_details',
        label: 'Bank Specific Details',
        displayOrder: apiResponse.commonFields?.length || 0,
        fieldType: FieldTypeDto.Container,
        isVisible: true,
        container: ContainerTypeDto.TabGroup,
        children: tabGroupChildren
      };
      
      elements.push(tabGroup);
    }

    return {
      templateId: apiResponse.templateInfo.templateId,
      templateName: apiResponse.templateInfo.templateName,
      templateDescription: `${apiResponse.templateInfo.bankName} - ${apiResponse.templateInfo.propertyType} valuation template`,
      bankDetails: {
        bankName: apiResponse.templateInfo.bankName,
        bankCode: apiResponse.templateInfo.bankCode
      },
      propertyType: this.mapPropertyType(apiResponse.templateInfo.propertyType),
      isActive: true,
      createdAt: apiResponse.aggregatedAt || new Date().toISOString(),
      calculationRules: [],
      elements: elements
    };
  }

  private convertFieldToBaseField(field: any): BaseField {
    const fieldType = this.mapFieldType(field.fieldType);
    
    if (field.fieldType === 'table') {
      return {
        $type: 'table',
        fieldId: field.fieldId,
        label: field.uiDisplayName || field.label,
        displayOrder: field.displayOrder || field.sortOrder || 0,
        fieldType: FieldTypeDto.Table,
        isVisible: field.isActive !== false,
        minRows: field.minRows || field.rows?.length || 1,
        allowAddRows: field.allowAddRows !== false,
        allowDeleteRows: field.allowDeleteRows !== false,
        showFooter: field.showFooter !== false,
        summaries: [],
        columns: (field.columns || []).map((col: any) => ({
          fieldId: col.fieldId,
          label: col.label,
          fieldType: this.mapFieldType(col.fieldType),
          isReadonly: col.isReadonly || false,
          options: col.options || undefined
        })),
        rows: field.rows || [] // ⭐ CRITICAL: Use rows from API
      } as TableField;
    } else if (field.fieldType === 'group' && field.subFields) {
      return {
        $type: 'container',
        fieldId: field.fieldId,
        label: field.uiDisplayName || field.label,
        displayOrder: field.displayOrder || field.sortOrder || 0,
        fieldType: FieldTypeDto.Container,
        isVisible: field.isActive !== false,
        container: ContainerTypeDto.Group,
        isCollapsible: false,
        isCollapsed: false,
        children: field.subFields.map((sub: any) => this.convertFieldToBaseField(sub))
      } as GroupField;
    } else {
      return {
        $type: 'input',
        fieldId: field.fieldId,
        label: field.uiDisplayName || field.label,
        displayOrder: field.displayOrder || field.sortOrder || 0,
        fieldType: FieldTypeDto.Text,
        isVisible: field.isActive !== false,
        specificType: fieldType,
        isRequired: field.isRequired || false,
        isReadonly: field.isReadonly || false,
        placeholderText: field.placeholder || '',
        helpText: field.helpText || '',
        defaultValue: field.defaultValue || undefined,
        options: field.options?.map((opt: any) => opt.label || opt) || undefined,
        validationRules: field.validation || undefined
      } as InputField;
    }
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
      'email': FieldTypeDto.Text, // Map email to Text
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
    return typeMap[type] || PropertyTypeDto.Land;
  }

  private buildFormControls(fields: BaseField[]) {
    for (const field of fields) {
      if (field.$type === 'input') {
        const f = field as InputField;
        const validators = [];
        if (f.isRequired) validators.push(Validators.required);
        if (f.validationRules?.min !== undefined) validators.push(Validators.min(f.validationRules.min));
        if (f.validationRules?.max !== undefined) validators.push(Validators.max(f.validationRules.max));
        if (f.validationRules?.minLength) validators.push(Validators.minLength(f.validationRules.minLength));
        if (f.validationRules?.maxLength) validators.push(Validators.maxLength(f.validationRules.maxLength));
        if (f.validationRules?.pattern) validators.push(Validators.pattern(f.validationRules.pattern));
        const defaultVal = f.defaultValue ?? (f.specificType === FieldTypeDto.Checkbox ? false : '');
        this.form.addControl(f.fieldId, new FormControl({ value: defaultVal, disabled: f.isReadonly }, validators));
      } else if (field.$type === 'container') {
        const c = field as ContainerField;
        if (c.container === ContainerTypeDto.TabGroup) {
          for (const tab of (c as TabsField).children) this.buildFormControls(tab.children);
        } else if (c.container === ContainerTypeDto.Tab) {
          this.buildFormControls((c as TabField).children);
        } else if (c.container === ContainerTypeDto.Section) {
          this.buildFormControls((c as SectionField).children);
        } else if (c.container === ContainerTypeDto.Group) {
          this.buildFormControls((c as GroupField).children);
        }
      }
    }
  }

  private collectTables(fields: BaseField[]) {
    for (const field of fields) {
      if (field.$type === 'table') {
        const t = field as TableField;
        // ⭐ Use rows from API if available, otherwise create empty rows
        if (t.rows && t.rows.length > 0) {
          this.tableRows[t.fieldId] = t.rows;
          console.log(`📊 Table ${t.fieldId}: Using ${t.rows.length} rows from API`);
        } else {
          this.tableRows[t.fieldId] = Array.from({ length: t.minRows }, () =>
            Object.fromEntries(t.columns.map(c => [c.fieldId, '']))
          );
          console.log(`📊 Table ${t.fieldId}: Created ${t.minRows} empty rows`);
        }
      } else if (field.$type === 'container') {
        const c = field as ContainerField;
        if (c.container === ContainerTypeDto.TabGroup) {
          for (const tab of (c as TabsField).children) this.collectTables(tab.children);
        } else if (c.container === ContainerTypeDto.Tab) {
          this.collectTables((c as TabField).children);
        } else if (c.container === ContainerTypeDto.Section) {
          this.collectTables((c as SectionField).children);
        } else if (c.container === ContainerTypeDto.Group) {
          this.collectTables((c as GroupField).children);
        }
      }
    }
  }

  private initCollapsedState(fields: BaseField[]) {
    for (const field of fields) {
      if (field.$type === 'container') {
        const c = field as ContainerField;
        if (c.container === ContainerTypeDto.Section) {
          this.collapsedMap[c.fieldId] = (c as SectionField).isCollapsed;
          this.initCollapsedState((c as SectionField).children);
        } else if (c.container === ContainerTypeDto.Group) {
          this.collapsedMap[c.fieldId] = (c as GroupField).isCollapsed;
          this.initCollapsedState((c as GroupField).children);
        } else if (c.container === ContainerTypeDto.TabGroup) {
          for (const tab of (c as TabsField).children) this.initCollapsedState(tab.children);
        }
      }
    }
  }

  onSubmit() {
    if (this.form.valid) {
      console.log('Form values:', this.form.value);
      console.log('Table rows:', this.tableRows);
    } else {
      this.form.markAllAsTouched();
    }
  }
}
