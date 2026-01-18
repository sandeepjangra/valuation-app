/**
 * Organization Dashboard Component
 * Main dashboard showing organization info, user management, and navigation based on user roles
 */

import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { Observable, forkJoin, catchError, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { 
  Organization, 
  User, 
  DashboardCard, 
  NavigationItem,
  UserRole 
} from '../../models/organization.model';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { ActivityLoggingService } from '../../services/activity-logging.service';
import { ActivityLogEntry } from '../../models/activity-log.model';

@Component({
  selector: 'app-organization-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="organization-dashboard">
      <!-- Header Section -->
      <div class="dashboard-header">
        <div class="organization-info">
          <h1>{{ organization()?.name || 'Loading...' }}</h1>
          <p class="organization-type">{{ getOrganizationTypeLabel() }}</p>
          <div class="user-info">
            <span class="user-name">{{ currentUser()?.email }}</span>
            <span class="user-roles">{{ getUserRolesLabel() }}</span>
          </div>
        </div>
        
        <div class="header-actions">
          <button 
            class="btn btn-outline"
            (click)="refreshDashboard()"
            [disabled]="isLoading()">
            🔄 Refresh
          </button>
          <button 
            class="btn btn-primary"
            (click)="logout()">
            Logout
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="isLoading()" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading dashboard data...</p>
      </div>

      <!-- Error State -->
      <div *ngIf="error()" class="error-container">
        <div class="error-message">
          <h3>⚠️ Error Loading Dashboard</h3>
          <p>{{ error() }}</p>
          <button class="btn btn-primary" (click)="refreshDashboard()">
            Try Again
          </button>
        </div>
      </div>

      <!-- Dashboard Content -->
      <div *ngIf="!isLoading() && !error()" class="dashboard-content">
        
        <!-- Statistics Cards -->
        <div class="stats-section">
          <h2>Organization Overview</h2>
          <div class="stats-grid">
            <div *ngFor="let card of dashboardCards()" 
                 class="stat-card"
                 [class.clickable]="card.route"
                 (click)="navigateToCard(card)">
              <div class="stat-icon" [style.background-color]="card.color">
                {{ card.icon }}
              </div>
              <div class="stat-content">
                <h3>{{ card.value }}</h3>
                <p>{{ card.title }}</p>
                <div *ngIf="card.trend" class="stat-trend" 
                     [class.positive]="card.trend.direction === 'up'"
                     [class.negative]="card.trend.direction === 'down'">
                  <span class="trend-arrow">
                    {{ card.trend.direction === 'up' ? '↗' : card.trend.direction === 'down' ? '↘' : '→' }}
                  </span>
                  <span class="trend-percentage">{{ card.trend.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="actions-section">
          <h2>Quick Actions</h2>
          <div class="actions-grid">
            <div *ngFor="let action of quickActions()" 
                 class="action-card"
                 (click)="executeAction(action)">
              <div class="action-icon">{{ action.icon }}</div>
              <div class="action-content">
                <h4>{{ action.label }}</h4>
                <p>{{ action.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation Menu -->
        <div class="navigation-section">
          <h2>Management Areas</h2>
          <div class="navigation-grid">
            <div *ngFor="let nav of navigationItems()" 
                 class="nav-card"
                 [class.disabled]="nav.disabled"
                 (click)="navigateTo(nav.route)"
                 [attr.title]="nav.disabled ? 'Access denied - insufficient permissions' : ''">
              <div class="nav-icon">{{ nav.icon }}</div>
              <div class="nav-content">
                <h4>{{ nav.label }}</h4>
                <div *ngIf="nav.roles" class="nav-roles">
                  Required: {{ nav.roles.join(', ') }}
                </div>
              </div>
              <div class="nav-arrow">→</div>
            </div>
          </div>
        </div>

        <!-- Recent Activity (if manager or admin) -->
        <div *ngIf="canViewAuditLogs()" class="activity-section">
          <h2>Recent Activity</h2>
          <div class="activity-list">
            <div *ngIf="recentActivity().length === 0" class="no-activity">
              No recent activity
            </div>
            <div *ngFor="let activity of recentActivity()" class="activity-item">
              <div class="activity-icon">{{ getActivityIcon(activity.actionType) }}</div>
              <div class="activity-content">
                <p><strong>{{ activity.description }}</strong></p>
                <small>{{ activity.action }} • {{ formatActivityDate(activity.timestamp!) }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./organization-dashboard.component.css']
})
export class OrganizationDashboardComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly organizationService = inject(OrganizationService);
  private readonly activityLoggingService = inject(ActivityLoggingService);
  private readonly router = inject(Router);

  // Component state
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);
  readonly organization = signal<Organization | null>(null);
  readonly dashboardStats = signal<any>(null);
  readonly recentActivity = signal<ActivityLogEntry[]>([]);

  // Auth state
  readonly currentUser = this.authService.currentUser;
  readonly organizationContext = this.authService.getOrganizationContext();
  readonly isSystemAdmin = () => this.authService.isSystemAdmin();
  readonly isManager = () => this.authService.isManager();
  readonly userRoles = () => this.authService.userRoles();

  // Computed dashboard data
  readonly dashboardCards = computed(() => this.buildDashboardCards());
  readonly quickActions = computed(() => this.buildQuickActions());
  readonly navigationItems = computed(() => this.buildNavigationItems());

  ngOnInit(): void {
    this.loadDashboardData();
  }

  /**
   * Load all dashboard data
   */
  loadDashboardData(): void {
    this.isLoading.set(true);
    this.error.set(null);

    const requests: Observable<any>[] = [
      this.organizationService.getCurrentOrganization().pipe(
        catchError(error => {
          console.error('Error loading organization:', error);
          return of(null);
        })
      )
    ];

    // Add activity logs for managers and admins
    if (this.canViewAuditLogs()) {
      const orgShortName = this.organizationContext()?.orgShortName;
      if (orgShortName) {
        requests.push(
          this.activityLoggingService.getOrgActivity(orgShortName, 10).pipe(
            map((response) => response.data as ActivityLogEntry[]),
            catchError(error => {
              console.error('Error loading recent activity:', error);
              return of([]);
            })
          )
        );
      }
    }

    forkJoin(requests).subscribe({
      next: (results) => {
        this.organization.set(results[0]);
        if (results[1]) {
          this.recentActivity.set(results[1]);
        }
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error loading dashboard:', error);
        this.error.set('Failed to load dashboard data');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Refresh dashboard data
   */
  refreshDashboard(): void {
    this.loadDashboardData();
  }

  /**
   * Logout user
   */
  logout(): void {
    this.authService.logout().subscribe();
  }

  /**
   * Navigate to a card's route
   */
  navigateToCard(card: DashboardCard): void {
    if (card.route) {
      this.router.navigate([card.route]);
    }
  }

  /**
   * Navigate to a route
   */
  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  /**
   * Execute a quick action
   */
  executeAction(action: any): void {
    if (action.route) {
      this.router.navigate([action.route]);
    } else if (action.action) {
      action.action();
    }
  }

  /**
   * Check if user can view audit logs
   */
  canViewAuditLogs(): boolean {
    return this.authService.hasPermission('audit_logs', 'read');
  }

  /**
   * Get organization type label
   */
  getOrganizationTypeLabel(): string {
    const org = this.organization();
    if (!org) return '';

    const labels: Record<string, string> = {
      'valuation_company': 'Valuation Company',
      'system': 'System Organization',
      'enterprise': 'Enterprise'
    };

    return labels[org.type] || org.type;
  }

  /**
   * Get user roles label
   */
  getUserRolesLabel(): string {
    const roles = this.userRoles();
    const labels: Record<UserRole, string> = {
      'system_admin': 'System Administrator',
      'manager': 'Manager',
      'employee': 'Employee'
    };

    return roles.map(role => labels[role as UserRole]).join(', ');
  }

  /**
   * Format date for display
   */
  formatDate(date: Date | string): string {
    const d = new Date(date);
    return d.toLocaleString();
  }

  /**
   * Format activity timestamp for display
   */
  formatActivityDate(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / 60000);
    const diffInHours = Math.floor(diffInMs / 3600000);
    const diffInDays = Math.floor(diffInMs / 86400000);

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  }

  /**
   * Get icon for activity type
   */
  getActivityIcon(actionType: string): string {
    const icons: Record<string, string> = {
      'authentication': '🔐',
      'organization': '🏢',
      'user_management': '👤',
      'report': '📄',
      'template': '📋',
      'draft': '✏️',
      'settings': '⚙️',
      'analytics': '📊'
    };
    
    return icons[actionType] || '📋';
  }

  // Private helper methods

  private buildDashboardCards(): DashboardCard[] {
    const stats = this.dashboardStats();
    const org = this.organization();
    
    const cards: DashboardCard[] = [
      {
        title: 'Total Users',
        value: stats?.total_users || org?.total_users || 0,
        icon: '👥',
        color: '#3b82f6',
        route: this.authService.hasPermission('users', 'read') ? '/organization/users' : undefined,
        trend: stats?.users_trend ? {
          direction: stats.users_trend > 0 ? 'up' : stats.users_trend < 0 ? 'down' : 'neutral',
          percentage: Math.abs(stats.users_trend)
        } : undefined
      },
      {
        title: 'Total Reports',
        value: stats?.total_reports || org?.total_reports || 0,
        icon: '📊',
        color: '#10b981',
        route: '/organization/reports',
        trend: stats?.reports_trend ? {
          direction: stats.reports_trend > 0 ? 'up' : stats.reports_trend < 0 ? 'down' : 'neutral',
          percentage: Math.abs(stats.reports_trend)
        } : undefined
      },
      {
        title: 'Active Users',
        value: stats?.active_users || 0,
        icon: '🟢',
        color: '#f59e0b',
      },
      {
        title: 'This Month',
        value: stats?.reports_this_month || 0,
        icon: '📈',
        color: '#8b5cf6',
      }
    ];

    // Add system admin specific cards
    if (this.isSystemAdmin()) {
      cards.push({
        title: 'All Organizations',
        value: stats?.total_organizations || 0,
        icon: '🏢',
        color: '#ef4444',
        route: '/system/organizations'
      });
    }

    return cards;
  }

  private buildQuickActions(): any[] {
    const actions = [];

    // Common actions
    actions.push({
      label: 'Create Report',
      description: 'Start a new valuation report',
      icon: '📝',
      route: '/reports/create'
    });

    // Manager/Admin actions
    if (this.authService.hasPermission('users', 'create')) {
      actions.push({
        label: 'Add User',
        description: 'Invite a new team member',
        icon: '👤',
        route: '/organization/users/create'
      });
    }

    // System admin actions
    if (this.isSystemAdmin()) {
      actions.push({
        label: 'System Settings',
        description: 'Manage system configuration',
        icon: '⚙️',
        route: '/system/settings'
      });
    }

    return actions;
  }

  private buildNavigationItems(): NavigationItem[] {
    const items: NavigationItem[] = [
      {
        label: 'Reports Management',
        route: '/organization/reports',
        icon: '📊',
        disabled: false
      },
      {
        label: 'User Management',
        route: '/organization/users',
        icon: '👥',
        roles: ['manager', 'system_admin'],
        disabled: !this.authService.hasPermission('users', 'read')
      },
      {
        label: 'Audit Logs',
        route: '/organization/audit-logs',
        icon: '📋',
        roles: ['manager', 'system_admin'],
        disabled: !this.authService.hasPermission('audit_logs', 'read')
      },
      {
        label: 'Organization Settings',
        route: '/organization/settings',
        icon: '⚙️',
        roles: ['manager', 'system_admin'],
        disabled: !this.isManager()
      }
    ];

    // Add system admin navigation
    if (this.isSystemAdmin()) {
      items.push({
        label: 'System Administration',
        route: '/system',
        icon: '🛠️',
        roles: ['system_admin'],
        disabled: false
      });
    }

    return items;
  }
}