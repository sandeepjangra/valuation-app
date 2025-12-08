/**
 * Custom Template Service
 * Handles all custom template operations including CRUD, field structure fetching, and auto-fill logic
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { AuthService } from './auth.service';
import {
  CustomTemplate,
  CustomTemplateListItem,
  CreateCustomTemplateRequest,
  UpdateCustomTemplateRequest,
  CloneCustomTemplateRequest,
  CustomTemplateFieldsResponse,
  CustomTemplatesListResponse,
  CustomTemplateResponse,
  CustomTemplateCreateResponse
} from '../models/custom-template.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CustomTemplateService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly API_BASE_URL = environment.apiUrl || 'http://localhost:8000/api';

  private getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Get field structure for a specific bank and property type
   * Used when creating/editing custom templates to show all available fields
   */
  getTemplateFields(bankCode: string, propertyType: 'land' | 'apartment'): Observable<CustomTemplateFieldsResponse> {
    const params = new HttpParams()
      .set('bank_code', bankCode)
      .set('property_type', propertyType);

    console.log(`🌐 CustomTemplateService: Fetching fields for ${bankCode}/${propertyType}`);

    return this.http.get<CustomTemplateFieldsResponse>(
      `${this.API_BASE_URL}/custom-templates/fields`,
      { params, headers: this.getAuthHeaders() }
    ).pipe(
      tap(response => {
        console.log('✅ Template fields fetched:', {
          commonFields: response.commonFields?.length || 0,
          bankSpecificTabs: response.bankSpecificTabs?.length || 0
        });
      }),
      catchError(error => {
        console.error('❌ Failed to fetch template fields:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * List all custom templates with optional filtering
   */
  getTemplates(bankCode?: string, propertyType?: 'land' | 'apartment'): Observable<CustomTemplatesListResponse> {
    let params = new HttpParams();
    
    if (bankCode) {
      params = params.set('bankCode', bankCode);
    }
    if (propertyType) {
      params = params.set('propertyType', propertyType);
    }

    console.log('🌐 CustomTemplateService: Listing templates', { bankCode, propertyType });

    return this.http.get<CustomTemplatesListResponse>(
      `${this.API_BASE_URL}/custom-templates`,
      { params, headers: this.getAuthHeaders() }
    ).pipe(
      tap(response => {
        console.log('✅ Templates fetched:', {
          total: response.data?.length || 0,
          data: response.data
        });
      }),
      catchError(error => {
        console.error('❌ Failed to fetch templates:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get a specific custom template by ID
   * Returns full template including all field values
   */
  getTemplate(templateId: string): Observable<CustomTemplate> {
    console.log(`🌐 CustomTemplateService: Fetching template ${templateId}`);

    return this.http.get<CustomTemplateResponse>(
      `${this.API_BASE_URL}/custom-templates/${templateId}`,
      { headers: this.getAuthHeaders() }
    ).pipe(
      map(response => response.data),
      tap(template => {
        console.log('✅ Template fetched:', template.templateName);
      }),
      catchError(error => {
        console.error('❌ Failed to fetch template:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Create a new custom template
   * Only Manager/Admin can create templates
   * Max 3 templates per bankCode+propertyType combination
   */
  createTemplate(request: CreateCustomTemplateRequest): Observable<CustomTemplate> {
    console.log('🌐 CustomTemplateService: Creating template', request.templateName);

    const endpoint = `${this.API_BASE_URL}/custom-templates`;
    const transformedRequest = {
      templateName: request.templateName,
      description: request.description,
      bankCode: request.bankCode,
      propertyType: request.propertyType,
      fieldValues: request.fieldValues
    };

    return this.http.post<CustomTemplateCreateResponse>(
      endpoint,
      transformedRequest,
      { headers: this.getAuthHeaders() }
    ).pipe(
      map(response => response.data.template || response.data),
      tap(template => {
        console.log('✅ Template created:', template._id || template.templateName);
      }),
      catchError(error => {
        console.error('❌ Failed to create template:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get organization context from current URL or auth service
   */
  private getOrganizationContext(): any {
    // First try to get from current URL path
    const currentPath = window.location.pathname;
    const orgMatch = currentPath.match(/\/org\/([^/]+)/);
    if (orgMatch) {
      return { orgShortName: orgMatch[1] };
    }

    // Fallback to localStorage
    try {
      const authData = localStorage.getItem('auth_data');
      if (authData) {
        const parsed = JSON.parse(authData);
        return {
          orgShortName: parsed.user?.org_short_name || parsed.organization?.org_short_name
        };
      }
    } catch (e) {
      console.error('Error getting organization context:', e);
    }
    return null;
  }

  /**
   * Update an existing custom template
   * Only Manager/Admin can update templates
   */
  updateTemplate(templateId: string, request: UpdateCustomTemplateRequest): Observable<CustomTemplate> {
    console.log(`🌐 CustomTemplateService: Updating template ${templateId}`);

    return this.http.put<CustomTemplateResponse>(
      `${this.API_BASE_URL}/custom-templates/${templateId}`,
      request,
      { headers: this.getAuthHeaders() }
    ).pipe(
      map(response => response.data),
      tap(template => {
        console.log('✅ Template updated:', template.templateName);
      }),
      catchError(error => {
        console.error('❌ Failed to update template:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Delete a custom template (soft delete)
   * Only Manager/Admin can delete templates
   */
  deleteTemplate(templateId: string): Observable<void> {
    console.log(`🌐 CustomTemplateService: Deleting template ${templateId}`);

    return this.http.delete<CustomTemplateResponse>(
      `${this.API_BASE_URL}/custom-templates/${templateId}`,
      { headers: this.getAuthHeaders() }
    ).pipe(
      map(() => void 0),
      tap(() => {
        console.log('✅ Template deleted');
      }),
      catchError(error => {
        console.error('❌ Failed to delete template:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Clone an existing custom template
   * Creates a copy with a new name
   * Only Manager/Admin can clone templates
   */
  cloneTemplate(templateId: string, request: CloneCustomTemplateRequest): Observable<CustomTemplate> {
    console.log(`🌐 CustomTemplateService: Cloning template ${templateId}`);

    return this.http.post<CustomTemplateCreateResponse>(
      `${this.API_BASE_URL}/custom-templates/${templateId}/clone`,
      request,
      { headers: this.getAuthHeaders() }
    ).pipe(
      map(response => response.data.template),
      tap(template => {
        console.log('✅ Template cloned:', template._id);
      }),
      catchError(error => {
        console.error('❌ Failed to clone template:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Apply template values to form data with specified strategy
   * @param formData Current form values (can be empty or partially filled)
   * @param templateValues Values from custom template
   * @param strategy 'fill_empty' | 'replace_all'
   * @returns Merged form data
   */
  applyTemplateToFormData(
    formData: Record<string, any>,
    templateValues: Record<string, any>,
    strategy: 'fill_empty' | 'replace_all'
  ): Record<string, any> {
    console.log('🔄 CustomTemplateService: Applying template with strategy:', strategy);

    const result = { ...formData };
    let updatedCount = 0;

    if (strategy === 'replace_all') {
      // Replace all values from template
      Object.keys(templateValues).forEach(key => {
        if (templateValues[key] !== null && templateValues[key] !== undefined) {
          result[key] = templateValues[key];
          updatedCount++;
        }
      });
    } else if (strategy === 'fill_empty') {
      // Only fill fields that are empty/null/undefined
      Object.keys(templateValues).forEach(key => {
        const currentValue = formData[key];
        const isEmpty = currentValue === null || 
                       currentValue === undefined || 
                       currentValue === '' ||
                       (Array.isArray(currentValue) && currentValue.length === 0);
        
        if (isEmpty && templateValues[key] !== null && templateValues[key] !== undefined) {
          result[key] = templateValues[key];
          updatedCount++;
        }
      });
    }

    console.log(`✅ Template applied: ${updatedCount} fields updated`);
    return result;
  }

  /**
   * Check if user can create more templates for given bank+property type
   * Returns true if count < 3
   */
  canCreateTemplate(bankCode: string, propertyType: 'land' | 'apartment'): Observable<boolean> {
    return this.getTemplates(bankCode, propertyType).pipe(
      map(response => response.count.filtered < 3),
      catchError(() => {
        // If error, assume can't create
        return throwError(() => new Error('Failed to check template count'));
      })
    );
  }

  /**
   * Get remaining template slots for a bank+property type combination
   */
  getRemainingSlots(bankCode: string, propertyType: 'land' | 'apartment'): Observable<number> {
    return this.getTemplates(bankCode, propertyType).pipe(
      map(response => Math.max(0, 3 - response.count.filtered)),
      catchError(() => {
        return throwError(() => new Error('Failed to get remaining slots'));
      })
    );
  }

  /**
   * Validate template name is unique for bank+property type
   * Used for client-side validation before creating/updating
   */
  isTemplateNameUnique(
    templateName: string, 
    bankCode: string, 
    propertyType: 'land' | 'apartment',
    excludeTemplateId?: string
  ): Observable<boolean> {
    return this.getTemplates(bankCode, propertyType).pipe(
      map(response => {
        return !response.data.some(template => 
          template.templateName.toLowerCase() === templateName.toLowerCase() &&
          template._id !== excludeTemplateId
        );
      }),
      catchError(() => {
        // If error, assume not unique (safer)
        return throwError(() => new Error('Failed to check template name uniqueness'));
      })
    );
  }
}
