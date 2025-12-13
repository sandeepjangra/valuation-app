import { Component, OnInit, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ReportsService, Report, ReportFilters } from '../../services/reports.service';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-reports-new',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reports-new.component.html',
  styleUrl: './reports-new.component.css'
})
export class ReportsNewComponent implements OnInit {
  
  // Data
  reports: Report[] = [];
  selectedReport: Report | null = null;
  banks: any[] = [];
  
  // State
  loading = true;
  requestInProgress = false;
  selectedTab = 'all'; // all, draft, submitted
  showFilters = false;
  currentOrgShortName = '';
  
  // Data storage
  allReports: Report[] = []; // Store all reports loaded initially
  filteredReports: Report[] = []; // Reports after applying current tab filter
  
  // Pagination
  currentPage = 1;
  totalPages = 1;
  totalReports = 0;
  reportsPerPage = 20;
  
  // Filters
  filters: ReportFilters = {
    page: 1,
    limit: 20
  };
  
  // Filter form values
  filterStatus = '';
  filterBank = '';
  filterCreatedBy = '';
  filterStartDate = '';
  filterEndDate = '';
  searchText = '';

  constructor(
    private reportsService: ReportsService,
    private dashboardService: DashboardService,
    private router: Router,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef,
    private zone: NgZone
  ) {}

  ngOnInit() {
    // Get organization context from route
    this.route.params.subscribe(params => {
      this.currentOrgShortName = params['orgShortName'] || '';
      console.log('Reports page - orgShortName:', this.currentOrgShortName);
      
      this.loadInitialData();
    });
  }

  async loadInitialData() {
    this.loading = true;
    console.log('🚀 Loading all initial data for org:', this.currentOrgShortName);
    
    // Load banks for filtering with timeout
    const banksTimeout = setTimeout(() => {
      console.warn('⚠️ Banks loading timeout');
      this.banks = []; // Use empty array if timeout
    }, 10000);
    
    this.dashboardService.getBanks().subscribe({
      next: (banks) => {
        clearTimeout(banksTimeout);
        this.banks = banks;
        console.log('✅ Banks loaded for reports filter:', banks.length, 'banks');
      },
      error: (error) => {
        clearTimeout(banksTimeout);
        console.error('❌ Error loading banks for reports filter:', error);
        this.banks = [];
      }
    });
    
    // Load ALL reports for this organization at once
    await this.loadAllReports();
  }

  // Load ALL reports for the organization once
  async loadAllReports(): Promise<void> {
    console.log('📊 Loading ALL reports for organization:', this.currentOrgShortName);
    
    if (this.requestInProgress) {
      console.log('🚫 Request already in progress, skipping');
      return;
    }

    this.requestInProgress = true;
    this.loading = true;

    // Load all reports without status filter
    const filters: ReportFilters = {
      page: 1,
      limit: 100, // Load more reports at once
    };

    console.log('📡 Making API call to load ALL reports with filters:', filters);

    return new Promise((resolve) => {
      this.reportsService.getReports(filters).subscribe({
        next: (response) => {
          console.log('✅ ALL Reports loaded successfully:', response);
          
          if (response.success && response.data) {
            // Store all reports
            this.allReports = response.data;
            console.log('📊 Total reports loaded:', this.allReports.length);
            
            // Apply current tab filter
            this.applyTabFilter();
            
            // Update pagination info
            this.totalReports = response.pagination.total;
            this.currentPage = response.pagination.page;
            this.totalPages = response.pagination.total_pages;
            
            console.log('📊 Pagination:', {
              total: this.totalReports,
              page: this.currentPage,
              totalPages: this.totalPages
            });
          } else {
            console.error('❌ Invalid response format:', response);
            this.allReports = [];
            this.filteredReports = [];
          }
          
          this.loading = false;
          this.requestInProgress = false;
          
          // Force change detection
          this.cdr.detectChanges();
          console.log('🔄 Change detection triggered after loading all reports');
          
          resolve();
        },
        error: (error) => {
          console.error('❌ Error loading reports:', error);
          this.allReports = [];
          this.filteredReports = [];
          this.loading = false;
          this.requestInProgress = false;
          this.cdr.detectChanges();
          resolve();
        }
      });
    });
  }

