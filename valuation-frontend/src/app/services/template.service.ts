import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { AggregatedTemplateResponse, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField, BankSpecificTab, BankSpecificSection } from '../models';

@Injectable({
  providedIn: 'root'
})
export class TemplateService {
  private readonly API_BASE_URL = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  /**
   * Get aggregated template fields (common + bank-specific) for a specific bank and template
   */
  getAggregatedTemplateFields(bankCode: string, templateCode: string): Observable<AggregatedTemplateResponse> {
    const url = `${this.API_BASE_URL}/templates/${bankCode}/${templateCode}/aggregated-fields`;
    
    console.log(`🌐 TemplateService: Making API call to ${url}`);
    
    return this.http.get<AggregatedTemplateResponse>(url).pipe(
      catchError(error => {
        console.error(`❌ TemplateService: API call failed for ${bankCode}/${templateCode}:`, error);
        if (error.status === 0) {
          console.error('❌ Network error - check if backend is running and CORS is configured');
        }
        return throwError(() => error);
      })
    );
  }

  /**
   * Process aggregated template response into organized field groups and tabs
   */
  processTemplateData(response: AggregatedTemplateResponse): ProcessedTemplateData {
    console.log('🔄 TemplateService.processTemplateData called with:', {
      commonFields: response.commonFields?.length || 0,
      bankSpecificTabs: response.bankSpecificTabs?.length || 0,
      templateInfo: response.templateInfo
    });

    // Process common fields into groups
    const commonFieldGroups = this.groupFieldsByGroup(response.commonFields, 'Common');
    console.log('🔥 Common field groups created:', commonFieldGroups.length);

    // Bank-specific tabs are already structured properly from the backend
    const bankSpecificTabs = response.bankSpecificTabs || [];
    console.log('🔥 Bank-specific tabs received:', bankSpecificTabs.length);

    // Combine all fields for form building (flatten tabs and sections)
    const allFields: (TemplateField | BankSpecificField)[] = [...response.commonFields];
    
    // Extract all fields from tabs and sections
    bankSpecificTabs.forEach(tab => {
      allFields.push(...tab.fields);
      if (tab.sections) {
        tab.sections.forEach(section => {
          allFields.push(...section.fields);
        });
      }
    });

    const processedData: ProcessedTemplateData = {
      templateInfo: response.templateInfo,
      commonFieldGroups,
      bankSpecificTabs,
      allFields,
      totalFieldCount: allFields.length
    };

    console.log('🔥 ProcessedTemplateData result:', {
      commonGroups: commonFieldGroups.length,
      bankSpecificTabs: bankSpecificTabs.length,
      totalFields: processedData.totalFieldCount,
      tabDetails: bankSpecificTabs.map(tab => ({
        tabId: tab.tabId,
        tabName: tab.tabName,
        fieldsCount: tab.fields.length,
        sectionsCount: tab.sections?.length || 0,
        hasSections: tab.hasSections
      }))
    });

    return processedData;
  }

  /**
   * Group fields by their fieldGroup property (used for common fields only)
   */
  private groupFieldsByGroup(fields: (TemplateField | BankSpecificField)[], defaultPrefix: string): FieldGroup[] {
    const groupMap = new Map<string, (TemplateField | BankSpecificField)[]>();

    fields.forEach(field => {
      const groupName = field.fieldGroup || 'default';
      if (!groupMap.has(groupName)) {
        groupMap.set(groupName, []);
      }
      groupMap.get(groupName)!.push(field);
    });

    // Convert to FieldGroup array and sort fields within each group
    const fieldGroups: FieldGroup[] = [];
    groupMap.forEach((groupFields, groupName) => {
      // Sort fields by sortOrder
      const sortedFields = groupFields.sort((a, b) => a.sortOrder - b.sortOrder);
      
      fieldGroups.push({
        groupName,
        displayName: this.formatGroupDisplayName(groupName, defaultPrefix),
        fields: sortedFields,
        sortOrder: Math.min(...sortedFields.map(f => f.sortOrder)) // Use minimum sortOrder for group sorting
      });
    });

    // Sort groups by their sortOrder
    return fieldGroups.sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0));
  }

  // Note: Bank-specific field grouping methods removed as we now use dynamic tabs from backend

  /**
   * Format group name for display
   */
  private formatGroupDisplayName(groupName: string, prefix: string): string {
    if (groupName === 'default') {
      return `${prefix} Fields`;
    }
    
    // Convert camelCase or snake_case to Title Case
    return groupName
      .replace(/([A-Z])/g, ' $1') // camelCase to spaces
      .replace(/_/g, ' ') // snake_case to spaces
      .replace(/\b\w/g, l => l.toUpperCase()) // Title Case
      .trim();
  }

  /**
   * Get all available templates for a bank
   */
  getTemplatesForBank(bankCode: string): Observable<any[]> {
    const url = `${this.API_BASE_URL}/templates/${bankCode}`;
    
    return this.http.get<any[]>(url).pipe(
      catchError(error => {
        console.error(`❌ Error fetching templates for bank ${bankCode}:`, error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get specific template information
   */
  getTemplate(templateId: string): Observable<any> {
    const url = `${this.API_BASE_URL}/templates/${templateId}`;
    
    return this.http.get<any>(url).pipe(
      catchError(error => {
        console.error(`❌ Error fetching template ${templateId}:`, error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Helper method to build form validation rules from field configuration
   */
  buildValidationRules(field: TemplateField | BankSpecificField): any[] {
    const validators = [];

    // Required validation
    if (field.isRequired) {
      validators.push('required');
    }

    // Pattern validation
    if (field.validation?.pattern) {
      validators.push({ pattern: field.validation.pattern });
    }

    // Length validations
    if (field.validation?.minLength) {
      validators.push({ minLength: field.validation.minLength });
    }
    if (field.validation?.maxLength) {
      validators.push({ maxLength: field.validation.maxLength });
    }

    // Numeric validations
    if (field.validation?.min !== undefined) {
      validators.push({ min: field.validation.min });
    }
    if (field.validation?.max !== undefined) {
      validators.push({ max: field.validation.max });
    }

    return validators;
  }

  /**
   * Get default value for a field based on its configuration
   */
  getFieldDefaultValue(field: TemplateField | BankSpecificField, contextData?: any): any {
    if (field.defaultValue) {
      // Handle special default value cases
      if (field.fieldType === 'date' && field.defaultValue === 'today') {
        return new Date().toISOString().split('T')[0];
      }
      return field.defaultValue;
    }

    // Context-based defaults
    if (contextData) {
      switch (field.fieldId) {
        case 'bank_name':
          return contextData.bankName || '';
        case 'bank_code':
          return contextData.bankCode || '';
        case 'template_name':
          return contextData.templateName || '';
        default:
          break;
      }
    }

    // Default values by field type
    switch (field.fieldType) {
      case 'text':
      case 'email':
      case 'tel':
      case 'textarea':
        return '';
      case 'number':
      case 'currency':
        return null;
      case 'date':
        return '';
      case 'select':
      case 'select_dynamic':
        return '';
      case 'checkbox':
        return false;
      case 'radio':
        return '';
      default:
        return '';
    }
  }
}