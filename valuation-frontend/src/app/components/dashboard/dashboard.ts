import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OrganizationService } from '../../services/organization.service';
import { Organization } from '../../models/organization.model';
import { AuthService } from '../../services/auth.service';
import { DashboardService, DashboardData, DashboardReport, DashboardBank, DashboardTemplate, DashboardActivity } from '../../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  
  // Current organization context
  currentOrg: Organization | null = null;
  currentOrgShortName = '';
  currentOrgDisplayName = ''; // Cached name for immediate display
  isSystemAdmin = false;
  isUserSystemAdmin = false; // Whether the USER has system admin privileges
  
  // Organization name cache for fast switching
  private orgNameCache: { [key: string]: string } = {
    'system-administration': 'System Administration',
    'sk-tindwal': 'Surinder Kumar Tindwal', 
    'yogesh-jangra': 'Yogesh Jangra'
  };
  
  // Organization switching for admins
  availableOrgs: Organization[] = [];
  selectedOrgForSwitch = '';
  showOrgSwitcher = false;
  
  // Dashboard data from API
  dashboardData: DashboardData | null = null;
  loading = false; // UI structure loads immediately
  dataLoading = true; // Individual data sections show loading state
  
  // Quick access to data sections
  get pendingReports(): DashboardReport[] { return this.dashboardData?.pendingReports || []; }
  get createdReports(): DashboardReport[] { return this.dashboardData?.createdReports || []; }
  get banks(): DashboardBank[] { return this.dashboardData?.banks || []; }
  get templates(): DashboardTemplate[] { return this.dashboardData?.templates || []; }
  get recentActivities(): DashboardActivity[] { return this.dashboardData?.recentActivities || []; }
  
  // Statistics data
  get stats() {
    return this.dashboardData?.stats || {
      total_reports: 0,
      pending_reports: 0,
      submitted_reports: 0,
      custom_templates: 0,
      recent_activities: 0,
      total_users: 0
    };
  }
  


  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private orgService: OrganizationService,
    private authService: AuthService,
    private dashboardService: DashboardService
  ) {}

  ngOnInit() {
    // Check if user has system admin privileges (independent of current org)
    this.checkUserSystemAdminStatus();
    
    // Get organization context from route
    this.route.params.subscribe(params => {
      const newOrgShortName = params['orgShortName'] || '';
      console.log('Route changed - Previous org:', this.currentOrgShortName, 'New org:', newOrgShortName);
      
      // IMMEDIATE UI UPDATE: Set cached name first for instant display
      this.currentOrgDisplayName = this.orgNameCache[newOrgShortName] || 'Loading...';
      
      // Reset organization data when route changes
      this.currentOrg = null;
      this.currentOrgShortName = newOrgShortName;
      
      console.log('Dashboard ngOnInit - orgShortName:', this.currentOrgShortName);
      console.log('Immediate display name set to:', this.currentOrgDisplayName);
      
      // Load full organization data in background
      this.loadOrganizationContext();
    });
  }

  checkUserSystemAdminStatus() {
    // Check if user has system admin privileges based on their authentication
    this.isUserSystemAdmin = this.authService.isSystemAdmin();
    console.log('User system admin status:', this.isUserSystemAdmin);
  }

  async loadOrganizationContext() {
    try {
      // Show UI immediately but keep data loading
      this.loading = false;
      this.dataLoading = true;
      console.log('loadOrganizationContext called with orgShortName:', this.currentOrgShortName);
      
      // Load current organization data
      if (this.currentOrgShortName) {
        // Use organization service to get all organizations
        this.orgService.getAllOrganizations(false, true).subscribe({
          next: (organizations: Organization[]) => {
            // Find current organization by org_short_name
            this.currentOrg = organizations.find(org => org.org_short_name === this.currentOrgShortName) || null;
            this.isSystemAdmin = this.currentOrgShortName === 'system-administration';
            
            // ALWAYS load available organizations for switching from orgNameCache
            // This ensures consistent org switching regardless of current org
            this.availableOrgs = [];
            
            // Build available orgs list from cache keys (all orgs user has access to)
            for (const orgShortName in this.orgNameCache) {
              if (orgShortName !== this.currentOrgShortName) {
                // Find full org data if available, otherwise create from cache
                const fullOrgData = organizations.find(org => org.org_short_name === orgShortName);
                
                if (fullOrgData) {
                  this.availableOrgs.push(fullOrgData);
                } else {
                  // Create org object from cache for switching (with required Organization fields)
                  this.availableOrgs.push({
                    _id: orgShortName,
                    org_short_name: orgShortName,
                    name: this.orgNameCache[orgShortName],
                    type: 'valuation_company' as const,
                    is_active: true,
                    created_at: new Date(),
                    updated_at: new Date()
                  } as Organization);
                }
              }
            }
            
            console.log('Available organizations for switching:', this.availableOrgs.map(org => ({
              short_name: org.org_short_name,
              display_name: org.name
            })));
            
            // Load dashboard data after organization is set
            this.loadDashboardData();
          },
          error: (error: any) => {
            console.error('Error loading organizations:', error);
            this.loadDashboardData();
          }
        });
      } else {
        console.error('No orgShortName provided in route');
        this.loadDashboardData();
      }
    } catch (error) {
      console.error('Error loading organization context:', error);
      this.loadDashboardData();
    }
  }



  loadDashboardData() {
    // Load organization-specific dashboard data
    if (this.currentOrg || this.currentOrgShortName) {
      const orgName = this.currentOrg?.name || this.currentOrgShortName;
      console.log('🔄 Loading dashboard data for organization:', orgName);
      
      // Keep UI visible but show data loading states
      this.dataLoading = true;
      
      // Fetch all dashboard data from API
      this.dashboardService.getDashboardData().subscribe({
        next: (data: DashboardData) => {
          console.log('✅ Dashboard data loaded:', data);
          this.dashboardData = data;
          this.dataLoading = false; // Hide loading skeletons
        },
        error: (error) => {
          console.error('❌ Error loading dashboard data:', error);
          this.dataLoading = false; // Hide loading skeletons even on error
          
          // Set empty data structure on error
          this.dashboardData = {
            pendingReports: [],
            createdReports: [],
            banks: [],
            templates: [],
            recentActivities: [],
            stats: {
              total_reports: 0,
              pending_reports: 0,
              submitted_reports: 0,
              custom_templates: 0,
              recent_activities: 0,
              total_users: 0
            }
          };
        }
      });
    } else {
      console.log('❌ No organization loaded, cannot fetch dashboard data');
      this.dataLoading = false;
    }
  }

  // Organization switching for admins
  toggleOrgSwitcher() {
    this.showOrgSwitcher = !this.showOrgSwitcher;
  }

  switchToOrganization() {
    if (this.selectedOrgForSwitch) {
      // Navigate to selected organization
      this.router.navigate(['/org', this.selectedOrgForSwitch, 'dashboard']);
      this.showOrgSwitcher = false;
    }
  }

  navigateToReports() {
    if (this.currentOrgShortName) {
      this.router.navigate(['/org', this.currentOrgShortName, 'reports']);
    } else {
      console.error('No organization context available for navigating to reports');
    }
  }

  navigateToBanks() {
    if (this.currentOrgShortName) {
      this.router.navigate(['/org', this.currentOrgShortName, 'banks']);
    } else {
      console.error('No organization context available for navigating to banks');
    }
  }

  navigateToTemplates() {
    if (this.currentOrgShortName) {
      this.router.navigate(['/org', this.currentOrgShortName, 'custom-templates']);
    } else {
      console.error('No organization context available for navigating to custom templates');
    }
  }

  createNewReport() {
    console.log('🚀 Create New Report clicked!', {
      currentOrgShortName: this.currentOrgShortName,
      currentOrg: this.currentOrg?.name
    });
    
    if (this.currentOrgShortName) {
      const targetRoute = ['/org', this.currentOrgShortName, 'reports', 'new'];
      console.log('📍 Navigating to:', targetRoute.join('/'));
      // Navigate to organization-specific new report page
      this.router.navigate(targetRoute);
    } else {
      console.error('❌ No organization context available for creating new report');
      // Fallback: try to get org from current route
      this.route.params.subscribe(params => {
        const orgShortName = params['orgShortName'];
        if (orgShortName) {
          console.log('🔄 Using orgShortName from route params:', orgShortName);
          this.router.navigate(['/org', orgShortName, 'reports', 'new']);
        }
      });
    }
  }

  getDisplayStats() {
    return this.stats; // Return real stats from API
  }

  formatDate(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'N/A';
    }
  }

  getActivityDescription(activity: DashboardActivity): string {
    const details = activity.details || {};
    
    switch (activity.action) {
      case 'report_created':
        return `Created report for ${details.property_address || 'property'}`;
      case 'report_updated':
        return `Updated report (${details.previous_status} → ${details.new_status})`;
      case 'report_submitted':
        return `Submitted report for ${details.property_address || 'property'}`;
      case 'report_deleted':
        return `Deleted report (${details.status})`;
      case 'template_created':
        return `Created custom template "${details.templateName}"`;
      case 'template_used':
        return `Applied template "${details.templateName}"`;
      default:
        return `${activity.action.replace('_', ' ')} ${activity.resource_type}`;
    }
  }

  getCurrentOrgName(): string {
    // Return cached name immediately for fast UI updates
    if (this.currentOrgDisplayName && this.currentOrgDisplayName !== 'Loading...') {
      return this.currentOrgDisplayName;
    }
    
    // Fallback to full organization data if available
    if (this.currentOrg) {
      const orgData = this.currentOrg as any;
      const name = orgData.name || orgData.org_display_name || orgData.org_name || 'Unknown Organization';
      this.currentOrgDisplayName = name; // Update cache
      return name;
    }
    
    return this.currentOrgDisplayName || 'Loading...';
  }



  getOrgDisplayName(org: any): string {
    return org.name || org.org_display_name || org.org_name || 'Unknown Organization';
  }

  getOrgSubscriptionPlan(org: any): string {
    return org.settings?.subscription_plan || 'Standard';
  }
}
