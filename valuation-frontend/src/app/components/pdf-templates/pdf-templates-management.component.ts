/**
 * PDF Templates Management Component
 * Manage PDF templates similar to custom templates
 */

import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { PDFTemplateService } from '../../services/pdf-template.service';
import { PDFTemplateListItem } from '../../models/pdf-template.model';
import { Bank } from '../../models/bank.model';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-pdf-templates-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pdf-templates-management.component.html',
  styleUrls: ['./pdf-templates-management.component.css']
})
export class PDFTemplatesManagementComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly pdfTemplateService = inject(PDFTemplateService);
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  
  // Organization context
  private readonly currentOrgShortName = signal<string>('');
  private readonly API_BASE_URL = 'http://localhost:8000/api';

  // Signals for reactive state
  templates = signal<PDFTemplateListItem[]>([]);
  banks = signal<Bank[]>([]);
  isLoading = signal<boolean>(false);
  error = signal<string | null>(null);
  selectedBankCode = signal<string>('');
  selectedPropertyType = signal<'land' | 'apartment' | ''>('');

  // Confirmation modal state - simplified for now
  showConfirmationModal = signal<boolean>(false);
  pendingDeleteTemplate = signal<PDFTemplateListItem | null>(null);

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

    return count < 5; // Allow up to 5 PDF templates per bank/property type
  });

  remainingSlots = computed(() => {
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();
    
    if (!bankCode || !propertyType) return 5;

    const count = this.templates().filter(
      t => t.bankCode === bankCode && t.propertyType === propertyType
    ).length;

    return Math.max(0, 5 - count);
  });

  ngOnInit(): void {
    // Get organization context from route
    this.route.parent?.params.subscribe(params => {
      const orgShortName = params['orgShortName'];
      if (orgShortName) {
        this.currentOrgShortName.set(orgShortName);
        console.log('📍 PDF Templates component - Current organization:', orgShortName);
        this.loadTemplates();
      }
    });

    // Check permissions
    if (!this.authService.isManager() && !this.authService.isSystemAdmin()) {
      this.error.set('You do not have permission to manage PDF templates.');
      setTimeout(() => this.router.navigate(['/dashboard']), 2000);
      return;
    }

    this.loadBanks();
    this.loadTemplates();
  }

  loadBanks(): void {
    this.isLoading.set(true);
    
    fetch(`${this.API_BASE_URL}/banks`)
      .then(response => response.json())
      .then((banks: Bank[]) => {
        this.banks.set(banks);
      })
      .catch(error => {
        console.error('❌ Error loading banks:', error);
        this.notificationService.error('Failed to load banks');
      })
      .finally(() => {
        this.isLoading.set(false);
      });
  }

  loadTemplates(): void {
    // For now, use empty array - will implement API call later
    this.templates.set([]);
  }

  onBankChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const bankCode = target.value;
    this.selectedBankCode.set(bankCode);
  }

  onPropertyTypeChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const propertyType = target.value as 'land' | 'apartment' | '';
    this.selectedPropertyType.set(propertyType);
  }

  clearFilters(): void {
    this.selectedBankCode.set('');
    this.selectedPropertyType.set('');
  }

  createPDFTemplate(): void {
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();

    if (!bankCode || !propertyType) {
      this.notificationService.warning('Please select a bank and property type first');
      return;
    }

    if (!this.canCreateMore()) {
      this.notificationService.warning('Maximum 5 PDF templates allowed for this bank and property type');
      return;
    }

    // Navigate to PDF template creation form
    const orgShortName = this.currentOrgShortName();
    if (orgShortName) {
      this.router.navigate(['/org', orgShortName, 'pdf-templates', 'create'], {
        queryParams: { bankCode, propertyType }
      });
    } else {
      const authOrgContext = this.authService.getOrganizationContext();
      if (authOrgContext?.orgShortName) {
        this.router.navigate(['/org', authOrgContext.orgShortName, 'pdf-templates', 'create'], {
          queryParams: { bankCode, propertyType }
        });
      } else {
        this.notificationService.error('Unable to determine organization context. Please refresh the page.');
      }
    }
  }

  openVisualDesigner(): void {
    const bankCode = this.selectedBankCode();
    const propertyType = this.selectedPropertyType();

    if (!bankCode || !propertyType) {
      this.notificationService.warning('Please select a bank and property type first');
      return;
    }

    if (!this.canCreateMore()) {
      this.notificationService.warning('Maximum 5 PDF templates allowed for this bank and property type');
      return;
    }

    // Navigate to PDF Visual Designer
    const orgShortName = this.currentOrgShortName();
    if (orgShortName) {
      this.router.navigate(['/org', orgShortName, 'pdf-templates', 'designer'], {
        queryParams: { bankCode, propertyType }
      });
    } else {
      const authOrgContext = this.authService.getOrganizationContext();
      if (authOrgContext?.orgShortName) {
        this.router.navigate(['/org', authOrgContext.orgShortName, 'pdf-templates', 'designer'], {
          queryParams: { bankCode, propertyType }
        });
      } else {
        this.notificationService.error('Unable to determine organization context. Please refresh the page.');
      }
    }
  }

  editPDFTemplate(templateId: string): void {
    const orgShortName = this.currentOrgShortName();
    if (orgShortName) {
      this.router.navigate(['/org', orgShortName, 'pdf-templates', 'edit', templateId]);
    } else {
      const authOrgContext = this.authService.getOrganizationContext();
      if (authOrgContext?.orgShortName) {
        this.router.navigate(['/org', authOrgContext.orgShortName, 'pdf-templates', 'edit', templateId]);
      }
    }
  }

  confirmDeletePDFTemplate(template: PDFTemplateListItem): void {
    const confirmed = confirm(`Are you sure you want to delete the PDF template "${template.name}"? This action cannot be undone.`);
    if (confirmed) {
      this.deletePDFTemplate(template._id);
    }
  }

  deletePDFTemplate(templateId: string): void {
    this.notificationService.info('Delete functionality coming soon!');
  }

  /**
   * Navigate back to custom templates
   */
  goBackToCustomTemplates(): void {
    const orgShortName = this.currentOrgShortName();
    if (orgShortName) {
      this.router.navigate(['/org', orgShortName, 'custom-templates']);
    } else {
      const authOrgContext = this.authService.getOrganizationContext();
      if (authOrgContext?.orgShortName) {
        this.router.navigate(['/org', authOrgContext.orgShortName, 'custom-templates']);
      } else {
        this.router.navigate(['/custom-templates']);
      }
    }
  }
}