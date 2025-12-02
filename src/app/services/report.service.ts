import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface ReportRequest {
  bank_code: string;
  template_id: string;
  template_name: string;
  property_type: string;
  form_data: any;
  status?: ReportStatus;
  metadata?: {
    created_by?: string;
    organization_id?: string;
    [key: string]: any;
  };
}

export interface ReportResponse {
  success: boolean;
  data?: {
    report_id: string;
    status: ReportStatus;
    created_at: string;
    updated_at: string;
  };
  message?: string;
  errors?: string[];
}

export interface SubmitReportResponse {
  success: boolean;
  data?: {
    report_id: string;
    status: ReportStatus;
    submitted_at: string;
    submitted_by: string;
  };
  message?: string;
  errors?: string[];
}

export type ReportStatus = 'draft' | 'completed' | 'submitted' | 'approved' | 'rejected';

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private readonly API_BASE_URL = environment.apiUrl || 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  /**
   * Save report as draft (no validation required)
   * Available for all roles: system_admin, manager, employee
   */
  saveDraft(reportData: ReportRequest): Observable<ReportResponse> {
    const draftData: ReportRequest = {
      ...reportData,
      status: 'draft'
    };

    console.log('💾 Saving report draft:', {
      bank_code: draftData.bank_code,
      template_id: draftData.template_id,
      status: draftData.status
    });

    return this.http.post<ReportResponse>(`${this.API_BASE_URL}/reports`, draftData)
      .pipe(
        tap(response => {
          if (response.success) {
            console.log('✅ Draft saved successfully:', response.data?.report_id);
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Save completed report (with validation)
   * Available for all roles: system_admin, manager, employee
   * Note: Employees can save but cannot submit
   */
  saveReport(reportData: ReportRequest): Observable<ReportResponse> {
    const completedData: ReportRequest = {
      ...reportData,
      status: 'completed'
    };

    console.log('💾 Saving completed report:', {
      bank_code: completedData.bank_code,
      template_id: completedData.template_id,
      status: completedData.status
    });

    return this.http.post<ReportResponse>(`${this.API_BASE_URL}/reports`, completedData)
      .pipe(
        tap(response => {
          if (response.success) {
            console.log('✅ Report saved successfully:', response.data?.report_id);
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Update existing report
   * Available for all roles: system_admin, manager, employee
   */
  updateReport(reportId: string, reportData: Partial<ReportRequest>): Observable<ReportResponse> {
    console.log('📝 Updating report:', reportId);

    return this.http.put<ReportResponse>(`${this.API_BASE_URL}/reports/${reportId}`, reportData)
      .pipe(
        tap(response => {
          if (response.success) {
            console.log('✅ Report updated successfully:', reportId);
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Submit report for approval/processing
   * Only available for: system_admin, manager
   * Employees cannot submit - they must save for manager review
   */
  submitReport(reportId: string, submitData?: any): Observable<SubmitReportResponse> {
    console.log('🚀 Submitting report for approval:', reportId);

    return this.http.post<SubmitReportResponse>(`${this.API_BASE_URL}/reports/${reportId}/submit`, submitData || {})
      .pipe(
        tap(response => {
          if (response.success) {
            console.log('✅ Report submitted successfully:', response.data?.report_id);
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Save and submit report in one operation (for managers/system_admin)
   * This combines save + submit for users who have submission permissions
   */
  saveAndSubmitReport(reportData: ReportRequest): Observable<SubmitReportResponse> {
    console.log('🚀 Saving and submitting report:', {
      bank_code: reportData.bank_code,
      template_id: reportData.template_id
    });

    const submitData: ReportRequest = {
      ...reportData,
      status: 'submitted'
    };

    return this.http.post<SubmitReportResponse>(`${this.API_BASE_URL}/reports`, submitData)
      .pipe(
        tap(response => {
          if (response.success) {
            console.log('✅ Report saved and submitted successfully:', response.data?.report_id);
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Get report by ID
   */
  getReport(reportId: string): Observable<ReportResponse> {
    return this.http.get<ReportResponse>(`${this.API_BASE_URL}/reports/${reportId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Delete report (only system_admin and manager)
   */
  deleteReport(reportId: string): Observable<ReportResponse> {
    console.log('🗑️ Deleting report:', reportId);

    return this.http.delete<ReportResponse>(`${this.API_BASE_URL}/reports/${reportId}`)
      .pipe(
        tap(response => {
          if (response.success) {
            console.log('✅ Report deleted successfully:', reportId);
          }
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.status === 0) {
        errorMessage = 'Unable to connect to server. Please check your connection.';
      } else if (error.error?.message) {
        errorMessage = error.error.message;
      } else if (error.error?.errors && Array.isArray(error.error.errors)) {
        errorMessage = error.error.errors.join(', ');
      } else {
        errorMessage = `Server Error ${error.status}: ${error.statusText}`;
      }
    }

    console.error('❌ Report Service Error:', {
      status: error.status,
      message: errorMessage,
      error: error.error
    });

    return throwError(() => new Error(errorMessage));
  }
}