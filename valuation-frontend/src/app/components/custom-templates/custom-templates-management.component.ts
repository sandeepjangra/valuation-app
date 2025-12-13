/**
 * Custom Templates Management Component
 * Allows Manager/Admin to create, view, edit, delete, and clone custom templates
 */

import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';
import { CustomTemplateService } from '../../services/custom-template.service';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { CustomTemplateListItem, CustomTemplate } from '../../models/custom-template.model';
import { Bank } from '../../models/bank.model';
import { ConfirmationModalComponent, ConfirmationModalData } from '../shared/confirmation-modal.component';

@Component({
  selector: 'app-custom-templates-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, ConfirmationModalComponent],
  templateUrl: './custom-templates-management.component.html',
  styleUrls: ['./custom-templates-management.component.css']
})
export class CustomTemplatesManagementComponent implements OnInit {
  private readonly customTemplateService = inject(CustomTemplateService);
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly fb = inject(FormBuilder);
  
  // Organization context
  private readonly currentOrgShortName = signal<string>('');

  private readonly API_BASE_URL = 'http://localhost:8000/api';

  // Signals for reactive state
  templates = signal<CustomTemplateListItem[]>([]);
  banks = signal<Bank[]>([]);
  isLoading = signal<boolean>(false);
  error = signal<string | null>(null);
  selectedBankCode = signal<string>('');
  selectedPropertyType = signal<'land' | 'apartment' | ''>('');

  // Confirmation modal state
  showConfirmationModal = signal<boolean>(false);
  confirmationModalData = signal<ConfirmationModalData | null>(null);
  pendingDeleteTemplate = signal<CustomTemplateListItem | null>(null);

  // Computed signals
  filteredTemplates = computed(() => {
    let filtered = this.templates();
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();

    if (bankCode) {
      filtered = filtered.filter(t => t.bankCode === bankCode);
    }
    if (propertyType) {
      filtered = filtered.filter(t => t.propertyType === propertyType);
    }

    return filtered;
  });

  canCreateMore = computed(() => {
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();
    
    if (!bankCode || !propertyType) return false;

    const count = this.templates().filter(
      t => t.bankCode === bankCode && t.propertyType === propertyType
    ).length;

    return count < 2; // Changed from 3 to 2
  });

  remainingSlots = computed(() => {
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();
    
    if (!bankCode || !propertyType) return 2;

    const count = this.templates().filter(
      t => t.bankCode === bankCode && t.propertyType === propertyType
    ).length;

    return Math.max(0, 2 - count);
  });

  // User permissions
  isManagerOrAdmin = computed(() => 
    this.authService.isManager() || this.authService.isSystemAdmin()
  );

  ngOnInit(): void {
    // Get organization context from route
    this.route.parent?.params.subscribe(params => {
      const orgShortName = params['orgShortName'];
      if (orgShortName) {
        this.currentOrgShortName.set(orgShortName);
        console.log('📍 Templates component - Current organization:', orgShortName);
        
        // Load templates directly for now
        this.loadTemplates();
      }
    });

    // Check permissions
    if (!this.isManagerOrAdmin()) {
      this.error.set('You do not have permission to manage custom templates.');
      setTimeout(() => this.router.navigate(['/dashboard']), 2000);
      return;
    }

    this.loadBanks();
    this.loadTemplates();
  }

  loadBanks(): void {
    this.isLoading.set(true);
    
    // Use fetch to get banks from API
    fetch(`${this.API_BASE_URL}/banks`)
      .then(response => response.json())
      .then((banks: Bank[]) => {
        this.banks.set(banks);
        this.isLoading.set(false);
      })
      .catch((error: any) => {
        console.error('❌ Failed to load banks:', error);
        this.error.set('Failed to load banks');
        this.isLoading.set(false);
      });
  }



  loadTemplates(): void {
    console.log('🔄 Loading templates...');
    this.isLoading.set(true);
    this.customTemplateService.getTemplates().subscribe({
      next: (response) => {
        console.log('✅ Templates loaded successfully:', response);
        console.log('📊 Number of templates found:', response.data.length);
        console.log('📋 Template details:', response.data.map(t => ({ id: t._id, name: t.templateName })));
        this.templates.set(response.data);
        this.isLoading.set(false);
        this.error.set(null);
      },
      error: (error) => {
        console.error('❌ Failed to load templates:', error);
        console.error('❌ Error details:', JSON.stringify(error, null, 2));
        this.error.set('Failed to load custom templates');
        this.isLoading.set(false);
      }
    });
  }

  onBankChange(event: Event): void {
    const bankCode = (event.target as HTMLSelectElement).value;
    this.selectedBankCode.set(bankCode);
  }

  onPropertyTypeChange(event: Event): void {
    const propertyType = (event.target as HTMLSelectElement).value as 'land' | 'apartment' | '';
    this.selectedPropertyType.set(propertyType);
  }

