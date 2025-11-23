import { Component, inject, computed, signal } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-header',
  imports: [RouterModule, CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {
  private readonly authService = inject(AuthService);

  // Mobile menu state
  private mobileMenuOpen = signal(false);

  // Computed properties for reactive updates
  readonly isAuthenticated = computed(() => this.authService.isAuthenticated());
  readonly currentUser = computed(() => this.authService.currentUser());
  readonly orgContext = computed(() => this.authService.getOrganizationContext());
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
    return this.authService.hasPermission('users', 'read');
  }

  /**
   * Check if user is system admin
   */
  isSystemAdmin(): boolean {
    const orgContext = this.orgContext();
    return orgContext?.isSystemAdmin || false;
  }
}
