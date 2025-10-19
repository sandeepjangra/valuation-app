import { Injectable, inject } from '@angular/core';
import { Observable, of } from 'rxjs';
import { delay, map, catchError } from 'rxjs/operators';
import { FormTemplate, FormSection, FormField, FormData } from '../models/form.models';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class FormTemplateService {
  private apiService = inject(ApiService);

  constructor() {}

  // Get template by ID from API
  getTemplate(templateId: string): Observable<FormTemplate | null> {
    console.log('FormTemplateService: getTemplate called with ID:', templateId);
    
    return this.apiService.get<FormTemplate>(`templates/${templateId}`).pipe(
      map(template => {
        console.log('Template received from API:', template);
        return template;
      }),
      catchError(error => {
        console.error('Error fetching template from API:', error);
        
        // Fallback to mock data if API fails
        console.log('Falling back to mock data...');
        return of(this.getMockTemplate(templateId));
      })
    );
  }

  // Get all templates
  getTemplates(): Observable<FormTemplate[]> {
    return this.apiService.get<FormTemplate[]>('templates').pipe(
      catchError(error => {
        console.error('Error fetching templates from API:', error);
        const mockTemplate = this.getMockTemplate('property-description-v1');
        return of(mockTemplate ? [mockTemplate] : []);
      })
    );
  }

  // Get templates by category
  getTemplatesByCategory(category: string): Observable<FormTemplate[]> {
    return this.getTemplates().pipe(
      map(templates => templates.filter(template => template.category === category))
    );
  }

  // Get bank-specific template
  getBankTemplate(bankId: string): Observable<FormTemplate | null> {
    // For now, return the default template
    // TODO: Implement bank-specific template logic
    return this.getTemplate('property-description-v1');
  }

  // Save form data
  saveFormData(formData: Partial<FormData>): Observable<FormData> {
    // TODO: Implement API call to save form data
    const savedData: FormData = {
      id: formData.id || 'temp-' + Date.now(),
      templateId: formData.templateId || '',
      templateVersion: formData.templateVersion || '1.0',
      userId: formData.userId || 'current-user',
      data: formData.data || {},
      status: formData.status || 'draft',
      createdDate: formData.createdDate || new Date(),
      updatedDate: new Date()
    };
    
    return of(savedData).pipe(delay(1000));
  }

  // Validate form data
  validateFormData(templateId: string, data: any): Observable<{ isValid: boolean; errors: string[] }> {
    return this.getTemplate(templateId).pipe(
      map(template => {
        if (!template) {
          return { isValid: false, errors: ['Template not found'] };
        }
        
        const errors: string[] = [];
        // TODO: Implement proper validation logic
        
        return { isValid: errors.length === 0, errors };
      })
    );
  }

  // Get mock template for fallback
  private getMockTemplate(templateId: string): FormTemplate | null {
    if (templateId === 'property-description-v1') {
      return {
        id: 'property-description-v1',
        name: 'Property Description Template',
        description: 'Standard template for property valuation report - Property Description section',
        version: '1.0',
        category: 'general',
        sections: [
          {
            id: 'basic-details',
            title: 'Basic Report Details',
            description: 'Essential information about the valuation report',
            order: 1,
            collapsible: true,
            expanded: true,
            visible: true,
            fields: [
              {
                id: 'reportDate',
                name: 'reportDate',
                label: 'Report Date',
                type: 'date',
                required: true,
                gridSize: 6,
                order: 1,
                visible: true,
                defaultValue: new Date().toISOString().split('T')[0]
              },
              {
                id: 'inspectionDate',
                name: 'inspectionDate',
                label: 'Inspection Date',
                type: 'date',
                required: true,
                gridSize: 6,
                order: 2,
                visible: true
              },
              {
                id: 'purpose',
                name: 'purpose',
                label: 'Purpose of Valuation',
                type: 'select',
                required: true,
                gridSize: 12,
                order: 3,
                visible: true,
                options: [
                  { value: 'mortgage', label: 'Mortgage/Loan' },
                  { value: 'sale', label: 'Sale Transaction' },
                  { value: 'insurance', label: 'Insurance' },
                  { value: 'taxation', label: 'Taxation' },
                  { value: 'investment', label: 'Investment Analysis' }
                ]
              }
            ]
          },
          {
            id: 'bank-details',
            title: 'Bank Details',
            description: 'Information about the bank and loan',
            order: 2,
            collapsible: true,
            expanded: false,
            visible: true,
            fields: [
              {
                id: 'bankName',
                name: 'bankName',
                label: 'Bank Name',
                type: 'text',
                required: true,
                gridSize: 6,
                order: 1,
                visible: true
              },
              {
                id: 'branchName',
                name: 'branchName',
                label: 'Branch Name',
                type: 'text',
                required: true,
                gridSize: 6,
                order: 2,
                visible: true
              }
            ]
          }
        ],
        isActive: true,
        createdBy: 'system',
        createdDate: new Date()
      };
    }
    return null;
  }
}