import { Component, Input, Output, EventEmitter, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, FormControl, Validators, AbstractControl, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import { 
  TemplateSnapshot, 
  TemplateSection, 
  TemplateField, 
  ValuationReport 
} from '../../models/template-versioning.models';
import { TemplateVersioningService } from '../../services/template-versioning.service';

/**
 * Dynamic Form Component
 * Renders forms dynamically based on template snapshots from the versioning system
 * Supports all SBI Land field types, calculations, and conditional logic
 */
@Component({
  selector: 'app-dynamic-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './dynamic-form.component.html',
  styleUrls: ['./dynamic-form.component.css']
})
export class DynamicFormComponent implements OnInit, OnDestroy {
  @Input() templateSnapshot!: TemplateSnapshot;
  @Input() initialData: Record<string, any> = {};
  @Input() mode: 'create' | 'edit' | 'view' = 'create';
  @Input() reportId?: string;
  
  @Output() dataChange = new EventEmitter<Record<string, any>>();
  @Output() formValid = new EventEmitter<boolean>();
  @Output() save = new EventEmitter<Record<string, any>>();
  @Output() submit = new EventEmitter<Record<string, any>>();
  @Output() cancel = new EventEmitter<void>();

  form!: FormGroup;
  formData: Record<string, any> = {};
  calculatedFields: Record<string, any> = {};
  conditionalFields: Record<string, boolean> = {};
  
  private destroy$ = new Subject<void>();
  private calculationDebounce$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private templateService: TemplateVersioningService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.initializeForm();
    this.setupCalculations();
    this.setupConditionalLogic();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Initialize the reactive form based on template structure
   */
  private initializeForm(): void {
    const formControls: Record<string, any> = {};
    
    this.templateSnapshot.template.sections.forEach((section: TemplateSection) => {
      this.processSectionFields(section.fields, formControls, '');
    });
    
    this.form = this.fb.group(formControls);
    
    // Set initial data
    if (this.initialData && Object.keys(this.initialData).length > 0) {
      this.form.patchValue(this.initialData);
      this.formData = { ...this.initialData };
    }
    
    // Watch for form changes
    this.form.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      takeUntil(this.destroy$)
    ).subscribe(value => {
      this.formData = value;
      this.dataChange.emit(value);
      this.formValid.emit(this.form.valid);
      this.calculationDebounce$.next();
    });
    
    // Initial validation
    this.formValid.emit(this.form.valid);
  }

  /**
   * Process section fields and create form controls
   */
  private processSectionFields(fields: TemplateField[], formControls: Record<string, any>, parentPath: string): void {
    fields.forEach(field => {
      const fieldPath = parentPath ? `${parentPath}.${field.fieldId}` : field.fieldId;
      
      switch (field.fieldType) {
        case 'group':
          if (field.subFields) {
            const groupControls: Record<string, any> = {};
            this.processSectionFields(field.subFields, groupControls, fieldPath);
            formControls[field.fieldId] = this.fb.group(groupControls);
          }
          break;
          
        case 'table':
          formControls[field.fieldId] = this.createTableFormArray(field);
          break;
          
        case 'dynamic_table':
          formControls[field.fieldId] = this.createDynamicTableFormArray(field);
          break;
          
        default:
          formControls[field.fieldId] = this.createFieldControl(field);
          break;
      }
    });
  }

  /**
   * Create form control for individual field
   */
  private createFieldControl(field: TemplateField): FormControl {
    const validators = [];
    
    if (field.isRequired) {
      validators.push(Validators.required);
    }
    
    if (field.validation) {
      if (field.validation.min !== undefined) {
        validators.push(Validators.min(field.validation.min));
      }
      if (field.validation.max !== undefined) {
        validators.push(Validators.max(field.validation.max));
      }
      if (field.validation.pattern) {
        validators.push(Validators.pattern(field.validation.pattern));
      }
    }
    
    const defaultValue = this.getFieldDefaultValue(field);
    const control = new FormControl({ 
      value: defaultValue, 
      disabled: field.isReadonly || this.mode === 'view' 
    }, validators);
    
    return control;
  }

  /**
   * Get default value for field
   */
  private getFieldDefaultValue(field: TemplateField): any {
    if (field.defaultValue !== undefined) {
      return field.defaultValue;
    }
    
    switch (field.fieldType) {
      case 'number':
      case 'currency':
        return 0;
      case 'select':
        return field.options?.[0]?.value || '';
      default:
        return '';
    }
  }

  /**
   * Create form array for static table fields
   */
  private createTableFormArray(field: TemplateField): FormArray {
    const formArray = this.fb.array([]);
    
    if (field.rows && field.columns) {
      field.rows.forEach((row: any) => {
        const rowGroup: Record<string, FormControl> = {};
        
        field.columns!.forEach((column: any) => {
          const value = row[column.columnId] || '';
          const disabled = column.isReadonly || this.mode === 'view';
          rowGroup[column.columnId] = new FormControl({ value, disabled });
        });
        
        formArray.push(this.fb.group(rowGroup) as any);
      });
    }
    
    return formArray;
  }

  /**
   * Create form array for dynamic table fields
   */
  private createDynamicTableFormArray(field: TemplateField): FormArray {
    const formArray = this.fb.array([]);
    
    if (field.tableConfig?.rows) {
      field.tableConfig.rows.forEach((row: any) => {
        const rowGroup: Record<string, FormControl> = {};
        
        // Add fixed columns
        field.tableConfig!.fixedColumns?.forEach((column: any) => {
          const value = row[column.columnId] || '';
          const disabled = column.isReadonly || this.mode === 'view';
          rowGroup[column.columnId] = new FormControl({ value, disabled });
        });
        
        // Add dynamic columns if they exist in the row
        Object.keys(row).forEach(key => {
          if (!rowGroup[key]) {
            rowGroup[key] = new FormControl(row[key]);
          }
        });
        
        formArray.push(this.fb.group(rowGroup) as any);
      });
    }
    
    return formArray;
  }

  /**
   * Setup real-time calculations
   */
  private setupCalculations(): void {
    this.calculationDebounce$.pipe(
      debounceTime(500),
      takeUntil(this.destroy$)
    ).subscribe(() => {
      this.performCalculations();
    });
  }

  /**
   * Perform calculations for formula fields
   */
  private performCalculations(): void {
    const calculations = this.templateService.calculateFields(this.formData, this.templateSnapshot);
    
    Object.keys(calculations).forEach(fieldId => {
      const value = calculations[fieldId];
      this.calculatedFields[fieldId] = value;
      
      // Update form control if it exists
      const control = this.getFormControl(fieldId);
      if (control && !control.disabled) {
        control.setValue(value, { emitEvent: false });
      }
    });
    
    this.cdr.detectChanges();
  }

  /**
   * Setup conditional logic for fields
   */
  private setupConditionalLogic(): void {
    const allFields = this.getAllFields();
    
    allFields.forEach(field => {
      if (field.conditionalLogic) {
        this.evaluateConditionalLogic(field);
      }
    });
    
    // Watch for changes in conditional trigger fields
    this.form.valueChanges.pipe(
      takeUntil(this.destroy$)
    ).subscribe(() => {
      allFields.forEach(field => {
        if (field.conditionalLogic) {
          this.evaluateConditionalLogic(field);
        }
      });
    });
  }

  /**
   * Evaluate conditional logic for a field
   */
  private evaluateConditionalLogic(field: TemplateField): void {
    if (!field.conditionalLogic) return;
    
    const { field: triggerField, operator, value } = field.conditionalLogic;
    const triggerValue = this.getFieldValue(triggerField);
    
    let isVisible = false;
    
    switch (operator) {
      case '==':
        isVisible = triggerValue === value;
        break;
      case '!=':
        isVisible = triggerValue !== value;
        break;
      case '>':
        isVisible = triggerValue > value;
        break;
      case '<':
        isVisible = triggerValue < value;
        break;
      case 'contains':
        isVisible = String(triggerValue).includes(String(value));
        break;
    }
    
    this.conditionalFields[field.fieldId] = isVisible;
    
    // Enable/disable form control based on visibility
    const control = this.getFormControl(field.fieldId);
    if (control) {
      if (isVisible) {
        control.enable({ emitEvent: false });
      } else {
        control.disable({ emitEvent: false });
        control.setValue('', { emitEvent: false });
      }
    }
  }

  /**
   * Get all fields from template (including nested fields)
   */
  private getAllFields(): TemplateField[] {
    const fields: TemplateField[] = [];
    
    this.templateSnapshot.template.sections.forEach((section: TemplateSection) => {
      this.addFieldsRecursively(section.fields, fields);
    });
    
    return fields;
  }

  /**
   * Add fields recursively including subFields
   */
  private addFieldsRecursively(fields: TemplateField[], allFields: TemplateField[]): void {
    fields.forEach(field => {
      allFields.push(field);
      
      if (field.subFields) {
        this.addFieldsRecursively(field.subFields, allFields);
      }
    });
  }

  /**
   * Get form control by field ID (supports nested paths)
   */
  private getFormControl(fieldId: string): AbstractControl | null {
    return this.form.get(fieldId);
  }

  /**
   * Get field value from form data
   */
  private getFieldValue(fieldId: string): any {
    const keys = fieldId.split('.');
    let value = this.formData;
    
    for (const key of keys) {
      value = value?.[key];
      if (value === undefined) break;
    }
    
    return value;
  }

  /**
   * Check if field should be visible based on conditional logic
   */
  isFieldVisible(field: TemplateField): boolean {
    if (!field.conditionalLogic) return true;
    return this.conditionalFields[field.fieldId] !== false;
  }

  /**
   * Get calculated value for field
   */
  getCalculatedValue(fieldId: string): any {
    return this.calculatedFields[fieldId];
  }

  /**
   * Add row to dynamic table
   */
  addTableRow(field: TemplateField): void {
    const formArray = this.form.get(field.fieldId) as FormArray;
    if (!formArray) return;
    
    const rowGroup: Record<string, FormControl> = {};
    
    // Add controls for fixed columns
    field.tableConfig?.fixedColumns?.forEach((column: any) => {
      rowGroup[column.columnId] = new FormControl('');
    });
    
    formArray.push(this.fb.group(rowGroup));
  }

  /**
   * Remove row from dynamic table
   */
  removeTableRow(field: TemplateField, index: number): void {
    const formArray = this.form.get(field.fieldId) as FormArray;
    if (formArray && index >= 0 && index < formArray.length) {
      formArray.removeAt(index);
    }
  }

  /**
   * Get form array for table field
   */
  getTableFormArray(fieldId: string): FormArray {
    return this.form.get(fieldId) as FormArray;
  }

  /**
   * Handle form save
   */
  onSave(): void {
    if (this.form.valid) {
      this.save.emit(this.formData);
    }
  }

  /**
   * Handle form submit
   */
  onSubmit(): void {
    if (this.form.valid) {
      this.submit.emit(this.formData);
    }
  }

  /**
   * Handle form cancel
   */
  onCancel(): void {
    this.cancel.emit();
  }

  /**
   * Reset form to initial state
   */
  resetForm(): void {
    this.form.reset();
    if (this.initialData) {
      this.form.patchValue(this.initialData);
    }
  }

  /**
   * Get field error message
   */
  getFieldErrorMessage(field: TemplateField): string {
    const control = this.getFormControl(field.fieldId);
    
    if (!control?.errors) return '';
    
    if (control.errors['required']) {
      return `${field.uiDisplayName} is required`;
    }
    
    if (control.errors['min']) {
      return `Minimum value is ${field.validation?.min}`;
    }
    
    if (control.errors['max']) {
      return `Maximum value is ${field.validation?.max}`;
    }
    
    if (control.errors['pattern']) {
      return field.validation?.message || 'Invalid format';
    }
    
    return 'Invalid value';
  }

  /**
   * Get information text for field tooltip
   * Prioritizes placeholder text over helpText
   */
  getFieldInfoText(field: TemplateField): string {
    if (field.placeholder && field.placeholder.trim()) {
      return field.placeholder;
    }
    
    if (field.helpText && field.helpText.trim()) {
      return field.helpText;
    }
    
    return '';
  }
}