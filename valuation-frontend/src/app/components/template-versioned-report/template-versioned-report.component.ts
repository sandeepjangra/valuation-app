import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { TemplateVersioningService } from '../../services/template-versioning.service';
import { DynamicFormComponent } from '../dynamic-form/dynamic-form.component';
import { 
  TemplateSnapshot, 
  TemplateVersion, 
  ValuationReport,
  CreateReportRequest 
} from '../../models/template-versioning.models';

/**
 * Template Versioned Report Creation Component
 * Demonstrates the dynamic form renderer with real SBI Land templates
 */
@Component({
  selector: 'app-template-versioned-report',
  standalone: true,
  imports: [CommonModule, DynamicFormComponent],
  templateUrl: './template-versioned-report.component.html',
  styleUrls: ['./template-versioned-report.component.css']
})
export class TemplateVersionedReportComponent implements OnInit {
  // State management
  isLoading = false;
  error: string | null = null;
  
  // Template selection
  availableTemplates: TemplateVersion[] = [];
  selectedTemplateId: string | null = null;
  templateSnapshot: TemplateSnapshot | null = null;
  
  // Report creation
  reportData: Record<string, any> = {};
  isFormValid = false;
  currentReport: ValuationReport | null = null;
  
  // UI state
  step: 'select' | 'create' | 'review' = 'select';

  constructor(
    private templateService: TemplateVersioningService,
    public router: Router
  ) {}

  ngOnInit(): void {
    this.loadAvailableTemplates();
  }

  /**
   * Load available template versions
   */
  async loadAvailableTemplates(): Promise<void> {
    this.isLoading = true;
    this.error = null;
    
    try {
      this.availableTemplates = await this.templateService.getTemplateVersions().toPromise() || [];
      console.log('Loaded templates:', this.availableTemplates);
    } catch (error) {
      this.error = 'Failed to load templates: ' + (error as Error).message;
      console.error('Error loading templates:', error);
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Select a template and load its snapshot
   */
  async selectTemplate(templateId: string): Promise<void> {
    this.isLoading = true;
    this.error = null;
    
    try {
      this.selectedTemplateId = templateId;
      this.templateSnapshot = await this.templateService.getLatestTemplateSnapshot(templateId).toPromise() || null;
      
      if (this.templateSnapshot) {
        this.step = 'create';
        console.log('Loaded template snapshot:', this.templateSnapshot);
      }
    } catch (error) {
      this.error = 'Failed to load template snapshot: ' + (error as Error).message;
      console.error('Error loading template snapshot:', error);
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Handle form data changes
   */
  onFormDataChange(data: Record<string, any>): void {
    this.reportData = data;
    console.log('Form data updated:', data);
  }

  /**
   * Handle form validation changes
   */
  onFormValidChange(isValid: boolean): void {
    this.isFormValid = isValid;
    console.log('Form validation changed:', isValid);
  }

  /**
   * Handle form save (draft)
   */
  async onSaveReport(data: Record<string, any>): Promise<void> {
    if (!this.templateSnapshot) return;
    
    this.isLoading = true;
    this.error = null;
    
    try {
      if (this.currentReport) {
        // Update existing report
        this.currentReport = await this.templateService.updateReport(
          this.currentReport.reportId!,
          { data, status: 'DRAFT' }
        ).toPromise() || null;
        
        console.log('Report updated:', this.currentReport);
        alert('Report saved successfully!');
      } else {
        // Create new report
        const request: CreateReportRequest = {
          templateId: this.templateSnapshot.templateId,
          bankCode: this.templateSnapshot.bankCode,
          propertyType: this.templateSnapshot.propertyType,
          reportType: this.templateSnapshot.templateCategory,
          initialData: data
        };
        
        this.currentReport = await this.templateService.createReport(request).toPromise() || null;
        
        console.log('Report created:', this.currentReport);
        alert('Report saved as draft!');
      }
    } catch (error) {
      this.error = 'Failed to save report: ' + (error as Error).message;
      console.error('Error saving report:', error);
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Handle form submit (for review)
   */
  async onSubmitReport(data: Record<string, any>): Promise<void> {
    if (!this.templateSnapshot) return;
    
    this.isLoading = true;
    this.error = null;
    
    try {
      if (!this.currentReport) {
        // Create report first if it doesn't exist
        await this.onSaveReport(data);
      }
      
      if (this.currentReport) {
        // Submit for review
        this.currentReport = await this.templateService.submitReport(
          this.currentReport.reportId!,
          'Submitted for review via dynamic form'
        ).toPromise() || null;
        
        console.log('Report submitted:', this.currentReport);
        alert('Report submitted for review!');
        this.step = 'review';
      }
    } catch (error) {
      this.error = 'Failed to submit report: ' + (error as Error).message;
      console.error('Error submitting report:', error);
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Handle form cancel
   */
  onCancelForm(): void {
    this.step = 'select';
    this.selectedTemplateId = null;
    this.templateSnapshot = null;
    this.reportData = {};
    this.currentReport = null;
    this.isFormValid = false;
  }

  /**
   * Go back to template selection
   */
  goBackToSelection(): void {
    this.step = 'select';
    this.selectedTemplateId = null;
    this.templateSnapshot = null;
  }

  /**
   * Get template display name
   */
  getTemplateDisplayName(template: TemplateVersion): string {
    return `${template.templateId} (${template.bankCode} ${template.propertyType})`;
  }

  /**
   * Get field count display
   */
  getFieldCountDisplay(template: TemplateVersion): string {
    return `${template.fieldCount} fields, ${template.sectionCount} sections`;
  }
}