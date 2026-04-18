import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { map, catchError, timeout, tap } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { OrganizationContextService } from './organization-context.service';

export interface Report {
  id?: string;
  reportId?: string;
  referenceNumber?: string;
  organizationId?: string;
  orgShortName?: string;
  bankCode?: string;
  templateId?: string;
  propertyType?: string;
  propertyAddress?: string;
  applicantName?: string;
  status?: 'draft' | 'in_progress' | 'under_review' | 'approved' | 'rejected' | 'submitted' | 'completed';
  createdBy?: string;
  createdByEmail?: string;
  assignedTo?: string;
  reportData?: any;
  formData?: any;
  workflow?: any;
  createdAt?: string;
  updatedAt?: string;
  
  // Legacy fields for compatibility
  _id?: string;
  report_id?: string;
  reference_number?: string;
  property_address?: string;
  applicant_name?: string;
  bank_branch?: string;
  bank_branch_name?: string;
  template_id?: string;
  property_type?: string;
  org_short_name?: string;
  created_by_email?: string;
  created_at?: string;
  updated_at?: string;
  submitted_at?: string;
  version?: number;
  report_data?: any;
  form_data?: any;  // Legacy snake_case field for backward compatibility
}

export interface ReportFilters {
  status?: string;
  bankCode?: string;
  templateId?: string;
  createdBy?: string;
  assignedTo?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
  
  // Legacy field names for compatibility
  bank_code?: string;
  template_id?: string;
  created_by?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
}

export interface ReportListResponse {
  success: boolean;
  message?: string;
  data?: {
    reports: Report[];
    pagination: {
      page: number;
      pageSize: number;
      totalCount: number;
      totalPages: number;
      hasNext: boolean;
      hasPrev: boolean;
    };
  };
  errors?: any;
  
  // Legacy format for compatibility
  pagination?: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters?: ReportFilters;
}

