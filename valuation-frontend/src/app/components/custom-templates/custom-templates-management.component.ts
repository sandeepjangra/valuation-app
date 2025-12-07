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
import { CustomTemplateListItem, CustomTemplate } from '../../models/custom-template.model';
import { Bank } from '../../models/bank.model';

@Component({
  selector: 'app-custom-templates-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './custom-templates-management.component.html',
  styleUrls: ['./custom-templates-management.component.css']
})
export class CustomTemplatesManagementComponent implements OnInit {
  private readonly customTemplateService = inject(CustomTemplateService);
  private readonly authService = inject(AuthService);
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

    return count < 3;
  });

  remainingSlots = computed(() => {
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();
    
    if (!bankCode || !propertyType) return 3;

    const count = this.templates().filter(
      t => t.bankCode === bankCode && t.propertyType === propertyType
    ).length;

    return Math.max(0, 3 - count);
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
    this.isLoading.set(true);
    this.customTemplateService.getTemplates().subscribe({
      next: (response) => {
        this.templates.set(response.data);
        this.isLoading.set(false);
        this.error.set(null);
      },
      error: (error) => {
        console.error('❌ Failed to load templates:', error);
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
      alert('Please select a bank and property type first');
      return;
    }

    if (!this.canCreateMore()) {
      alert('Maximum 3 templates allowed for this bank and property type');
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
        alert('Unable to determine organization context. Please refresh the page.');
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
      alert('Cannot clone: Maximum 3 templates allowed for this bank and property type');
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
        alert(`Template "${clonedTemplate.templateName}" created successfully!`);
      },
      error: (error) => {
        console.error('❌ Failed to clone template:', error);
        const errorMsg = error.error?.error || 'Failed to clone template';
        alert(errorMsg);
        this.isLoading.set(false);
      }
    });
  }

  deleteTemplate(template: CustomTemplateListItem): void {
    const confirmMsg = `Are you sure you want to delete "${template.templateName}"?\n\nThis action cannot be undone.`;
    
    if (!confirm(confirmMsg)) {
      return;
    }

    this.isLoading.set(true);
    this.customTemplateService.deleteTemplate(template._id).subscribe({
      next: () => {
        console.log('✅ Template deleted successfully');
        this.loadTemplates();
        alert('Template deleted successfully');
      },
      error: (error) => {
        console.error('❌ Failed to delete template:', error);
        const errorMsg = error.error?.error || 'Failed to delete template';
        alert(errorMsg);
        this.isLoading.set(false);
      }
    });
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
