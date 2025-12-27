import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { Router } from '@angular/router';

export interface User {
  _id?: string;
  user_id: string;
  email: string;
  full_name: string;
  organization_id: string;
  org_short_name?: string;
  organization_name?: string;
  role: string;
  roles: string[];
  status: string;
  is_active?: boolean;
  is_system_admin?: boolean;
  phone?: string;
  department?: string;
  created_at?: Date;
  last_login?: Date;
  permissions?: {
    can_submit_reports: boolean;
    can_manage_users: boolean;
    is_manager: boolean;
    is_admin: boolean;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  data: {
    access_token: string;
    id_token: string;
    refresh_token: string;
    expires_in: number;
    user: User;
  };
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/auth';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private tokenSubject = new BehaviorSubject<string | null>(null);

  public currentUser$ = this.currentUserSubject.asObservable();
  public token$ = this.tokenSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Load user and token from localStorage on service initialization
    this.loadStoredAuth();
  }

  private loadStoredAuth(): void {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('current_user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.tokenSubject.next(token);
        this.currentUserSubject.next(user);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        this.clearStoredAuth();
      }
    }
  }

  private clearStoredAuth(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credentials)
      .pipe(
        tap(response => {
          if (response.success && response.data) {
            // Store tokens
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('id_token', response.data.id_token);
            localStorage.setItem('refresh_token', response.data.refresh_token);
            localStorage.setItem('current_user', JSON.stringify(response.data.user));
            
            // Update subjects
            this.tokenSubject.next(response.data.access_token);
            this.currentUserSubject.next(response.data.user);
          }
        }),
        catchError(error => {
          console.error('Login error:', error);
          return throwError(error);
        })
      );
  }

  logout(): Observable<any> {
    const headers = this.getAuthHeaders();
    
    return this.http.post(`${this.apiUrl}/logout`, {}, { headers })
      .pipe(
        tap(() => {
          this.clearStoredAuth();
          this.router.navigate(['/login']);
        }),
        catchError(error => {
          // Even if logout fails on server, clear local storage
          this.clearStoredAuth();
          this.router.navigate(['/login']);
          return throwError(error);
        })
      );
  }

  getCurrentUser(): Observable<User> {
    const headers = this.getAuthHeaders();
    
    return this.http.get<{success: boolean, data: User}>(`${this.apiUrl}/me`, { headers })
      .pipe(
        map(response => response.data),
        tap(user => {
          localStorage.setItem('current_user', JSON.stringify(user));
          this.currentUserSubject.next(user);
        }),
        catchError(error => {
          if (error.status === 401) {
            this.clearStoredAuth();
            this.router.navigate(['/login']);
          }
          return throwError(error);
        })
      );
  }

  updateProfile(profileData: {full_name?: string, phone?: string}): Observable<any> {
    const headers = this.getAuthHeaders();
    
    return this.http.put(`${this.apiUrl}/me`, profileData, { headers })
      .pipe(
        tap(() => {
          // Refresh user data after update
          this.getCurrentUser().subscribe();
        }),
        catchError(error => {
          console.error('Profile update error:', error);
          return throwError(error);
        })
      );
  }

  registerUser(userData: {
    email: string;
    password: string;
    full_name: string;
    organization_id: string;
    role: string;
    phone?: string;
  }): Observable<any> {
    const headers = this.getAuthHeaders();
    
    return this.http.post(`${this.apiUrl}/register`, userData, { headers })
      .pipe(
        catchError(error => {
          console.error('User registration error:', error);
          return throwError(error);
        })
      );
  }

  updateUserRole(userId: string, role: string): Observable<any> {
    const headers = this.getAuthHeaders();
    
    return this.http.put(`${this.apiUrl}/users/${userId}/role`, { role }, { headers })
      .pipe(
        catchError(error => {
          console.error('Role update error:', error);
          return throwError(error);
        })
      );
  }

  disableUser(userId: string): Observable<any> {
    const headers = this.getAuthHeaders();
    
    return this.http.post(`${this.apiUrl}/users/${userId}/disable`, {}, { headers })
      .pipe(
        catchError(error => {
          console.error('User disable error:', error);
          return throwError(error);
        })
      );
  }

  enableUser(userId: string): Observable<any> {
    const headers = this.getAuthHeaders();
    
    return this.http.post(`${this.apiUrl}/users/${userId}/enable`, {}, { headers })
      .pipe(
        catchError(error => {
          console.error('User enable error:', error);
          return throwError(error);
        })
      );
  }

  private getAuthHeaders(): HttpHeaders {
    const token = this.tokenSubject.value;
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  // Utility methods
  get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  get tokenValue(): string | null {
    return this.tokenSubject.value;
  }

  isAuthenticated(): boolean {
    return !!this.tokenValue && !!this.currentUserValue;
  }

  isAdmin(): boolean {
    const user = this.currentUserValue;
    return user?.permissions?.is_admin || user?.is_system_admin || user?.role === 'admin' || false;
  }

  isManager(): boolean {
    const user = this.currentUserValue;
    return user?.permissions?.is_manager || user?.role === 'manager' || false;
  }

  canSubmitReports(): boolean {
    const user = this.currentUserValue;
    return user?.permissions?.can_submit_reports || false;
  }

  canManageUsers(): boolean {
    const user = this.currentUserValue;
    return user?.permissions?.can_manage_users || false;
  }

  hasRole(role: string): boolean {
    const user = this.currentUserValue;
    return user?.roles?.includes(role.toLowerCase()) || false;
  }

  getOrganizationId(): string | null {
    return this.currentUserValue?.organization_id || null;
  }

  getOrgShortName(): string | null {
    return this.currentUserValue?.org_short_name || this.currentUserValue?.organization_id || null;
  }

  getUserRole(): string | null {
    return this.currentUserValue?.role || null;
  }

  // Missing methods for compilation
  currentUser(): User | null {
    return this.currentUserValue;
  }

  getOrganizationContext(): any {
    const user = this.currentUserValue;
    if (!user) return null;
    
    return {
      organizationId: user.organization_id,
      orgShortName: user.org_short_name || user.organization_id,
      role: user.role,
      permissions: user.permissions,
      isSystemAdmin: user.is_system_admin || user.role === 'admin' || user.permissions?.is_admin || false,
      isManager: user.permissions?.is_manager || user.role === 'manager' || false,
      isEmployee: user.role === 'employee'
    };
  }

  hasPermission(resource: string, action: string): boolean {
    const user = this.currentUserValue;
    if (!user) return false;
    
    // Admin has all permissions
    if (user.is_system_admin || user.role === 'admin' || user.permissions?.is_admin) return true;
    
    if (resource === 'users' && action === 'read') {
      return user.permissions?.can_manage_users || false;
    }
    
    if (resource === 'reports' && action === 'submit') {
      return user.permissions?.can_submit_reports || false;
    }
    
    if (resource === 'templates' && action === 'save') {
      return user.role === 'admin' || user.role === 'manager' || user.is_system_admin || 
             user.roles?.includes('admin') || user.roles?.includes('manager') || false;
    }
    
    return false;
  }

  canSaveTemplates(): boolean {
    return this.hasPermission('templates', 'save');
  }

  canEditTemplates(): boolean {
    return this.canSaveTemplates();
  }

  canCreateTemplates(): boolean {
    return this.canSaveTemplates();
  }

  refreshToken(): Observable<any> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      return throwError('No refresh token available');
    }
    
    return this.http.post(`${this.apiUrl}/refresh`, { refresh_token: refreshToken })
      .pipe(
        tap((response: any) => {
          if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
            this.tokenSubject.next(response.access_token);
          }
        }),
        catchError(error => {
          this.clearStoredAuth();
          this.router.navigate(['/login']);
          return throwError(error);
        })
      );
  }

  getToken(): string | null {
    return this.tokenValue;
  }

  // Additional methods needed by components
  isSystemAdmin(): boolean {
    const user = this.currentUserValue;
    return user?.is_system_admin || user?.role === 'system_admin' || user?.role === 'admin' || this.hasRole('system_admin');
  }

  isEmployee(): boolean {
    const user = this.currentUserValue;
    return user?.role === 'employee' || this.hasRole('employee');
  }

  getCurrentRole(): string | null {
    return this.getUserRole();
  }

  userRoles(): string[] {
    const user = this.currentUserValue;
    return user?.roles || [];
  }

  loginWithDevToken(email: string, orgShortName: string, role: string = 'manager'): Observable<any> {
    const devLoginData = {
      email,
      organizationId: orgShortName,
      role
    };

    console.log('🧪 Development login with:', devLoginData);

    return this.http.post<LoginResponse>(`${this.apiUrl}/dev-login`, devLoginData)
      .pipe(
        tap(response => {
          if (response.success && response.data) {
            // Store tokens and user data
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('id_token', response.data.id_token);
            localStorage.setItem('refresh_token', response.data.refresh_token);
            localStorage.setItem('current_user', JSON.stringify(response.data.user));
            
            // Update subjects
            this.tokenSubject.next(response.data.access_token);
            this.currentUserSubject.next(response.data.user);

            console.log('✅ Dev login successful:', response.data.user);
          }
        }),
        catchError(error => {
          console.error('❌ Dev login failed:', error);
          return throwError(error);
        })
      );
  }
}