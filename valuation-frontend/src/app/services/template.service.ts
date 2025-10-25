import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { AggregatedTemplateResponse, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField } from '../models';

@Injectable({
  providedIn: 'root'
})
export class TemplateService {
  private readonly API_BASE_URL = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  /**
   * Get aggregated template fields (common + bank-specific) for a specific bank and template
   */
  getAggregatedTemplateFields(bankCode: string, templateId: string): Observable<AggregatedTemplateResponse> {
    const url = `${this.API_BASE_URL}/templates/${bankCode}/${templateId}/aggregated-fields`;
    
    console.log(`� TemplateService: Making API call to ${url}`);
    
    return this.http.get<AggregatedTemplateResponse>(url).pipe(
      catchError(error => {
        console.error(`❌ TemplateService: API call failed for ${bankCode}/${templateId}:`, error);
        if (error.status === 0) {
          console.error('❌ Network error - check if backend is running and CORS is configured');
        }
        return throwError(() => error);
      })
    );
  }

  /**
   * Process aggregated template response into organized field groups
   */
  processTemplateData(response: AggregatedTemplateResponse): ProcessedTemplateData {
    console.log('� TemplateService.processTemplateData called with:', {
      commonFields: response.commonFields?.length || 0,
      bankSpecificFields: response.bankSpecificFields?.length || 0,
      templateInfo: response.templateInfo
    });

    // Process common fields into groups
    const commonFieldGroups = this.groupFieldsByGroup(response.commonFields, 'Common');
    console.log('🔥 Common field groups created:', commonFieldGroups.length);

    // Process bank-specific fields into groups
    const bankSpecificFieldGroups = this.groupFieldsByGroup(response.bankSpecificFields, 'Bank-Specific');
    console.log('🔥 Bank-specific field groups created:', bankSpecificFieldGroups.length);

    // Combine all fields for form building
    const allFields = [...response.commonFields, ...response.bankSpecificFields];

    const processedData: ProcessedTemplateData = {
      templateInfo: response.templateInfo,
      commonFieldGroups,
      bankSpecificFieldGroups,
      allFields,
      totalFieldCount: allFields.length
    };

    console.log('🔥 ProcessedTemplateData result:', {
      commonGroups: commonFieldGroups.length,
      bankSpecificGroups: bankSpecificFieldGroups.length,
      totalFields: processedData.totalFieldCount,
      processedData: processedData
    });

    return processedData;
  }

