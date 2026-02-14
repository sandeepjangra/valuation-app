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
  filterPropertyType = '';
  filterReference = '';
  filterApplicantName = '';
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
            this.allReports = response.data.reports;
            console.log('📊 Total reports loaded:', this.allReports.length);
            
            // Apply current tab filter
            this.applyTabFilter();
            
            // Update pagination info
            this.totalReports = response.pagination?.total || 0;
            this.currentPage = response.pagination?.page || 1;
            this.totalPages = response.pagination?.total_pages || 1;
            
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
        
        // Debug: Log first report data for analysis
        if (response.data && response.data.reports && response.data.reports.length > 0) {
          const firstReport = response.data.reports[0];
          console.log('🔍 First report data:', {
            reference: firstReport.reference_number,
            bank_code: firstReport.bankCode,
            template_id: firstReport.templateId,
            report_data_keys: firstReport.report_data ? Object.keys(firstReport.report_data) : 'No report_data'
          });
        }
        console.log('📊 Data array length:', response.data?.reports?.length);
        console.log('📊 First report:', response.data?.reports?.[0]);
        console.log('📊 All report statuses:', response.data?.reports?.map((r: Report) => r.status));
        clearTimeout(timeoutId); // Clear timeout on success
        console.log('🎯 API SUCCESS - about to update loading state and data');
        console.log('🎯 Current selected tab:', this.selectedTab);
        console.log('🎯 Should this response be applied to current tab?');
        
        if (response.success) {
          this.reports = response.data?.reports || [];
          this.currentPage = response.data?.pagination?.page || 1;
          this.totalPages = response.data?.pagination?.totalPages || 1;
          this.totalReports = response.data?.pagination?.totalCount || 0;
          
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
    console.log('🔍 Applying enhanced filters');
    
    // If we have all reports loaded, do client-side filtering
    if (this.allReports.length > 0) {
      let filtered = [...this.allReports];
      
      // Apply status filter
      if (this.filterStatus) {
        filtered = filtered.filter(report => report.status === this.filterStatus);
      }
      
      // Apply bank filter
      if (this.filterBank) {
        filtered = filtered.filter(report => report.bankCode === this.filterBank);
      }
      
      // Apply property type filter
      if (this.filterPropertyType) {
        filtered = filtered.filter(report => 
          report.templateId === this.filterPropertyType ||
          (report.report_data && report.report_data.property_type === this.filterPropertyType)
        );
      }
      
      // Apply created by filter
      if (this.filterCreatedBy) {
        const searchTerm = this.filterCreatedBy.toLowerCase();
        filtered = filtered.filter(report => 
          report.created_by_email?.toLowerCase().includes(searchTerm)
        );
      }
      
      // Apply reference filter
      if (this.filterReference) {
        const searchTerm = this.filterReference.toLowerCase();
        filtered = filtered.filter(report => 
          (report.reference_number && report.reference_number.toLowerCase().includes(searchTerm)) ||
          report.report_id?.toLowerCase().includes(searchTerm)
        );
      }
      
      // Apply applicant name filter
      if (this.filterApplicantName) {
        const searchTerm = this.filterApplicantName.toLowerCase();
        filtered = filtered.filter(report => 
          this.getApplicantName(report).toLowerCase().includes(searchTerm)
        );
      }
      
      // Apply current tab filter
      switch (this.selectedTab) {
        case 'draft':
          filtered = filtered.filter(report => report.status === 'draft');
          break;
        case 'submitted':
          filtered = filtered.filter(report => report.status === 'submitted');
          break;
      }
      
      this.filteredReports = filtered;
      this.reports = filtered;
      
      console.log('🔍 Client-side filter results:', {
        original: this.allReports.length,
        filtered: filtered.length
      });
      
    } else {
      // Fallback to server-side filtering
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
  }

  clearFilters() {
    this.filterStatus = '';
    this.filterBank = '';
    this.filterCreatedBy = '';
    this.filterStartDate = '';
    this.filterEndDate = '';
    this.filterPropertyType = '';
    this.filterReference = '';
    this.filterApplicantName = '';
    this.searchText = '';
    
    this.filters = {
      page: 1,
      limit: this.reportsPerPage
    };
    
    this.applyFilters();
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
    console.log('📄 Viewing report - full object:', report);
    console.log('📋 Report ID fields:', {
      report_id: report.report_id,
      reportId: report.reportId,
      id: report.id,
      _id: (report as any)._id
    });
    
    const reportId = report.report_id || report.reportId || report.id || (report as any)._id;
    
    if (!reportId) {
      console.error('❌ No report ID found');
      console.error('Available keys:', Object.keys(report));
      alert('Cannot view report: Report ID is missing');
      return;
    }
    
    console.log('✅ Navigating to view with ID:', reportId);
    
    // Navigate to report view/edit page using the report ID route
    this.router.navigate(['/org', this.currentOrgShortName, 'reports', reportId], {
      queryParams: {
        mode: 'view'
      }
    });
  }

  editReport(report: Report, event: Event) {
    event.stopPropagation(); // Prevent triggering viewReport
    
    console.log('✏️ Editing report - full object:', report);
    console.log('📋 Report ID fields:', {
      report_id: report.report_id,
      reportId: report.reportId,
      id: report.id,
      _id: (report as any)._id
    });
    
    const reportId = report.report_id || report.reportId || report.id || (report as any)._id;
    
    if (!reportId) {
      console.error('❌ No report ID found');
      console.error('Available keys:', Object.keys(report));
      alert('Cannot edit report: Report ID is missing');
      return;
    }
    
    // Only allow editing of non-submitted reports
    if (report.status === 'submitted' || report.status === 'completed') {
      alert('Cannot edit submitted or completed reports');
      return;
    }
    
    console.log('✅ Navigating to edit with ID:', reportId);
    
    // Navigate to report edit page using the report ID route
    this.router.navigate(['/org', this.currentOrgShortName, 'reports', reportId], {
      queryParams: {
        mode: 'edit'
      }
    });
  }

  deleteReport(report: Report, event: Event) {
    event.stopPropagation(); // Prevent triggering viewReport
    
    const confirmMessage = `Are you sure you want to delete the report for "${report.property_address}"?`;
    if (confirm(confirmMessage)) {
      const reportId = report.report_id || report.reportId || report.id;
      if (!reportId) {
        alert('Cannot delete report: Invalid report ID');
        return;
      }
      console.log('🗑️ Deleting report:', reportId);
      
      this.reportsService.deleteReport(reportId).subscribe({
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

  // Helper method to get reference number with fallbacks
  getReferenceNumber(report: Report): string {
    // Check camelCase first (backend JSON serialization)
    const camelRef = (report as any).referenceNumber;
    if (camelRef && camelRef.trim()) {
      return camelRef;
    }
    
    // Check PascalCase
    const pascalRef = (report as any).ReferenceNumber;
    if (pascalRef && pascalRef.trim()) {
      return pascalRef;
    }
    
    // Check snake_case (database field)
    if (report.reference_number && report.reference_number.trim()) {
      return report.reference_number;
    }
    
    // Fallback to report ID
    return report.report_id || report.reportId || (report as any).ReportId || 'N/A';
  }
  
  // Helper method to get created by email with fallbacks
  getCreatedByEmail(report: Report): string {
    // Check camelCase first
    const camelEmail = (report as any).createdByEmail;
    if (camelEmail && camelEmail.trim()) {
      return camelEmail;
    }
    
    // Check PascalCase
    const pascalEmail = (report as any).CreatedByEmail;
    if (pascalEmail && pascalEmail.trim()) {
      return pascalEmail;
    }
    
    // Check snake_case
    if (report.created_by_email && report.created_by_email.trim()) {
      return report.created_by_email;
    }
    
    return 'N/A';
  }
  
  // Helper method to get created date with fallbacks
  getCreatedDate(report: Report): string {
    // Check camelCase first
    const camelDate = (report as any).createdAt;
    if (camelDate) {
      return this.formatDate(camelDate);
    }
    
    // Check PascalCase
    const pascalDate = (report as any).CreatedAt;
    if (pascalDate) {
      return this.formatDate(pascalDate);
    }
    
    // Check snake_case
    if (report.created_at) {
      return this.formatDate(report.created_at);
    }
    
    return 'N/A';
  }
  
  // Helper method to get updated date with fallbacks
  getUpdatedDate(report: Report): string {
    // Check camelCase first
    const camelDate = (report as any).updatedAt;
    if (camelDate) {
      return this.formatDate(camelDate);
    }
    
    // Check PascalCase
    const pascalDate = (report as any).UpdatedAt;
    if (pascalDate) {
      return this.formatDate(pascalDate);
    }
    
    // Check snake_case
    if (report.updated_at) {
      return this.formatDate(report.updated_at);
    }
    
    return 'N/A';
  }

  // New methods for enhanced table display
  getApplicantName(report: Report): string {
    console.log('🔍 getApplicantName called for report:', report.report_id || report.reportId);
    console.log('🔍 report.applicant_name =', report.applicant_name);
    console.log('🔍 report.applicantName =', (report as any).applicantName);
    console.log('🔍 report.ApplicantName =', (report as any).ApplicantName);
    console.log('🔍 report.report_data?.applicant_name =', report.report_data?.applicant_name);
    
    // PRIORITY 1: Check camelCase (backend JSON serialization)
    const camelName = (report as any).applicantName;
    if (camelName && camelName !== 'N/A') {
      console.log('✅ Using camelCase applicantName:', camelName);
      return camelName;
    }
    
    // PRIORITY 2: Check PascalCase (just in case)
    const pascalName = (report as any).ApplicantName;
    if (pascalName && pascalName !== 'N/A') {
      console.log('✅ Using PascalCase ApplicantName:', pascalName);
      return pascalName;
    }
    
    // PRIORITY 3: Check snake_case (database field)
    if (report.applicant_name && report.applicant_name !== 'N/A') {
      console.log('✅ Using snake_case applicant_name:', report.applicant_name);
      return report.applicant_name;
    }

    // PRIORITY 4: Fallback to searching in report_data
    // Try to extract applicant name from report data
    if (report.report_data) {
      const data = report.report_data;
      
      // Check all possible field name variations
      const possibleNameFields = [
        'applicant_name', 'borrower_name', 'customer_name', 'client_name',
        'name', 'full_name', 'person_name', 'owner_name',
        'first_name', 'lastName', 'firstName',
        'Applicant Name', 'Borrower Name', 'Customer Name', 'Name'
      ];
      
      for (const field of possibleNameFields) {
        const value = data[field];
        if (value && typeof value === 'string' && value.trim() && value !== 'N/A') {
          console.log(`✅ Found name in report_data["${field}"]: ${value}`);
          return value.trim();
        }
      }
      
      // Try to construct from first/last name
      const firstName = data.first_name || data.firstName || data['First Name'];
      const lastName = data.last_name || data.lastName || data['Last Name'];
      if (firstName && lastName) {
        return `${firstName.trim()} ${lastName.trim()}`;
      }
      
      // Search for any field containing "name"
      for (const [key, value] of Object.entries(data)) {
        if (key.toLowerCase().includes('name') && 
            typeof value === 'string' && 
            value.trim() && 
            value !== 'N/A' &&
            value.length > 2 &&
            value.length < 100) {
          console.log(`✅ Found potential name in "${key}": ${value}`);
          return value.trim();
        }
      }
    }
    
    return 'N/A';
  }

  getPostalAddress(report: Report): string {
    // Check camelCase property first (backend JSON serialization)
    const camelAddress = (report as any).propertyAddress;
    if (camelAddress && camelAddress !== 'Property Address TBD' && camelAddress !== 'N/A') {
      return camelAddress;
    }
    
    // Check PascalCase property
    const pascalAddress = (report as any).PropertyAddress;
    if (pascalAddress && pascalAddress !== 'Property Address TBD' && pascalAddress !== 'N/A') {
      return pascalAddress;
    }
    
    // Check snake_case property (database field)
    if (report.property_address && 
        report.property_address !== 'Property Address TBD' && 
        report.property_address !== 'N/A') {
      return report.property_address;
    }
    
    // Try to extract postal address from form data (single source of truth)
    if (report.form_data || (report as any).formData || report.report_data || (report as any).reportData) {
      // Prefer formData, fallback to reportData for backward compatibility
      const data = report.form_data || (report as any).formData || report.report_data || (report as any).reportData;
      
      // Check all possible address field names
      const possibleAddressFields = [
        'postal_address', 'property_address', 'address', 'full_address', 
        'complete_address', 'street_address', 'location',
        'Postal Address', 'Property Address', 'Address', 'Location'
      ];
      
      for (const field of possibleAddressFields) {
        let address = data[field];
        
        if (address && address.trim() && 
            address !== 'Property Address TBD' && 
            address !== 'N/A' && 
            address.length > 5) {
          
          // If it's an object, try to construct address string
          if (typeof address === 'object') {
            const parts = [
              address.street || address.address_line_1 || address.line1,
              address.city || address.address_line_2 || address.line2,
              address.state || address.district,
              address.pincode || address.postal_code || address.zip
            ].filter(part => part && part.trim());
            
            if (parts.length > 0) {
              return parts.join(', ');
            }
          } else {
            if (report.reference_number === 'CEV/RVO/299/0003/13122025') {
              console.log(`🏠 Found address in field "${field}": ${address}`);
            }
            return address.trim();
          }
        }
      }
      
      // Try to construct from individual address components
      const addressParts = [
        data.door_no || data.house_no || data.building_no,
        data.street || data.street_name,
        data.city_town_village || data.city || data.town || data.village,
        data.mandal_district || data.district,
        data.ward_taluka_tehsil || data.taluka || data.tehsil,
        data.state,
        data.pincode || data.pin_code
      ].filter(part => part && part.trim() && part !== 'N/A');
      
      if (addressParts.length > 1) {
        return addressParts.join(', ');
      }
      
      // Search for any field containing "address" or location terms
      for (const [key, value] of Object.entries(data)) {
        if ((key.toLowerCase().includes('address') || 
             key.toLowerCase().includes('location') ||
             key.toLowerCase().includes('street') ||
             key.toLowerCase().includes('postal')) && 
            typeof value === 'string' && 
            value.trim() && 
            value !== 'N/A' &&
            value !== 'Property Address TBD' &&
            value.length > 10) {
          if (report.reference_number === 'CEV/RVO/299/0003/13122025') {
            console.log(`🏠 Found potential address in "${key}": ${value}`);
          }
          return value.trim();
        }
      }
    }
    
    // Fallback to property_address from report metadata
    return report.property_address && report.property_address !== 'Property Address TBD' 
           ? report.property_address 
           : 'N/A';
  }

  getPropertyTypeDisplayName(report: Report): string {
    // Extract property type from template_id or report data
    if (report.report_data) {
      const data = report.report_data;
      
      // Check for property type in report data
      const possiblePropertyFields = [
        'property_type', 'propertyType', 'property_category', 'category',
        'Property Type', 'Property Category', 'type'
      ];
      
      for (const field of possiblePropertyFields) {
        const propertyType = data[field];
        
        if (propertyType && typeof propertyType === 'string' && propertyType.trim()) {
          // Check if it's a MongoDB ObjectId (24 character hex string)
          if (propertyType.length === 24 && /^[0-9a-fA-F]+$/.test(propertyType)) {
            // It's an ObjectId, skip it
            console.log('🔍 Skipping ObjectId in property type:', propertyType);
            continue;
          } else if (propertyType.length > 50) {
            // It's too long to be a property type, skip it
            console.log('🔍 Skipping long string in property type:', propertyType.substring(0, 50) + '...');
            continue;
          } else {
            return propertyType;
          }
        }
      }
    }
    
    // Map template_id to readable property type
    const templateMap: { [key: string]: string } = {
      'land-property': 'Land Property',
      'residential': 'Residential', 
      'commercial': 'Commercial',
      'industrial': 'Industrial',
      'apartment': 'Apartment'
    };
    
    const templateId = report.template_id || report.templateId;
    if (templateId) {
      const mappedType = templateMap[templateId];
      if (mappedType) {
        return mappedType;
      }
      // If template_id exists but not in map, use it as-is (cleaned up)
      return templateId.replace(/-/g, ' ')
                               .replace(/([a-z])([A-Z])/g, '$1 $2')
                               .replace(/^\w/, c => c.toUpperCase());
    }
    
    return 'N/A';
  }

}