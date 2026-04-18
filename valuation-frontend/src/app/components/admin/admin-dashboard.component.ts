import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="admin-dashboard">
      <div class="dashboard-header">
        <h1>🏠 System Settings</h1>
        <div class="system-status">
          <span class="status-label">System Status:</span>
          <span [class]="'status-badge status-' + systemStatus()">
            {{ systemStatus() === 'healthy' ? '✅ HEALTHY' : 
               systemStatus() === 'degraded' ? '🟡 DEGRADED' : 
               '🔴 DOWN' }}
          </span>
        </div>
      </div>

      <nav class="tab-navigation">
        <button 
          *ngFor="let tab of tabs" 
          [class.active]="activeTab() === tab.id"
          (click)="selectTab(tab.id)"
          class="tab-button">
          {{ tab.icon }} {{ tab.label }}
        </button>
      </nav>

      <div class="tab-content">
        @switch (activeTab()) {
          @case ('overview') {
            <router-outlet></router-outlet>
          }
          @case ('organizations') {
            <router-outlet></router-outlet>
          }
          @case ('activity-logs') {
            <router-outlet></router-outlet>
          }
          @case ('server-logs') {
            <router-outlet></router-outlet>
          }
          @case ('health') {
            <router-outlet></router-outlet>
          }
        }
      </div>
    </div>
  `,
  styles: [`
    .admin-dashboard {
      padding: 24px;
      max-width: 1600px;
      margin: 0 auto;
    }

    .dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 32px;
      padding-bottom: 16px;
      border-bottom: 2px solid #e5e7eb;
    }

    .dashboard-header h1 {
      margin: 0;
      font-size: 32px;
      color: #111827;
    }

    .system-status {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .status-label {
      font-weight: 600;
      color: #6b7280;
    }

    .status-badge {
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 14px;
    }

    .status-healthy {
      background: #d1fae5;
      color: #065f46;
    }

    .status-degraded {
      background: #fef3c7;
      color: #92400e;
    }

    .status-down {
      background: #fee2e2;
      color: #991b1b;
    }

    .tab-navigation {
      display: flex;
      gap: 8px;
      margin-bottom: 32px;
      border-bottom: 2px solid #e5e7eb;
      overflow-x: auto;
    }

    .tab-button {
      padding: 12px 24px;
      border: none;
      background: none;
      font-size: 16px;
      font-weight: 600;
      color: #6b7280;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      transition: all 0.2s;
      white-space: nowrap;
    }

    .tab-button:hover {
      color: #111827;
      background: #f9fafb;
    }

    .tab-button.active {
      color: #3b82f6;
      border-bottom-color: #3b82f6;
    }

    .tab-content {
      min-height: 400px;
    }

    .coming-soon {
      text-align: center;
      padding: 64px 24px;
      background: #f9fafb;
      border-radius: 12px;
      border: 2px dashed #d1d5db;
    }

    .coming-soon h2 {
      margin: 0 0 16px 0;
      color: #6b7280;
    }

    .coming-soon p {
      margin: 0;
      color: #9ca3af;
      font-size: 18px;
    }
  `]
})
export class AdminDashboardComponent implements OnInit {
  activeTab = signal('overview');
  systemStatus = signal<'healthy' | 'degraded' | 'down'>('healthy');
  orgShortName = 'system-administration'; // Default to system-administration

  tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'organizations', label: 'Organizations', icon: '🏢' },
    { id: 'activity-logs', label: 'Activity Logs', icon: '🔍' },
    { id: 'server-logs', label: 'Server Logs', icon: '📝' },
    { id: 'health', label: 'Health Check', icon: '💚' }
  ];

  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    // Get organization from route params
    this.route.parent?.params.subscribe(params => {
      if (params['orgShortName']) {
        this.orgShortName = params['orgShortName'];
      }
    });

    // Load health status on init
    this.loadSystemStatus();
    
    // Set initial active tab based on current route
    const currentPath = this.router.url;
    if (currentPath.includes('/system-settings/overview') || currentPath.includes('/admin/overview')) {
      this.activeTab.set('overview');
    } else if (currentPath.includes('/system-settings/health') || currentPath.includes('/admin/health')) {
      this.activeTab.set('health');
    } else if (currentPath.includes('/system-settings/activity') || currentPath.includes('/admin/activity')) {
      this.activeTab.set('activity-logs');
    } else if (currentPath.includes('/system-settings/organizations') || currentPath.includes('/admin/organizations')) {
      this.activeTab.set('organizations');
    } else if (currentPath.includes('/system-settings/server-logs') || currentPath.includes('/admin/server-logs')) {
      this.activeTab.set('server-logs');
    }
  }

  selectTab(tabId: string) {
    this.activeTab.set(tabId);
    
    // Navigate to the appropriate route using organization context
    const basePath = `/org/${this.orgShortName}/system-settings`;
    
    if (tabId === 'overview') {
      this.router.navigate([basePath, 'overview']);
    } else if (tabId === 'health') {
      this.router.navigate([basePath, 'health']);
    } else if (tabId === 'activity-logs') {
      this.router.navigate([basePath, 'activity']);
    } else if (tabId === 'organizations') {
      this.router.navigate([basePath, 'organizations']);
    } else if (tabId === 'server-logs') {
      this.router.navigate([basePath, 'server-logs']);
    }
  }

  loadSystemStatus() {
    // TODO: Fetch actual system status from API
    this.systemStatus.set('healthy');
  }
}
