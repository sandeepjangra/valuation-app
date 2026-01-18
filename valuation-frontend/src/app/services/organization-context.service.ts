import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { environment } from '../../environments/environment';

/**
 * Service to manage organization context across the application
 * Extracts orgShortName from route and provides helper methods for org-based URLs
 */
@Injectable({
  providedIn: 'root'
})
export class OrganizationContextService {
  private currentOrgShortName$ = new BehaviorSubject<string | null>(null);
  private baseApiUrl = environment.apiUrl; // Dynamically loaded from environment

  constructor(private router: Router) {
    // Listen to route changes and extract orgShortName
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.extractOrgFromRoute();
      });

    // Initialize on service creation
    this.extractOrgFromRoute();
  }

  /**
   * Extract organization shortName from current route
   */
  private extractOrgFromRoute(): void {
    const urlSegments = this.router.url.split('/');
    const orgIndex = urlSegments.indexOf('org');
    
    if (orgIndex !== -1 && urlSegments.length > orgIndex + 1) {
      const orgShortName = urlSegments[orgIndex + 1];
      // Remove query params if present
      const cleanOrgName = orgShortName.split('?')[0];
      this.setOrganization(cleanOrgName);
    } else {
      this.setOrganization(null);
    }
  }

  /**
   * Set current organization
   */
  setOrganization(orgShortName: string | null): void {
    if (this.currentOrgShortName$.value !== orgShortName) {
      console.log('🏢 Organization context changed:', orgShortName);
      this.currentOrgShortName$.next(orgShortName);
      
      // Store in sessionStorage for persistence
      if (orgShortName) {
        sessionStorage.setItem('currentOrg', orgShortName);
      } else {
        sessionStorage.removeItem('currentOrg');
      }
    }
  }

  /**
   * Get current organization shortName
   */
  getOrganization(): string | null {
    let org = this.currentOrgShortName$.value;
    
    // Fallback to sessionStorage if not set
    if (!org) {
      org = sessionStorage.getItem('currentOrg');
      if (org) {
        this.currentOrgShortName$.next(org);
      }
    }
    
    return org;
  }

  /**
   * Get current organization as observable
   */
  getOrganization$(): Observable<string | null> {
    return this.currentOrgShortName$.asObservable();
  }

  /**
   * Build organization-scoped API URL
   * @param path - The API path after /org/{orgShortName}/
   * @returns Full API URL or null if no org context
   */
  getOrgApiUrl(path: string): string | null {
    const org = this.getOrganization();
    if (!org) {
      console.warn('⚠️ No organization context available for API call');
      return null;
    }
    
    // Remove leading slash from path if present
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    
    return `${this.baseApiUrl}/org/${org}/${cleanPath}`;
  }

  /**
   * Build shared (non-org-scoped) API URL
   * @param path - The API path (e.g., 'organizations', 'auth/login')
   * @returns Full API URL
   */
  getSharedApiUrl(path: string): string {
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return `${this.baseApiUrl}/${cleanPath}`;
  }

  /**
   * Navigate to organization-scoped route
   * @param path - Path within organization (e.g., 'dashboard', 'reports')
   */
  navigateInOrg(path: string): void {
    const org = this.getOrganization();
    if (!org) {
      console.error('❌ Cannot navigate: No organization context');
      return;
    }
    
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    this.router.navigate(['/org', org, cleanPath]);
  }

  /**
   * Check if currently in organization context
   */
  hasOrganizationContext(): boolean {
    return this.getOrganization() !== null;
  }

  /**
   * Clear organization context
   */
  clearOrganization(): void {
    this.setOrganization(null);
  }
}
