import { Component, OnInit } from '@angular/core';
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
  selectedTab = 'all'; // all, draft, submitted
  showFilters = false;
  currentOrgShortName = '';
  
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
    private route: ActivatedRoute
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
    
    // Load banks for filtering
    this.dashboardService.getBanks().subscribe(banks => {
      this.banks = banks;
    });
    
    // Load reports
    await this.loadReports();
  }

  async loadReports() {
    this.loading = true;
    
    // Set tab-specific filters
    const tabFilters = this.getTabFilters();
    const combinedFilters = { ...this.filters, ...tabFilters };
    
    this.reportsService.getReports(combinedFilters).subscribe({
      next: (response) => {
        console.log('✅ Reports loaded:', response);
        
        if (response.success) {
          this.reports = response.data;
          this.currentPage = response.pagination.page;
          this.totalPages = response.pagination.total_pages;
          this.totalReports = response.pagination.total;
        }
        
        this.loading = false;
      },
      error: (error) => {
        console.error('❌ Error loading reports:', error);
        this.loading = false;
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

  // Tab management
  selectTab(tab: string) {
    this.selectedTab = tab;
    this.currentPage = 1;
    this.filters.page = 1;
    this.loadReports();
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