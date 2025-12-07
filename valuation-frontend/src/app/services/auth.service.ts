/**
 * Angular Authentication Service for Organization Management
 * Handles JWT tokens, login/logout, and organization context
 */

import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, BehaviorSubject, throwError, of } from 'rxjs';
import { map, catchError, tap, shareReplay } from 'rxjs/operators';
import { 
  JwtPayload, 
  OrganizationContext, 
  User, 
  UserRole, 
  ApiResponse,
  ErrorResponse 
} from '../models/organization.model';
import { environment } from '../../environments/environment';

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse extends ApiResponse {
  data: {
    access_token: string;
    refresh_token?: string;
    expires_in: number;
    user: User;
    organization: {
      id: string;
      name: string;
      type: string;
    };
  };
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  // API endpoints
  private readonly API_BASE = environment.apiUrl || 'http://localhost:8000/api';
  
  // Storage keys
  private readonly TOKEN_KEY = 'valuation_app_token';
  private readonly REFRESH_TOKEN_KEY = 'valuation_app_refresh_token';
  private readonly USER_KEY = 'valuation_app_user';
  private readonly ORG_CONTEXT_KEY = 'valuation_app_org_context';

  // State management using Angular signals
  private readonly _isAuthenticated = signal<boolean>(false);
  private readonly _currentUser = signal<User | null>(null);
  private readonly _organizationContext = signal<OrganizationContext | null>(null);
  private readonly _isLoading = signal<boolean>(false);

  // Public readonly signals
  readonly isAuthenticated = this._isAuthenticated.asReadonly();
  readonly currentUser = this._currentUser.asReadonly();
  readonly organizationContext = this._organizationContext.asReadonly();
  readonly isLoading = this._isLoading.asReadonly();

  // Computed signals for role checks
  readonly isSystemAdmin = computed(() => 
    this._organizationContext()?.isSystemAdmin ?? false
  );
  readonly isManager = computed(() => 
    this._organizationContext()?.isManager ?? false
  );
  readonly isEmployee = computed(() => 
    this._organizationContext()?.isEmployee ?? false
  );
  readonly userRoles = computed(() => 
    this._organizationContext()?.roles ?? []
  );

  // Token refresh timer
  private tokenRefreshTimer?: ReturnType<typeof setTimeout>;

  constructor() {
    this.initializeAuthState();
  }

  /**
   * Initialize authentication state from stored tokens
   */
  private initializeAuthState(): void {
    const token = this.getStoredToken();
    
    if (token) {
      try {
        if (!this.isTokenValid(token)) {
          console.log('⚠️ Token expired, clearing stored data');
          this.clearStoredData();
          this._isAuthenticated.set(false);
          return;
        }
        
        const payload = this.parseJwtPayload(token);
        const orgContext = this.createOrganizationContext(payload, token);
        const user = this.getStoredUser();

        this._isAuthenticated.set(true);
        this._organizationContext.set(orgContext);
        
        if (user) {
          this._currentUser.set(user);
        }

        // Set up token refresh
        this.scheduleTokenRefresh(payload.exp);
        
        console.log('✅ Auth state initialized from stored token', {
          email: orgContext.email,
          orgShortName: orgContext.orgShortName,
          roles: orgContext.roles
        });
      } catch (error) {
        console.error('❌ Failed to initialize auth state:', error);
        this.clearStoredData();
        this._isAuthenticated.set(false);
      }
    } else {
      console.log('ℹ️ No stored token found');
      this._isAuthenticated.set(false);
    }
  }

  /**
   * Login with email and password
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    this._isLoading.set(true);
    
    return this.http.post<LoginResponse>(`${this.API_BASE}/auth/login`, credentials)
      .pipe(
        tap(response => {
          if (response.success && response.data) {
            this.handleLoginSuccess(response.data);
          }
        }),
        catchError(this.handleError.bind(this)),
        tap(() => this._isLoading.set(false))
      );
  }

  /**
   * Login with development token (for testing)
   * Now calls the backend dev-login endpoint for proper token generation
   */
  loginWithDevToken(email: string, orgShortName: string, role: UserRole): Observable<boolean> {
    this._isLoading.set(true);
    
    console.log('🔐 Development login attempt:', { email, orgShortName, role });
    
    // Call backend dev-login endpoint
    return this.http.post<LoginResponse>(`${this.API_BASE}/auth/dev-login`, {
      email,
      organizationId: orgShortName,
      role
    }).pipe(
      tap(response => {
        if (response.success && response.data) {
          this.handleLoginSuccess(response.data);
          console.log('✅ Development login successful');
        }
      }),
      map(() => true),
      catchError(error => {
        console.error('❌ Development login failed:', error);
        this._isLoading.set(false);
        return throwError(() => error);
      }),
      tap(() => this._isLoading.set(false))
    );
  }

  /**
   * Logout user and clear all stored data
   */
  logout(): Observable<boolean> {
    // Clear token refresh timer
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
      this.tokenRefreshTimer = undefined;
    }

    // Clear all stored data immediately
    this.clearStoredData();
    
    // Reset signals
    this._isAuthenticated.set(false);
    this._currentUser.set(null);
    this._organizationContext.set(null);
    this._isLoading.set(false);
    
    console.log('✅ Logout completed - user signed out');
    
    // Redirect to login
    this.router.navigate(['/login']);
    
    // Optionally call logout endpoint (don't wait for it)
    if (this._isAuthenticated()) {
      this.http.post(`${this.API_BASE}/auth/logout`, {})
        .pipe(catchError(() => of({})))
        .subscribe({
          next: () => console.log('✅ Logout endpoint called successfully'),
          error: () => console.log('⚠️ Logout endpoint failed (ignored)')
        });
    }
    
    return of(true);
  }

  /**
   * Refresh access token
   */
  refreshToken(): Observable<string> {
    const refreshToken = localStorage.getItem(this.REFRESH_TOKEN_KEY);
    
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http.post<{access_token: string, expires_in: number}>(
      `${this.API_BASE}/auth/refresh`, 
      { refresh_token: refreshToken }
    ).pipe(
      tap(response => {
        const newToken = response.access_token;
        const payload = this.parseJwtPayload(newToken);
        
        // Update stored token
        localStorage.setItem(this.TOKEN_KEY, newToken);
        
        // Update organization context
        const orgContext = this.createOrganizationContext(payload, newToken);
        this._organizationContext.set(orgContext);
        
        // Schedule next refresh
        this.scheduleTokenRefresh(payload.exp);
        
        console.log('✅ Token refreshed successfully');
      }),
      map(response => response.access_token),
      catchError(error => {
        console.error('❌ Token refresh failed:', error);
        this.logout();
        return throwError(() => error);
      })
    );
  }

  /**
   * Get current JWT token
   */
  getToken(): string | null {
    return this.getStoredToken();
  }

  /**
   * Get current organization context
   */
  getOrganizationContext(): OrganizationContext | null {
    return this._organizationContext();
  }

  /**
   * Get current organization short name
   */
  getOrgShortName(): string | null {
    return this._organizationContext()?.orgShortName || null;
  }

  /**
   * Get current user role(s)
   */
  getCurrentRole(): UserRole | null {
    const roles = this.userRoles();
    const orgContext = this._organizationContext();
    
    // Check if system admin based on organization context
    if (orgContext?.isSystemAdmin) return 'system_admin';
    if (roles.includes('system_admin')) return 'system_admin';

    if (roles.includes('manager')) return 'manager';
    if (roles.includes('employee')) return 'employee';
    return null;
  }

  /**
   * Check if user has specific role
   */
  hasRole(role: UserRole): boolean {
    return this.userRoles().includes(role);
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(roles: UserRole[]): boolean {
    return roles.some(role => this.hasRole(role));
  }

  /**
   * Check if user has permission for resource action
   */
  hasPermission(resource: string, action: string): boolean {
    const orgContext = this._organizationContext();
    if (!orgContext) return false;

    // System admin has all permissions
    if (orgContext.isSystemAdmin) return true;

    // Define permission matrix (matching backend)
    const permissions: Record<string, Record<string, UserRole[]>> = {
      reports: {
        create: ['system_admin', 'manager', 'employee'],
        read: ['system_admin', 'manager', 'employee'],
        update: ['system_admin', 'manager', 'employee'],
        delete: ['system_admin', 'manager'],
        submit: ['system_admin', 'manager'] // Only Manager can submit
      },
      users: {
        create: ['system_admin'], // Only system admin can create users
        read: ['system_admin', 'manager'],
        update: ['system_admin', 'manager'], 
        delete: ['system_admin'] // Only system admin can delete users
      },
      audit_logs: {
        read: ['system_admin', 'manager']
      },
      organizations: {
        read: ['system_admin'],
        create: ['system_admin'],
        update: ['system_admin'],
        delete: ['system_admin']
      }
    };

    const allowedRoles = permissions[resource]?.[action];
    return allowedRoles ? this.hasAnyRole(allowedRoles) : false;
  }

  /**
   * Check if current user can submit reports
   * Only Managers and System Admins can submit reports
   */
  canSubmitReports(): boolean {
    return this.hasPermission('reports', 'submit');
  }

  /**
   * Check if current user can view activity logs
   * Only Managers and System Admins can view audit logs
   */
  canViewActivityLogs(): boolean {
    return this.hasPermission('audit_logs', 'read');
  }

  /**
   * Get current user information from backend
   * This validates the token and returns fresh user data
   */
  getCurrentUserFromBackend(): Observable<any> {
    return this.http.get(`${this.API_BASE}/auth/me`)
      .pipe(
        tap((response: any) => {
          if (response.success && response.data) {
            const userData = response.data;
            
            // Update current user if we have the full user object
            if (userData.user_id) {
              const user: User = {
                _id: userData.user_id,
                organization_id: userData.organization_id,
                email: userData.email,
                first_name: userData.email.split('@')[0],
                roles: userData.roles || [],
                is_active: true,
                created_at: new Date(),
                updated_at: new Date()
              };
              this._currentUser.set(user);
            }
            
            console.log('✅ Current user info refreshed from backend:', {
              email: userData.email,
              roles: userData.roles,
              permissions: userData.permissions
            });
          }
        }),
        catchError(error => {
          console.error('❌ Failed to get current user from backend:', error);
          // If token is invalid, logout
          if (error.status === 401) {
            this.logout();
          }
          return throwError(() => error);
        })
      );
  }

  // Private helper methods

  private handleLoginSuccess(loginData: LoginResponse['data']): void {
    try {
      const { access_token, refresh_token, user } = loginData;
      
      // Parse JWT payload
      const payload = this.parseJwtPayload(access_token);
      
      // Create organization context
      const orgContext = this.createOrganizationContext(payload, access_token);
      
      // Override system admin status if backend provides it
      if ((user as any).is_system_admin) {
        orgContext.isSystemAdmin = true;
        orgContext.isManager = true;
      }
      
      // Merge user data from loginData with parsed token data
      const enhancedUser: User = {
        ...user,
        roles: orgContext.roles // Ensure roles from token are used
      };
      
      // Store data
      localStorage.setItem(this.TOKEN_KEY, access_token);
      if (refresh_token) {
        localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh_token);
      }
      localStorage.setItem(this.USER_KEY, JSON.stringify(enhancedUser));
      localStorage.setItem(this.ORG_CONTEXT_KEY, JSON.stringify(orgContext));
      
      // Update signals
      this._isAuthenticated.set(true);
      this._currentUser.set(enhancedUser);
      this._organizationContext.set(orgContext);
      
      // Schedule token refresh
      this.scheduleTokenRefresh(payload.exp);
      
      console.log('✅ Login successful:', {
        user: enhancedUser.email,
        organization: orgContext.organizationId,
        roles: orgContext.roles,
        canSubmitReports: this.canSubmitReports(),
        canViewLogs: this.canViewActivityLogs()
      });
      
    } catch (error) {
      console.error('❌ Login processing failed:', error);
      throw error;
    }
  }

  private parseJwtPayload(token: string): JwtPayload {
    try {
      // Handle development tokens
      if (token.startsWith('dev_')) {
        // Parse development token format: dev_username_domain_org-short-name_role
        // Backend converts hyphens to underscores in token, we need to convert back
        const parts = token.replace('dev_', '').split('_');
        if (parts.length >= 4) {
          const username = parts[0];
          const domain = parts[1];
          const email = `${username}@${domain}`;
          
          // Handle special case: system-administration
          let orgShortName: string, role: string;
          if (parts.length >= 6 && parts[2] === 'system' && parts[3] === 'administration') {
            orgShortName = 'system-administration';
            role = parts[parts.length - 1] === 'admin' ? 'system_admin' : parts[parts.length - 1]; // Convert admin to system_admin
          } else if (parts.length >= 6 && parts[2] === 'system' && parts[3] === 'admin') {
            orgShortName = 'system_admin';
            role = 'system_admin';
          } else {
            // Join org parts (all except last which is role) and convert underscores back to hyphens
            const orgParts = parts.slice(2, -1);
            orgShortName = orgParts.join('_').replace(/_/g, '-');
            role = parts[parts.length - 1];
          }
          
          return {
            sub: `dev_user_${username}`,
            email: email,
            'custom:org_short_name': orgShortName,
            'custom:organization_id': orgShortName, // Backward compatibility
            'cognito:groups': [role as UserRole],
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + 3600,
            dev_mode: true
          };
        }
        throw new Error('Invalid development token format');
      }
      
      // Parse regular JWT token
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid JWT token format');
      }
      
      const payload = JSON.parse(atob(parts[1]));
      
      // Ensure org_short_name is present, fallback to organization_id for backward compatibility
      if (!payload['custom:org_short_name'] && payload['custom:organization_id']) {
        payload['custom:org_short_name'] = payload['custom:organization_id'];
      }
      
      return payload as JwtPayload;
      
    } catch (error) {
      console.error('❌ JWT parsing failed:', error);
      throw new Error('Invalid token format');
    }
  }

  private createOrganizationContext(payload: JwtPayload, token: string): OrganizationContext {
    const roles = payload['cognito:groups'] || [];
    // Use org_short_name if available, fallback to organization_id for backward compatibility
    const orgShortName = payload['custom:org_short_name'] || payload['custom:organization_id'] || 'unknown';
    
    // Check for system admin status from multiple sources
    const isSystemAdmin = roles.includes('system_admin') || 
                         orgShortName === 'system-administration' || orgShortName === 'system_admin';
    
    return {
      userId: payload.sub,
      email: payload.email,
      orgShortName: orgShortName,
      organizationId: orgShortName, // Backward compatibility alias
      roles: roles,
      isSystemAdmin: isSystemAdmin,
      isManager: roles.includes('manager') || isSystemAdmin,
      isEmployee: roles.length > 0,
      token: token,
      expiresAt: new Date(payload.exp * 1000)
    };
  }

  private isTokenValid(token: string): boolean {
    try {
      const payload = this.parseJwtPayload(token);
      const now = Math.floor(Date.now() / 1000);
      return payload.exp > now;
    } catch {
      return false;
    }
  }

  private scheduleTokenRefresh(expiration: number): void {
    // Clear existing timer
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
    }

    // Schedule refresh 5 minutes before expiration
    const now = Math.floor(Date.now() / 1000);
    const refreshTime = (expiration - now - 300) * 1000; // 5 minutes before expiry
    
    if (refreshTime > 0) {
      this.tokenRefreshTimer = setTimeout(() => {
        this.refreshToken().subscribe({
          error: (error) => console.error('❌ Auto token refresh failed:', error)
        });
      }, refreshTime);
    }
  }

  private getStoredToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private getStoredUser(): User | null {
    const userData = localStorage.getItem(this.USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  private clearStoredData(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    localStorage.removeItem(this.ORG_CONTEXT_KEY);
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      const errorResponse = error.error as ErrorResponse;
      errorMessage = errorResponse.error || `HTTP ${error.status}: ${error.message}`;
    }
    
    console.error('❌ Auth service error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}