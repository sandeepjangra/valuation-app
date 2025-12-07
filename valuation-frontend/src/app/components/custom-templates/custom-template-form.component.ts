/**
 * Custom Template Form Component
 * Allows Manager/Admin to create or edit custom templates
 * Dynamically loads fields from selected bank template and allows saving default values
 */

import { Component, OnInit, signal, computed, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CustomTemplateService } from '../../services/custom-template.service';
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
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly fb = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);
  
  // HTTP client for direct testing
  private readonly http = inject(HttpClient);

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
  mainForm!: FormGroup; // For template metadata
  metadataForm!: FormGroup;
  fieldsForm!: FormGroup;

  // Removed tab state - no longer needed for simplified view

  // Computed
  canSave = computed(() => {
    // Only check if not currently saving
    // Authentication and form validation will be checked in onSubmit
    return !this.isSaving();
  });

  ngOnInit(): void {
    this.initializeForms();
    this.loadRouteParams();
  }

  private initializeForms(): void {
    // Main form for template metadata (matches HTML)
    // Make only templateName required, remove strict validators
    this.mainForm = this.fb.group({
      templateName: ['', [Validators.required, Validators.minLength(3)]],
      description: ['']
    });
    
    this.metadataForm = this.fb.group({
      templateName: ['', [Validators.required, Validators.minLength(3)]],
      description: ['']
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
    
    // Use the exact same template mapping as the Report Form component
    // The Report Form uses templateCode = this.selectedTemplateId.toLowerCase()
    // where selectedTemplateId comes from the New Report page's template selection
    const templateCode = `${propertyType}-property`; // This matches what New Report passes
    
    console.log(`🔄 Loading template fields for: ${bankCode}/${templateCode} (same as Report Form)`);
    
    this.customTemplateService.getTemplateFields(bankCode, propertyType).subscribe({
      next: (response) => {
        console.log('✅ Raw filtered API Response (Custom Template):', response);
        console.log('✅ API Response type:', typeof response);
        console.log('✅ API Response keys:', Object.keys(response));
        
        // Process template data - the filtered endpoint returns a different structure
        // Convert to ProcessedTemplateData format
        const allFields = [
          ...(response.commonFields || []),
          ...(response.bankSpecificTabs?.flatMap(tab => tab.fields || []) || [])
        ];

        const processedData: ProcessedTemplateData = {
          templateInfo: {
            templateId: response.templateInfo?.templateId || '',
            templateName: response.templateInfo?.templateName || '',
            bankCode: response.bankCode || this.bankCode(),
            bankName: response.templateInfo?.bankName || '',
            propertyType: response.propertyType || this.propertyType(),
            version: '1.0'
          },
          commonFieldGroups: response.commonFields ? [{
            groupName: 'Common Fields',
            displayName: 'Common Fields', 
            fields: response.commonFields
          }] : [],
          bankSpecificTabs: response.bankSpecificTabs || [],
          allFields: allFields,
          totalFieldCount: allFields.length
        };
        
        console.log('🔍 Processed template data (Custom Template vs Report Form comparison):', {
          commonFieldGroups: processedData.commonFieldGroups?.length || 0,
          bankSpecificTabs: processedData.bankSpecificTabs?.length || 0,
          totalFieldCount: processedData.totalFieldCount || 0,
          bankSpecificTabDetails: processedData.bankSpecificTabs?.map(tab => ({
            tabId: tab.tabId,
            tabName: tab.tabName,
            fieldsCount: tab.fields?.length || 0,
            sectionsCount: tab.sections?.length || 0,
            sectionsDetails: tab.sections?.map(section => ({
              sectionName: section.sectionName,
              fieldsCount: section.fields?.length || 0,
              fieldIds: section.fields?.map(f => f.fieldId) || []
            }))
          }))
        });
        
        // Log specific Property Details tab data
        const propertyDetailsTab = processedData.bankSpecificTabs?.find(tab => tab.tabId === 'property_details');
        if (propertyDetailsTab) {
          console.log('🏠 Property Details Tab Analysis:', {
            tabName: propertyDetailsTab.tabName,
            directFields: propertyDetailsTab.fields?.length || 0,
            sectionsCount: propertyDetailsTab.sections?.length || 0,
            totalSectionFields: propertyDetailsTab.sections?.reduce((total, section) => total + (section.fields?.length || 0), 0) || 0,
            sections: propertyDetailsTab.sections?.map(section => ({
              sectionName: section.sectionName,
              fieldsCount: section.fields?.length || 0,
              fieldsList: section.fields?.map(f => ({
                fieldId: f.fieldId,
                displayName: f.uiDisplayName,
                fieldType: f.fieldType,
                includeInCustomTemplate: (f as any).includeInCustomTemplate
              })) || []
            }))
          });
        }
        
        this.templateData.set(processedData);
        
        // Build form controls for ALL fields (but make only includeInCustomTemplate=true editable)
        this.buildFieldControls(processedData);
        
        // No tab initialization needed for simplified view
        
        // If editing, populate with existing values
        if (this.existingTemplate()) {
          this.populateFieldValues(this.existingTemplate()!.fieldValues);
          // Also populate mainForm metadata
          this.mainForm.patchValue({
            templateName: this.existingTemplate()!.templateName,
            description: this.existingTemplate()!.description
          });
        }

        // No tab initialization needed for simplified view

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
    const fieldIdsProcessed = new Set<string>(); // Track processed field IDs to avoid duplicates

    console.log('🔨 Building field controls...');

    // Helper function to add field controls with editable/readonly logic
    const addFieldControl = (field: any, source: string) => {
      if (field.fieldType !== 'group') {
        // Skip if already processed (handles duplicate fields in tab.fields and sections[].fields)
        if (fieldIdsProcessed.has(field.fieldId)) {
          console.log(`⏭️  Skipping duplicate field: ${field.fieldId} from ${source}`);
          return;
        }

        const isFieldActive = field.isActive !== false;
        // Create form control - all active fields should be editable in custom templates
        const control = this.fb.control('');
        // No need to disable controls - we handle editability in the template with readonly attribute
        formGroup[field.fieldId] = control;
        fieldIdsProcessed.add(field.fieldId);
        console.log(`✅ Added control for field: ${field.fieldId} (isActive: ${isFieldActive}, editable: ${isFieldActive}) from ${source}`);
      } else if (field.subFields) {
        // Add sub-fields from group fields
        field.subFields.forEach((subField: any) => {
          if (fieldIdsProcessed.has(subField.fieldId)) {
            console.log(`⏭️  Skipping duplicate subfield: ${subField.fieldId} from ${source}`);
            return;
          }

          const isSubFieldActive = subField.isActive !== false;
          const control = this.fb.control('');
          // No need to disable controls - we handle editability in the template with readonly attribute
          formGroup[subField.fieldId] = control;
          fieldIdsProcessed.add(subField.fieldId);
          console.log(`✅ Added control for subfield: ${subField.fieldId} (isActive: ${isSubFieldActive}, editable: ${isSubFieldActive}) from ${source}`);
        });
      }
    };

    // Skip common fields entirely for custom templates
    console.log('⏭️ Skipping common field groups for custom templates');

    // Add bank-specific fields (show all, editable based on includeInCustomTemplate flag)
    console.log('🏦 Processing bank-specific tabs:', data.bankSpecificTabs.length);
    data.bankSpecificTabs.forEach((tab, tabIdx) => {
      console.log(`  Tab ${tabIdx + 1}: ${tab.tabName} - ${tab.fields.length} tab-level fields, ${tab.sections?.length || 0} sections`);
      
      // Tab-level fields (only if no sections - to avoid duplicates)
      if (!tab.sections || tab.sections.length === 0) {
        tab.fields.forEach(field => {
          addFieldControl(field, `tab-${tab.tabName}`);
        });
      } else {
        console.log(`  ⏭️  Skipping tab-level fields for ${tab.tabName} because it has sections`);
      }

      // Section-level fields
      if (tab.sections) {
        tab.sections.forEach((section, secIdx) => {
          console.log(`    Section ${secIdx + 1}: ${section.sectionName} - ${section.fields.length} fields`);
          section.fields.forEach(field => {
            addFieldControl(field, `tab-${tab.tabName}-section-${section.sectionName}`);
          });
        });
      }
    });

    this.fieldsForm = this.fb.group(formGroup);
    console.log('✅ Form controls built successfully!');
    console.log(`📊 Total form controls created: ${Object.keys(formGroup).length}`);
    console.log(`📊 Unique fields processed: ${fieldIdsProcessed.size}`);
    console.log('📋 Form has these controls:', Object.keys(formGroup));
  }

  private populateFieldValues(fieldValues: Record<string, any>): void {
    if (!fieldValues || !this.fieldsForm) return;

    Object.keys(fieldValues).forEach(key => {
      if (this.fieldsForm.contains(key)) {
        this.fieldsForm.patchValue({ [key]: fieldValues[key] });
      }
    });
  }

  // Method removed - not needed for new structure

  // Removed tab change method - no longer needed

  goBack(): void {
    this.router.navigate(['/custom-templates']);
  }

  onSubmit(): void {
    // Mark form as touched to show validation errors
    this.mainForm.markAllAsTouched();
    
    // Check if template name is provided (minimum requirement)
    if (this.mainForm.invalid) {
      this.error.set('❌ Please fix the validation errors before saving');
      return;
    }
    
    const metadata = this.mainForm.value;
    if (!metadata.templateName || metadata.templateName.trim().length < 3) {
      this.error.set('❌ Template name is required (minimum 3 characters)');
      return;
    }

    // Check for token (more reliable than isAuthenticated signal)
    const token = this.authService.getToken();
    const orgContext = this.authService.getOrganizationContext();
    
    console.log('🔍 onSubmit - Authentication check:', {
      hasToken: !!token,
      tokenPreview: token?.substring(0, 30) + '...',
      orgContext: orgContext,
      orgShortName: orgContext?.orgShortName
    });
    
    if (!token) {
      this.error.set('❌ Not authenticated. Please log in again.');
      console.error('❌ No authentication token found');
      // Redirect to login after 2 seconds
      setTimeout(() => this.router.navigate(['/login']), 2000);
      return;
    }

    this.isSaving.set(true);
    this.error.set(null);

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

  /**
   * Filter template fields to only include those marked for custom templates
   */
  private filterFieldsForCustomTemplate(data: ProcessedTemplateData): ProcessedTemplateData {
    console.log('🔍 Filtering template fields for custom templates...');
    
    const filteredData = { ...data };
    
    // Filter bank-specific tabs
    filteredData.bankSpecificTabs = data.bankSpecificTabs.map(tab => {
      const filteredTab = { ...tab };
      
      // Filter tab-level fields
      filteredTab.fields = tab.fields.filter(field => {
        const includeInCustom = (field as any).includeInCustomTemplate;
        console.log(`Field ${field.fieldId}: includeInCustomTemplate = ${includeInCustom}`);
        return includeInCustom === true;
      }).map(field => {
        // If it's a group field, filter sub-fields too
        if (field.fieldType === 'group' && field.subFields) {
          return {
            ...field,
            subFields: field.subFields.filter(subField => 
              (subField as any).includeInCustomTemplate === true
            )
          };
        }
        return field;
      });
      
      // Filter section-level fields if sections exist
      if (tab.sections) {
        filteredTab.sections = tab.sections.map(section => ({
          ...section,
          fields: section.fields.filter(field => {
            const includeInCustom = (field as any).includeInCustomTemplate;
            console.log(`Section field ${field.fieldId}: includeInCustomTemplate = ${includeInCustom}`);
            return includeInCustom === true;
          }).map(field => {
            // If it's a group field, filter sub-fields too
            if (field.fieldType === 'group' && field.subFields) {
              return {
                ...field,
                subFields: field.subFields.filter(subField => 
                  (subField as any).includeInCustomTemplate === true
                )
              };
            }
            return field;
          })
        }));
      }
      
      return filteredTab;
    });
    
    // Also filter common field groups (though they might not be saved, we might show them)
    filteredData.commonFieldGroups = data.commonFieldGroups.map(group => ({
      ...group,
      fields: group.fields.filter(field => {
        const includeInCustom = (field as any).includeInCustomTemplate;
        return includeInCustom === true;
      })
    }));
    
    console.log('✅ Field filtering completed');
    console.log('Filtered tabs:', filteredData.bankSpecificTabs.map(tab => ({
      tabId: tab.tabId,
      fieldsCount: tab.fields.length,
      sectionsCount: tab.sections?.length || 0
    })));
    
    return filteredData;
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

  // Quick dev login with different org admin
  devLogin(): void {
    console.log('🔐 Performing dev login as admin in different org...');
    
    this.authService.loginWithDevToken('admin@demo-org.com', 'demo-org-001', 'manager').subscribe({
      next: (success) => {
        console.log('✅ Dev login successful:', success);
        alert('Dev login successful as admin in demo-org-001!');
      },
      error: (error) => {
        console.error('❌ Dev login failed:', error);
        alert('Dev login failed: ' + error.message);
      }
    });
  }

  // Test authentication connectivity
  testAuth(): void {
    console.log('🧪 Testing authentication...');
    
    // Check auth service state
    const isAuth = this.authService.isAuthenticated();
    const token = this.authService.getToken();
    const orgContext = this.authService.getOrganizationContext();
    
    console.log('🔍 Auth service state:', {
      isAuthenticated: isAuth,
      hasToken: !!token,
      tokenLength: token?.length || 0,
      tokenPreview: token?.substring(0, 30) + '...',
      orgContext: orgContext
    });
    
    if (!isAuth || !token) {
      console.log('❌ Not authenticated - no token available');
      alert('Not authenticated. Click "Dev Login" first.');
      return;
    }

    // Clear previous logs
    sessionStorage.removeItem('jwt-debug-logs');
    
    // Test basic auth endpoint
    this.http.get('http://localhost:8000/api/auth/me').subscribe({
      next: (response) => {
        console.log('✅ Auth test successful:', response);
        this.showDebugLogs();
        alert('Authentication test successful! Check console for debug logs.');
      },
      error: (error) => {
        console.error('❌ Auth test failed:', error);
        this.showDebugLogs();
        alert(`Auth test failed: ${error.status} ${error.statusText}. Check console for debug logs.`);
      }
    });
  }

  private showDebugLogs(): void {
    const logs = JSON.parse(sessionStorage.getItem('jwt-debug-logs') || '[]');
    console.log('📜 JWT Debug Logs:', logs);
    
    // Create downloadable log file
    const logContent = JSON.stringify(logs, null, 2);
    const blob = new Blob([logContent], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jwt-debug-${new Date().toISOString().slice(0, 19)}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    console.log('📁 Debug logs downloaded as JSON file');
  }

  // Removed tab navigation - no longer needed

  // Helper methods for template structure (same as New Report)
  hasCommonFields(): boolean {
    const data = this.templateData();
    return data ? data.commonFieldGroups?.length > 0 : false;
  }

  getCommonFieldGroups(): any[] {
    return []; // Always return empty for custom templates
  }

  getBankSpecificTabs(): any[] {
    return this.templateData()?.bankSpecificTabs || [];
  }

  // Field editability check (for custom template - all active fields should be editable)
  isFieldEditable(field: any): boolean {
    // For custom templates, all active fields should be editable
    const isEditable = field.isActive !== false;
    console.log(`🔍 Field editability check: ${field.fieldId} - isActive: ${field.isActive}, isEditable: ${isEditable}`);
    return isEditable;
  }

  // Field disabled check (matching New Report pattern - disabled if NOT editable)
  isFieldDisabled(field: any): boolean {
    return !this.isFieldEditable(field);
  }

  // Check if field is empty (for placeholder styling)
  isFieldEmpty(fieldId: string): boolean {
    const value = this.fieldsForm.get(fieldId)?.value;
    return value === null || value === undefined || value === '';
  }

  // Get field error message (matching New Report pattern)
  getFieldError(fieldId: string): string | null {
    const control = this.fieldsForm.get(fieldId);
    if (!control || !control.errors || !control.touched) return null;

    if (control.errors['required']) return 'This field is required';
    if (control.errors['minlength']) return `Minimum length is ${control.errors['minlength'].requiredLength}`;
    if (control.errors['maxlength']) return `Maximum length is ${control.errors['maxlength'].requiredLength}`;
    if (control.errors['pattern']) return 'Invalid format';
    if (control.errors['min']) return `Minimum value is ${control.errors['min'].min}`;
    if (control.errors['max']) return `Maximum value is ${control.errors['max'].max}`;

    return 'Invalid value';
  }

  // Removed bank-specific tab switching - no longer needed

  // Check if tab has sections
  tabHasSections(tab: any): boolean {
    return tab.sections && tab.sections.length > 0;
  }

  // Get tab sections
  getTabSections(tab: any): any[] {
    return tab.sections || [];
  }

  // Field validation helper
  isFieldInvalid(fieldId: string): boolean {
    const control = this.fieldsForm.get(fieldId);
    return control ? control.invalid && (control.dirty || control.touched) : false;
  }

  // Methods matching New Report page structure
  hasBankSpecificFields(): boolean {
    const data = this.templateData();
    return data ? data.bankSpecificTabs?.length > 0 : false;
  }

  isFormReady(): boolean {
    return !this.isLoading() && this.templateData() !== null;
  }

  getTabTotalFields(tab: any): number {
    let totalFields = tab.fields?.length || 0;
    if (tab.sections) {
      totalFields += tab.sections.reduce((sum: number, section: any) => 
        sum + (section.fields?.length || 0), 0);
    }
    return totalFields;
  }
}
