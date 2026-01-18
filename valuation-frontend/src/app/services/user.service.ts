import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { OrganizationContextService } from './organization-context.service';

export interface User {
  id?: string;
  userId?: string;
  email: string;
  fullName: string;
  phone?: string;
  organizationId?: string;
  orgShortName?: string;
  organizationName?: string;
  role?: string;
  roles?: string[];
  status?: string;
  isActive?: boolean;
  isSystemAdmin?: boolean;
  department?: string;
  permissions?: UserPermissions;
  createdAt?: string;
  updatedAt?: string;
  lastLogin?: string;
}

export interface UserPermissions {
  canSubmitReports?: boolean;
  canManageUsers?: boolean;
  isManager?: boolean;
  isAdmin?: boolean;
}

export interface UserProfile {
  id?: string;
  userId?: string;
  email?: string;
  orgShortName?: string;
  lastLogin?: string;
  loginCount?: number;
  reportsCreated?: number;
  reportsSubmitted?: number;
  lastActivity?: string;
  preferences?: UserPreferences;
  activityLogs?: ActivityLog[];
  createdAt?: string;
  updatedAt?: string;
}

export interface UserPreferences {
  theme?: string;
  language?: string;
  notificationsEnabled?: boolean;
  defaultBank?: string;
  dashboardLayout?: string;
}

export interface ActivityLog {
  action?: string;
  resourceType?: string;
  resourceId?: string;
  details?: string;
  timestamp?: string;
  ipAddress?: string;
  userAgent?: string;
}

export interface CreateUserRequest {
  email: string;
  fullName: string;
  password: string;
  phone?: string;
  role?: string;
  roles?: string[];
  department?: string;
  permissions?: UserPermissions;
}

export interface UpdateUserRequest {
  fullName?: string;
  phone?: string;
  role?: string;
  roles?: string[];
  department?: string;
  permissions?: UserPermissions;
}

export interface ResetPasswordRequest {
  newPassword: string;
}

export interface UserListResponse {
  success: boolean;
  message?: string;
  data?: {
    users: User[];
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
}

export interface UserDetailsResponse {
  success: boolean;
  message?: string;
  data?: {
    user: User;
    profile: UserProfile;
  };
  errors?: any;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private orgContext: OrganizationContextService
  ) {}

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
   * Get all users in organization with pagination
   */
  getUsers(page: number = 1, pageSize: number = 50): Observable<UserListResponse> {
    const url = this.orgContext.getOrgApiUrl('users');
    
    if (!url) {
      console.error('❌ No organization context available');
      return of(this.getErrorResponse());
    }

    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());

    return this.http.get<UserListResponse>(url, { 
      headers: this.getHeaders(),
      params 
    }).pipe(
      tap(response => {
        console.log('✅ Users fetched:', response.data?.pagination.totalCount || 0);
      }),
      catchError(error => {
        console.error('❌ Error fetching users:', error);
        return of(this.getErrorResponse());
      })
    );
  }

  /**
   * Get specific user details with profile
   */
  getUserDetails(userId: string): Observable<UserDetailsResponse | null> {
    const url = this.orgContext.getOrgApiUrl(`users/${userId}`);
    
    if (!url) {
      return of(null);
    }

    return this.http.get<UserDetailsResponse>(url, { 
      headers: this.getHeaders() 
    }).pipe(
      tap(response => {
        console.log('✅ User details fetched:', response.data?.user.email);
      }),
      catchError(error => {
        console.error('❌ Error fetching user details:', error);
        return of(null);
      })
    );
  }

  /**
   * Create a new user (admin only)
   */
  createUser(request: CreateUserRequest): Observable<any> {
    const url = this.orgContext.getOrgApiUrl('users');
    
    if (!url) {
      return throwError(() => new Error('No organization context'));
    }

    return this.http.post<any>(url, request, { 
      headers: this.getHeaders() 
    }).pipe(
      tap(response => {
        console.log('✅ User created:', response.data?.user_id);
      }),
      catchError(error => {
        console.error('❌ Error creating user:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Update an existing user (admin only)
   */
  updateUser(userId: string, request: UpdateUserRequest): Observable<any> {
    const url = this.orgContext.getOrgApiUrl(`users/${userId}`);
    
    if (!url) {
      return throwError(() => new Error('No organization context'));
    }

    return this.http.put<any>(url, request, { 
      headers: this.getHeaders() 
    }).pipe(
      tap(() => {
        console.log('✅ User updated:', userId);
      }),
      catchError(error => {
        console.error('❌ Error updating user:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Deactivate a user (admin only)
   */
  deactivateUser(userId: string): Observable<boolean> {
    const url = this.orgContext.getOrgApiUrl(`users/${userId}`);
    
    if (!url) {
      return of(false);
    }

    return this.http.delete<any>(url, { 
      headers: this.getHeaders() 
    }).pipe(
      map(response => response.success),
      tap(() => {
        console.log('✅ User deactivated:', userId);
      }),
      catchError(error => {
        console.error('❌ Error deactivating user:', error);
        return of(false);
      })
    );
  }

  /**
   * Reset user password (admin only)
   */
  resetPassword(userId: string, newPassword: string): Observable<boolean> {
    const url = this.orgContext.getOrgApiUrl(`users/${userId}/reset-password`);
    
    if (!url) {
      return of(false);
    }

    const request: ResetPasswordRequest = { newPassword };

    return this.http.post<any>(url, request, { 
      headers: this.getHeaders() 
    }).pipe(
      map(response => response.success),
      tap(() => {
        console.log('✅ Password reset for user:', userId);
      }),
      catchError(error => {
        console.error('❌ Error resetting password:', error);
        return of(false);
      })
    );
  }

  /**
   * Get user activity logs
   */
  getUserActivities(userId: string, limit: number = 50): Observable<ActivityLog[]> {
    const url = this.orgContext.getOrgApiUrl(`users/${userId}/activities`);
    
    if (!url) {
      return of([]);
    }

    const params = new HttpParams().set('limit', limit.toString());

    return this.http.get<any>(url, { 
      headers: this.getHeaders(),
      params 
    }).pipe(
      map(response => response.data || []),
      tap(activities => {
        console.log('✅ Activities fetched:', activities.length);
      }),
      catchError(error => {
        console.error('❌ Error fetching activities:', error);
        return of([]);
      })
    );
  }

  /**
   * Helper to create error response
   */
  private getErrorResponse(): UserListResponse {
    return {
      success: false,
      data: {
        users: [],
        pagination: {
          page: 1,
          pageSize: 50,
          totalCount: 0,
          totalPages: 0,
          hasNext: false,
          hasPrev: false
        }
      }
    };
  }
}
