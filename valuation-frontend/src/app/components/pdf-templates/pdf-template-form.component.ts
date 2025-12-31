/**
 * PDF Template Form Component
 * Create and edit PDF templates
 */

import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { PDFTemplateService } from '../../services/pdf-template.service';
import { PDFTemplate } from '../../models/pdf-template.model';
import { Bank } from '../../models/bank.model';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-pdf-template-form',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './pdf-template-form.component.html',
  styleUrls: ['./pdf-template-form.component.css']
})
export class PDFTemplateFormComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly pdfTemplateService = inject(PDFTemplateService);
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly fb = inject(FormBuilder);

  // Organization context
  private readonly currentOrgShortName = signal<string>('');
  private readonly API_BASE_URL = 'http://localhost:8000/api';

  // Form and state
  templateForm: FormGroup;
  isLoading = signal<boolean>(false);
  isSaving = signal<boolean>(false);
  error = signal<string | null>(null);
  templateId = signal<string | null>(null);
  banks = signal<Bank[]>([]);

  // Computed properties
  isEditMode = computed(() => !!this.templateId());
  pageTitle = computed(() => this.isEditMode() ? 'Edit PDF Template' : 'Create PDF Template');

  constructor() {
    this.templateForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      bankCode: ['', Validators.required],
      propertyType: ['', Validators.required],
      description: [''],
      pageSize: ['A4', Validators.required],
      orientation: ['portrait', Validators.required],
      marginTop: [20, [Validators.required, Validators.min(0)]],
      marginRight: [20, [Validators.required, Validators.min(0)]],
      marginBottom: [20, [Validators.required, Validators.min(0)]],
      marginLeft: [20, [Validators.required, Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    // Get organization context from route
    this.route.parent?.params.subscribe(params => {
      const orgShortName = params['orgShortName'];
      if (orgShortName) {
        this.currentOrgShortName.set(orgShortName);
        console.log('📍 PDF Template Form - Current organization:', orgShortName);
      }
    });

    // Check permissions
    if (!this.authService.isManager() && !this.authService.isSystemAdmin()) {
      this.error.set('You do not have permission to manage PDF templates.');
      setTimeout(() => this.router.navigate(['/dashboard']), 2000);
      return;
    }

    // Load banks
    this.loadBanks();

    // Check if editing existing template
    this.route.params.subscribe(params => {
      const id = params['id'];
      if (id) {
        this.templateId.set(id);
        this.loadTemplate(id);
      }
    });

    // Set query parameters for create mode
    this.route.queryParams.subscribe(params => {
      if (params['bankCode']) {
        this.templateForm.patchValue({ bankCode: params['bankCode'] });
      }
      if (params['propertyType']) {
        this.templateForm.patchValue({ propertyType: params['propertyType'] });
      }
    });
  }

  loadBanks(): void {
    fetch(`${this.API_BASE_URL}/banks`)
      .then(response => response.json())
      .then((banks: Bank[]) => {
        this.banks.set(banks);
      })
      .catch(error => {
        console.error('❌ Error loading banks:', error);
        this.notificationService.error('Failed to load banks');
      });
  }

  loadTemplate(templateId: string): void {
    this.isLoading.set(true);
    // For now, show placeholder - will implement API call later
    this.notificationService.info('Template loading not yet implemented');
    this.isLoading.set(false);
  }

  onSubmit(): void {
    if (this.templateForm.invalid) {
      this.templateForm.markAllAsTouched();
      return;
    }

    this.isSaving.set(true);
    const formData = this.templateForm.value;

    // Create template object
    const template: Omit<PDFTemplate, '_id' | 'createdAt' | 'updatedAt'> = {
      name: formData.name,
      bankCode: formData.bankCode,
      propertyType: formData.propertyType,
      description: formData.description,
      layout: {
        pageSize: formData.pageSize,
        orientation: formData.orientation,
        margins: {
          top: formData.marginTop,
          right: formData.marginRight,
          bottom: formData.marginBottom,
          left: formData.marginLeft
        },
        sections: [] // Will be populated later with visual designer
      },
      organizationId: this.authService.getOrganizationContext()?.organizationId || '',
      createdBy: 'current-user' // Will get from auth service properly later
    };

    // Simulate save for now
    setTimeout(() => {
      this.isSaving.set(false);
      this.notificationService.success(
        this.isEditMode() ? 'PDF template updated successfully!' : 'PDF template created successfully!'
      );
      this.goBack();
    }, 1000);
  }

  onCancel(): void {
    this.goBack();
  }

  goBack(): void {
    const orgShortName = this.currentOrgShortName();
    if (orgShortName) {
      this.router.navigate(['/org', orgShortName, 'pdf-templates']);
    } else {
      const authOrgContext = this.authService.getOrganizationContext();
      if (authOrgContext?.orgShortName) {
        this.router.navigate(['/org', authOrgContext.orgShortName, 'pdf-templates']);
      } else {
        this.router.navigate(['/pdf-templates']);
      }
    }
  }

  // Helper methods for form validation
  isFieldInvalid(fieldName: string): boolean {
    const field = this.templateForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  getFieldError(fieldName: string): string {
    const field = this.templateForm.get(fieldName);
    if (field?.errors) {
      if (field.errors['required']) return 'This field is required';
      if (field.errors['minlength']) return `Minimum length is ${field.errors['minlength'].requiredLength}`;
      if (field.errors['min']) return `Minimum value is ${field.errors['min'].min}`;
    }
    return '';
  }
}