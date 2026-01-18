/**
 * Permission Guard
 * Protects routes based on required permissions
 * Usage in routes:
 * {
 *   path: 'admin',
 *   canActivate: [PermissionGuard],
 *   data: { 
 *     permissions: ['organizations.viewAll'],
 *     mode: 'all' // or 'any'
 *   }
 * }
 */

import { inject } from '@angular/core';
import { 
  CanActivateFn, 
  Router, 
  ActivatedRouteSnapshot, 
  RouterStateSnapshot 
} from '@angular/router';
import { PermissionsService } from '../services/permissions.service';

export const PermissionGuard: CanActivateFn = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => {
  const permissionsService = inject(PermissionsService);
  const router = inject(Router);

  // Get required permissions from route data
  const requiredPermissions = route.data['permissions'] as string[] | undefined;
  const mode = (route.data['mode'] as 'all' | 'any') || 'all';

  // If no permissions specified, allow access
  if (!requiredPermissions || requiredPermissions.length === 0) {
    return true;
  }

  // Check permissions
  const hasPermission = mode === 'all'
    ? permissionsService.hasAllPermissions(requiredPermissions)
    : permissionsService.hasAnyPermission(requiredPermissions);

  if (hasPermission) {
    return true;
  }

  // Permission denied - redirect to unauthorized page
  console.warn(`Access denied to ${state.url}. Required permissions:`, requiredPermissions);
  router.navigate(['/unauthorized'], {
    queryParams: { returnUrl: state.url }
  });
  
  return false;
};

/**
 * Role Guard
 * Simpler guard that checks user role
 * Usage:
 * {
 *   path: 'admin',
 *   canActivate: [RoleGuard],
 *   data: { 
 *     roles: ['system_admin', 'org_admin']
 *   }
 * }
 */
export const RoleGuard: CanActivateFn = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => {
  const permissionsService = inject(PermissionsService);
  const router = inject(Router);

  const requiredRoles = route.data['roles'] as string[] | undefined;
  
  if (!requiredRoles || requiredRoles.length === 0) {
    return true;
  }

  const userRole = permissionsService.getUserRole();
  
  if (userRole && requiredRoles.includes(userRole)) {
    return true;
  }

  console.warn(`Access denied to ${state.url}. Required roles:`, requiredRoles);
  router.navigate(['/unauthorized'], {
    queryParams: { returnUrl: state.url }
  });
  
  return false;
};
