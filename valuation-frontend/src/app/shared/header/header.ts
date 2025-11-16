import { Component, inject, computed } from '@angular/core';
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

  // Computed properties for reactive updates
  readonly isAuthenticated = computed(() => this.authService.isAuthenticated());
  readonly currentUser = computed(() => this.authService.currentUser());
  readonly orgContext = computed(() => this.authService.getOrganizationContext());

  /**
   * Logout user
   */
  logout(): void {
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
