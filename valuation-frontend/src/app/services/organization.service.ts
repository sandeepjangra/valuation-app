/**
 * Angular Organization Service
 * Handles organization management API calls with automatic JWT headers and error handling
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError, shareReplay } from 'rxjs/operators';
import {
  Organization,
  User,
  AuditLog,
  CreateUserRequest,
  UpdateUserRequest,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  ApiResponse,
  PaginatedResponse,
  ErrorResponse,
  OrganizationSettings
} from '../models/organization.model';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

export interface GetUsersParams {
  page?: number;
  limit?: number;
  role?: string;
  search?: string;
  is_active?: boolean;
}

export interface GetAuditLogsParams {
  page?: number;
  limit?: number;
  user_id?: string;
  action?: string;
  resource_type?: string;
  start_date?: Date;
  end_date?: Date;
}

export interface GetReportsParams {
  page?: number;
  limit?: number;
  created_by?: string;
  start_date?: Date;
  end_date?: Date;
  status?: string;
}

@Injectable({
  providedIn: 'root'
})
export class OrganizationService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);

  // API endpoints
  private readonly API_BASE = environment.apiUrl || 'http://localhost:8000/api';

  constructor() {}

  // Organization Management

  /**
   * Get current user's organization information
   */
  getCurrentOrganization(): Observable<Organization> {
    return this.http.get<ApiResponse<Organization>>(`${this.API_BASE}/organization`)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to get organization');
          }
          return response.data;
        }),
        catchError(this.handleError.bind(this)),
        shareReplay(1)
      );
  }

  /**
   * Get all organizations (system admin only)
   */
  getAllOrganizations(includeInactive = false, includeSystem = false): Observable<Organization[]> {
    const params = new HttpParams()
      .set('active_only', (!includeInactive).toString())
      .set('include_system', includeSystem.toString());
      
    return this.http.get<Organization[]>(`${this.API_BASE}/organizations/`, { params })
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Get organization by short name
   */
  getOrganizationByShortName(shortName: string): Observable<Organization> {
    return this.http.get<Organization>(`${this.API_BASE}/organizations/${shortName}`)
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Get organization by ID
   */
  getOrganizationById(id: string): Observable<Organization> {
    return this.http.get<Organization>(`${this.API_BASE}/organizations/${id}`)
      .pipe(
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Create a new organization (system admin only)
   */
  createOrganization(organizationData: CreateOrganizationRequest): Observable<string> {
    return this.http.post<ApiResponse<{organization_id: string}>>(`${this.API_BASE}/system/organizations`, organizationData)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to create organization');
          }
          return response.data.organization_id;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Update organization (system admin only)
   */
  updateOrganization(organizationId: string, updates: UpdateOrganizationRequest): Observable<boolean> {
    return this.http.put<ApiResponse>(`${this.API_BASE}/system/organizations/${organizationId}`, updates)
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Delete organization (system admin only)
   */
  deleteOrganization(organizationId: string): Observable<boolean> {
    return this.http.delete<ApiResponse>(`${this.API_BASE}/system/organizations/${organizationId}`)
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  // User Management

  /**
   * Get users in the organization
   */
  getOrganizationUsers(params: GetUsersParams = {}): Observable<PaginatedResponse<User>> {
    let httpParams = new HttpParams();
    
    if (params.page) httpParams = httpParams.set('page', params.page.toString());
    if (params.limit) httpParams = httpParams.set('limit', params.limit.toString());
    if (params.role) httpParams = httpParams.set('role', params.role);
    if (params.search) httpParams = httpParams.set('search', params.search);
    if (params.is_active !== undefined) httpParams = httpParams.set('is_active', params.is_active.toString());

    return this.http.get<PaginatedResponse<User>>(`${this.API_BASE}/users`, { params: httpParams })
      .pipe(
        map(response => {
          if (!response.success) {
            throw new Error(response.message || 'Failed to get users');
          }
          return response;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Get specific user details
   */
  getUser(userId: string): Observable<User> {
    return this.http.get<ApiResponse<User>>(`${this.API_BASE}/users/${userId}`)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to get user');
          }
          return response.data;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Create a new user in the organization
   */
  createUser(userData: CreateUserRequest): Observable<string> {
    return this.http.post<ApiResponse<{user_id: string}>>(`${this.API_BASE}/users`, userData)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to create user');
          }
          return response.data.user_id;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Update user information
   */
  updateUser(userId: string, updates: UpdateUserRequest): Observable<boolean> {
    return this.http.put<ApiResponse>(`${this.API_BASE}/users/${userId}`, updates)
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Delete user (deactivate)
   */
  deleteUser(userId: string): Observable<boolean> {
    return this.http.delete<ApiResponse>(`${this.API_BASE}/users/${userId}`)
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Activate/deactivate user
   */
  toggleUserStatus(userId: string, isActive: boolean): Observable<boolean> {
    return this.http.patch<ApiResponse>(`${this.API_BASE}/users/${userId}/status`, { is_active: isActive })
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  // Report Management

  /**
   * Get organization reports
   */
  getOrganizationReports(params: GetReportsParams = {}): Observable<PaginatedResponse<any>> {
    let httpParams = new HttpParams();
    
    if (params.page) httpParams = httpParams.set('page', params.page.toString());
    if (params.limit) httpParams = httpParams.set('limit', params.limit.toString());
    if (params.created_by) httpParams = httpParams.set('created_by', params.created_by);
    if (params.start_date) httpParams = httpParams.set('start_date', params.start_date.toISOString());
    if (params.end_date) httpParams = httpParams.set('end_date', params.end_date.toISOString());
    if (params.status) httpParams = httpParams.set('status', params.status);

    return this.http.get<PaginatedResponse<any>>(`${this.API_BASE}/reports`, { params: httpParams })
      .pipe(
        map(response => {
          if (!response.success) {
            throw new Error(response.message || 'Failed to get reports');
          }
          return response;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Get specific report
   */
  getReport(reportId: string): Observable<any> {
    return this.http.get<ApiResponse<any>>(`${this.API_BASE}/reports/${reportId}`)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to get report');
          }
          return response.data;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Create a new report
   */
  createReport(reportData: any): Observable<string> {
    return this.http.post<ApiResponse<{report_id: string}>>(`${this.API_BASE}/reports`, reportData)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to create report');
          }
          return response.data.report_id;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Update report
   */
  updateReport(reportId: string, updates: any): Observable<boolean> {
    return this.http.put<ApiResponse>(`${this.API_BASE}/reports/${reportId}`, updates)
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Delete report
   */
  deleteReport(reportId: string): Observable<boolean> {
    return this.http.delete<ApiResponse>(`${this.API_BASE}/reports/${reportId}`)
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  // Audit Log Management

  /**
   * Get audit logs for the organization
   */
  getAuditLogs(params: GetAuditLogsParams = {}): Observable<PaginatedResponse<AuditLog>> {
    let httpParams = new HttpParams();
    
    if (params.page) httpParams = httpParams.set('page', params.page.toString());
    if (params.limit) httpParams = httpParams.set('limit', params.limit.toString());
    if (params.user_id) httpParams = httpParams.set('user_id', params.user_id);
    if (params.action) httpParams = httpParams.set('action', params.action);
    if (params.resource_type) httpParams = httpParams.set('resource_type', params.resource_type);
    if (params.start_date) httpParams = httpParams.set('start_date', params.start_date.toISOString());
    if (params.end_date) httpParams = httpParams.set('end_date', params.end_date.toISOString());

    return this.http.get<PaginatedResponse<AuditLog>>(`${this.API_BASE}/audit-logs`, { params: httpParams })
      .pipe(
        map(response => {
          if (!response.success) {
            throw new Error(response.message || 'Failed to get audit logs');
          }
          return response;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  // Organization Settings

  /**
   * Get organization settings
   */
  getOrganizationSettings(): Observable<OrganizationSettings> {
    return this.http.get<ApiResponse<OrganizationSettings>>(`${this.API_BASE}/organization/settings`)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to get organization settings');
          }
          return response.data;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Update organization settings
   */
  updateOrganizationSettings(settings: Partial<OrganizationSettings>): Observable<boolean> {
    return this.http.put<ApiResponse>(`${this.API_BASE}/organization/settings`, settings)
      .pipe(
        map(response => response.success),
        catchError(this.handleError.bind(this))
      );
  }

  // Statistics and Dashboard Data

  /**
   * Get organization dashboard statistics
   */
  getDashboardStats(): Observable<any> {
    return this.http.get<ApiResponse<any>>(`${this.API_BASE}/organization/stats`)
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to get dashboard stats');
          }
          return response.data;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Get user activity summary
   */
  getUserActivitySummary(days: number = 30): Observable<any> {
    const params = new HttpParams().set('days', days.toString());
    
    return this.http.get<ApiResponse<any>>(`${this.API_BASE}/organization/user-activity`, { params })
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to get user activity');
          }
          return response.data;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  /**
   * Get report statistics
   */
  getReportStats(period: 'week' | 'month' | 'year' = 'month'): Observable<any> {
    const params = new HttpParams().set('period', period);
    
    return this.http.get<ApiResponse<any>>(`${this.API_BASE}/organization/report-stats`, { params })
      .pipe(
        map(response => {
          if (!response.success || !response.data) {
            throw new Error(response.message || 'Failed to get report statistics');
          }
          return response.data;
        }),
        catchError(this.handleError.bind(this))
      );
  }

  // Utility Methods

  /**
   * Check if current user can perform action
   */
  canPerformAction(resource: string, action: string): boolean {
    return this.authService.hasPermission(resource, action);
  }

  /**
   * Get current user's organization context
   */
  getOrganizationContext() {
    return this.authService.getOrganizationContext();
  }

  // Private helper methods

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      const errorResponse = error.error as ErrorResponse;
      
      if (errorResponse.error) {
        errorMessage = errorResponse.error;
      } else if (error.status === 401) {
        errorMessage = 'Unauthorized access';
        // Trigger logout for unauthorized requests
        this.authService.logout();
      } else if (error.status === 403) {
        errorMessage = 'Access denied';
      } else if (error.status === 404) {
        errorMessage = 'Resource not found';
      } else if (error.status >= 500) {
        errorMessage = 'Server error occurred';
      } else {
        errorMessage = `HTTP ${error.status}: ${error.message}`;
      }
    }
    
    console.error('❌ Organization service error:', {
      status: error.status,
      message: errorMessage,
      url: error.url
    });
    
    return throwError(() => new Error(errorMessage));
  }
}