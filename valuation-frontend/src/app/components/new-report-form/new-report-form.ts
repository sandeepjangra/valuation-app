import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
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

@Component({
  selector: 'app-new-report-form',
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './new-report-form.html',
  styleUrl: './new-report-form.css',
})
export class NewReportForm {

  // Expose enums to template
  FieldTypeDto = FieldTypeDto;
  ContainerTypeDto = ContainerTypeDto;

  // Active tab index per TabsField: key = TabsField.fieldId, value = active tab index
  activeTabMap: Record<string, number> = {};

  // Collapsed state per SectionField / GroupField
  collapsedMap: Record<string, boolean> = {};

  // Reactive form — one FormControl per InputField (built recursively)
  form = new FormGroup({});

  // Table rows: key = TableField.fieldId, value = array of row objects
  tableRows: Record<string, Record<string, any>[]> = {};

  // ── Sample template object matching the new C# hierarchy ─────────────────
  template: ValuationTemplate = {
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

      // ── Root-level InputField (no tab, rendered directly) ──────────────
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

      // ── TabsField (containerType = TabGroup) ───────────────────────────
      // Children are TabField[] — each TabField is one tab panel
      {
        $type: 'container',
        fieldId: 'tabs_main',
        label: 'Main Tabs',
        displayOrder: 1,
        fieldType: FieldTypeDto.Container,
        isVisible: true,
        container: ContainerTypeDto.TabGroup,
        children: [

          // ── Tab 1: Property Details ──────────────────────────────────
          {
            $type: 'container',
            fieldId: 'tab_property_details',
            label: 'Property Details',
            displayOrder: 0,
            fieldType: FieldTypeDto.Tab,
            isVisible: true,
            container: ContainerTypeDto.Tab,
            children: [

              // SectionField inside Tab
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
                  {
                    $type: 'input', fieldId: 'property_address', label: 'Property Address',
                    displayOrder: 0, fieldType: FieldTypeDto.Textarea, isVisible: true,
                    specificType: FieldTypeDto.Textarea, isRequired: true, isReadonly: false,
                    placeholderText: 'Enter full property address'
                  } as InputField,
                  {
                    $type: 'input', fieldId: 'city', label: 'City / Town',
                    displayOrder: 1, fieldType: FieldTypeDto.Text, isVisible: true,
                    specificType: FieldTypeDto.Text, isRequired: true, isReadonly: false,
                    placeholderText: 'City or town name'
                  } as InputField,
                  {
                    $type: 'input', fieldId: 'state', label: 'State',
                    displayOrder: 2, fieldType: FieldTypeDto.Dropdown, isVisible: true,
                    specificType: FieldTypeDto.Dropdown, isRequired: true, isReadonly: false,
                    options: ['Andhra Pradesh', 'Delhi', 'Gujarat', 'Karnataka', 'Maharashtra', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal']
                  } as InputField,
                  {
                    $type: 'input', fieldId: 'pin_code', label: 'PIN Code',
                    displayOrder: 3, fieldType: FieldTypeDto.Text, isVisible: true,
                    specificType: FieldTypeDto.Text, isRequired: true, isReadonly: false,
                    placeholderText: '6-digit PIN code',
                    validationRules: { pattern: '^[1-9][0-9]{5}$', errorMessage: 'Enter a valid 6-digit PIN code' }
                  } as InputField
                ]
              } as SectionField,

              // GroupField inside Tab
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
                  {
                    $type: 'input', fieldId: 'land_area', label: 'Land Area (sq ft)',
                    displayOrder: 0, fieldType: FieldTypeDto.Number, isVisible: true,
                    specificType: FieldTypeDto.Number, isRequired: true, isReadonly: false,
                    validationRules: { min: 1 }
                  } as InputField,
                  {
                    $type: 'input', fieldId: 'land_shape', label: 'Land Shape',
                    displayOrder: 1, fieldType: FieldTypeDto.Dropdown, isVisible: true,
                    specificType: FieldTypeDto.Dropdown, isRequired: false, isReadonly: false,
                    options: ['Regular', 'Irregular', 'Corner Plot', 'L-Shaped']
                  } as InputField,
                  {
                    $type: 'input', fieldId: 'road_width', label: 'Road Width (ft)',
                    displayOrder: 2, fieldType: FieldTypeDto.Number, isVisible: true,
                    specificType: FieldTypeDto.Number, isRequired: false, isReadonly: false
                  } as InputField,
                  {
                    $type: 'input', fieldId: 'is_corner_plot', label: 'Corner Plot?',
                    displayOrder: 3, fieldType: FieldTypeDto.Checkbox, isVisible: true,
                    specificType: FieldTypeDto.Checkbox, isRequired: false, isReadonly: false
                  } as InputField
                ]
              } as GroupField,

              // TableField inside Tab
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

          // ── Tab 2: Valuation ─────────────────────────────────────────
          {
            $type: 'container',
            fieldId: 'tab_valuation',
            label: 'Valuation',
            displayOrder: 1,
            fieldType: FieldTypeDto.Tab,
            isVisible: true,
            container: ContainerTypeDto.Tab,
            children: [
              {
                $type: 'input', fieldId: 'valuation_date', label: 'Valuation Date',
                displayOrder: 0, fieldType: FieldTypeDto.Date, isVisible: true,
                specificType: FieldTypeDto.Date, isRequired: true, isReadonly: false
              } as InputField,
              {
                $type: 'input', fieldId: 'rate_per_sqft', label: 'Market Rate (₹/sq ft)',
                displayOrder: 1, fieldType: FieldTypeDto.Currency, isVisible: true,
                specificType: FieldTypeDto.Currency, isRequired: true, isReadonly: false,
                validationRules: { min: 0 }
              } as InputField,
              {
                $type: 'input', fieldId: 'estimated_value', label: 'Estimated Value (₹)',
                displayOrder: 2, fieldType: FieldTypeDto.Currency, isVisible: true,
                specificType: FieldTypeDto.Currency, isRequired: false, isReadonly: true,
                helpText: 'Auto-calculated: Land Area × Market Rate'
              } as InputField,
              {
                $type: 'input', fieldId: 'valuation_purpose', label: 'Purpose of Valuation',
                displayOrder: 3, fieldType: FieldTypeDto.Dropdown, isVisible: true,
                specificType: FieldTypeDto.Dropdown, isRequired: true, isReadonly: false,
                options: ['Home Loan', 'Mortgage', 'Sale', 'Insurance', 'Legal', 'Other']
              } as InputField,
              {
                $type: 'input', fieldId: 'valuation_remarks', label: 'Remarks',
                displayOrder: 4, fieldType: FieldTypeDto.Textarea, isVisible: true,
                specificType: FieldTypeDto.Textarea, isRequired: false, isReadonly: false,
                placeholderText: 'Any additional remarks...'
              } as InputField,
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

          // ── Tab 3: Documents ─────────────────────────────────────────
          {
            $type: 'container',
            fieldId: 'tab_documents',
            label: 'Documents',
            displayOrder: 2,
            fieldType: FieldTypeDto.Tab,
            isVisible: true,
            container: ContainerTypeDto.Tab,
            children: [
              {
                $type: 'attachment', fieldId: 'title_deed', label: 'Title Deed',
                displayOrder: 0, fieldType: FieldTypeDto.FileUpload, isVisible: true,
                allowedExtensions: ['.pdf', '.jpg', '.png'], maxFileSize: 5242880,
                allowMultiple: false, category: AttachmentCategoryDto.LegalDocument
              } as AttachmentField,
              {
                $type: 'attachment', fieldId: 'property_photos', label: 'Property Photos',
                displayOrder: 1, fieldType: FieldTypeDto.FileUpload, isVisible: true,
                allowedExtensions: ['.jpg', '.jpeg', '.png'], maxFileSize: 10485760,
                allowMultiple: true, category: AttachmentCategoryDto.PropertyPhoto
              } as AttachmentField,
              {
                $type: 'attachment', fieldId: 'site_map', label: 'Site Map / Sketch',
                displayOrder: 2, fieldType: FieldTypeDto.FileUpload, isVisible: true,
                allowedExtensions: ['.pdf', '.jpg', '.png'], maxFileSize: 5242880,
                allowMultiple: false, category: AttachmentCategoryDto.MapOrSketch
              } as AttachmentField
            ]
          } as TabField

        ]
      } as TabsField

    ]
  };