  clearFilters(): void {
    this.selectedBankCode.set('');
    this.selectedPropertyType.set('');
  }

  createTemplate(): void {
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();

    if (!bankCode || !propertyType) {
      this.notificationService.warning('Please select a bank and property type first');
      return;
    }

    if (!this.canCreateMore()) {
      this.notificationService.warning('Maximum 2 templates allowed for this bank and property type');
      return;
    }

    // Navigate to organization-specific template creation form
    const orgShortName = this.currentOrgShortName();
    console.log('🔍 Creating template - orgShortName:', orgShortName);
    
    if (orgShortName) {
      console.log('✅ Navigating to org-specific route:', `/org/${orgShortName}/custom-templates/create`);
      this.router.navigate(['/org', orgShortName, 'custom-templates', 'create'], {
        queryParams: { bankCode, propertyType }
      });
    } else {
      console.error('❌ No organization context available for navigation');
      // Get org from auth service as fallback
      const authOrgContext = this.authService.getOrganizationContext();
      if (authOrgContext?.orgShortName) {
        console.log('✅ Using auth service org context:', authOrgContext.orgShortName);
        this.router.navigate(['/org', authOrgContext.orgShortName, 'custom-templates', 'create'], {
          queryParams: { bankCode, propertyType }
        });
      } else {
        console.error('❌ No organization context available anywhere');
        this.notificationService.error('Unable to determine organization context. Please refresh the page.');
      }
    }
  }

  editTemplate(templateId: string): void {
    const orgShortName = this.currentOrgShortName();
    if (orgShortName) {
      this.router.navigate(['/org', orgShortName, 'custom-templates', 'edit', templateId]);
    } else {
      console.error('❌ No organization context available for edit navigation');
      this.router.navigate(['/custom-templates/edit', templateId]);
    }
  }

  cloneTemplate(template: CustomTemplateListItem): void {
    const newName = prompt(`Enter name for cloned template (cloning "${template.templateName}"):`, 
      `${template.templateName} - Copy`);

    if (!newName || newName.trim() === '') {
      return;
    }

    // Check if can create more for this bank+property type
    const count = this.templates().filter(
      t => t.bankCode === template.bankCode && t.propertyType === template.propertyType
    ).length;

    if (count >= 3) {
      this.notificationService.warning('Cannot clone: Maximum 2 templates allowed for this bank and property type');
      return;
    }

    this.isLoading.set(true);
    this.customTemplateService.cloneTemplate(template._id, {
      newTemplateName: newName.trim(),
      description: template.description
    }).subscribe({
      next: (clonedTemplate) => {
        console.log('✅ Template cloned successfully:', clonedTemplate);
        this.loadTemplates();
        this.notificationService.success(`Template "${clonedTemplate.templateName}" created successfully!`);
      },
      error: (error) => {
        console.error('❌ Failed to clone template:', error);
        const errorMsg = error.error?.error || 'Failed to clone template';
        this.notificationService.error(errorMsg);
        this.isLoading.set(false);
      }
    });
  }

  deleteTemplate(template: CustomTemplateListItem): void {
    // Store the template to be deleted
    this.pendingDeleteTemplate.set(template);
    
    // Configure the confirmation modal
    this.confirmationModalData.set({
      title: 'Delete Template',
      message: `Are you sure you want to delete "${template.templateName}"?\n\nThis action cannot be undone and will permanently remove all associated data.`,
      confirmText: 'Delete Template',
      cancelText: 'Cancel',
      type: 'danger'
    });
    
    // Show the modal
    this.showConfirmationModal.set(true);
  }

  onDeleteConfirmed(): void {
    const template = this.pendingDeleteTemplate();
    if (!template) return;

    this.isLoading.set(true);
    this.showConfirmationModal.set(false);
    this.pendingDeleteTemplate.set(null);

    this.customTemplateService.deleteTemplate(template._id).subscribe({
      next: () => {
        console.log('✅ Template deleted successfully');
        this.loadTemplates();
        this.notificationService.success('Template deleted successfully');
      },
      error: (error) => {
        console.error('❌ Failed to delete template:', error);
        const errorMsg = error.error?.error || 'Failed to delete template';
        this.notificationService.error(errorMsg);
        this.isLoading.set(false);
      }
    });
  }

  onDeleteCancelled(): void {
    this.showConfirmationModal.set(false);
    this.pendingDeleteTemplate.set(null);
    this.confirmationModalData.set(null);
  }

  formatDate(date: Date | string): string {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getPropertyTypeLabel(propertyType: string): string {
    return propertyType === 'land' ? 'Land' : 'Apartment';
  }

  getBankName(bankCode: string): string {
    const bank = this.banks().find(b => b.bankCode === bankCode);
    return bank?.bankName || bankCode;
  }
}
