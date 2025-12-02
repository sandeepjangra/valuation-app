import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-org-header',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './org-header.component.html',
  styleUrls: ['./org-header.component.css']
})
export class OrgHeaderComponent implements OnInit {
  currentOrgShortName = '';
  currentOrgName = '';
  isSystemAdmin = false;
  availableOrgs: any[] = [];
  selectedOrgForSwitch = '';
  showOrgDropdown = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    // Listen to route changes to update organization context
    this.route.params.subscribe(params => {
      this.currentOrgShortName = params['orgShortName'] || '';
      this.loadOrganizationInfo();
    });
  }

  async loadOrganizationInfo() {
    try {
      if (this.currentOrgShortName) {
        // Load current organization info
        const response = await fetch(`http://localhost:8000/api/organizations/${this.currentOrgShortName}`);
        if (response.ok) {
          const org = await response.json();
          this.currentOrgName = org.org_display_name || org.org_name;
          this.isSystemAdmin = org.is_system_org || false;

          // Always load available organizations for switching (admins can switch between orgs)
          await this.loadAvailableOrganizations();
        }
      }
    } catch (error) {
      console.error('Error loading organization info:', error);
    }
  }

  async loadAvailableOrganizations() {
    try {
      // Use our organization name cache for consistent switching
      const orgNameCache: { [key: string]: string } = {
        'system-administration': 'System Administration',
        'sk-tindwal': 'Surinder Kumar Tindwal',
        'yogesh-jangra': 'Yogesh Jangra'
      };

      // Always load from cache for consistent experience
      this.availableOrgs = [];
      
      for (const orgShortName in orgNameCache) {
        if (orgShortName !== this.currentOrgShortName) {
          // Try to get full data from API
          try {
            const response = await fetch(`http://localhost:8000/api/organizations/${orgShortName}`);
            if (response.ok) {
              const orgData = await response.json();
              this.availableOrgs.push({
                org_short_name: orgShortName,
                org_display_name: orgNameCache[orgShortName],
                name: orgNameCache[orgShortName],
                settings: orgData.settings || { subscription_plan: 'Standard' }
              });
            } else {
              // Fallback to cache data
              this.availableOrgs.push({
                org_short_name: orgShortName,
                org_display_name: orgNameCache[orgShortName],
                name: orgNameCache[orgShortName],
                settings: { subscription_plan: 'Standard' }
              });
            }
          } catch {
            // Fallback to cache data
            this.availableOrgs.push({
              org_short_name: orgShortName,
              org_display_name: orgNameCache[orgShortName],
              name: orgNameCache[orgShortName],
              settings: { subscription_plan: 'Standard' }
            });
          }
        }
      }

      console.log('Available organizations loaded:', this.availableOrgs.map(org => ({
        short_name: org.org_short_name,
        display_name: org.org_display_name
      })));
    } catch (error) {
      console.error('Error loading organizations:', error);
    }
  }

  toggleOrgDropdown() {
    this.showOrgDropdown = !this.showOrgDropdown;
  }

  selectOrgForSwitch(orgShortName: string) {
    this.selectedOrgForSwitch = orgShortName;
  }

  switchToOrganization() {
    if (this.selectedOrgForSwitch) {
      this.router.navigate(['/org', this.selectedOrgForSwitch, 'dashboard']);
      this.showOrgDropdown = false;
    }
  }

  navigateToAdminDashboard() {
    this.router.navigate(['/org', 'system-administration', 'dashboard']);
  }
}