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
    const allFields: (TemplateField | BankSpecificField)[] = [...response.commonFields];
    
    // Extract all fields from tabs and sections, including sub-fields from group fields
    bankSpecificTabs.forEach(tab => {
      // Add tab-level fields
      tab.fields.forEach(field => {
        allFields.push(field);
        // If it's a group field, also add its sub-fields
        if (field.fieldType === 'group' && field.subFields) {
          allFields.push(...field.subFields);
        }
      });
      
      // Add section-level fields
      if (tab.sections) {
        tab.sections.forEach(section => {
          section.fields.forEach(field => {
            allFields.push(field);
            // If it's a group field, also add its sub-fields
            if (field.fieldType === 'group' && field.subFields) {
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
