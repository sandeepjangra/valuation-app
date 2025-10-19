import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Observable, BehaviorSubject, of, throwError } from 'rxjs';
import { map, tap, delay, catchError } from 'rxjs/operators';
import { ApiService } from './api.service';
import { User, UserRole } from '../models';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  organization?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private isLoggedInSubject = new BehaviorSubject<boolean>(false);
  public isLoggedIn$ = this.isLoggedInSubject.asObservable();

  // Dummy users for testing
  private dummyUsers: User[] = [
    {
      id: '1',
      username: 'admin',
      email: 'admin@valuationapp.com',
      role: 'admin',
      firstName: 'Admin',
      lastName: 'User',
      isActive: true,
      permissions: {
        canCreateReports: true,
        canEditReports: true,
        canViewReports: true,
        canDeleteReports: true,
        canSubmitReports: true,
        canApproveReports: true,
        canRejectReports: true,
        canViewAllReports: true,
        canManageTemplates: true,
        canManageBanks: true,
        canManageUsers: true,
        canExportReports: true,
        canViewDashboard: true
      },
      createdDate: new Date(),
      lastLoginDate: new Date()
    },
    {
      id: '2',
      username: 'manager',
      email: 'manager@valuationapp.com',
      role: 'manager',
      firstName: 'Manager',
      lastName: 'User',
      isActive: true,
      permissions: {
        canCreateReports: true,
        canEditReports: true,
        canViewReports: true,
        canDeleteReports: false,
        canSubmitReports: true,
        canApproveReports: true,
        canRejectReports: true,
        canViewAllReports: true,
        canManageTemplates: true,
        canManageBanks: false,
        canManageUsers: false,
        canExportReports: true,
        canViewDashboard: true
      },
      createdDate: new Date(),
      lastLoginDate: new Date()
    },
    {
      id: '3',
      username: 'employee',
      email: 'employee@valuationapp.com',
      role: 'employee',
      firstName: 'Employee',
      lastName: 'User',
      isActive: true,
      permissions: {
        canCreateReports: true,
        canEditReports: true,
        canViewReports: true,
        canDeleteReports: false,
        canSubmitReports: false,
        canApproveReports: false,
        canRejectReports: false,
        canViewAllReports: false,
        canManageTemplates: false,
        canManageBanks: false,
        canManageUsers: false,
        canExportReports: true,
        canViewDashboard: true
      },
      createdDate: new Date(),
      lastLoginDate: new Date()
    }
  ];

  constructor(
    private apiService: ApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.checkStoredAuth();
  }

  login(username: string, password: string): Observable<boolean> {
    // Simulate API call with dummy authentication
    return of(null).pipe(
      delay(1000), // Simulate network delay
      map(() => {
        const user = this.dummyUsers.find(u => 
          u.username === username && 
          password === u.username // password same as username for dummy
        );
        
        if (!user) {
          return false;
        }
        
        const mockToken = 'mock-jwt-token-' + user.role;
        this.setAuth(mockToken, user);
        return true;
      }),
      catchError((error) => {
        console.error('Login error:', error);
        return of(false);
      })
    );
  }

  signup(signupData: SignupData): Observable<User> {
    // Simulate API call for signup
    return of(null).pipe(
      delay(1000),
      map(() => {
        // Check if user already exists
        const existingUser = this.dummyUsers.find(u => 
          u.username === signupData.username || u.email === signupData.email
        );
        
        if (existingUser) {
          throw new Error('User already exists');
        }
        
        // Create new user (for demo, assign 'employee' role by default)
        const newUser: User = {
          id: (this.dummyUsers.length + 1).toString(),
          username: signupData.email,
          email: signupData.email,
          role: 'employee',
          firstName: signupData.firstName,
          lastName: signupData.lastName,
          isActive: true,
          permissions: {
            canCreateReports: true,
            canEditReports: true,
            canViewReports: true,
            canDeleteReports: false,
            canSubmitReports: false,
            canApproveReports: false,
            canRejectReports: false,
            canViewAllReports: false,
            canManageTemplates: false,
            canManageBanks: false,
            canManageUsers: false,
            canExportReports: true,
            canViewDashboard: true
          },
          createdDate: new Date(),
          lastLoginDate: new Date()
        };
        
        this.dummyUsers.push(newUser);
        const mockToken = 'mock-jwt-token-' + newUser.role;
        this.setAuth(mockToken, newUser);
        return newUser;
      })
    );
  }

  logout(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('current_user');
    }
    this.apiService.removeAuthToken();
    this.currentUserSubject.next(null);
    this.isLoggedInSubject.next(false);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return this.isLoggedInSubject.value;
  }

  hasRole(role: UserRole): boolean {
    const currentUser = this.getCurrentUser();
    return currentUser ? currentUser.role === role : false;
  }

  hasPermission(permission: keyof User['permissions']): boolean {
    const currentUser = this.getCurrentUser();
    return currentUser ? currentUser.permissions[permission] : false;
  }

  canAccessFeature(feature: string): boolean {
    const currentUser = this.getCurrentUser();
    if (!currentUser) return false;

    switch (feature) {
      case 'user-management':
        return this.hasPermission('canManageUsers');
      case 'bank-management':
        return this.hasPermission('canManageBanks');
      case 'template-management':
        return this.hasPermission('canManageTemplates');
      case 'report-approval':
        return this.hasPermission('canApproveReports');
      case 'all-reports':
        return this.hasPermission('canViewAllReports');
      default:
        return false;
    }
  }

  getDummyUsers(): User[] {
    return this.dummyUsers.filter(user => user.isActive);
  }

  private setAuth(token: string, user: User): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('auth_token', token);
      localStorage.setItem('current_user', JSON.stringify(user));
    }
    this.apiService.setAuthToken(token);
    this.currentUserSubject.next(user);
    this.isLoggedInSubject.next(true);
  }

  private checkStoredAuth(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return; // Skip if not in browser (SSR)
    }
    
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('current_user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.setAuth(token, user);
      } catch (error) {
        this.logout();
      }
    }
  }
}