  constructor() {
    this.initForm();
    this.initTables();
    this.initActiveTabs();
  }

  // ── Initialisation ────────────────────────────────────────────────────────

  private initForm() {
    this.buildFormControls(this.template.elements);
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
        // TabsField children are TabField[], each TabField has BaseField[] children
        if (c.container === ContainerTypeDto.TabGroup) {
          for (const tab of (c as TabsField).children) {
            this.buildFormControls(tab.children);
          }
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

  private initTables() {
    this.collectTables(this.template.elements);
  }

  private collectTables(fields: BaseField[]) {
    for (const field of fields) {
      if (field.$type === 'table') {
        const t = field as TableField;
        this.tableRows[t.fieldId] = Array.from({ length: t.minRows }, () =>
          Object.fromEntries(t.columns.map(c => [c.fieldId, '']))
        );
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

  private initActiveTabs() {
    this.setDefaultTabs(this.template.elements);
  }

  private setDefaultTabs(fields: BaseField[]) {
    for (const field of fields) {
      if (field.$type === 'container') {
        const c = field as ContainerField;
        if (c.container === ContainerTypeDto.TabGroup) {
          // Default to first tab active
          this.activeTabMap[c.fieldId] = 0;
          for (const tab of (c as TabsField).children) this.setDefaultTabs(tab.children);
        } else if (c.container === ContainerTypeDto.Section) {
          this.collapsedMap[c.fieldId] = (c as SectionField).isCollapsed;
          this.setDefaultTabs((c as SectionField).children);
        } else if (c.container === ContainerTypeDto.Group) {
          this.collapsedMap[c.fieldId] = (c as GroupField).isCollapsed;
          this.setDefaultTabs((c as GroupField).children);
        }
      }
    }
  }

  // ── Type cast helpers (used in template) ─────────────────────────────────

  asInput(f: BaseField): InputField         { return f as InputField; }
  asTabsField(f: BaseField): TabsField      { return f as TabsField; }
  asTabField(f: BaseField): TabField        { return f as TabField; }
  asSection(f: BaseField): SectionField     { return f as SectionField; }
  asGroup(f: BaseField): GroupField         { return f as GroupField; }
  asTable(f: BaseField): TableField         { return f as TableField; }
  asAttachment(f: BaseField): AttachmentField { return f as AttachmentField; }

  // ── Tab helpers ───────────────────────────────────────────────────────────

  setActiveTab(tabsFieldId: string, index: number) {
    this.activeTabMap[tabsFieldId] = index;
  }

  // ── Collapse helpers ──────────────────────────────────────────────────────

  toggleCollapse(fieldId: string) {
    this.collapsedMap[fieldId] = !this.collapsedMap[fieldId];
  }

  isCollapsed(fieldId: string): boolean {
    return !!this.collapsedMap[fieldId];
  }

  // ── Table helpers ─────────────────────────────────────────────────────────

  addRow(tableId: string, table: TableField) {
    this.tableRows[tableId].push(Object.fromEntries(table.columns.map(c => [c.fieldId, ''])));
  }

  removeRow(tableId: string, index: number) {
    const rows = this.tableRows[tableId];
    if (rows.length > 1) rows.splice(index, 1);
  }

  getColumnSum(tableId: string, colId: string): number {
    return (this.tableRows[tableId] || []).reduce((sum, row) => sum + (parseFloat(row[colId]) || 0), 0);
  }

  // ── Form submission ───────────────────────────────────────────────────────

  onSubmit() {
    if (this.form.valid) {
      console.log('Form values:', this.form.value);
      console.log('Table rows:', this.tableRows);
    } else {
      this.form.markAllAsTouched();
    }
  }

  hasError(fieldId: string): boolean {
    const ctrl = this.form.get(fieldId);
    return !!(ctrl && ctrl.invalid && ctrl.touched);
  }

  getErrorMessage(fieldId: string, field: InputField): string {
    const ctrl = this.form.get(fieldId);
    if (!ctrl?.errors) return '';
    if (ctrl.errors['required'])   return `${field.label} is required`;
    if (ctrl.errors['minlength'])  return `Minimum ${field.validationRules?.minLength} characters required`;
    if (ctrl.errors['maxlength'])  return `Maximum ${field.validationRules?.maxLength} characters allowed`;
    if (ctrl.errors['min'])        return `Minimum value is ${field.validationRules?.min}`;
    if (ctrl.errors['max'])        return `Maximum value is ${field.validationRules?.max}`;
    if (ctrl.errors['pattern'])    return field.validationRules?.errorMessage || 'Invalid format';
    return 'Invalid value';
  }

  formatFileSize(bytes: number): string {
    return bytes >= 1048576 ? `${(bytes / 1048576).toFixed(0)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
  }
}