@Injectable({
  providedIn: 'root'
})
export class ReportsService {

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private orgContext: OrganizationContextService
  ) { }

  /**
   * Get HTTP headers with authorization token
   */
  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Get all reports with filtering and pagination
   */
  getReports(filters: ReportFilters = {}): Observable<ReportListResponse> {
    console.log('🔄 ReportsService.getReports called with filters:', filters);
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl('reports');
    
    if (!url) {
      return of(this.getErrorResponse());
    }
    
    // Build query parameters
    let params = new HttpParams();
    if (filters.status) params = params.set('status', filters.status);
    if (filters.bankCode || filters.bank_code) params = params.set('bankCode', filters.bankCode || filters.bank_code!);
    if (filters.page) params = params.set('page', filters.page.toString());
    if (filters.pageSize || filters.limit) params = params.set('pageSize', (filters.pageSize || filters.limit || 20).toString());
    
    console.log('📡 Making HTTP request to:', url);
    console.log('🎛️ Request params:', params.toString());
    
    return this.http.get<ReportListResponse>(url, { headers, params })
      .pipe(
        timeout(10000),
        catchError(error => {
          console.error('❌ Error fetching reports:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
          });
          return of(this.getErrorResponse());
        })
      );
  }

  /**
   * Helper to create error response
   */
  private getErrorResponse(): ReportListResponse {
    return {
      success: false,
      data: {
        reports: [],
        pagination: {
          page: 1,
          pageSize: 20,
          totalCount: 0,
          totalPages: 0,
          hasNext: false,
          hasPrev: false
        }
      }
    };
  }

  /**
   * Get a specific report by ID
   */
  getReportById(reportId: string): Observable<Report | null> {
    console.log('🔄 ReportsService.getReportById called for:', reportId);
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl(`reports/${reportId}`);
    
    if (!url) {
      return of(null);
    }
    
    return this.http.get<any>(url, { headers })
      .pipe(
        timeout(10000),
        map(response => response.success ? response.data : null),
        catchError(error => {
          console.error('❌ Error fetching report:', {
            status: error.status,
            message: error.message,
            url: url
          });
          return of(null);
        })
      );
  }

  /**
   * Delete a report
   */
  deleteReport(reportId: string): Observable<boolean> {
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl(`reports/${reportId}`);
    
    if (!url) {
      return of(false);
    }
    
    return this.http.delete<any>(url, { headers })
      .pipe(
        map(response => response.success),
        catchError(error => {
          console.error('❌ Error deleting report:', error);
          return of(false);
        })
      );
  }

  /**
   * Approve a submitted report (Manager only)
   */
  approveReport(reportId: string): Observable<any> {
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl(`reports/${reportId}/approve`);
    const user = this.authService.currentUser();
    
    if (!url) {
      return throwError(() => new Error('Organization context not available'));
    }
    
    const body = {
      approvedBy: user?.email || ''
    };
    
    return this.http.post<any>(url, body, { headers })
      .pipe(
        tap(response => console.log('✅ Report approved:', response)),
        catchError(error => {
          console.error('❌ Error approving report:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Reject a submitted report (Manager only)
   */
  rejectReport(reportId: string, rejectionReason: string): Observable<any> {
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl(`reports/${reportId}/reject`);
    const user = this.authService.currentUser();
    
    if (!url) {
      return throwError(() => new Error('Organization context not available'));
    }
    
    const body = {
      rejectedBy: user?.email || '',
      rejectionReason: rejectionReason
    };
    
    return this.http.post<any>(url, body, { headers })
      .pipe(
        tap(response => console.log('✅ Report rejected:', response)),
        catchError(error => {
          console.error('❌ Error rejecting report:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Get available banks for filtering
   */
  getBanks(): Observable<any[]> {
    const headers = this.getHeaders();
    const url = this.orgContext.getSharedApiUrl('banks');
    
    return this.http.get<any>(url, { headers })
      .pipe(
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching banks:', error);
          return of([]);
        })
      );
  }

  /**
   * Format status for display
   */
  getStatusDisplayName(status: string): string {
    switch (status) {
      case 'draft': return 'Draft';
      case 'in_progress': return 'In Progress';
      case 'submitted': return 'Submitted';
      case 'completed': return 'Completed';
      default: return status;
    }
  }

  /**
   * Get status badge class for styling
   */
  getStatusClass(status: string): string {
    switch (status) {
      case 'draft': return 'status-draft';
      case 'in_progress': return 'status-progress';
      case 'submitted': return 'status-submitted';
      case 'completed': return 'status-completed';
      default: return 'status-default';
    }
  }

  /**
   * Save a new draft report (NO VALIDATION)
   * Accepts any data - incomplete, "NA" values, empty fields, etc.
   */
  saveDraft(reportData: any): Observable<any> {
    console.log('💾 ReportsService.saveDraft called with:', reportData);
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl('reports/draft');
    
    if (!url) {
      console.error('❌ No organization context available');
      return throwError(() => new Error('Organization context not available'));
    }

    // Get current user info
    const currentUser = this.authService.currentUserValue;
    
    // Prepare draft payload
    const draftPayload = {
      bankCode: reportData.bankCode || reportData.bank_code || '',
      propertyType: reportData.propertyType || reportData.property_type || '',
      applicantName: reportData.applicantName || reportData.applicant_name || '',
      templateId: reportData.templateId || reportData.template_id || '',
      createdBy: currentUser?.user_id || '',
      createdByEmail: currentUser?.email || '',
      reportData: reportData.reportData || reportData.report_data || reportData,
      formData: reportData.formData || reportData.form_data || null
    };

    console.log('📤 Sending draft to backend:', url);
    
    return this.http.post<any>(url, draftPayload, { headers })
      .pipe(
        timeout(15000),
        catchError(error => {
          console.error('❌ Error saving draft:', {
            status: error.status,
            message: error.message,
            error: error.error
          });
          return throwError(() => error);
        })
      );
  }

  /**
   * Update an existing draft report (NO VALIDATION)
   */
  updateDraft(reportId: string, reportData: any): Observable<any> {
    console.log('🔄 ReportsService.updateDraft called for:', reportId);
    console.log('🔄 Update data received:', reportData);
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl(`reports/draft/${reportId}`);
    
    if (!url) {
      console.error('❌ No organization context available');
      return throwError(() => new Error('Organization context not available'));
    }

    // Prepare update payload - only include fields that have values
    const updatePayload: any = {
      reportData: reportData.reportData || reportData.report_data || reportData,
      formData: reportData.formData || reportData.form_data || null
    };
    
    // Only include optional fields if they have non-empty values
    const bankCode = reportData.bankCode || reportData.bank_code;
    if (bankCode) {
      updatePayload.bankCode = bankCode;
    }
    
    const propertyType = reportData.propertyType || reportData.property_type;
    if (propertyType) {
      updatePayload.propertyType = propertyType;
    }
    
    const applicantName = reportData.applicantName || reportData.applicant_name;
    if (applicantName) {
      updatePayload.applicantName = applicantName;
    }
    
    const templateId = reportData.templateId || reportData.template_id;
    if (templateId) {
      updatePayload.templateId = templateId;
    }

    console.log('📤 Updating draft:', url);
    console.log('📤 Payload:', updatePayload);
    
    return this.http.put<any>(url, updatePayload, { headers })
      .pipe(
        timeout(15000),
        catchError(error => {
          console.error('❌ Error updating draft:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Submit a report for review
   * Changes status from 'draft' to 'submitted'
   */
  submitReport(reportId: string, reportData: any): Observable<any> {
    console.log('📤 ReportsService.submitReport called for:', reportId);
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl(`reports/${reportId}/submit`);
    
    if (!url) {
      console.error('❌ No organization context available');
      return throwError(() => new Error('Organization context not available'));
    }

    // Get current user info
    const currentUser = this.authService.currentUserValue;
    
    // Prepare submit payload with updated data and status change
    const submitPayload = {
      status: 'submitted',
      reportData: reportData.reportData || reportData.report_data || reportData,
      formData: reportData.formData || reportData.form_data || null,
      submittedBy: currentUser?.user_id || '',
      submittedByEmail: currentUser?.email || '',
      submittedAt: new Date().toISOString()
    };

    console.log('📤 Submitting report to backend:', url);
    
    return this.http.post<any>(url, submitPayload, { headers })
      .pipe(
        timeout(15000),
        tap(response => {
          console.log('✅ Report submitted successfully:', response);
        }),
        catchError(error => {
          console.error('❌ Error submitting report:', {
            status: error.status,
            message: error.message,
            error: error.error
          });
          return throwError(() => error);
        })
      );
  }

  /**
   * Get all draft reports for current user
   */
  getDrafts(page: number = 1, pageSize: number = 50): Observable<any> {
    console.log('📋 ReportsService.getDrafts called');
    const headers = this.getHeaders();
    const url = this.orgContext.getOrgApiUrl('reports/drafts');
    
    if (!url) {
      return of({ success: false, data: { reports: [], total_count: 0 } });
    }

    const currentUser = this.authService.currentUserValue;
    let params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    
    if (currentUser?.email) {
      params = params.set('userEmail', currentUser.email);
    }

    return this.http.get<any>(url, { headers, params })
      .pipe(
        timeout(10000),
        tap(response => {
          console.log('📋 getDrafts API Response:', response);
          if (response?.data?.reports && response.data.reports.length > 0) {
            console.log('📋 First report sample:', response.data.reports[0]);
            console.log('📋 First report applicant_name:', response.data.reports[0].applicant_name);
            console.log('📋 First report report_data.applicant_name:', response.data.reports[0].report_data?.applicant_name);
          }
        }),
        catchError(error => {
          console.error('❌ Error fetching drafts:', error);
          return of({ success: false, data: { reports: [], total_count: 0 } });
        })
      );
  }
}
