import { Component, inject, computed, signal, OnInit } from '@angular/core';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { filter, map } from 'rxjs/operators';

@Component({
  selector: 'app-header',
  imports: [RouterModule, CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  // Mobile menu state
  private mobileMenuOpen = signal(false);
  
  // Current organization from route
  private currentOrgShortName = signal<string>('system-administration');

  ngOnInit() {
    // Listen to route changes to extract organization context
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      map(event => event as NavigationEnd)
    ).subscribe(event => {
      const urlSegments = event.url.split('/');
      if (urlSegments[1] === 'org' && urlSegments[2]) {
        this.currentOrgShortName.set(urlSegments[2]);
      }
    });

    // Set initial organization from current URL
    const currentUrl = this.router.url;
    const urlSegments = currentUrl.split('/');
    if (urlSegments[1] === 'org' && urlSegments[2]) {
      this.currentOrgShortName.set(urlSegments[2]);
    }
  }

  // Computed properties for reactive updates
  readonly isAuthenticated = computed(() => {
    const hasToken = !!this.authService.tokenValue;
    const hasUser = !!this.authService.currentUserValue;
    const auth = hasToken && hasUser;
    console.log('🔍 Header isAuthenticated:', { hasToken, hasUser, auth });
    return auth;
  });
  readonly currentUser = computed(() => this.authService.currentUser());
  readonly orgContext = computed(() => {
    const context = this.authService.getOrganizationContext();
    console.log('🔍 Header orgContext:', context);
    return context;
  });
  readonly isMobileMenuOpen = computed(() => this.mobileMenuOpen());

  /**
   * Toggle mobile menu
   */
  toggleMobileMenu(): void {
    this.mobileMenuOpen.set(!this.mobileMenuOpen());
  }

  /**
   * Close mobile menu
   */
  closeMobileMenu(): void {
    this.mobileMenuOpen.set(false);
  }

  /**
   * Logout user
   */
  logout(): void {
    this.closeMobileMenu();
    this.authService.logout().subscribe();
  }

  /**
   * Check if user has manager permissions
   */
  hasManagerPermissions(): boolean {
    const hasPermission = this.authService.hasPermission('users', 'read');
    const isManager = this.authService.isManager();
    const result = hasPermission || isManager;
    console.log('🔍 Header hasManagerPermissions:', { hasPermission, isManager, result });
    return result;
  }

  /**
   * Check if user is manager by role
   */
  isManager(): boolean {
    const isManager = this.authService.isManager();
    console.log('🔍 Header isManager:', isManager);
    return isManager;
  }

  /**
   * Check if user is system admin
   */
  isSystemAdmin(): boolean {
    const isAuthServiceSystemAdmin = this.authService.isSystemAdmin();
    const orgContext = this.orgContext();
    const isOrgContextSystemAdmin = orgContext?.isSystemAdmin || false;
    const isSystemAdmin = isAuthServiceSystemAdmin || isOrgContextSystemAdmin;
    
    console.log('🔍 Header isSystemAdmin:', {
      isAuthServiceSystemAdmin,
      orgContext,
      isOrgContextSystemAdmin,
      isSystemAdmin,
      orgShortName: orgContext?.orgShortName,
      roles: orgContext?.roles
    });
    return isSystemAdmin;
  }

  /**
   * Get current organization short name for routing
   */
  getCurrentOrgShortName(): string {
    return this.currentOrgShortName();
  }

  /**
   * Get organization-aware navigation links
   */
  getNavLinks() {
    const orgShortName = this.getCurrentOrgShortName();
    return {
      dashboard: `/org/${orgShortName}/dashboard`,
      newReport: `/org/${orgShortName}/reports/new`,
      reports: `/org/${orgShortName}/reports`,
      banks: `/org/${orgShortName}/banks`,
      templates: `/org/${orgShortName}/custom-templates`,
      pdfTemplates: `/org/${orgShortName}/pdf-templates`,
      employeeActivities: `/org/${orgShortName}/organization/users`
    };
  }
}
