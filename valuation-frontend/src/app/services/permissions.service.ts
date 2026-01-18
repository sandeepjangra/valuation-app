/**
 * Permissions Service
 * Manages user permissions and provides permission checking methods
 */

import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { map, tap, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { 
  PermissionTemplate, 
  PermissionSet, 
  UserWithPermissions 
} from '../models/permissions.model';

@Injectable({
  providedIn: 'root'
})
export class PermissionsService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/permissions`;

  // Cache permission templates
  private permissionTemplatesCache = new BehaviorSubject<PermissionTemplate[]>([]);
  
  // Current user's permissions
  private userPermissions = signal<PermissionSet | null>(null);
  
  // Current user's role
  private userRole = signal<'system_admin' | 'org_admin' | 'employee' | null>(null);
  
  // Is system admin flag
  private isSystemAdmin = signal<boolean>(false);

  constructor() {
    this.loadPermissionTemplates();
  }

  /**
   * Load all permission templates from backend
   */
  private loadPermissionTemplates(): void {
    this.http.get<any>(`${this.apiUrl}/templates`).pipe(
      map(response => response.data || []),
      catchError(err => {
        console.error('Failed to load permission templates:', err);
        return of([]);
      })
    ).subscribe(templates => {
      this.permissionTemplatesCache.next(templates);
    });
  }

  /**
   * Get all permission templates
   */
  getPermissionTemplates(): Observable<PermissionTemplate[]> {
    return this.permissionTemplatesCache.asObservable();
  }

  /**
   * Get permission template for specific role
   */
  getPermissionTemplate(role: string): Observable<PermissionTemplate | null> {
    return this.http.get<any>(`${this.apiUrl}/templates/${role}`).pipe(
      map(response => response.data || null),
      catchError(err => {
        console.error(`Failed to load permission template for role ${role}:`, err);
        return of(null);
      })
    );
  }

  /**
   * Set current user's permissions
   * Called after login or when user context changes
   */
  setUserPermissions(user: any): void {
    const role = user.role || user.user_role || 'employee';
    const isSystemAdmin = user.isSystemAdmin || user.is_system_admin || false;
    
    this.userRole.set(role);
    this.isSystemAdmin.set(isSystemAdmin);

    // Load permissions for this role
    this.getPermissionTemplate(role).subscribe(template => {
      if (template) {
        // Apply any permission overrides
        const permissions = this.applyPermissionOverrides(
          template.permissions,
          user.permissionOverrides || user.permission_overrides || {}
        );
        this.userPermissions.set(permissions);
        console.log('✅ User permissions loaded:', { role, isSystemAdmin, permissions });
      }
    });
  }

  /**
   * Apply permission overrides to base role permissions
   */
  private applyPermissionOverrides(
    basePermissions: PermissionSet,
    overrides: Record<string, boolean>
  ): PermissionSet {
    const permissions = JSON.parse(JSON.stringify(basePermissions)); // Deep clone
    
    for (const [key, value] of Object.entries(overrides)) {
      const parts = key.split('.');
      if (parts.length === 2) {
        const [category, permission] = parts;
        if (permissions[category as keyof PermissionSet]) {
          (permissions[category as keyof PermissionSet] as any)[permission] = value;
        }
      }
    }
    
    return permissions;
  }

  /**
   * Check if user has a specific permission
   * Usage: hasPermission('reports.create')
   */
  hasPermission(permission: string): boolean {
    const permissions = this.userPermissions();
    if (!permissions) return false;

    const parts = permission.split('.');
    if (parts.length !== 2) {
      console.warn(`Invalid permission format: ${permission}. Use 'category.permission'`);
      return false;
    }

    const [category, perm] = parts;
    const categoryPerms = permissions[category as keyof PermissionSet];
    
    if (!categoryPerms) {
      console.warn(`Unknown permission category: ${category}`);
      return false;
    }

    return (categoryPerms as any)[perm] === true;
  }

  /**
   * Check multiple permissions (AND logic - all must be true)
   */
  hasAllPermissions(permissions: string[]): boolean {
    return permissions.every(p => this.hasPermission(p));
  }

  /**
   * Check multiple permissions (OR logic - at least one must be true)
   */
  hasAnyPermission(permissions: string[]): boolean {
    return permissions.some(p => this.hasPermission(p));
  }

  /**
   * Get current user's role
   */
  getUserRole(): 'system_admin' | 'org_admin' | 'employee' | null {
    return this.userRole();
  }

  /**
   * Check if current user is system admin
   */
  isUserSystemAdmin(): boolean {
    return this.isSystemAdmin();
  }

  /**
   * Get all current user's permissions
   */
  getUserPermissions(): PermissionSet | null {
    return this.userPermissions();
  }

  /**
   * Clear permissions (on logout)
   */
  clearPermissions(): void {
    this.userPermissions.set(null);
    this.userRole.set(null);
    this.isSystemAdmin.set(false);
  }

  /**
   * Permission helper methods for common checks
   */
  
  canManageOrganizations(): boolean {
    return this.hasPermission('organizations.create') || 
           this.hasPermission('organizations.editAny');
  }

  canManageUsers(): boolean {
    return this.hasPermission('users.create') || 
           this.hasPermission('users.editAny');
  }

  canSubmitReports(): boolean {
    return this.hasPermission('reports.submit');
  }

  canCreateCustomTemplates(): boolean {
    return this.hasPermission('templates.createCustom');
  }

  canViewAnalytics(): boolean {
    return this.hasPermission('analytics.viewOrgActivity') ||
           this.hasPermission('analytics.viewAllActivity');
  }

  canManageSettings(): boolean {
    return this.hasPermission('settings.editOrgSettings') ||
           this.hasPermission('settings.editSystemSettings');
  }
}
