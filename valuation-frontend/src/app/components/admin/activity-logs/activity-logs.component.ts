import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

interface ActivityLog {
  _id: string;
  timestamp: string;
  action: string;
  user_id: string;
  user_email: string;
  organization_id: string;
  organization_name: string;
  status: 'success' | 'failed' | 'partial';
  details: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  error_message?: string;
}

interface ActivityLogsData {
  activities: ActivityLog[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface ActivityStats {
  total_activities: number;
  success_count: number;
  failed_count: number;
  success_rate: number;
  actions_breakdown: Record<string, number>;
  top_organizations: Array<{
    organization_id: string;
    organization_name: string;
    activity_count: number;
  }>;
}

@Component({
  selector: 'app-activity-logs',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './activity-logs.component.html',
  styleUrls: ['./activity-logs.component.css']
})
export class ActivityLogsComponent implements OnInit {
  // Signals for reactive state
  activitiesData = signal<ActivityLogsData | null>(null);
  stats = signal<ActivityStats | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);
  
  // Filter signals
  selectedOrganization = signal<string>('');
  selectedAction = signal<string>('');
  selectedStatus = signal<string>('');
  searchTerm = signal<string>('');
  startDate = signal<string>('');
  endDate = signal<string>('');
  
  // Pagination
  currentPage = signal(1);
  pageSize = signal(50);
  
  // Available filter options
  availableActions = [
    'LOGIN',
    'LOGOUT',
    'CREATE_REPORT',
    'UPDATE_REPORT',
    'DELETE_REPORT',
    'VIEW_REPORT',
    'DOWNLOAD_REPORT',
    'ADD_USER',
    'EDIT_USER',
    'DELETE_USER',
    'UPLOAD_FILE',
    'DELETE_FILE',
    'EDIT_ORG',
    'CREATE_ORG',
    'DELETE_ORG',
    'UPDATE_TEMPLATE',
    'UPLOAD_TEMPLATE'
  ];
  
  availableStatuses = ['success', 'failed', 'partial'];
  
  // Expanded row tracking
  expandedRows = new Set<string>();
  
  // Make Object available in template
  Object = Object;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadActivities();
    this.loadStats();
  }

  async loadActivities() {
    this.loading.set(true);
    this.error.set(null);
    
    try {
      // Build query parameters
      const params: any = {
        page: this.currentPage().toString(),
        page_size: this.pageSize().toString()
      };
      
      if (this.selectedOrganization()) {
        params.organization_id = this.selectedOrganization();
      }
      
      if (this.selectedAction()) {
        params.action = this.selectedAction();
      }
      
      if (this.selectedStatus()) {
        params.status = this.selectedStatus();
      }
      
      if (this.searchTerm()) {
        params.search = this.searchTerm();
      }
      
      if (this.startDate()) {
        params.start_date = new Date(this.startDate()).toISOString();
      }
      
      if (this.endDate()) {
        params.end_date = new Date(this.endDate()).toISOString();
      }
      
      const url = `${environment.apiUrl}/admin/dashboard/activity-logs`;
      
      this.http.get<{ success: boolean; data: ActivityLogsData }>(url, { params }).subscribe({
        next: (response) => {
          this.activitiesData.set(response.data);
          this.loading.set(false);
        },
        error: (err) => {
          console.error('Error loading activities:', err);
          this.error.set(err.error?.error || 'Failed to load activity logs');
          this.loading.set(false);
        }
      });
    } catch (err: any) {
      this.error.set(err.message || 'Failed to load activity logs');
      this.loading.set(false);
    }
  }

  async loadStats() {
    try {
      const params: any = {};
      
      if (this.selectedOrganization()) {
        params.organization_id = this.selectedOrganization();
      }
      
      if (this.startDate()) {
        params.start_date = new Date(this.startDate()).toISOString();
      }
      
      if (this.endDate()) {
        params.end_date = new Date(this.endDate()).toISOString();
      }
      
      const url = `${environment.apiUrl}/admin/dashboard/activity-stats`;
      
      this.http.get<{ success: boolean; data: ActivityStats }>(url, { params }).subscribe({
        next: (response) => {
          this.stats.set(response.data);
        },
        error: (err) => {
          console.error('Error loading stats:', err);
        }
      });
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  }

  refresh() {
    this.loadActivities();
    this.loadStats();
  }

  applyFilters() {
    this.currentPage.set(1); // Reset to first page
    this.loadActivities();
    this.loadStats();
  }

  clearFilters() {
    this.selectedOrganization.set('');
    this.selectedAction.set('');
    this.selectedStatus.set('');
    this.searchTerm.set('');
    this.startDate.set('');
    this.endDate.set('');
    this.currentPage.set(1);
    this.loadActivities();
    this.loadStats();
  }

  goToPage(page: number) {
    this.currentPage.set(page);
    this.loadActivities();
  }

  nextPage() {
    const data = this.activitiesData();
    if (data && this.currentPage() < data.total_pages) {
      this.currentPage.update(p => p + 1);
      this.loadActivities();
    }
  }

  previousPage() {
    if (this.currentPage() > 1) {
      this.currentPage.update(p => p - 1);
      this.loadActivities();
    }
  }

  toggleRow(activityId: string) {
    if (this.expandedRows.has(activityId)) {
      this.expandedRows.delete(activityId);
    } else {
      this.expandedRows.add(activityId);
    }
  }

  isRowExpanded(activityId: string): boolean {
    return this.expandedRows.has(activityId);
  }

  getRelativeTime(timestamp: string): string {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffMs = now.getTime() - activityTime.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSeconds < 60) {
      return `${diffSeconds} seconds ago`;
    } else if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    }
  }

  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString();
  }

  getActionColor(action: string): string {
    if (action.includes('DELETE')) return '#ef4444';
    if (action.includes('CREATE') || action.includes('ADD')) return '#10b981';
    if (action.includes('UPDATE') || action.includes('EDIT')) return '#f59e0b';
    if (action.includes('LOGIN')) return '#3b82f6';
    if (action.includes('LOGOUT')) return '#6b7280';
    return '#8b5cf6';
  }

  getStatusBadgeClass(status: string): string {
    switch (status) {
      case 'success':
        return 'status-success';
      case 'failed':
        return 'status-failed';
      case 'partial':
        return 'status-partial';
      default:
        return '';
    }
  }

  getPaginationRange(): number[] {
    const data = this.activitiesData();
    if (!data) return [];
    
    const totalPages = data.total_pages;
    const current = this.currentPage();
    const range: number[] = [];
    
    // Show max 5 page numbers
    let start = Math.max(1, current - 2);
    let end = Math.min(totalPages, current + 2);
    
    // Adjust if at start or end
    if (current <= 3) {
      end = Math.min(5, totalPages);
    }
    if (current >= totalPages - 2) {
      start = Math.max(1, totalPages - 4);
    }
    
    for (let i = start; i <= end; i++) {
      range.push(i);
    }
    
    return range;
  }

  getStatsActionEntries(): Array<[string, number]> {
    const stats = this.stats();
    if (!stats) return [];
    return Object.entries(stats.actions_breakdown).sort((a, b) => b[1] - a[1]);
  }
}
