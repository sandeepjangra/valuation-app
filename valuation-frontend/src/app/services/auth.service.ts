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
    
    if (token && this.isTokenValid(token)) {
      try {
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
        
        console.log('✅ Auth state initialized from stored token');
      } catch (error) {
        console.error('❌ Failed to initialize auth state:', error);
        this.logout();
      }
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
   */
  loginWithDevToken(email: string, organizationId: string, role: UserRole): Observable<boolean> {
    this._isLoading.set(true);
    
    // Create development token (matching backend format)
    const [username, domain] = email.split('@');
    const devToken = `dev_${username}_${domain}_${organizationId}_${role}`;
    
    try {
      // Create mock JWT payload for development
      const mockPayload: JwtPayload = {
        sub: `dev_user_${username}`,
        email: email,
        'custom:organization_id': organizationId,
        'cognito:groups': [role],
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour
        dev_mode: true
      };

      // Create mock user data
      const mockUser: User = {
        _id: mockPayload.sub,
        organization_id: organizationId,
        email: email,
        first_name: username,
        roles: [role],
        is_active: true,
        created_at: new Date(),
        updated_at: new Date()
      };

      const loginData = {
        access_token: devToken,
        expires_in: 3600,
        user: mockUser,
        organization: {
          id: organizationId,
          name: organizationId === 'system_admin' ? 'System Administration' : 'Demo Organization 001',
          type: organizationId === 'system_admin' ? 'system' : 'valuation_company'
        }
      };

      this.handleLoginSuccess(loginData);
      this._isLoading.set(false);
      
      console.log('✅ Development login successful');
      return of(true);
      
    } catch (error) {
      console.error('❌ Development login failed:', error);
      this._isLoading.set(false);
      return throwError(() => error);
    }
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

    // Call logout endpoint if authenticated
    const logoutRequest = this._isAuthenticated() 
      ? this.http.post(`${this.API_BASE}/auth/logout`, {})
      : of({});

    return logoutRequest.pipe(
      catchError(() => of({})), // Ignore logout endpoint errors
      tap(() => {
        // Clear all stored data
        this.clearStoredData();
        
        // Reset signals
        this._isAuthenticated.set(false);
        this._currentUser.set(null);
        this._organizationContext.set(null);
        this._isLoading.set(false);
        
        // Redirect to login
        this.router.navigate(['/login']);
        
        console.log('✅ Logout completed');
      }),
      map(() => true)
    );
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
        delete: ['system_admin', 'manager']
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

  // Private helper methods

  private handleLoginSuccess(loginData: LoginResponse['data']): void {
    try {
      const { access_token, refresh_token, user } = loginData;
      
      // Parse JWT payload
      const payload = this.parseJwtPayload(access_token);
      
      // Create organization context
      const orgContext = this.createOrganizationContext(payload, access_token);
      
      // Store data
      localStorage.setItem(this.TOKEN_KEY, access_token);
      if (refresh_token) {
        localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh_token);
      }
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      localStorage.setItem(this.ORG_CONTEXT_KEY, JSON.stringify(orgContext));
      
      // Update signals
      this._isAuthenticated.set(true);
      this._currentUser.set(user);
      this._organizationContext.set(orgContext);
      
      // Schedule token refresh
      this.scheduleTokenRefresh(payload.exp);
      
      console.log('✅ Login successful:', {
        user: user.email,
        organization: orgContext.organizationId,
        roles: orgContext.roles
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
        // Parse development token format: dev_username_domain_orgid_role
        const parts = token.replace('dev_', '').split('_');
        if (parts.length >= 4) {
          const username = parts[0];
          const domain = parts[1];
          const email = `${username}@${domain}`;
          
          // Handle system_admin case
          let orgId: string, role: string;
          if (parts.length >= 6 && parts[2] === 'system' && parts[3] === 'admin') {
            orgId = 'system_admin';
            role = 'system_admin';
          } else {
            orgId = parts.slice(2, -1).join('_');
            role = parts[parts.length - 1];
          }
          
          return {
            sub: `dev_user_${username}`,
            email: email,
            'custom:organization_id': orgId,
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
      return payload as JwtPayload;
      
    } catch (error) {
      console.error('❌ JWT parsing failed:', error);
      throw new Error('Invalid token format');
    }
  }

  private createOrganizationContext(payload: JwtPayload, token: string): OrganizationContext {
    const roles = payload['cognito:groups'] || [];
    const organizationId = payload['custom:organization_id'];
    
    return {
      userId: payload.sub,
      email: payload.email,
      organizationId: organizationId,
      roles: roles,
      isSystemAdmin: roles.includes('system_admin'),
      isManager: roles.includes('manager') || roles.includes('system_admin'),
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