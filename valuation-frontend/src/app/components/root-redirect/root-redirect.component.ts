import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

/**
 * Root Redirect Component
 * 
 * Handles the default "/" route and redirects users to their appropriate organization dashboard
 * - System admins → /org/system-administration/dashboard
 * - Regular users → /org/{their-org}/dashboard
 * - Unauthenticated → /login
 */
@Component({
  selector: 'app-root-redirect',
  standalone: true,
  template: `
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column;">
      <div class="spinner"></div>
      <p style="margin-top: 1rem; color: #666;">Redirecting...</p>
    </div>
    
    <style>
      .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    </style>
  `
})
export class RootRedirectComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  ngOnInit() {
    this.redirectToAppropriateOrg();
  }

  private redirectToAppropriateOrg() {
    const user = this.authService.currentUserValue;

    if (!user) {
      // Not authenticated - redirect to login
      console.log('🔄 Root redirect: Not authenticated, redirecting to login');
      this.router.navigate(['/login']);
      return;
    }

    // Get user's organization
    const orgShortName = user.org_short_name;

    if (!orgShortName) {
      console.error('❌ Root redirect: User has no org_short_name', user);
      // Fallback to system-administration
      this.router.navigate(['/org/system-administration/dashboard']);
      return;
    }

    // Redirect to user's organization dashboard
    console.log(`✅ Root redirect: Redirecting to /org/${orgShortName}/dashboard`);
    this.router.navigate([`/org/${orgShortName}/dashboard`]);
  }
}
