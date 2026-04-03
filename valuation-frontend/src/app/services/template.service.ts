import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError, map } from 'rxjs';
import { AggregatedTemplateResponse, ProcessedTemplateData, FieldGroup, TemplateField, BankSpecificField, BankSpecificTab, BankSpecificSection, FieldType, FieldOption } from '../models';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TemplateService {
  private readonly API_BASE_URL = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Get aggregated template fields (common + bank-specific) for a specific bank and template
   */
  getAggregatedTemplateFields(bankCode: string, templateCode: string): Observable<AggregatedTemplateResponse> {
    // Capitalize first letter of propertyType to match backend format (land -> Land, apartment -> Apartment)
    const propertyType = templateCode.charAt(0).toUpperCase() + templateCode.slice(1).toLowerCase();
    
    // Backend endpoint: /api/templates/{bankCode}/{propertyType}
    const url = `${this.API_BASE_URL}/templates/${bankCode}/${propertyType}`;
    
    console.log(`🌐 TemplateService: Making API call to ${url} (templateCode: ${templateCode} -> propertyType: ${propertyType})`);
    
    return this.http.get<any>(url).pipe(
      map((apiResponse: any) => {
        console.log('📦 Backend API Response:', apiResponse);
        
        // Extract template data from ApiResponse wrapper
        const templateData = apiResponse.data || apiResponse;
        console.log('📦 Extracted template data:', {
          templateId: templateData.templateId,
          elementCount: templateData.elements?.length || 0
        });
        
        // Transform new backend DTO format to frontend expected format
        return this.transformBackendDtoToFrontend(templateData, bankCode);
      }),
      catchError(error => {
        console.error(`❌ TemplateService: API call failed for ${bankCode}/${propertyType}:`, error);
        if (error.status === 0) {
          console.error('❌ Network error - check if backend is running and CORS is configured');
        } else if (error.status === 404) {
          console.error('❌ Template not found - check if template exists in database');
        }
        return throwError(() => error);
      })
    );
  }

  /**
   * Transform new backend DTO format to frontend expected format
   */
  private transformBackendDtoToFrontend(templateDto: any, bankCode: string): AggregatedTemplateResponse {
    console.log('🔄 Transforming backend DTO to frontend format');
    
    const elements = templateDto.elements || [];
    
    // Separate root-level elements into common fields and bank-specific tabs
    const commonFields: TemplateField[] = [];
    const bankSpecificTabs: BankSpecificTab[] = [];
    
    elements.forEach((element: any, index: number) => {
      console.log(`🔍 Element ${index}: $type=${element.$type}, container=${element.container}, fieldId=${element.fieldId}`);
      
      if (element.$type === 'container' && element.container === 'TabGroup') {
        // New structure: TabGroup container with Tab children
        console.log(`📂 Found TabGroup: ${element.fieldId} - ${element.label}`);
        const tabs = element.children || [];
        tabs.forEach((tab: any) => {
          console.log(`  📁 Processing Tab: ${tab.fieldId} - ${tab.label}`);
          const transformedTab = this.transformContainerToTab(tab);
          bankSpecificTabs.push(transformedTab);
        });
      } else if (element.$type === 'container' && element.container === 'Tab') {
        // Standalone Tab (shouldn't happen with new structure, but support for compatibility)
        console.log(`📁 Found standalone tab: ${element.fieldId} - ${element.label}`);
        const tab = this.transformContainerToTab(element);
        bankSpecificTabs.push(tab);
      } else if (element.$type === 'tab') {
        // Old structure: Tab element (colleague's refactor uses $type: 'tab')
        console.log(`📁 Found old tab: ${element.fieldId} - ${element.label}`);
        const tab = this.transformContainerToTab(element);
        bankSpecificTabs.push(tab);
      } else if (element.$type === 'tabgroup') {
        // Old structure: TabGroup element
        console.log(`📂 Found old tabgroup: ${element.fieldId} - ${element.label}`);
        const tab = this.transformContainerToTab(element);
        bankSpecificTabs.push(tab);
      } else if (element.$type === 'input' || element.$type === 'group' || element.$type === 'table' || element.$type === 'attachment') {
        // Non-container at root level = Common field (Basic Information)
        console.log(`📄 Found common field: ${element.fieldId} - ${element.label}`);
        const field = this.transformElementToField(element, true); // true = isCommonField, no grouping
        commonFields.push(field);
      } else {
        console.warn('⚠️ Unknown element type at root level:', element.$type, element);
      }
    });
    
    console.log(`✅ Transformed ${commonFields.length} common fields and ${bankSpecificTabs.length} bank-specific tabs`);
    
    return {
      templateInfo: {
        templateId: templateDto.templateId,
        templateName: templateDto.templateName,
        propertyType: this.mapBackendPropertyTypeToFrontend(templateDto.propertyType),
        bankCode: bankCode,
        bankName: templateDto.bankDetails?.bankName || bankCode,
        version: '1.0'
      },
      commonFields: commonFields,
      bankSpecificTabs: bankSpecificTabs,
      documentTypes: [], // Document types not in current response
      aggregatedAt: new Date().toISOString()
    };
  }

  /**
   * Transform a backend element to frontend field format
   */
  private transformElementToField(element: any, isCommonField: boolean = false): TemplateField {
    const fieldLabel = element.label || this.formatFieldName(element.fieldId);
    
    return {
      _id: element._id || '',
      fieldId: element.fieldId,
      technicalName: element.fieldId,
      uiDisplayName: fieldLabel,
      fieldType: this.mapBackendFieldTypeToFrontend(element.fieldType, element.$type) as FieldType,
      displayOrder: element.displayOrder || 0,
      sortOrder: element.displayOrder || 0,
      isRequired: element.isRequired || false,
      isReadonly: element.isReadonly || false,
      helpText: element.helpText || '',
      placeholder: element.placeholderText || '',
      defaultValue: element.defaultValue || null,
      options: this.transformOptions(element.options),
      validation: element.validationRules || undefined,
      isActive: element.isVisible !== false,
      // Only set fieldGroup for non-common fields
      fieldGroup: isCommonField ? undefined : this.determineFieldGroup(element.fieldId),
      gridSize: this.parseGridSize(this.determineGridSize(element.fieldType, element.$type)),
      
      // Table-specific fields
      columns: element.columns || undefined,
      rows: element.rows || undefined,
      
      // Container-specific fields (for groups)
      subFields: element.children ? element.children.map((child: any) => this.transformElementToField(child, false)) : undefined
    } as TemplateField;
  }

  /**
   * Transform a container element to a bank-specific tab
   * Container enum: 0 = Tab, 1 = Group, 2 = Section
   */
  private transformContainerToTab(container: any): BankSpecificTab {
    const children = container.children || [];
    
    // Separate direct fields from sections/groups
    const directFields: TemplateField[] = [];
    const sections: BankSpecificSection[] = [];
    
    children.forEach((child: any) => {
      console.log(`  🔍 Tab child: $type=${child.$type}, container=${child.container}, fieldId=${child.fieldId}`);
      
      if (child.$type === 'container' && child.container === 'Section') {
        // New structure: Section container
        console.log(`    📑 Processing section (new): ${child.fieldId}`);
        sections.push(this.transformContainerToSection(child));
      } else if (child.$type === 'container' && child.container === 'Group') {
        // New structure: Group container at tab level - treat as a section
        console.log(`    📦 Processing group as section (new): ${child.fieldId}`);
        sections.push(this.transformGroupToField(child));
      } else if (child.$type === 'section') {
        // Old structure: Section element (colleague's refactor)
        console.log(`    📑 Processing section (old): ${child.fieldId}`);
        sections.push(this.transformContainerToSection(child));
      } else if (child.$type === 'group') {
        // Old structure: Group element at tab level - treat as a section
        console.log(`    📦 Processing group as section (old): ${child.fieldId}`);
        sections.push(this.transformGroupToField(child));
      } else if (child.$type === 'container') {
        // Legacy container format with numeric types
        if (child.container === 3 || child.container === 'Section') {
          // Container type 3 or "Section" = Section
          sections.push(this.transformContainerToSection(child));
        } else if (child.container === 2 || child.container === 'Group') {
          // Container type 2 or "Group" = Group - treat as section for now
          sections.push(this.transformGroupToField(child));
        } else {
          console.warn('⚠️ Unexpected nested container:', child);
        }
      } else if (child.$type === 'table') {
        // Table element - add as direct field
        console.log(`    📊 Processing table: ${child.fieldId}`);
        directFields.push(this.transformTableToField(child));
      } else {
        // Direct field in tab (input, attachment, etc.)
        console.log(`    📄 Processing direct field: ${child.fieldId}`);
        directFields.push(this.transformElementToField(child, false));
      }
    });
    
    console.log(`  ✅ Tab ${container.fieldId}: ${directFields.length} direct fields, ${sections.length} sections`);
    
    return {
      tabId: container.fieldId,
      tabName: container.label || this.formatFieldName(container.fieldId),
      sortOrder: container.displayOrder || 0,
      fields: directFields,
      sections: sections,
      hasSections: sections.length > 0
    };
  }

  /**
   * Transform a container element to a section within a tab
   * Handles both Section and Group elements
   */
  private transformContainerToSection(container: any): BankSpecificSection {
    const children = container.children || [];
    
    // Process children
    const fields: any[] = [];
    
    children.forEach((child: any) => {
      console.log(`      🔍 Section child: $type=${child.$type}, container=${child.container}, fieldId=${child.fieldId}`);
      
      if (child.$type === 'container' && child.container === 'Group') {
        // New structure: Group container within Section
        console.log(`        📦 Processing group (new): ${child.fieldId}`);
        fields.push(this.transformGroupToField(child));
      } else if (child.$type === 'container' && child.container === 'Section') {
        // New structure: Nested Section container
        console.log(`        📑 Processing nested section (new): ${child.fieldId}`);
        const nestedSection = this.transformContainerToSection(child);
        fields.push(nestedSection);
      } else if (child.$type === 'group') {
        // Old structure: Group within Section
        console.log(`        📦 Processing group (old): ${child.fieldId}`);
        fields.push(this.transformGroupToField(child));
      } else if (child.$type === 'section') {
        // Old structure: Nested Section
        console.log(`        📑 Processing nested section (old): ${child.fieldId}`);
        const nestedSection = this.transformContainerToSection(child);
        fields.push(nestedSection);
      } else if (child.$type === 'table') {
        // Table element
        console.log(`        📊 Processing table: ${child.fieldId}`);
        fields.push(this.transformTableToField(child));
      } else if (child.$type === 'container') {
        // Legacy container format with numeric types
        if (child.container === 2 || child.container === 'Group') {
          // Container type 2 or "Group" = Group
          fields.push(this.transformGroupToField(child));
        } else if (child.container === 3 || child.container === 'Section') {
          // Container type 3 = Section
          const nestedSection = this.transformContainerToSection(child);
          fields.push(nestedSection);
        }
      } else {
        // Regular field (input, attachment, etc.)
        console.log(`        📄 Processing field: ${child.fieldId}`);
        fields.push(this.transformElementToField(child, false));
      }
    });
    
    console.log(`      ✅ Section ${container.fieldId}: ${fields.length} fields`);
    
    return {
      sectionId: container.fieldId,
      sectionName: container.label || this.formatFieldName(container.fieldId),
      sortOrder: container.displayOrder || 0,
      fields: fields
    };
  }

  /**
   * Transform a Group container to a group field with subFields
   */
  private transformGroupToField(container: any): any {
    const children = container.children || [];
    const subFields = children.map((child: any) => {
      if (child.$type === 'container' && child.container === 'Group') {
        // New structure: Nested Group container - recursive
        return this.transformGroupToField(child);
      } else if (child.$type === 'group') {
        // Old structure: Nested group - recursive
        return this.transformGroupToField(child);
      } else {
        return this.transformElementToField(child, false);
      }
    });
    
    const fieldLabel = container.label || this.formatFieldName(container.fieldId);
    
    // Groups should use grid-3 (which means 4 fields per row: 12/3 = 4)
    // This ensures group fields align with regular input fields
    const gridSize = 3;
    
    return {
      fieldId: container.fieldId,
      label: fieldLabel,
      uiDisplayName: fieldLabel,
      fieldType: 'group',
      displayOrder: container.displayOrder || 0,
      sortOrder: container.displayOrder || 0,
      isRequired: false,
      isReadonly: false,
      isVisible: container.isVisible !== false,
      subFields: subFields,
      gridSize: gridSize  // Return as number, not string
    };
  }

  /**
   * Transform a table element to a field
   */
  private transformTableToField(table: any): any {
    const fieldLabel = table.label || this.formatFieldName(table.fieldId);
    
    // Transform columns to ensure they have proper field types
    const columns = (table.columns || []).map((col: any) => ({
      fieldId: col.fieldId,
      label: col.label,
      fieldType: this.mapBackendFieldTypeToFrontend(col.fieldType, 'input'),
      width: col.width || null,
      isReadonly: col.isReadonly || false,
      options: col.options ? this.transformOptions(col.options) : null,
      validationRules: col.validationRules || null
    }));
    
    // Initialize rows based on minRows if no rows provided by API
    let rows = table.rows || [];
    const minRows = table.minRows || 1;
    
    // Only create empty rows if API didn't provide any AND minRows > 0
    if (rows.length === 0 && minRows > 0) {
      // Create empty rows with default values
      rows = Array.from({ length: minRows }, () => {
        const row: any = {};
        columns.forEach((col: any) => {
          row[col.fieldId] = '';
        });
        return row;
      });
    }
    
    return {
      fieldId: table.fieldId,
      label: fieldLabel,
      uiDisplayName: fieldLabel,
      fieldType: 'table',
      displayOrder: table.displayOrder || 0,
      sortOrder: table.displayOrder || 0,
      isRequired: false,
      isReadonly: false,
      isVisible: table.isVisible !== false,
      columns: columns,
      rows: rows,
      minRows: minRows,
      maxRows: table.maxRows || undefined,
      allowAddRows: table.allowAddRows !== false,
      allowDeleteRows: table.allowDeleteRows !== false,
      showFooter: table.showFooter !== false,
      gridSize: 12  // Full width as number, not string
    };
  }

  /**
   * Transform backend options array
   */
  private transformOptions(options: any): any[] {
    if (!options || !Array.isArray(options)) {
      return [];
    }
    
    // If options are already in {value, label} format, return as-is
    if (options.length > 0 && typeof options[0] === 'object' && options[0].value !== undefined) {
      return options;
    }
    
    // If options are strings (from C# backend which returns List<string>), 
    // transform them to {value, label} format
    if (options.length > 0 && typeof options[0] === 'string') {
      return options.map((opt: string) => ({
        value: this.stringToValue(opt),
        label: opt
      }));
    }
    
    // Empty or invalid format
    return [];
  }

  /**
   * Convert a label string to a valid value format
   * Example: "Home Loan" -> "home_loan"
   */
  private stringToValue(label: string): string {
    return label
      .toLowerCase()
      .replace(/\s+/g, '_')
      .replace(/[^\w_]/g, '');
  }

  /**
   * Map backend field type enum to frontend string
   */
  private mapBackendFieldTypeToFrontend(backendFieldType: number, discriminator: string): string {
    // Use $type discriminator for base type
    if (discriminator === 'table') return 'table';
    if (discriminator === 'container') return 'container';
    if (discriminator === 'attachment') return 'attachment';
    
    // Map input field types (fieldType enum from backend)
    const fieldTypeMap: { [key: number]: string } = {
      0: 'text',       // Text
      1: 'number',     // Number  
      2: 'date',       // Date
      3: 'select',     // Dropdown (mapped to 'select' for frontend compatibility)
      4: 'textarea',   // TextArea
      5: 'currency',   // Currency
      6: 'checkbox',   // Checkbox
      7: 'radio',      // Radio
      8: 'email',      // Email
      9: 'phone',      // Phone
      10: 'url',       // Url
      11: 'file'       // File
    };
    
    return fieldTypeMap[backendFieldType] || 'text';
  }

  /**
   * Map backend property type enum to frontend string
   */
  private mapBackendPropertyTypeToFrontend(propertyType: number): string {
    const propertyTypeMap: { [key: number]: string } = {
      1: 'house',
      2: 'apartment',
      3: 'land',
      4: 'commercial'
    };
    
    return propertyTypeMap[propertyType] || 'land';
  }

  /**
   * Determine field group based on field ID
   */
  private determineFieldGroup(fieldId: string): string {
    if (fieldId.includes('applicant') || fieldId.includes('name') || fieldId.includes('contact')) {
      return 'basic_information';
    }
    if (fieldId.includes('property') || fieldId.includes('location') || fieldId.includes('address')) {
      return 'property_details';
    }
    if (fieldId.includes('document') || fieldId.includes('title') || fieldId.includes('legal')) {
      return 'document_details';
    }
    if (fieldId.includes('boundary') || fieldId.includes('measurement') || fieldId.includes('dimension')) {
      return 'property_measurements';
    }
    if (fieldId.includes('valuation') || fieldId.includes('rate') || fieldId.includes('value') || fieldId.includes('market')) {
      return 'valuation';
    }
    
    return 'basic_information'; // Default group
  }

  /**
   * Format field name from fieldId (convert snake_case to Title Case)
   */
  private formatFieldName(fieldId: string): string {
    return fieldId
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
   * Determine grid size for field layout
   */
  private determineGridSize(fieldType: number, discriminator: string): string {
    // Tables and containers take full width
    if (discriminator === 'table' || discriminator === 'container') {
      return 'full';
    }
    
    // Textareas take full width
    if (fieldType === 4) { // TextArea
      return 'full';
    }
    
    // Default to grid-3 (4 fields per row: 12/3 = 4)
    return '3';
  }

  /**
   * Parse grid size string to number for TemplateField interface
   */
  private parseGridSize(gridSize: string): number {
    if (gridSize === 'full' || gridSize === '12') {
      return 12;
    }
    const parsed = parseInt(gridSize, 10);
    return isNaN(parsed) ? 3 : parsed;
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

    // Debug common fields structure before grouping
    console.log('🔍 Raw common fields structure:', response.commonFields);
    if (response.commonFields && response.commonFields.length > 0) {
      console.log('🔍 First common field:', response.commonFields[0]);
    }

    // Process common fields into groups
    const commonFieldGroups = this.groupFieldsByGroup(response.commonFields, 'Common');
    console.log('🔥 Common field groups created:', {
      groupCount: commonFieldGroups.length,
      groups: commonFieldGroups.map(g => ({
        name: g.groupName,
        displayName: g.displayName,
        fieldsCount: g.fields.length
      }))
    });

    // Bank-specific tabs are already structured properly from the backend
    const bankSpecificTabs = response.bankSpecificTabs || [];
    console.log('🔥 Bank-specific tabs received:', bankSpecificTabs.length);

    // Combine all fields for form building (flatten tabs and sections)
    const allFields: (TemplateField | BankSpecificField)[] = [...(response.commonFields || [])];

    // Extract all fields from tabs and sections, including sub-fields from group fields
    (bankSpecificTabs || []).forEach(tab => {
      // Add tab-level fields (guard against null/undefined)
      const tabFields = Array.isArray(tab.fields) ? tab.fields : [];
      tabFields.forEach(field => {
        allFields.push(field);
        // If it's a group field, also add its sub-fields
        if (field && field.fieldType === 'group' && Array.isArray(field.subFields)) {
          allFields.push(...field.subFields);
        }
      });

      // Add section-level fields (guard against missing sections)
      if (Array.isArray(tab.sections)) {
        tab.sections.forEach(section => {
          const sectionFields = Array.isArray(section.fields) ? section.fields : [];
          sectionFields.forEach(field => {
            allFields.push(field);
            // If it's a group field, also add its sub-fields
            if (field && field.fieldType === 'group' && Array.isArray(field.subFields)) {
              allFields.push(...field.subFields);
            }
          });
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
      bankSpecificTabs: (bankSpecificTabs || []).length,
      totalFields: processedData.totalFieldCount,
      tabDetails: (bankSpecificTabs || []).map(tab => ({
        tabId: tab?.tabId,
        tabName: tab?.tabName,
        fieldsCount: Array.isArray(tab?.fields) ? tab.fields.length : 0,
        sectionsCount: Array.isArray(tab?.sections) ? tab.sections.length : 0,
        hasSections: !!tab?.hasSections
      }))
    });

    return processedData;
  }

  /**
   * Group fields by their fieldGroup property (used for common fields only)
   */
  private groupFieldsByGroup(fields: (TemplateField | BankSpecificField)[], defaultPrefix: string): FieldGroup[] {
    console.log('🔍 groupFieldsByGroup called with:', {
      fieldsLength: fields?.length || 0,
      defaultPrefix,
      firstField: fields?.[0]
    });

    if (!fields || fields.length === 0) {
      console.log('⚠️ No fields provided to groupFieldsByGroup');
      return [];
    }

    const groupMap = new Map<string, (TemplateField | BankSpecificField)[]>();

    fields.forEach((field, index) => {
      const groupName = field.fieldGroup || 'default';
      console.log(`🔍 Field ${index}: ${field.fieldId} -> group: ${groupName}`, field);
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
        return null;
      default:
        return '';
    }
  }

  /**
   * Create a custom template from a filled report form
   * 
   * @param orgShortName Organization short name
   * @param templateName Name for the new custom template
   * @param description Optional description for the template
   * @param bankCode Bank code (e.g., 'SBI', 'HDFC')
   * @param templateCode Template code (e.g., 'land-property')
   * @param fieldValues All field values from the report form
   * @returns Observable with the created template response
   */
  createTemplateFromReport(
    orgShortName: string,
    templateName: string,
    description: string | null,
    bankCode: string,
    templateCode: string,
    fieldValues: Record<string, any>
  ): Observable<any> {
    const url = `${this.API_BASE_URL}/organizations/${orgShortName}/templates/from-report`;
    
    const payload = {
      templateName,
      description: description || undefined,
      bankCode,
      templateCode,
      fieldValues
    };

    // Get token from localStorage and add to headers manually
    const token = localStorage.getItem('valuation_app_token');
    
    const options = token ? {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    } : {};

    console.log('🌐 TemplateService.createTemplateFromReport:', {
      url,
      templateName,
      bankCode,
      templateCode,
      fieldCount: Object.keys(fieldValues).length,
      hasToken: !!token,
      tokenPreview: token?.substring(0, 30)
    });

    return this.http.post<any>(url, payload, options).pipe(
      catchError(error => {
        console.error('❌ TemplateService.createTemplateFromReport failed:', error);
        
        // Enhanced error logging
        if (error.status === 400) {
          console.error('❌ Validation error:', error.error?.error || error.message);
        } else if (error.status === 403) {
          console.error('❌ Permission denied:', error.error?.error || error.message);
        } else if (error.status === 404) {
          console.error('❌ Resource not found:', error.error?.error || error.message);
        } else if (error.status === 0) {
          console.error('❌ Network error - check if backend is running');
        }
        
        return throwError(() => error);
      })
    );
  }

  // ================================
  // REPORT MANAGEMENT METHODS
  // ================================

  /**
   * Create a new report with properly structured data
   */
  createReport(request: any): Observable<any> {
    console.log('🔄 TemplateService.createReport called with:', request);
    
    // Structure the data properly for the backend
    const reportData = {
      bank_code: request.bankCode,
      template_id: request.templateId || 'land-property', // Default template
      property_address: request.propertyAddress || 'Property Address TBD',
      report_data: this.organizeReportDataByTabs(request.initialData || {})
    };
    
    console.log('📋 Organized report data for creation:', reportData);
    
    // Get token and organization context with proper headers type
    const token = localStorage.getItem('valuation_app_token');
    const options: any = {};
    if (token) {
      options.headers = { 'Authorization': `Bearer ${token}` };
    }
    
    return this.http.post<any>(`${this.API_BASE_URL}/reports`, reportData, options).pipe(
      catchError(error => {
        console.error('❌ TemplateService.createReport failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Update an existing report with properly structured data
   */
  updateReport(reportId: string, updates: any): Observable<any> {
    console.log('🔄 TemplateService.updateReport called:', { reportId, updates });
    
    // Structure the data properly for the backend
    const updateData = {
      report_data: this.organizeReportDataByTabs(updates.data || {}),
      status: updates.status || 'draft'
    };
    
    console.log('📋 Organized update data:', updateData);
    
    // Get token with proper headers type
    const token = localStorage.getItem('valuation_app_token');
    const options: any = {};
    if (token) {
      options.headers = { 'Authorization': `Bearer ${token}` };
    }
    
    return this.http.put<any>(`${this.API_BASE_URL}/reports/${reportId}`, updateData, options).pipe(
      catchError(error => {
        console.error('❌ TemplateService.updateReport failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Submit a report for review
   */
  submitReport(reportId: string, message: string): Observable<any> {
    console.log('🔄 TemplateService.submitReport called:', { reportId, message });
    
    // Get token with proper headers type
    const token = localStorage.getItem('valuation_app_token');
    const options: any = {};
    if (token) {
      options.headers = { 'Authorization': `Bearer ${token}` };
    }
    
    return this.http.post<any>(`${this.API_BASE_URL}/reports/${reportId}/submit`, { message }, options).pipe(
      catchError(error => {
        console.error('❌ TemplateService.submitReport failed:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Organize flat form data into proper tab structure for backend storage
   * This is the KEY method that fixes the data structure issue
   */
  private organizeReportDataByTabs(flatData: Record<string, any>): Record<string, any> {
    console.log('🔄 Organizing flat data into tab structure:', flatData);
    
    // Define the expected tab structure for land property valuation
    const organizedData: Record<string, any> = {
      property_details: {
        property_part_a: {},
        property_part_b: {},
        property_part_c: {},
        property_part_d: {}
      },
      site_characteristics: {
        site_part_a: {},
        site_part_b: {}
      },
      valuation: {
        valuation_part_a: {},
        valuation_part_b: {}
      },
      construction_specifications: {
        construction_part_a: {},
        construction_part_b: {}
      },
      detailed_valuation: {}
    };

    // Complete field mappings based on SBI Land template structure
    // Note: Group fields should have their subFields mapped individually
    const fieldMappings: Record<string, string> = {
      // Property Details - Part A (Documents)
      'agreement_to_sell': 'property_details.property_part_a.agreement_to_sell',
      'list_of_documents_produced': 'property_details.property_part_a.list_of_documents_produced',
      'allotment_letter': 'property_details.property_part_a.allotment_letter',
      'layout_plan': 'property_details.property_part_a.layout_plan',
      'sales_deed': 'property_details.property_part_a.sales_deed',
      'ats': 'property_details.property_part_a.ats',
      'sanctioned_building_plan': 'property_details.property_part_a.sanctioned_building_plan',
      
      // Property Details - Part B (Address Details)
      'owner_details': 'property_details.property_part_b.owner_details',
      'borrower_name': 'property_details.property_part_b.borrower_name',
      'postal_address': 'property_details.property_part_b.postal_address',
      'property_description': 'property_details.property_part_b.property_description',
      
      // Property Location Group (in property_part_b)
      'property_location': 'property_details.property_part_b.property_location',
      'plot_survey_no': 'property_details.property_part_b.property_location.plot_survey_no',
      'door_no': 'property_details.property_part_b.property_location.door_no',
      'ts_no_village': 'property_details.property_part_b.property_location.ts_no_village',
      'ward_taluka_tehsil': 'property_details.property_part_b.property_location.ward_taluka_tehsil',
      'mandal_district': 'property_details.property_part_b.property_location.mandal_district',
      
      'city_town_village': 'property_details.property_part_b.city_town_village',
      
      // Property Details - Part C (Property Information)
      // Area Classification Group (in property_part_c)
      'area_classification': 'property_details.property_part_c.area_classification',
      'socio_economic_class': 'property_details.property_part_c.area_classification.socio_economic_class',
      'urban_rural': 'property_details.property_part_c.area_classification.urban_rural',
      'area_type': 'property_details.property_part_c.area_classification.area_type',
      'municipal_corporation': 'property_details.property_part_c.area_classification.municipal_corporation',
      
      // Government Regulation Group (in property_part_c)
      'government_regulation': 'property_details.property_part_c.government_regulation',
      'state_enactments': 'property_details.property_part_c.government_regulation.state_enactments',
      'agriculture_conversion': 'property_details.property_part_c.government_regulation.agriculture_conversion',
      
      // Property Details - Part D (Boundaries and Coordinates)
      'boundaries_dimensions_table': 'property_details.property_part_d.boundaries_dimensions_table',
      
      // Coordinates Group (in property_part_d)
      'coordinates': 'property_details.property_part_d.coordinates',
      'longitude': 'property_details.property_part_d.coordinates.longitude',
      'latitude': 'property_details.property_part_d.coordinates.latitude',
      
      // Land Area and Occupancy Group (in property_part_d)
      'land_area_and_occupancy': 'property_details.property_part_d.land_area_and_occupancy',
      'site_area': 'property_details.property_part_d.land_area_and_occupancy.site_area',
      'valuation_area': 'property_details.property_part_d.land_area_and_occupancy.valuation_area',
      'occupied_by': 'property_details.property_part_d.land_area_and_occupancy.occupied_by',
      
      // Site Characteristics - Part A (Locality & Features)
      'locality_surroundings': 'site_characteristics.site_part_a.locality_surroundings',
      'locality_classification': 'site_characteristics.site_part_a.locality_classification',
      'surrounding_area': 'site_characteristics.site_part_a.surrounding_area',
      'physical_characteristics': 'site_characteristics.site_part_a.physical_characteristics',
      'civic_amenities_feasibility': 'site_characteristics.site_part_a.civic_amenities_feasibility',
      'land_usage': 'site_characteristics.site_part_a.land_usage',
      'land_level_topography': 'site_characteristics.site_part_a.land_level_topography',
      'land_shape': 'site_characteristics.site_part_a.land_shape',
      'flooding_possibility': 'site_characteristics.site_part_a.flooding_possibility',
      'usage_type': 'site_characteristics.site_part_a.usage_type',
      'usage_restrictions': 'site_characteristics.site_part_a.usage_restrictions',
      'planning_approvals': 'site_characteristics.site_part_a.planning_approvals',
      'town_planning_approved': 'site_characteristics.site_part_a.town_planning_approved',
      
      // Site Characteristics - Part B (Access & Services)
      'road_access': 'site_characteristics.site_part_b.road_access',
      'corner_or_intermittent': 'site_characteristics.site_part_b.corner_or_intermittent',
      'road_facilities': 'site_characteristics.site_part_b.road_facilities',
      'road_type_present': 'site_characteristics.site_part_b.road_type_present',
      'road_width': 'site_characteristics.site_part_b.road_width',
      'landlocked_status': 'site_characteristics.site_part_b.landlocked_status',
      
      // Utility Services Group (in site_part_b)
      'utility_services_group': 'site_characteristics.site_part_b.utility_services_group',
      'water_potentiality': 'site_characteristics.site_part_b.utility_services_group.water_potentiality',
      'underground_sewerage': 'site_characteristics.site_part_b.utility_services_group.underground_sewerage',
      'power_supply_available': 'site_characteristics.site_part_b.utility_services_group.power_supply_available',
      
      'additional_information': 'site_characteristics.site_part_b.additional_information',
      'site_advantages': 'site_characteristics.site_part_b.site_advantages',
      'special_remarks': 'site_characteristics.site_part_b.special_remarks',
      
      // Valuation - Part A (Land Valuation)
      'plot_size': 'valuation.valuation_part_a.plot_size',
      'north_south_dimension': 'valuation.valuation_part_a.north_south_dimension',
      'east_west_dimension': 'valuation.valuation_part_a.east_west_dimension',
      'total_extent_plot': 'valuation.valuation_part_a.total_extent_plot',
      'market_rate': 'valuation.valuation_part_a.market_rate',
      'market_rate_min': 'valuation.valuation_part_a.market_rate_min',
      'market_rate_max': 'valuation.valuation_part_a.market_rate_max',
      'registrar_rate': 'valuation.valuation_part_a.registrar_rate',
      'valuation_rate': 'valuation.valuation_part_a.valuation_rate',
      'estimated_valuation': 'valuation.valuation_part_a.estimated_valuation',
      'estimated_land_value': 'valuation.valuation_part_a.estimated_land_value',
      
      // Valuation - Part B (Building Details)
      'building_constructed': 'valuation.valuation_part_b.building_constructed',
      
      // Building Basic Info Group (in valuation_part_b)
      'building_basic_info': 'valuation.valuation_part_b.building_basic_info',
      'building_type': 'valuation.valuation_part_b.building_basic_info.building_type',
      'construction_type': 'valuation.valuation_part_b.building_basic_info.construction_type',
      'construction_year': 'valuation.valuation_part_b.building_basic_info.construction_year',
      'number_of_floors': 'valuation.valuation_part_b.building_basic_info.number_of_floors',
      'floor_height': 'valuation.valuation_part_b.building_basic_info.floor_height',
      'plinth_area_floorwise': 'valuation.valuation_part_b.building_basic_info.plinth_area_floorwise',
      
      // Building Dimensions Group (in valuation_part_b)  
      'building_dimensions': 'valuation.valuation_part_b.building_dimensions',
      
      // Building Condition Group (in valuation_part_b)
      'building_condition': 'valuation.valuation_part_b.building_condition',
      'exterior_condition': 'valuation.valuation_part_b.building_condition.exterior_condition',
      'interior_condition': 'valuation.valuation_part_b.building_condition.interior_condition',
      'building_age_remarks': 'valuation.valuation_part_b.building_condition.building_age_remarks',
      
      // Approval Documents Group (in valuation_part_b)
      'approval_documents': 'valuation.valuation_part_b.approval_documents',
      'approved_map_date_validity': 'valuation.valuation_part_b.approval_documents.approved_map_date_validity',
      'approved_map_authority': 'valuation.valuation_part_b.approval_documents.approved_map_authority',
      'map_authenticity_verified': 'valuation.valuation_part_b.approval_documents.map_authenticity_verified',
      'valuer_comments_authenticity': 'valuation.valuation_part_b.approval_documents.valuer_comments_authenticity',
      
      'no_building_remarks': 'valuation.valuation_part_b.no_building_remarks',
      'land_only_confirmation': 'valuation.valuation_part_b.land_only_confirmation',
      'land_valuation_basis': 'valuation.valuation_part_b.land_valuation_basis',
      
      // Construction Specifications - Part A (Building Specifications)
      'building_specifications_table': 'construction_specifications.construction_part_a.building_specifications_table',
      'floor_wise_valuation_table': 'construction_specifications.construction_part_a.floor_wise_valuation_table',
      
      // Construction Specifications - Part B (Material Specifications)
      // Compound Wall Details Group
      'compound_wall_details': 'construction_specifications.construction_part_b.compound_wall_details',
      'compound_wall': 'construction_specifications.construction_part_b.compound_wall_details.compound_wall',
      'height': 'construction_specifications.construction_part_b.compound_wall_details.height',
      'length': 'construction_specifications.construction_part_b.compound_wall_details.length',
      
      // Electrical Installation Group
      'electrical_installation': 'construction_specifications.construction_part_b.electrical_installation',
      'wiring_type': 'construction_specifications.construction_part_b.electrical_installation.wiring_type',
      'fittings_class': 'construction_specifications.construction_part_b.electrical_installation.fittings_class',
      'fan_points': 'construction_specifications.construction_part_b.electrical_installation.fan_points',
      'spare_plug_points': 'construction_specifications.construction_part_b.electrical_installation.spare_plug_points',
      
      // Plumbing Installation Group
      'plumbing_installation': 'construction_specifications.construction_part_b.plumbing_installation',
      'water_closets': 'construction_specifications.construction_part_b.plumbing_installation.water_closets',
      'wash_basins': 'construction_specifications.construction_part_b.plumbing_installation.wash_basins',
      'urinals': 'construction_specifications.construction_part_b.plumbing_installation.urinals',
      'bath_tubs': 'construction_specifications.construction_part_b.plumbing_installation.bath_tubs',
      'water_meter_taps': 'construction_specifications.construction_part_b.plumbing_installation.water_meter_taps',
      'other_fixtures_sink': 'construction_specifications.construction_part_b.plumbing_installation.other_fixtures_sink',
      
      // Extra Items (individual fields)
      'extra_items': 'construction_specifications.construction_part_b.extra_items',
      'portico': 'construction_specifications.construction_part_b.portico',
      'ornamental_front_door': 'construction_specifications.construction_part_b.ornamental_front_door',
      'sitout_verandah_grills': 'construction_specifications.construction_part_b.sitout_verandah_grills',
      'overhead_water_tank': 'construction_specifications.construction_part_b.overhead_water_tank',
      'extra_steel_gates': 'construction_specifications.construction_part_b.extra_steel_gates',
      'wardrobes': 'construction_specifications.construction_part_b.wardrobes',
      'glazed_tiles': 'construction_specifications.construction_part_b.glazed_tiles',
      'extra_sinks_bathtubs': 'construction_specifications.construction_part_b.extra_sinks_bathtubs',
      'marble_ceramic_flooring': 'construction_specifications.construction_part_b.marble_ceramic_flooring',
      'interior_decorations': 'construction_specifications.construction_part_b.interior_decorations',
      'architectural_elevation': 'construction_specifications.construction_part_b.architectural_elevation',
      'paneling_works': 'construction_specifications.construction_part_b.paneling_works',
      'aluminum_works': 'construction_specifications.construction_part_b.aluminum_works',
      'aluminum_handrails': 'construction_specifications.construction_part_b.aluminum_handrails',
      'false_ceiling': 'construction_specifications.construction_part_b.false_ceiling',
      
      // Amenities (individual fields)
      'amenities': 'construction_specifications.construction_part_b.amenities',
      'separate_toilet': 'construction_specifications.construction_part_b.separate_toilet',
      'separate_lumber_room': 'construction_specifications.construction_part_b.separate_lumber_room',
      'separate_water_tank_sump': 'construction_specifications.construction_part_b.separate_water_tank_sump',
      
      // Miscellaneous (individual fields)
      'miscellaneous': 'construction_specifications.construction_part_b.miscellaneous',
      'trees_gardening': 'construction_specifications.construction_part_b.trees_gardening',
      
      // Services (individual fields)
      'services': 'construction_specifications.construction_part_b.services',
      'water_supply_arrangements': 'construction_specifications.construction_part_b.water_supply_arrangements',
      'drainage_arrangements': 'construction_specifications.construction_part_b.drainage_arrangements',
      'cb_deposits_fittings': 'construction_specifications.construction_part_b.cb_deposits_fittings',
      'pavement': 'construction_specifications.construction_part_b.pavement',
      
      // Detailed Valuation (direct fields, no sections)
      'land_total': 'detailed_valuation.land_total',
      'building_total': 'detailed_valuation.building_total',
      'extra_items_total': 'detailed_valuation.extra_items_total',
      'amenities_total': 'detailed_valuation.amenities_total',
      'miscellaneous_total': 'detailed_valuation.miscellaneous_total',
      'services_total': 'detailed_valuation.services_total',
      'grand_total': 'detailed_valuation.grand_total',
      'report_reference_number': 'detailed_valuation.report_reference_number',
      'valuation_date': 'detailed_valuation.valuation_date',
      'inspection_date': 'detailed_valuation.inspection_date',
      'applicant_name': 'detailed_valuation.applicant_name',
      'valuation_purpose': 'detailed_valuation.valuation_purpose',
      'bank_branch': 'detailed_valuation.bank_branch'
    };

    // Organize the data according to mappings
    for (const [fieldId, value] of Object.entries(flatData)) {
      const targetPath = fieldMappings[fieldId];
      
      if (targetPath) {
        // Set the value at the mapped location
        this.setNestedValue(organizedData, targetPath, value);
        console.log(`📍 Mapped ${fieldId} -> ${targetPath}:`, value);
      } else {
        // Log unmapped fields but don't add them anywhere
        console.warn(`⚠️ Unmapped field ${fieldId}, skipping:`, value);
      }
    }

    console.log('✅ Final organized data structure:', organizedData);
    return organizedData;
  }

  /**
   * Helper method to set nested object values using dot notation
   */
  private setNestedValue(obj: any, path: string, value: any): void {
    const parts = path.split('.');
    let current = obj;
    
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (!current[part]) {
        current[part] = {};
      }
      current = current[part];
    }
    
    current[parts[parts.length - 1]] = value;
  }
}
