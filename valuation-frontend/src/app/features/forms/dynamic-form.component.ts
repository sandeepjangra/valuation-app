import { Component, Input, Output, EventEmitter, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatRadioModule } from '@angular/material/radio';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';

import { FormTemplate, FormSection, FormField, FormData } from '../../core/models/form.models';
import { FormTemplateService } from '../../core/services/form-template.service';

@Component({
  selector: 'app-dynamic-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatRadioModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatButtonModule,
    MatIconModule,
    MatExpansionModule,
    MatProgressSpinnerModule,
    MatSnackBarModule
  ],
  templateUrl: './dynamic-form.component.html',
  styleUrl: './dynamic-form.component.scss'
})
export class DynamicFormComponent implements OnInit {
  @Input() templateId!: string;
  @Input() formData?: FormData;
  @Input() readonly: boolean = false;
  @Output() formSubmit = new EventEmitter<any>();
  @Output() formSave = new EventEmitter<any>();

  private fb = inject(FormBuilder);
  private formTemplateService = inject(FormTemplateService);
  private snackBar = inject(MatSnackBar);

  template: FormTemplate | null = null;
  dynamicForm: FormGroup = this.fb.group({});
  isLoading = true;
  isSaving = false;
  isSubmitting = false;

  ngOnInit(): void {
    console.log('DynamicFormComponent: ngOnInit called with templateId:', this.templateId);
    if (!this.templateId) {
      console.error('DynamicFormComponent: templateId is not provided!');
      this.isLoading = false;
      return;
    }
    this.loadTemplate();
  }

  private loadTemplate(): void {
    console.log('DynamicFormComponent: loadTemplate called');
    this.isLoading = true;
    this.formTemplateService.getTemplate(this.templateId).subscribe({
      next: (template) => {
        console.log('DynamicFormComponent: Template received:', template);
        if (template) {
          this.template = template;
          this.buildForm();
          this.populateFormData();
        } else {
          console.error('DynamicFormComponent: Template is null');
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading template:', error);
        this.snackBar.open('Failed to load form template', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  private buildForm(): void {
    if (!this.template) return;

    const formControls: { [key: string]: any } = {};

    this.template.sections.forEach(section => {
      section.fields.forEach(field => {
        const validators = [];
        
        if (field.required) {
          validators.push(Validators.required);
        }
        
        if (field.validation) {
          if (field.validation.minLength) {
            validators.push(Validators.minLength(field.validation.minLength));
          }
          if (field.validation.maxLength) {
            validators.push(Validators.maxLength(field.validation.maxLength));
          }
          if (field.validation.pattern) {
            validators.push(Validators.pattern(field.validation.pattern));
          }
          if (field.validation.min !== undefined) {
            validators.push(Validators.min(field.validation.min));
          }
          if (field.validation.max !== undefined) {
            validators.push(Validators.max(field.validation.max));
          }
        }

        if (field.type === 'email') {
          validators.push(Validators.email);
        }

        formControls[field.name] = [field.defaultValue || '', validators];
      });
    });

    this.dynamicForm = this.fb.group(formControls);

    if (this.readonly) {
      this.dynamicForm.disable();
    }
  }

  private populateFormData(): void {
    if (this.formData && this.formData.data) {
      this.dynamicForm.patchValue(this.formData.data);
    }
  }

  onSave(): void {
    if (!this.template) return;

    this.isSaving = true;
    const formData: Partial<FormData> = {
      templateId: this.template.id,
      templateVersion: this.template.version,
      data: this.dynamicForm.value,
      status: 'draft'
    };

    this.formTemplateService.saveFormData(formData).subscribe({
      next: (savedData) => {
        this.snackBar.open('Form saved successfully', 'Close', { duration: 3000 });
        this.formSave.emit(savedData);
        this.isSaving = false;
      },
      error: (error) => {
        console.error('Error saving form:', error);
        this.snackBar.open('Failed to save form', 'Close', { duration: 3000 });
        this.isSaving = false;
      }
    });
  }

  onSubmit(): void {
    if (!this.template || !this.dynamicForm.valid) {
      this.markFormGroupTouched();
      this.snackBar.open('Please fill all required fields', 'Close', { duration: 3000 });
      return;
    }

    this.isSubmitting = true;
    const formData: Partial<FormData> = {
      templateId: this.template.id,
      templateVersion: this.template.version,
      data: this.dynamicForm.value,
      status: 'submitted'
    };

    this.formTemplateService.saveFormData(formData).subscribe({
      next: (savedData) => {
        this.snackBar.open('Form submitted successfully', 'Close', { duration: 3000 });
        this.formSubmit.emit(savedData);
        this.isSubmitting = false;
      },
      error: (error) => {
        console.error('Error submitting form:', error);
        this.snackBar.open('Failed to submit form', 'Close', { duration: 3000 });
        this.isSubmitting = false;
      }
    });
  }

  private markFormGroupTouched(): void {
    Object.keys(this.dynamicForm.controls).forEach(key => {
      this.dynamicForm.get(key)?.markAsTouched();
    });
  }

  getFieldError(field: FormField): string {
    const control = this.dynamicForm.get(field.name);
    if (!control || !control.errors || !control.touched) return '';

    if (control.errors['required']) return `${field.label} is required`;
    if (control.errors['email']) return 'Please enter a valid email address';
    if (control.errors['minlength']) return `Minimum length is ${control.errors['minlength'].requiredLength}`;
    if (control.errors['maxlength']) return `Maximum length is ${control.errors['maxlength'].requiredLength}`;
    if (control.errors['min']) return `Minimum value is ${control.errors['min'].min}`;
    if (control.errors['max']) return `Maximum value is ${control.errors['max'].max}`;
    if (control.errors['pattern']) return `Please enter a valid ${field.label.toLowerCase()}`;

    return 'Invalid input';
  }

  isFieldVisible(field: FormField): boolean {
    if (!field.visible) return false;
    
    if (!field.dependsOn) return true;

    const dependentFieldValue = this.dynamicForm.get(field.dependsOn.fieldId)?.value;
    
    switch (field.dependsOn.condition) {
      case 'equals':
        return dependentFieldValue === field.dependsOn.value;
      case 'not_equals':
        return dependentFieldValue !== field.dependsOn.value;
      case 'greater_than':
        return dependentFieldValue > field.dependsOn.value;
      case 'less_than':
        return dependentFieldValue < field.dependsOn.value;
      default:
        return true;
    }
  }

  getCurrentLocation(): void {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const latitude = position.coords.latitude;
          const longitude = position.coords.longitude;
          
          // Update form controls with current location
          this.dynamicForm.patchValue({
            propertyLatitude: latitude,
            propertyLongitude: longitude
          });
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    } else {
      console.error('Geolocation is not supported by this browser.');
    }
  }

  getSectionIcon(sectionId: string): string {
    const iconMap: { [key: string]: string } = {
      'basic-details': 'info',
      'bank-details': 'account_balance',
      'valuer-details': 'person',
      'borrower-details': 'group',
      'property-details': 'home',
      'location-details': 'place',
      'default': 'folder'
    };
    
    return iconMap[sectionId] || iconMap['default'];
  }
}