  /**
   * Group fields by their fieldGroup property or intelligently categorize them
   */
  private groupFieldsByGroup(fields: (TemplateField | BankSpecificField)[], defaultPrefix: string): FieldGroup[] {
    // For bank-specific fields, use the correct document-based grouping
    if (defaultPrefix === 'Bank-Specific') {
      return this.createDocumentBasedFieldGroups(fields);
    }
    
    // For common fields, use the existing logic
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

  /**
   * Create field groups based on the SBI Land document structure
   */
  private createDocumentBasedFieldGroups(fields: (TemplateField | BankSpecificField)[]): FieldGroup[] {
    console.log('🔧 Creating document-based field groups for SBI Land template:', fields.length);

    // Define the expected 5 tabs based on SBI Land structure
    const fieldGroups: FieldGroup[] = [];
    let currentIndex = 0;

    // Tab 1: Property Details (first 17 fields)
    if (fields.length >= 17) {
      fieldGroups.push({
        groupName: 'property_details',
        displayName: 'Property Details',
        fields: fields.slice(0, 17),
        sortOrder: 1
      });
      currentIndex = 17;
    }

    // Tab 2: Site Characteristics (next 19 fields)  
    if (fields.length >= currentIndex + 19) {
      fieldGroups.push({
        groupName: 'site_characteristics',
        displayName: 'Site Characteristics',
        fields: fields.slice(currentIndex, currentIndex + 19),
        sortOrder: 2
      });
      currentIndex += 19;
    }

    // Tab 3: Land Valuation (next 6 fields - this represents Part A + Part B combined)
    // Note: In the flattened structure, we're getting fewer fields than expected
    // So we'll take what's available after the first two groups
    const remainingFields = fields.length - currentIndex;
    const landValuationCount = Math.min(6, Math.floor(remainingFields / 3)); // Distribute remaining fields across 3 tabs
    
    if (remainingFields > 0 && landValuationCount > 0) {
      fieldGroups.push({
        groupName: 'land_valuation',
        displayName: 'Land Valuation',
        fields: fields.slice(currentIndex, currentIndex + landValuationCount),
        sortOrder: 3
      });
      currentIndex += landValuationCount;
    }

    // Tab 4: Construction Specifications (next batch of fields)
    const constructionCount = Math.min(10, fields.length - currentIndex - 6); // Leave some for detailed valuation
    if (fields.length > currentIndex && constructionCount > 0) {
      fieldGroups.push({
        groupName: 'construction_specifications',
        displayName: 'Construction Specifications',
        fields: fields.slice(currentIndex, currentIndex + constructionCount),
        sortOrder: 4
      });
      currentIndex += constructionCount;
    }

    // Tab 5: Detailed Valuation (remaining fields)
    if (currentIndex < fields.length) {
      fieldGroups.push({
        groupName: 'detailed_valuation',
        displayName: 'Detailed Valuation',
        fields: fields.slice(currentIndex),
        sortOrder: 5
      });
    }

    console.log('📋 Created 5 document-based groups:', fieldGroups.map(g => `${g.displayName} (${g.fields.length})`));
    
    return fieldGroups.sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0));
  }

  /**
   * Create intelligent field groups for bank-specific fields based on content and purpose
   */
  private createIntelligentBankFieldGroups(fields: (TemplateField | BankSpecificField)[]): FieldGroup[] {
    // Define category interface for proper typing
    interface CategoryDefinition {
      name: string;
      keywords: string[];
      sortOrder: number;
      fields: (TemplateField | BankSpecificField)[];
    }

    const categories: Record<string, CategoryDefinition> = {
      'property_basics': {
        name: 'Property Details',
        keywords: ['document', 'address', 'description', 'city', 'area_type', 'municipal', 'classification', 'location', 'property', 'plot', 'survey', 'ownership'],
        sortOrder: 1,
        fields: []
      },
      'location_boundaries': {
        name: 'Location & Boundaries', 
        keywords: ['boundary', 'boundaries', 'dimension', 'longitude', 'latitude', 'site_area', 'valuation_area', 'occupied', 'north', 'south', 'east', 'west', 'measurement', 'extent'],
        sortOrder: 2,
        fields: []
      },
      'infrastructure': {
        name: 'Infrastructure & Amenities',
        keywords: ['road', 'water', 'power', 'sewerage', 'flooding', 'civic', 'topography', 'usage', 'planning', 'connectivity', 'transport', 'drainage', 'supply'],
        sortOrder: 3,
        fields: []
      },
      'construction': {
        name: 'Construction Details',
        keywords: ['foundation', 'basement', 'superstructure', 'joinery', 'rcc', 'plaster', 'floor', 'roof', 'drainage', 'compound', 'height', 'length', 'construction', 'building', 'structure'],
        sortOrder: 4,
        fields: []
      },
      'installations': {
        name: 'Installations',
        keywords: ['electrical', 'plumbing', 'installation', 'fitting', 'fixture'],
        sortOrder: 5,
        fields: []
      },
      'misc': {
        name: 'Additional Information',
        keywords: [], // Catch-all for remaining fields
        sortOrder: 6,
        fields: []
      }
    };

    console.log('🔧 Categorizing fields for intelligent grouping:', fields.length);

    // Categorize fields based on keywords and content
    fields.forEach(field => {
      const fieldId = field.fieldId.toLowerCase();
      const displayName = (field.uiDisplayName || '').toLowerCase();
      const helpText = (field.helpText || '').toLowerCase();
      let assigned = false;

      console.log(`🔍 Processing field: ${field.fieldId} (${field.uiDisplayName})`);

      // Try to assign to appropriate category based on keywords
      for (const [categoryKey, category] of Object.entries(categories)) {
        if (categoryKey === 'misc') continue; // Skip misc for now
        
        const hasKeyword = category.keywords.some(keyword => 
          fieldId.includes(keyword) || displayName.includes(keyword) || helpText.includes(keyword)
        );
        
        if (hasKeyword) {
          category.fields.push(field);
          assigned = true;
          console.log(`  ✅ Assigned to ${category.name}`);
          break;
        }
      }

      // If not assigned, put in misc category
      if (!assigned) {
        categories['misc'].fields.push(field);
        console.log(`  ⚠️ Assigned to Additional Information (fallback)`);
      }
    });

    // Create FieldGroup objects, excluding empty categories
    const fieldGroups: FieldGroup[] = [];
    
    Object.entries(categories).forEach(([categoryKey, category]) => {
      if (category.fields.length > 0) {
        // Sort fields within category by their original sortOrder
        const sortedFields = category.fields.sort((a, b) => a.sortOrder - b.sortOrder);
        
        fieldGroups.push({
          groupName: categoryKey,
          displayName: category.name,
          fields: sortedFields,
          sortOrder: category.sortOrder
        });

        console.log(`📋 Created group "${category.name}" with ${sortedFields.length} fields`);
      }
    });

    const finalGroups = fieldGroups.sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0));
    console.log('🎯 Final group structure:', finalGroups.map(g => `${g.displayName} (${g.fields.length})`));
    
    return finalGroups;
  }

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