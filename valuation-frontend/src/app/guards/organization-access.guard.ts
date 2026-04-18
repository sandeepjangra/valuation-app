import { Injectable, inject } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Organization Access Guard
 * 
 * Validates that the authenticated user has access to the requested organization
 * 
 * Rules:
 * - System Admins (org: system-administration) can access ANY organization
 * - Regular users can ONLY access their own organization
 * - Unauthenticated users are redirected to login
 * - Users attempting to access other orgs get 403 Forbidden
 */
@Injectable({
  providedIn: 'root'
})
export class OrganizationAccessGuard implements CanActivate {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    // Check if user is authenticated
    const user = this.authService.currentUserValue;
    if (!user) {
      console.warn('🚫 OrganizationAccessGuard: User not authenticated');
      return this.router.createUrlTree(['/login'], { 
        queryParams: { returnUrl: state.url } 
      });
    }

    // Extract requested organization from route
    const requestedOrgShortName = route.paramMap.get('orgShortName');
    
    if (!requestedOrgShortName) {
      console.warn('🚫 OrganizationAccessGuard: No organization in route');
      return true; // Let other guards handle this
    }

    // Get user's organization
    const userOrgShortName = user.org_short_name;
    
    if (!userOrgShortName) {
      console.error('🚫 OrganizationAccessGuard: User has no org_short_name', user);
      this.router.navigate(['/unauthorized'], { 
        queryParams: { 
          message: 'Your account is missing organization information. Please contact support.' 
        }
      });
      return false;
    }

    // System administrators can access any organization
    const isSystemAdmin = userOrgShortName === 'system-administration';
    
    if (isSystemAdmin) {
      console.log('✅ OrganizationAccessGuard: System admin accessing', requestedOrgShortName);
      return true;
    }

    // Regular users can ONLY access their own organization
    if (userOrgShortName === requestedOrgShortName) {
      console.log('✅ OrganizationAccessGuard: User accessing own org', requestedOrgShortName);
      return true;
    }

    // User attempting to access different organization - FORBIDDEN
    console.warn(
      `🚫 OrganizationAccessGuard: User from '${userOrgShortName}' attempted to access '${requestedOrgShortName}'`
    );

    // Redirect to user's own organization's dashboard
    const userOrgDashboard = `/org/${userOrgShortName}/dashboard`;
    
    alert(
      `Access Denied!\n\nYou do not have permission to access organization '${requestedOrgShortName}'.\n` +
      `You can only access your own organization: '${userOrgShortName}'.`
    );

    return this.router.createUrlTree([userOrgDashboard]);
  }
}
