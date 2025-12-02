import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import {
  TemplateSnapshot,
  TemplateVersion,
  TemplateVersionsResponse,
  ValuationReport,
  CreateReportRequest,
  UpdateReportRequest,
  ApiResponse,
  HealthResponse
} from '../models/template-versioning.models';

/**
 * Template Versioning API Service
 * Handles all communication with the Template-Versioned Reports API backend
 */
@Injectable({
  providedIn: 'root'
})
export class TemplateVersioningService {
  private readonly baseUrl = environment.templateVersioningApiUrl || 'http://localhost:8000';
  
  private readonly httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient) {}

  /**
   * Health check for the API server
   */
  getHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.baseUrl}/health`, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Get all available template versions
   */
  getTemplateVersions(): Observable<TemplateVersion[]> {
    return this.http.get<TemplateVersionsResponse>(`${this.baseUrl}/api/v1/templates/versions`, this.httpOptions)
      .pipe(
        map(response => response.templates),
        catchError(this.handleError)
      );
  }

  /**
   * Get template snapshot by ID
   */
  getTemplateSnapshot(snapshotId: string): Observable<TemplateSnapshot> {
    return this.http.get<TemplateSnapshot>(`${this.baseUrl}/api/v1/templates/snapshot/${snapshotId}`, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Create a new valuation report
   */
  createReport(request: CreateReportRequest): Observable<ValuationReport> {
    return this.http.post<ValuationReport>(`${this.baseUrl}/api/v1/reports`, request, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Get valuation report by ID
   */
  getReport(reportId: string): Observable<ValuationReport> {
    return this.http.get<ValuationReport>(`${this.baseUrl}/api/v1/reports/${reportId}`, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Update valuation report
   */
  updateReport(reportId: string, request: UpdateReportRequest): Observable<ValuationReport> {
    return this.http.put<ValuationReport>(`${this.baseUrl}/api/v1/reports/${reportId}`, request, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Submit report for review
   */
  submitReport(reportId: string, comments?: string): Observable<ValuationReport> {
    const request = { comments: comments || '' };
    return this.http.post<ValuationReport>(`${this.baseUrl}/api/v1/reports/${reportId}/submit`, request, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Get list of reports with optional filtering
   */
  getReports(params?: {
    bankCode?: string;
    propertyType?: string;
    status?: string;
    page?: number;
    limit?: number;
  }): Observable<ValuationReport[]> {
    let httpParams = new HttpParams();
    
    if (params) {
      Object.keys(params).forEach(key => {
        const value = (params as any)[key];
        if (value !== undefined && value !== null) {
          httpParams = httpParams.append(key, value.toString());
        }
      });
    }

    return this.http.get<ValuationReport[]>(`${this.baseUrl}/api/v1/reports`, {
      ...this.httpOptions,
      params: httpParams
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get template versions filtered by bank and property type
   */
  getTemplateVersionsFiltered(bankCode?: string, propertyType?: string): Observable<TemplateVersion[]> {
    let httpParams = new HttpParams();
    
    if (bankCode) {
      httpParams = httpParams.append('bankCode', bankCode);
    }
    if (propertyType) {
      httpParams = httpParams.append('propertyType', propertyType);
    }

    return this.http.get<TemplateVersionsResponse>(`${this.baseUrl}/api/v1/templates/versions`, {
      ...this.httpOptions,
      params: httpParams
    }).pipe(
      map(response => response.templates),
      catchError(this.handleError)
    );
  }

  /**
   * Get the latest template snapshot for a specific template ID
   */
  getLatestTemplateSnapshot(templateId: string): Observable<TemplateSnapshot> {
    return this.getTemplateVersions().pipe(
      map(versions => {
        const template = versions.find(v => v.templateId === templateId && v.isLatest);
        if (!template) {
          throw new Error(`Template ${templateId} not found or not latest`);
        }
        return template.templateId;
      }),
      switchMap((snapshotId: string) => this.getTemplateSnapshot(snapshotId)),
      catchError(this.handleError)
    );
  }

  /**
   * Calculate field values based on formulas
   */
  calculateFields(reportData: Record<string, any>, templateSnapshot: TemplateSnapshot): Record<string, number> {
    const calculations: Record<string, number> = {};
    
    // Extract all fields with calculation metadata
    const allFields = this.getAllFields(templateSnapshot.template.sections);
    
    allFields.forEach(field => {
      if (field.calculationMetadata?.isCalculatedField && field.formula) {
        try {
          const result = this.evaluateFormula(field.formula, reportData);
          calculations[field.fieldId] = result;
        } catch (error) {
          console.error(`Error calculating field ${field.fieldId}:`, error);
          calculations[field.fieldId] = 0;
        }
      }
    });
    
    return calculations;
  }

  /**
   * Extract all fields from template sections (including nested fields)
   */
  private getAllFields(sections: any[]): any[] {
    const fields: any[] = [];
    
    sections.forEach(section => {
      section.fields.forEach((field: any) => {
        fields.push(field);
        
        // Add subFields if they exist
        if (field.subFields && Array.isArray(field.subFields)) {
          fields.push(...field.subFields);
        }
      });
    });
    
    return fields;
  }

  /**
   * Evaluate formula with report data
   */
  private evaluateFormula(formula: string, data: Record<string, any>): number {
    try {
      // Replace field IDs with actual values
      let expression = formula;
      
      // Find all field references in the formula
      const fieldReferences = formula.match(/[a-zA-Z_][a-zA-Z0-9_]*/g) || [];
      
      fieldReferences.forEach(fieldId => {
        const value = data[fieldId] || 0;
        const numericValue = typeof value === 'number' ? value : parseFloat(value) || 0;
        expression = expression.replace(new RegExp(`\\b${fieldId}\\b`, 'g'), numericValue.toString());
      });
      
      // Safely evaluate the expression
      const result = Function('"use strict"; return (' + expression + ')')();
      return typeof result === 'number' ? result : 0;
    } catch (error) {
      console.error('Formula evaluation error:', error);
      return 0;
    }
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: any): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Server Error: ${error.status} - ${error.error?.message || error.message}`;
    }
    
    console.error('TemplateVersioningService Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}