/**
 * Custom Template Form Component
 * Allows Manager/Admin to create or edit custom templates
 * Dynamically loads fields from selected bank template and allows saving default values
 */

import { Component, OnInit, signal, computed, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { CustomTemplateService } from '../../services/custom-template.service';
import { TemplateService } from '../../services/template.service';
import { AuthService } from '../../services/auth.service';
import { CustomTemplate } from '../../models/custom-template.model';
import { ProcessedTemplateData, TemplateField, BankSpecificField } from '../../models';

@Component({
  selector: 'app-custom-template-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './custom-template-form.component.html',
  styleUrls: ['./custom-template-form.component.css']
})
export class CustomTemplateFormComponent implements OnInit {
  private readonly customTemplateService = inject(CustomTemplateService);
  private readonly templateService = inject(TemplateService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly fb = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);

  // Signals for reactive state
  isLoading = signal<boolean>(false);
  isSaving = signal<boolean>(false);
  error = signal<string | null>(null);
  isEditMode = signal<boolean>(false);
  
  // Template data
  templateId = signal<string | null>(null);
  bankCode = signal<string>('');
  propertyType = signal<'land' | 'apartment' | ''>('');
  templateData = signal<ProcessedTemplateData | null>(null);
  existingTemplate = signal<CustomTemplate | null>(null);

  // Forms
  metadataForm!: FormGroup;
  fieldsForm!: FormGroup;

  // Active tab state
  activeSection = signal<'metadata' | 'fields'>('metadata');
  activeBankSpecificTab = signal<string | null>(null);

  // Computed
  canSave = computed(() => {
    return this.metadataForm?.valid && !this.isSaving();
  });

  ngOnInit(): void {
    this.initializeForms();
    this.loadRouteParams();
  }

  private initializeForms(): void {
    this.metadataForm = this.fb.group({
      templateName: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]],
      description: ['', Validators.maxLength(500)]
    });

    this.fieldsForm = this.fb.group({});
  }

  private loadRouteParams(): void {
    // Check if editing existing template
    const templateId = this.route.snapshot.paramMap.get('id');
    
    if (templateId) {
      // Edit mode
      this.isEditMode.set(true);
      this.templateId.set(templateId);
      this.loadExistingTemplate(templateId);
    } else {
      // Create mode - get bank and property type from query params
      this.route.queryParams.subscribe(params => {
        const bankCode = params['bankCode'];
        const propertyType = params['propertyType'] as 'land' | 'apartment';
        
        if (!bankCode || !propertyType) {
          this.error.set('Missing bank code or property type');
          setTimeout(() => this.router.navigate(['/custom-templates']), 2000);
          return;
        }

        this.bankCode.set(bankCode);
        this.propertyType.set(propertyType);
        this.loadTemplateFields();
      });
    }
  }

  private loadExistingTemplate(templateId: string): void {
    this.isLoading.set(true);
    
    this.customTemplateService.getTemplate(templateId).subscribe({
      next: (template) => {
        this.existingTemplate.set(template);
        this.bankCode.set(template.bankCode);
        this.propertyType.set(template.propertyType);
        
        // Populate metadata form
        this.metadataForm.patchValue({
          templateName: template.templateName,
          description: template.description || ''
        });

        // Load field structure
        this.loadTemplateFields();
      },
      error: (error) => {
        console.error('❌ Failed to load template:', error);
        this.error.set('Failed to load template');
        this.isLoading.set(false);
      }
    });
  }

  private loadTemplateFields(): void {
    const bankCode = this.bankCode();
    const propertyType = this.propertyType();
    
    if (!bankCode || !propertyType) return;

    this.isLoading.set(true);
    
    this.customTemplateService.getTemplateFields(bankCode, propertyType).subscribe({
      next: (response) => {
        // Process template data using TemplateService
        // Cast response to AggregatedTemplateResponse type for processing
        const processedData = this.templateService.processTemplateData(response as any);
        this.templateData.set(processedData);
        
        // Build form controls for all fields
        this.buildFieldControls(processedData);
        
        // If editing, populate with existing values
        if (this.existingTemplate()) {
          this.populateFieldValues(this.existingTemplate()!.fieldValues);
        }

        // Initialize first tab if available
        if (processedData.bankSpecificTabs.length > 0) {
          this.activeBankSpecificTab.set(processedData.bankSpecificTabs[0].tabId);
        }

        this.isLoading.set(false);
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('❌ Failed to load template fields:', error);
        this.error.set('Failed to load template field structure');
        this.isLoading.set(false);
      }
    });
  }

  private buildFieldControls(data: ProcessedTemplateData): void {
    const formGroup: any = {};

    // Add common fields
    data.commonFieldGroups.forEach(group => {
      group.fields.forEach(field => {
        formGroup[field.fieldId] = [''];
      });
    });

    // Add bank-specific fields
    data.bankSpecificTabs.forEach(tab => {
      // Tab-level fields
      tab.fields.forEach(field => {
        if (field.fieldType !== 'group') {
          formGroup[field.fieldId] = [''];
        } else if (field.subFields) {
          // Add sub-fields from group fields
          field.subFields.forEach(subField => {
            formGroup[subField.fieldId] = [''];
          });
        }
      });

      // Section-level fields
      if (tab.sections) {
        tab.sections.forEach(section => {
          section.fields.forEach(field => {
            if (field.fieldType !== 'group') {
              formGroup[field.fieldId] = [''];
            } else if (field.subFields) {
              field.subFields.forEach(subField => {
                formGroup[subField.fieldId] = [''];
              });
            }
          });
        });
      }
    });

    this.fieldsForm = this.fb.group(formGroup);
  }

  private populateFieldValues(fieldValues: Record<string, any>): void {
    if (!fieldValues || !this.fieldsForm) return;

    Object.keys(fieldValues).forEach(key => {
      if (this.fieldsForm.contains(key)) {
        this.fieldsForm.patchValue({ [key]: fieldValues[key] });
      }
    });
  }

  onSectionChange(section: 'metadata' | 'fields'): void {
    this.activeSection.set(section);
  }

  onBankTabChange(tabId: string): void {
    this.activeBankSpecificTab.set(tabId);
  }

  goBack(): void {
    this.router.navigate(['/custom-templates']);
  }

  onSubmit(): void {
    if (!this.canSave()) {
      return;
    }

    this.isSaving.set(true);
    this.error.set(null);

    // Get metadata
    const metadata = this.metadataForm.value;

    // Get all field values (only non-empty values to save storage)
    const fieldValues: Record<string, any> = {};
    Object.keys(this.fieldsForm.value).forEach(key => {
      const value = this.fieldsForm.value[key];
      if (value !== null && value !== undefined && value !== '') {
        fieldValues[key] = value;
      }
    });

    if (this.isEditMode()) {
      // Update existing template
      this.updateTemplate(metadata, fieldValues);
    } else {
      // Create new template
      this.createTemplate(metadata, fieldValues);
    }
  }

  private createTemplate(metadata: any, fieldValues: Record<string, any>): void {
    const request = {
      templateName: metadata.templateName,
      description: metadata.description,
      bankCode: this.bankCode(),
      propertyType: this.propertyType() as 'land' | 'apartment',
      fieldValues
    };

    this.customTemplateService.createTemplate(request).subscribe({
      next: (template) => {
        console.log('✅ Template created successfully:', template);
        alert('Template created successfully!');
        this.router.navigate(['/custom-templates']);
      },
      error: (error) => {
        console.error('❌ Failed to create template:', error);
        const errorMsg = error.error?.error || 'Failed to create template';
        this.error.set(errorMsg);
        this.isSaving.set(false);
      }
    });
  }

  private updateTemplate(metadata: any, fieldValues: Record<string, any>): void {
    const request = {
      templateName: metadata.templateName,
      description: metadata.description,
      fieldValues
    };

    this.customTemplateService.updateTemplate(this.templateId()!, request).subscribe({
      next: (template) => {
        console.log('✅ Template updated successfully:', template);
        alert('Template updated successfully!');
        this.router.navigate(['/custom-templates']);
      },
      error: (error) => {
        console.error('❌ Failed to update template:', error);
        const errorMsg = error.error?.error || 'Failed to update template';
        this.error.set(errorMsg);
        this.isSaving.set(false);
      }
    });
  }

  // Helper methods for templates

  getFieldValue(fieldId: string): any {
    return this.fieldsForm.get(fieldId)?.value || '';
  }

  setFieldValue(fieldId: string, value: any): void {
    if (this.fieldsForm.contains(fieldId)) {
      this.fieldsForm.patchValue({ [fieldId]: value });
    }
  }

  isFieldFilled(fieldId: string): boolean {
    const value = this.getFieldValue(fieldId);
    return value !== null && value !== undefined && value !== '';
  }

  clearAllFields(): void {
    if (confirm('Are you sure you want to clear all field values? This will reset the form.')) {
      this.fieldsForm.reset();
    }
  }

  getFilledFieldsCount(): number {
    let count = 0;
    Object.keys(this.fieldsForm.value).forEach(key => {
      if (this.isFieldFilled(key)) {
        count++;
      }
    });
    return count;
  }

  getTotalFieldsCount(): number {
    return Object.keys(this.fieldsForm.controls).length;
  }
}
