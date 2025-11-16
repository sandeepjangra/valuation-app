/**
 * Angular Auth Guard for Organization Management
 * Route guard for protected pages with role-based access control and organization validation
 */

import { Injectable, inject } from '@angular/core';
import { 
  CanActivate, 
  CanActivateChild, 
  CanMatch,
  Route,
  UrlSegment,
  ActivatedRouteSnapshot, 
  RouterStateSnapshot, 
  Router,
  UrlTree 
} from '@angular/router';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../models/organization.model';

export interface RouteGuardConfig {
  requireAuth?: boolean;
  requiredRoles?: UserRole[];
  requiredPermissions?: Array<{
    resource: string;
    action: string;
  }>;
  redirectTo?: string;
  allowUnauthenticated?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate, CanActivateChild, CanMatch {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  /**
   * Guard for individual route activation
   */
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return this.checkAccess(route, state.url);
  }

  /**
   * Guard for child route activation
   */
  canActivateChild(
    childRoute: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return this.checkAccess(childRoute, state.url);
  }

  /**
   * Guard for route matching
   */
  canMatch(
    route: Route,
    segments: UrlSegment[]
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    const url = segments.map(s => s.path).join('/');
    return this.checkRouteAccess(route.data as RouteGuardConfig, url);
  }

  /**
   * Check access for a specific route
   */
  private checkAccess(
    route: ActivatedRouteSnapshot, 
    url: string
  ): Observable<boolean | UrlTree> | boolean | UrlTree {
    const config = route.data as RouteGuardConfig;
    return this.checkRouteAccess(config, url);
  }

  /**
   * Main access checking logic
   */
  private checkRouteAccess(
    config: RouteGuardConfig = {},
    url: string
  ): Observable<boolean | UrlTree> | boolean | UrlTree {
    const {
      requireAuth = true,
      requiredRoles = [],
      requiredPermissions = [],
      redirectTo = '/login',
      allowUnauthenticated = false
    } = config;

    // Allow unauthenticated access if configured
    if (allowUnauthenticated) {
      return true;
    }

    // Check authentication status
    if (requireAuth && !this.authService.isAuthenticated()) {
      console.log('🚫 Access denied: Not authenticated');
      return this.redirectToLogin(url, redirectTo);
    }

    // If not requiring auth and user is not authenticated, allow access
    if (!requireAuth && !this.authService.isAuthenticated()) {
      return true;
    }

    // Check role requirements
    if (requiredRoles.length > 0) {
      const hasRequiredRole = this.authService.hasAnyRole(requiredRoles);
      if (!hasRequiredRole) {
        console.log('🚫 Access denied: Insufficient role permissions', {
          required: requiredRoles,
          userRoles: this.authService.userRoles()
        });
        return this.redirectToAccessDenied();
      }
    }

    // Check specific permissions
    if (requiredPermissions.length > 0) {
      const hasAllPermissions = requiredPermissions.every(permission => 
        this.authService.hasPermission(permission.resource, permission.action)
      );
      
      if (!hasAllPermissions) {
        console.log('🚫 Access denied: Insufficient permissions', {
          required: requiredPermissions,
          user: this.authService.getOrganizationContext()?.email
        });
        return this.redirectToAccessDenied();
      }
    }

    // All checks passed
    console.log('✅ Access granted:', {
      url,
      user: this.authService.getOrganizationContext()?.email,
      roles: this.authService.userRoles()
    });
    
    return true;
  }

  /**
   * Redirect to login page
   */
  private redirectToLogin(attemptedUrl: string, redirectTo: string): UrlTree {
    // Store attempted URL for post-login redirect
    sessionStorage.setItem('attempted_url', attemptedUrl);
    
    return this.router.createUrlTree([redirectTo], {
      queryParams: { returnUrl: attemptedUrl }
    });
  }

  /**
   * Redirect to access denied page
   */
  private redirectToAccessDenied(): UrlTree {
    return this.router.createUrlTree(['/access-denied']);
  }
}

/**
 * Role-specific guard factory functions
 */

