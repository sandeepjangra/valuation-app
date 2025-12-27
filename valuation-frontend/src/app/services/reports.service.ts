import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, of, timer } from 'rxjs';
import { map, catchError, timeout, timeoutWith } from 'rxjs/operators';
import { AuthService } from './auth.service';

export interface Report {
  _id: string;
  report_id: string;
  reference_number: string;
  property_address: string;
  bank_code: string;
  bank_branch?: string;  // NEW: Bank branch ID
  bank_branch_name?: string;  // NEW: Bank branch display name
  template_id: string;
  property_type: string;
  status: 'draft' | 'in_progress' | 'submitted' | 'completed';
  created_by_email: string;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  version: number;
  report_data?: any;
}

export interface ReportFilters {
  status?: string;
  bank_code?: string;
  template_id?: string;
  created_by?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  limit?: number;
}

export interface ReportListResponse {
  success: boolean;
  data: Report[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters: ReportFilters;
}

@Injectable({
  providedIn: 'root'
})
export class ReportsService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(
    private http: HttpClient,
    private authService: AuthService
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
    const url = `${this.baseUrl}/reports`;
    
    // Build query parameters
    let params = new HttpParams();
    
    // Add organization context - CRITICAL FIX
    const orgShortName = this.authService.getOrgShortName();
    if (orgShortName) {
      params = params.set('organization_id', orgShortName);
      console.log('🏢 Adding organization context to request:', orgShortName);
    } else {
      console.warn('⚠️ No organization context available - API may return wrong data');
    }
    
    if (filters.status) params = params.set('status', filters.status);
    if (filters.bank_code) params = params.set('bank_code', filters.bank_code);
    if (filters.template_id) params = params.set('template_id', filters.template_id);
    if (filters.created_by) params = params.set('created_by', filters.created_by);
    if (filters.start_date) params = params.set('start_date', filters.start_date);
    if (filters.end_date) params = params.set('end_date', filters.end_date);
    if (filters.page) params = params.set('page', filters.page.toString());
    if (filters.limit) params = params.set('limit', filters.limit.toString());
    
    console.log('📡 Making HTTP request to:', url);
    console.log('🎛️ Request params:', params.toString());
    
    const errorResponse: ReportListResponse = {
      success: false,
      data: [],
      pagination: {
        total: 0,
        page: 1,
        limit: 20,
        total_pages: 0,
        has_next: false,
        has_prev: false
      },
      filters: {}
    };
    
    return this.http.get<ReportListResponse>(url, { headers, params })
      .pipe(
        timeout(10000), // 10 second timeout
        catchError(error => {
          console.error('❌ Error fetching reports:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
          });
          
          if (error.name === 'TimeoutError') {
            console.warn('⏰ getReports request timed out after 10 seconds');
          }
          
          return of(errorResponse);
        })
      );
  }

  /**
   * Get a specific report by ID
   */
  getReportById(reportId: string): Observable<Report | null> {
    console.log('🔄 ReportsService.getReportById called for:', reportId);
    const headers = this.getHeaders();
    const url = `${this.baseUrl}/reports/${reportId}`;
    
    // Build query parameters for organization context
    let params = new HttpParams();
    const orgShortName = this.authService.getOrgShortName();
    if (orgShortName) {
      params = params.set('organization_id', orgShortName);
      console.log('🏢 Adding organization context to getReportById:', orgShortName);
    }
    
    return this.http.get<any>(url, { headers, params })
      .pipe(
        timeout(10000), // 10 second timeout
        map(response => response.success ? response.data : null),
        catchError(error => {
          console.error('❌ Error fetching report:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
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
    
    // Build query parameters for organization context
    let params = new HttpParams();
    const orgShortName = this.authService.getOrgShortName();
    if (orgShortName) {
      params = params.set('organization_id', orgShortName);
      console.log('🏢 Adding organization context to deleteReport:', orgShortName);
    }
    
    return this.http.delete<any>(`${this.baseUrl}/reports/${reportId}`, { headers, params })
      .pipe(
        map(response => response.success),
        catchError(error => {
          console.error('❌ Error deleting report:', error);
          return of(false);
        })
      );
  }

  /**
   * Get available banks for filtering
   */
  getBanks(): Observable<any[]> {
    const headers = this.getHeaders();
    return this.http.get<any>(`${this.baseUrl}/dashboard/banks`, { headers })
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
}