  // Apply tab filter to loaded reports (client-side filtering)
  applyTabFilter() {
    console.log('🔍 Applying tab filter:', this.selectedTab, 'to', this.allReports.length, 'reports');
    
    switch (this.selectedTab) {
      case 'draft':
        this.filteredReports = this.allReports.filter(report => report.status === 'draft');
        break;
      case 'submitted':
        this.filteredReports = this.allReports.filter(report => report.status === 'submitted');
        break;
      case 'all':
      default:
        this.filteredReports = [...this.allReports]; // Copy all reports
        break;
    }
    
    console.log('🔍 Filtered results:', {
      tab: this.selectedTab,
      total: this.allReports.length,
      filtered: this.filteredReports.length,
      statuses: this.filteredReports.map(r => r.status)
    });
    
    // Update reports property for template
    this.reports = this.filteredReports;
  }

  async loadReports() {
    // Cancel any previous request if one is in progress
    if (this.requestInProgress) {
      console.log('⚠️ Request already in progress, canceling previous and starting new');
    }

    console.log('🔄 STARTING loadReports - setting loading = true');
    this.loading = true;
    this.requestInProgress = true;
    console.log('🔄 Loading reports for org:', this.currentOrgShortName);
    console.log('🔄 Selected tab:', this.selectedTab);
    
    // Set a timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      console.warn('⚠️ Reports loading timeout - stopping loading state');
      this.loading = false;
      this.requestInProgress = false;
    }, 15000); // 15 second timeout
    
    // Set tab-specific filters
    const tabFilters = this.getTabFilters();
    const combinedFilters = { ...this.filters, ...tabFilters };
    console.log('🎛️ Tab filters:', tabFilters);
    console.log('🎛️ Combined filters:', combinedFilters);
    console.log('📡 About to call API with filters:', JSON.stringify(combinedFilters));
    
    this.reportsService.getReports(combinedFilters).subscribe({
      next: (response) => {
        console.log('✅ Reports loaded:', response);
        console.log('📊 Response data array:', response.data);
        console.log('📊 Data array length:', response.data?.length);
        console.log('📊 First report:', response.data?.[0]);
        console.log('📊 All report statuses:', response.data?.map(r => r.status));
        clearTimeout(timeoutId); // Clear timeout on success
        console.log('🎯 API SUCCESS - about to update loading state and data');
        console.log('🎯 Current selected tab:', this.selectedTab);
        console.log('🎯 Should this response be applied to current tab?');
        
        if (response.success) {
          this.reports = response.data;
          this.currentPage = response.pagination.page;
          this.totalPages = response.pagination.total_pages;
          this.totalReports = response.pagination.total;
          
          console.log('📋 Component reports array set:', this.reports);
          console.log('📋 Component reports length:', this.reports.length);
          console.log('📋 Loading state BEFORE setting to false:', this.loading);
        } else {
          // Show empty state on API error
          this.reports = [];
          this.currentPage = 1;
          this.totalPages = 1;
          this.totalReports = 0;
        }
        
        console.log('🎯 SETTING loading = false NOW');
        this.loading = false;
        this.requestInProgress = false;
        console.log('📋 Final loading state AFTER setting to false:', this.loading);
        
        // Force change detection to ensure UI updates
        this.cdr.detectChanges();
        console.log('🔄 Change detection triggered');
        

        

        console.log('📋 Reports array after load:', this.reports);
        console.log('📋 Should show reports now - loading is false');
        
        // Force change detection
        setTimeout(() => {
          console.log('📋 After timeout - Loading:', this.loading, 'Reports count:', this.reports.length);
        }, 100);
      },
      error: (error) => {
        console.error('❌ Error loading reports:', error);
        clearTimeout(timeoutId); // Clear timeout on error
        
        // Show empty state on error
        this.reports = [];
        this.currentPage = 1;
        this.totalPages = 1;
        this.totalReports = 0;
        
        this.loading = false;
        this.requestInProgress = false;
      }
    });
  }

  getTabFilters(): Partial<ReportFilters> {
    switch (this.selectedTab) {
      case 'draft':
        return { status: 'draft' };
      case 'submitted':
        return { status: 'submitted' };
      default:
        return {};
    }
  }

  // Tab management - Now uses client-side filtering!
  selectTab(tab: string) {
    console.log('🔄 Switching to tab:', tab, '(client-side filtering)');
    this.selectedTab = tab;
    this.currentPage = 1;
    
    // Apply filter to already loaded data
    this.applyTabFilter();
    
    // Force change detection to update UI immediately
    this.cdr.detectChanges();
    
    console.log('✅ Tab switched instantly - no API call needed!');
  }

  // Filter management
  toggleFilters() {
    this.showFilters = !this.showFilters;
  }

  applyFilters() {
    // Build filters object
    this.filters = {
      page: 1,
      limit: this.reportsPerPage,
      status: this.filterStatus || undefined,
      bank_code: this.filterBank || undefined,
      created_by: this.filterCreatedBy || undefined,
      start_date: this.filterStartDate || undefined,
      end_date: this.filterEndDate || undefined
    };
    
    this.currentPage = 1;
    this.loadReports();
  }

  clearFilters() {
    this.filterStatus = '';
    this.filterBank = '';
    this.filterCreatedBy = '';
    this.filterStartDate = '';
    this.filterEndDate = '';
    this.searchText = '';
    
    this.filters = {
      page: 1,
      limit: this.reportsPerPage
    };
    
    this.loadReports();
  }

  // Pagination
  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.filters.page = page;
      this.loadReports();
    }
  }

  // Report actions
  viewReport(report: Report) {
    console.log('📄 Viewing report:', report.report_id);
    // Navigate to report view/edit page using the report ID route
    this.router.navigate(['/org', this.currentOrgShortName, 'reports', report.report_id], {
      queryParams: {
        mode: 'view'
      }
    });
  }

  editReport(report: Report, event: Event) {
    event.stopPropagation(); // Prevent triggering viewReport
    console.log('✏️ Editing report:', report.report_id);
    
    // Only allow editing of non-submitted reports
    if (report.status === 'submitted' || report.status === 'completed') {
      alert('Cannot edit submitted or completed reports');
      return;
    }
    
    // Navigate to report edit page using the report ID route
    this.router.navigate(['/org', this.currentOrgShortName, 'reports', report.report_id], {
      queryParams: {
        mode: 'edit'
      }
    });
  }

  deleteReport(report: Report, event: Event) {
    event.stopPropagation(); // Prevent triggering viewReport
    
    const confirmMessage = `Are you sure you want to delete the report for "${report.property_address}"?`;
    if (confirm(confirmMessage)) {
      console.log('🗑️ Deleting report:', report.report_id);
      
      this.reportsService.deleteReport(report.report_id).subscribe({
        next: (success) => {
          if (success) {
            console.log('✅ Report deleted successfully');
            this.loadReports(); // Reload the list
          } else {
            alert('Failed to delete report');
          }
        },
        error: (error) => {
          console.error('❌ Error deleting report:', error);
          alert('Error deleting report. Please try again.');
        }
      });
    }
  }

  createNewReport() {
    console.log('➕ Creating new report');
    this.router.navigate(['/org', this.currentOrgShortName, 'reports', 'new']);
  }

  // Utility methods
  formatDate(dateString: string): string {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric',
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return 'N/A';
    }
  }

  getStatusDisplayName(status: string): string {
    return this.reportsService.getStatusDisplayName(status);
  }

  getStatusClass(status: string): string {
    return this.reportsService.getStatusClass(status);
  }

  canEdit(report: Report): boolean {
    return report.status === 'draft' || report.status === 'in_progress';
  }

  canDelete(report: Report): boolean {
    // Only allow deleting draft reports for now
    return report.status === 'draft';
  }
}