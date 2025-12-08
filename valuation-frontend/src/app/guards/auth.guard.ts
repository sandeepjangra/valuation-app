import { Injectable, inject } from '@angular/core';
import { CanActivate, CanActivateChild, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate, CanActivateChild {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.checkAuth(route, state);
  }

  canActivateChild(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    return this.checkAuth(route, state);
  }

  private checkAuth(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
    return this.authService.currentUser$.pipe(
      take(1),
      map(user => {
        if (user) {
          // Check role-based access if specified in route data
          const requiredRoles = route.data['roles'] as string[];
          const requiredPermissions = route.data['permissions'] as string[];
          
          if (requiredRoles && requiredRoles.length > 0) {
            const hasRequiredRole = requiredRoles.some(role => 
              this.authService.hasRole(role)
            );
            
            if (!hasRequiredRole) {
              console.warn('Access denied: insufficient role');
              this.router.navigate(['/unauthorized']);
              return false;
            }
          }
          
          if (requiredPermissions && requiredPermissions.length > 0) {
            const hasRequiredPermission = this.checkPermissions(requiredPermissions);
            
            if (!hasRequiredPermission) {
              console.warn('Access denied: insufficient permissions');
              this.router.navigate(['/unauthorized']);
              return false;
            }
          }
          
          return true;
        } else {
          // Not authenticated, redirect to login
          this.router.navigate(['/login'], { 
            queryParams: { returnUrl: state.url } 
          });
          return false;
        }
      })
    );
  }

  private checkPermissions(requiredPermissions: string[]): boolean {
    return requiredPermissions.every(permission => {
      switch (permission) {
        case 'submit_reports':
          return this.authService.canSubmitReports();
        case 'manage_users':
          return this.authService.canManageUsers();
        case 'admin':
          return this.authService.isAdmin();
        case 'manager':
          return this.authService.isManager();
        default:
          return false;
      }
    });
  }
}

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): Observable<boolean> {
    return this.authService.currentUser$.pipe(
      take(1),
      map(user => {
        if (user && this.authService.isAdmin()) {
          return true;
        } else {
          this.router.navigate(['/unauthorized']);
          return false;
        }
      })
    );
  }
}

@Injectable({
  providedIn: 'root'
})
export class ManagerGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): Observable<boolean> {
    return this.authService.currentUser$.pipe(
      take(1),
      map(user => {
        if (user && (this.authService.isManager() || this.authService.isAdmin())) {
          return true;
        } else {
          this.router.navigate(['/unauthorized']);
          return false;
        }
      })
    );
  }
}

// Functional guards for modern Angular routing

export const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  return authService.currentUser$.pipe(
    take(1),
    map(user => {
      if (user) {
        return true;
      } else {
        router.navigate(['/login']);
        return false;
      }
    })
  );
};

export const managerGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  return authService.currentUser$.pipe(
    take(1),
    map(user => {
      if (user && (authService.isManager() || authService.isAdmin())) {
        return true;
      } else {
        router.navigate(['/unauthorized']);
        return false;
      }
    })
  );
};

export const systemAdminGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  return authService.currentUser$.pipe(
    take(1),
    map(user => {
      if (user && authService.isSystemAdmin()) {
        return true;
      } else {
        router.navigate(['/unauthorized']);
        return false;
      }
    })
  );
};