@Injectable({
  providedIn: 'root'
})
export class SystemAdminGuard implements CanActivate, CanActivateChild {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  canActivate(): boolean | UrlTree {
    if (this.authService.isSystemAdmin()) {
      return true;
    }
    return this.router.createUrlTree(['/access-denied']);
  }

  canActivateChild(): boolean | UrlTree {
    return this.canActivate();
  }
}

@Injectable({
  providedIn: 'root'
})
export class ManagerGuard implements CanActivate, CanActivateChild {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  canActivate(): boolean | UrlTree {
    if (this.authService.isManager()) {
      return true;
    }
    return this.router.createUrlTree(['/access-denied']);
  }

  canActivateChild(): boolean | UrlTree {
    return this.canActivate();
  }
}

/**
 * Permission-specific guard factory
 */
export function createPermissionGuard(resource: string, action: string) {
  @Injectable({
    providedIn: 'root'
  })
  class PermissionGuard implements CanActivate {
    private readonly authService = inject(AuthService);
    private readonly router = inject(Router);

    canActivate(): boolean | UrlTree {
      if (this.authService.hasPermission(resource, action)) {
        return true;
      }
      return this.router.createUrlTree(['/access-denied']);
    }
  }

  return PermissionGuard;
}

/**
 * Functional guards for modern Angular routing
 */
export const authGuard = (config?: RouteGuardConfig) => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);
    
    const {
      requireAuth = true,
      requiredRoles = [],
      requiredPermissions = [],
      redirectTo = '/login'
    } = config || {};

    if (requireAuth && !authService.isAuthenticated()) {
      return router.createUrlTree([redirectTo]);
    }

    if (requiredRoles.length > 0 && !authService.hasAnyRole(requiredRoles)) {
      return router.createUrlTree(['/access-denied']);
    }

    if (requiredPermissions.length > 0) {
      const hasAllPermissions = requiredPermissions.every(permission => 
        authService.hasPermission(permission.resource, permission.action)
      );
      
      if (!hasAllPermissions) {
        return router.createUrlTree(['/access-denied']);
      }
    }

    return true;
  };
};

export const systemAdminGuard = () => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);
    
    return authService.isSystemAdmin() || router.createUrlTree(['/access-denied']);
  };
};

export const managerGuard = () => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);
    
    return authService.isManager() || router.createUrlTree(['/access-denied']);
  };
};

export const permissionGuard = (resource: string, action: string) => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);
    
    return authService.hasPermission(resource, action) || router.createUrlTree(['/access-denied']);
  };
};

/**
 * Guard configuration helpers
 */
export const GuardConfig = {
  /**
   * Require authentication only
   */
  requireAuth: (): RouteGuardConfig => ({
    requireAuth: true
  }),

  /**
   * Require specific roles
   */
  requireRoles: (...roles: UserRole[]): RouteGuardConfig => ({
    requireAuth: true,
    requiredRoles: roles
  }),

  /**
   * Require specific permissions
   */
  requirePermissions: (...permissions: Array<{resource: string, action: string}>): RouteGuardConfig => ({
    requireAuth: true,
    requiredPermissions: permissions
  }),

  /**
   * System admin only
   */
  systemAdminOnly: (): RouteGuardConfig => ({
    requireAuth: true,
    requiredRoles: ['system_admin']
  }),

  /**
   * Manager or system admin
   */
  managerOrAdmin: (): RouteGuardConfig => ({
    requireAuth: true,
    requiredRoles: ['manager', 'system_admin']
  }),

  /**
   * Any authenticated user
   */
  authenticated: (): RouteGuardConfig => ({
    requireAuth: true
  }),

  /**
   * Allow unauthenticated access
   */
  public: (): RouteGuardConfig => ({
    requireAuth: false,
    allowUnauthenticated: true
  })
};

// Utility type for route data
export interface GuardedRoute {
  path: string;
  component?: any;
  canActivate?: any[];
  data?: RouteGuardConfig;
  children?: GuardedRoute[];
}