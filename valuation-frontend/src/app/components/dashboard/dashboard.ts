import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OrganizationService } from '../../services/organization.service';
import { Organization } from '../../models/organization.model';
import { AuthService } from '../../services/auth.service';

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
  
  // Statistics data - will be populated from services later
  companyStats = {
    pendingReports: 12,
    createdReports: 145,
    totalBanks: 8
  };
  
  // Mock collective stats for admin
  collectiveStats = {
    pendingReports: 47,
    createdReports: 523,
    totalBanks: 8,
    totalCompanies: 4
  };
  
  // Recent activity for last 5 business days
  recentActivity = [
    { date: '2025-10-24', type: 'created', count: 3, company: 'TechCorp Valuations' },
    { date: '2025-10-23', type: 'pending', count: 2, company: 'Global Properties' },
    { date: '2025-10-22', type: 'created', count: 5, company: 'TechCorp Valuations' },
    { date: '2025-10-21', type: 'pending', count: 1, company: 'Metro Appraisals' },
    { date: '2025-10-18', type: 'created', count: 4, company: 'City Valuations' }
  ];

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private orgService: OrganizationService,
    private authService: AuthService
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
    if (this.currentOrg) {
      console.log('Loading dashboard data for organization:', this.currentOrg.name);
      
      // TODO: Load organization-specific data:
      // - Pending reports for this organization
      // - Created reports for this organization  
      // - Available banks for this organization
      // - Recent activity for this organization
      
      // For now, keep mock data but should be replaced with real API calls
      this.companyStats = {
        pendingReports: 12,
        createdReports: 145,
        totalBanks: 8
      };
      
      console.log('Dashboard data loaded for:', this.currentOrg.name);
    } else {
      console.log('No organization loaded, cannot fetch dashboard data');
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
    return this.companyStats; // For now, return organization-specific stats
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
