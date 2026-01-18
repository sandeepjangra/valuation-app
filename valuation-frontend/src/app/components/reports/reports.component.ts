/**
 * Reports Component
 * Handles report creation, viewing, and management for organization users
 */

import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { ReportsService, Report as ApiReport } from '../../services/reports.service';
import { User, OrganizationContext } from '../../models/organization.model';

// Using ApiReport from ReportsService

interface ReportFilters {
  type?: string;
  status?: string;
  createdBy?: string;
  dateRange?: 'week' | 'month' | 'quarter' | 'year';
  search?: string;
}

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `
    <div class="reports-container">
      <!-- Header Section -->
      <div class="reports-header">
        <div class="header-content">
          <div class="header-title">
            <h1>📊 Reports</h1>
            <p>Manage property valuations and market analysis reports</p>
          </div>
          
          <div class="header-actions">
            <button 
              class="btn btn-primary"
              (click)="openCreateReportModal()">
              <span class="btn-icon">+</span>
              Create New Report
            </button>
          </div>
        </div>

        <!-- Statistics Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-content">
              <div class="stat-value">{{ reportStats().total }}</div>
              <div class="stat-label">Total Reports</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-content">
              <div class="stat-value">{{ reportStats().inProgress }}</div>
              <div class="stat-label">In Progress</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
              <div class="stat-value">{{ reportStats().completed }}</div>
              <div class="stat-label">Completed</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-content">
              <div class="stat-value">{{ formatCurrency(reportStats().totalValue) }}</div>
              <div class="stat-label">Total Value</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters Section -->
      <div class="filters-section">
        <div class="filters-row">
          <div class="filter-group">
            <label>Search Reports</label>
            <div class="search-input">
              <input 
                type="text" 
                [(ngModel)]="searchTerm"
                (input)="onSearch()"
                placeholder="Search by title, address, or description..."
                class="form-input">
              <span class="search-icon">🔍</span>
            </div>
          </div>

          <div class="filter-group">
            <label>Report Type</label>
            <select 
              [(ngModel)]="selectedFilters.type"
              (change)="applyFilters()"
              class="form-select">
              <option value="">All Types</option>
              <option value="property_valuation">Property Valuation</option>
              <option value="market_analysis">Market Analysis</option>
              <option value="comparative_analysis">Comparative Analysis</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Status</label>
            <select 
              [(ngModel)]="selectedFilters.status"
              (change)="applyFilters()"
              class="form-select">
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="reviewed">Reviewed</option>
            </select>
          </div>

          <div class="filter-group" *ngIf="canManageReports()">
            <label>Created By</label>
            <select 
              [(ngModel)]="selectedFilters.createdBy"
              (change)="applyFilters()"
              class="form-select">
              <option value="">All Users</option>
              <option *ngFor="let user of organizationUsers()" [value]="user._id">
                {{ user.first_name }} {{ user.last_name }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>Date Range</label>
            <select 
              [(ngModel)]="selectedFilters.dateRange"
              (change)="applyFilters()"
              class="form-select">
              <option value="">All Time</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="quarter">Last Quarter</option>
              <option value="year">Last Year</option>
            </select>
          </div>
        </div>

        <div class="active-filters" *ngIf="hasActiveFilters()">
          <span class="filter-label">Active filters:</span>
          <span *ngIf="selectedFilters.type" class="filter-tag">
            Type: {{ getTypeLabel(selectedFilters.type) }}
            <button (click)="clearFilter('type')">×</button>
          </span>
          <span *ngIf="selectedFilters.status" class="filter-tag">
            Status: {{ getStatusLabel(selectedFilters.status) }}
            <button (click)="clearFilter('status')">×</button>
          </span>
          <span *ngIf="selectedFilters.createdBy" class="filter-tag">
            Created by: {{ getUserName(selectedFilters.createdBy) }}
            <button (click)="clearFilter('createdBy')">×</button>
          </span>
          <button class="clear-all-filters" (click)="clearAllFilters()">Clear all</button>
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="isLoading()" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading reports...</p>
      </div>

      <!-- Error State -->
      <div *ngIf="error()" class="error-container">
        <div class="error-message">
          <h3>⚠️ Error Loading Reports</h3>
          <p>{{ error() }}</p>
          <button class="btn btn-primary" (click)="loadReports()">
            Try Again
          </button>
        </div>
      </div>

      <!-- Reports Grid -->
      <div *ngIf="!isLoading() && !error()" class="reports-grid">
        <!-- Empty State -->
        <div *ngIf="filteredReports().length === 0" class="empty-state">
          <div class="empty-icon">📄</div>
          <h3>No reports found</h3>
          <p *ngIf="hasActiveFilters()">
            Try adjusting your filters or search terms.
          </p>
          <p *ngIf="!hasActiveFilters()">
            Create your first report to get started with property valuations.
          </p>
          <button 
            class="btn btn-primary"
            (click)="openCreateReportModal()">
            Create New Report
          </button>
        </div>

        <!-- Reports List -->
        <div *ngIf="filteredReports().length > 0" class="reports-list">
          <div *ngFor="let report of filteredReports(); trackBy: trackByReportId" 
               class="report-card"
               [class.draft]="report.status === 'draft'"
               [class.completed]="report.status === 'completed'">
            
            <div class="report-header">
              <div class="report-title-section">
                <h3 class="report-title">{{ report.reference_number }}</h3>
                <div class="report-meta">
                  <span class="report-type">{{ report.bankCode }}</span>
                  <span class="report-date">{{ report.created_at ? formatDate(report.created_at) : 'N/A' }}</span>
                </div>
              </div>
              
              <div class="report-status">
                <span [class]="'status-badge status-' + (report.status || 'draft')">
                  {{ report.status ? getStatusLabel(report.status) : 'Draft' }}
                </span>
              </div>
            </div>

            <div class="report-content">
              <p class="report-description">Report ID: {{ report.report_id }}</p>
              
              <div class="report-details">
                <div *ngIf="report.property_address" class="detail-item">
                  <span class="detail-label">📍 Property:</span>
                  <span class="detail-value">{{ report.property_address }}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">🏦 Bank:</span>
                  <span class="detail-value">{{ report.bankCode }}</span>
                </div>
                
                <div *ngIf="report.bank_branch_name" class="detail-item">
                  <span class="detail-label">🏢 Branch:</span>
                  <span class="detail-value">{{ report.bank_branch_name }}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">� Created by:</span>
                  <span class="detail-value">{{ report.created_by_email }}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">� Created:</span>
                  <span class="detail-value">{{ report.created_at ? formatDate(report.created_at) : 'N/A' }}</span>
                </div>
              </div>
            </div>

            <div class="report-actions">
              <button class="btn btn-outline" (click)="viewReport(report)">
                <span class="btn-icon">👁️</span>
                View
              </button>
              
              <button 
                *ngIf="canEditReport(report)"
                class="btn btn-outline" 
                (click)="editReport(report)">
                <span class="btn-icon">✏️</span>
                Edit
              </button>
              
              <!-- Delete functionality temporarily disabled
              <button 
                *ngIf="canDeleteReport(report)"
                class="btn btn-outline btn-danger" 
                (click)="deleteReport(report)">
                <span class="btn-icon">🗑️</span>
                Delete
              </button>
              -->
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div *ngIf="totalPages() > 1" class="pagination">
          <button 
            class="btn btn-outline"
            [disabled]="currentPage() === 1"
            (click)="goToPage(currentPage() - 1)">
            Previous
          </button>
          
          <span class="pagination-info">
            Page {{ currentPage() }} of {{ totalPages() }}
          </span>
          
          <button 
            class="btn btn-outline"
            [disabled]="currentPage() === totalPages()"
            (click)="goToPage(currentPage() + 1)">
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Create Report Modal -->
    <div *ngIf="showCreateModal()" class="modal-overlay" (click)="closeCreateModal()">
      <div class="modal-dialog" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h2>Create New Report</h2>
          <button class="modal-close" (click)="closeCreateModal()">×</button>
        </div>
        
        <form [formGroup]="createReportForm" (ngSubmit)="submitCreateReport()">
          <div class="modal-body">
            <div class="form-group">
              <label for="reportTitle">Report Title *</label>
              <input 
                id="reportTitle"
                type="text" 
                formControlName="title"
                placeholder="Enter report title"
                class="form-input">
            </div>

            <div class="form-group">
              <label for="reportType">Report Type *</label>
              <select id="reportType" formControlName="type" class="form-select">
                <option value="">Select type</option>
                <option value="property_valuation">Property Valuation</option>
                <option value="market_analysis">Market Analysis</option>
                <option value="comparative_analysis">Comparative Analysis</option>
              </select>
            </div>

            <div class="form-group">
              <label for="reportDescription">Description</label>
              <textarea 
                id="reportDescription"
                formControlName="description"
                placeholder="Enter report description"
                class="form-textarea"
                rows="3"></textarea>
            </div>

            <div class="form-group" *ngIf="createReportForm.get('type')?.value === 'property_valuation'">
              <label for="propertyAddress">Property Address</label>
              <input 
                id="propertyAddress"
                type="text" 
                formControlName="propertyAddress"
                placeholder="Enter property address"
                class="form-input">
            </div>
          </div>
          
          <div class="modal-footer">
            <button type="button" class="btn btn-outline" (click)="closeCreateModal()">
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              [disabled]="createReportForm.invalid || isCreating()">
              <span *ngIf="isCreating()" class="btn-spinner"></span>
              {{ isCreating() ? 'Creating...' : 'Create Report' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .reports-container {
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .reports-header {
      margin-bottom: 32px;
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .header-title h1 {
      margin: 0 0 8px 0;
      font-size: 2rem;
      font-weight: 700;
      color: #1f2937;
    }

    .header-title p {
      margin: 0;
      color: #6b7280;
      font-size: 1rem;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 32px;
    }

    .stat-card {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .stat-icon {
      font-size: 2rem;
      background: #f3f4f6;
      padding: 12px;
      border-radius: 50%;
    }

    .stat-value {
      font-size: 2rem;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 4px;
    }

    .stat-label {
      color: #6b7280;
      font-size: 0.875rem;
    }

    .filters-section {
      background: white;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .filters-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
    }

    .filter-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .filter-group label {
      font-weight: 600;
      color: #374151;
      font-size: 0.875rem;
    }

    .search-input {
      position: relative;
    }

    .search-input input {
      padding-right: 40px;
    }

    .search-icon {
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: #9ca3af;
    }

    .form-input, .form-select {
      padding: 10px 12px;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      font-size: 0.9rem;
    }

    .form-input:focus, .form-select:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .active-filters {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #e5e7eb;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .filter-label {
      font-weight: 600;
      color: #374151;
    }

    .filter-tag {
      background: #eff6ff;
      color: #1e40af;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.8rem;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .filter-tag button {
      background: none;
      border: none;
      color: #1e40af;
      cursor: pointer;
      font-weight: 600;
    }

    .clear-all-filters {
      background: #f3f4f6;
      border: none;
      padding: 4px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      color: #374151;
    }

    .loading-container, .error-container {
      text-align: center;
      padding: 60px 20px;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f4f6;
      border-top: 4px solid #3b82f6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .error-message {
      background: #fee2e2;
      border-radius: 12px;
      padding: 24px;
      max-width: 400px;
      margin: 0 auto;
    }

    .error-message h3 {
      margin: 0 0 8px 0;
      color: #dc2626;
    }

    .error-message p {
      margin: 0 0 16px 0;
      color: #dc2626;
    }

    .reports-grid {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
    }

    .empty-icon {
      font-size: 4rem;
      margin-bottom: 16px;
    }

    .empty-state h3 {
      margin: 0 0 12px 0;
      color: #1f2937;
    }

    .empty-state p {
      margin: 0 0 20px 0;
      color: #6b7280;
    }

    .reports-list {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .report-card {
      border: 2px solid #f3f4f6;
      border-radius: 12px;
      padding: 24px;
      transition: all 0.2s ease;
    }

    .report-card:hover {
      border-color: #e5e7eb;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .report-card.completed {
      border-color: #d1fae5;
      background: #f0fdf4;
    }

    .report-card.draft {
      border-color: #fef3c7;
      background: #fffbeb;
    }

    .report-header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 16px;
    }

    .report-title {
      margin: 0 0 8px 0;
      font-size: 1.25rem;
      font-weight: 600;
      color: #1f2937;
    }

    .report-meta {
      display: flex;
      gap: 16px;
      font-size: 0.875rem;
      color: #6b7280;
    }

    .report-type {
      font-weight: 500;
    }

    .status-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
    }

    .status-draft { background: #fef3c7; color: #92400e; }
    .status-in_progress { background: #dbeafe; color: #1e40af; }
    .status-completed { background: #d1fae5; color: #065f46; }
    .status-reviewed { background: #e0e7ff; color: #3730a3; }

    .report-description {
      margin: 0 0 16px 0;
      color: #4b5563;
      line-height: 1.5;
    }

    .report-details {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 20px;
    }

    .detail-item {
      display: flex;
      gap: 8px;
      font-size: 0.875rem;
    }

    .detail-label {
      font-weight: 500;
      color: #6b7280;
      min-width: 100px;
    }

    .detail-value {
      color: #1f2937;
    }

    .report-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .btn {
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.875rem;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-primary {
      background: #3b82f6;
      color: white;
      border: 2px solid #3b82f6;
    }

    .btn-primary:hover:not(:disabled) {
      background: #2563eb;
      border-color: #2563eb;
    }

    .btn-outline {
      background: transparent;
      color: #374151;
      border: 2px solid #e5e7eb;
    }

    .btn-outline:hover:not(:disabled) {
      border-color: #3b82f6;
      color: #3b82f6;
    }

    .btn-danger {
      color: #dc2626;
      border-color: #fecaca;
    }

    .btn-danger:hover:not(:disabled) {
      background: #fee2e2;
      border-color: #dc2626;
    }

    .btn-icon {
      font-size: 1rem;
    }

    .btn-spinner {
      width: 16px;
      height: 16px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 16px;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #e5e7eb;
    }

    .pagination-info {
      color: #6b7280;
      font-size: 0.875rem;
    }

    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }

    .modal-dialog {
      background: white;
      border-radius: 16px;
      max-width: 500px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24px 24px 0;
    }

    .modal-header h2 {
      margin: 0;
      color: #1f2937;
    }

    .modal-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      color: #9ca3af;
      cursor: pointer;
      padding: 4px;
    }

    .modal-body {
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .form-group label {
      font-weight: 600;
      color: #374151;
      font-size: 0.875rem;
    }

    .form-textarea {
      padding: 10px 12px;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      font-size: 0.9rem;
      font-family: inherit;
      resize: vertical;
    }

    .form-textarea:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .modal-footer {
      padding: 0 24px 24px;
      display: flex;
      gap: 12px;
      justify-content: end;
    }

    @media (max-width: 768px) {
      .reports-container {
        padding: 16px;
      }

      .header-content {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
      }

      .stats-grid {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      }

      .filters-row {
        grid-template-columns: 1fr;
      }

      .report-header {
        flex-direction: column;
        gap: 12px;
      }

      .report-actions {
        justify-content: start;
      }

      .pagination {
        flex-direction: column;
        gap: 12px;
      }

      .modal-dialog {
        margin: 10px;
        max-height: calc(100vh - 20px);
      }
    }
  `]
})
export class ReportsComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly organizationService = inject(OrganizationService);
  private readonly reportsService = inject(ReportsService);
  private readonly fb = inject(FormBuilder);

  // Component state
  readonly isLoading = signal<boolean>(true);
  readonly error = signal<string | null>(null);
  readonly isCreating = signal<boolean>(false);
  readonly showCreateModal = signal<boolean>(false);

  // Data
  readonly allReports = signal<ApiReport[]>([]);
  readonly organizationUsers = signal<User[]>([]);
  readonly currentPage = signal<number>(1);
  readonly itemsPerPage = 10;

  // Filters
  searchTerm = '';
  selectedFilters: ReportFilters = {};

  // Forms
  createReportForm: FormGroup;

  // Computed properties
  readonly orgContext = computed(() => this.authService.getOrganizationContext());
  
  readonly filteredReports = computed(() => {
    let reports = this.allReports();
    
    // Apply search filter
    if (this.searchTerm.trim()) {
      const search = this.searchTerm.toLowerCase();
      reports = reports.filter(report =>
        report.reference_number?.toLowerCase().includes(search) ||
        (report.property_address && report.property_address.toLowerCase().includes(search)) ||
        report.bankCode?.toLowerCase().includes(search)
      );
    }
    
    // Apply status filter
    if (this.selectedFilters.status) {
      reports = reports.filter(report => report.status === this.selectedFilters.status);
    }
    
    if (this.selectedFilters.createdBy) {
      reports = reports.filter(report => report.created_by_email === this.selectedFilters.createdBy);
    }
    
    // Apply date range filter
    if (this.selectedFilters.dateRange) {
      const now = new Date();
      const filterDate = new Date();
      
      switch (this.selectedFilters.dateRange) {
        case 'week':
          filterDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case 'quarter':
          filterDate.setMonth(now.getMonth() - 3);
          break;
        case 'year':
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
      }
      
      reports = reports.filter(report => report.created_at && new Date(report.created_at) >= filterDate);
    }
    
    // Apply pagination
    const startIndex = (this.currentPage() - 1) * this.itemsPerPage;
    return reports.slice(startIndex, startIndex + this.itemsPerPage);
  });

  readonly reportStats = computed(() => {
    const reports = this.allReports();
    return {
      total: reports.length,
      inProgress: reports.filter(r => r.status === 'in_progress').length,
      completed: reports.filter(r => r.status === 'completed').length,
      totalValue: 0 // Real reports don't have valuation in the basic data
    };
  });

  readonly totalPages = computed(() => 
    Math.ceil(this.allReports().length / this.itemsPerPage)
  );

  constructor() {
    this.createReportForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      type: ['', [Validators.required]],
      description: [''],
      propertyAddress: ['']
    });
  }

  ngOnInit(): void {
    this.loadReports();
    this.loadOrganizationUsers();
  }

  /**
   * Load reports from API
   */
  loadReports(): void {
    this.isLoading.set(true);
    this.error.set(null);

    console.log('🔄 Loading reports from API...');
    
    this.reportsService.getReports().subscribe({
      next: (response) => {
        console.log('✅ Reports loaded successfully:', response);
        console.log('📊 Number of reports found:', response.data?.reports?.length || 0);
        this.allReports.set(response.data?.reports || []);
        this.isLoading.set(false);
        this.error.set(null);
      },
      error: (error) => {
        console.error('❌ Failed to load reports:', error);
        this.error.set('Failed to load reports. Please try again.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Load organization users for filtering
   */
  loadOrganizationUsers(): void {
    if (!this.canManageReports()) return;

    // Simulate API call for now
    const mockUsers: User[] = [
      {
        _id: 'user-1',
        user_id: 'user-1',
        organization_id: 'demo_org_001',
        email: 'john.doe@demo.com',
        first_name: 'John',
        last_name: 'Doe',
        full_name: 'John Doe',
        role: 'employee',
        roles: ['employee'],
        status: 'active',
        is_active: true,
        created_at: new Date(),
        updated_at: new Date(),
        last_login: new Date(),
        permissions: {
          can_submit_reports: true,
          can_manage_users: false,
          is_manager: false,
          is_admin: false
        }
      },
      {
        _id: 'user-2',
        user_id: 'user-2',
        organization_id: 'demo_org_001',
        email: 'jane.smith@demo.com',
        first_name: 'Jane',
        last_name: 'Smith',
        full_name: 'Jane Smith',
        role: 'manager',
        roles: ['manager'],
        status: 'active',
        is_active: true,
        created_at: new Date(),
        updated_at: new Date(),
        last_login: new Date(),
        permissions: {
          can_submit_reports: true,
          can_manage_users: true,
          is_manager: true,
          is_admin: false
        }
      }
    ];

    this.organizationUsers.set(mockUsers);
  }

  /**
   * Permission checks
   */
  canManageReports(): boolean {
    return this.authService.hasPermission('reports', 'manage') || 
           this.authService.hasPermission('users', 'read');
  }

  canEditReport(report: ApiReport): boolean {
    const orgContext = this.orgContext();
    return orgContext?.userId === report.created_by_email || this.canManageReports();
  }

  canDeleteReport(report: ApiReport): boolean {
    return this.canEditReport(report);
  }

  /**
   * Filtering and search
   */
  onSearch(): void {
    this.currentPage.set(1);
  }

  applyFilters(): void {
    this.currentPage.set(1);
  }

  hasActiveFilters(): boolean {
    return !!(
      this.selectedFilters.type ||
      this.selectedFilters.status ||
      this.selectedFilters.createdBy ||
      this.selectedFilters.dateRange
    );
  }

  clearFilter(filterKey: keyof ReportFilters): void {
    delete this.selectedFilters[filterKey];
    this.applyFilters();
  }

  clearAllFilters(): void {
    this.selectedFilters = {};
    this.searchTerm = '';
    this.applyFilters();
  }

  /**
   * Pagination
   */
  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

  /**
   * Report actions
   */
  openCreateReportModal(): void {
    this.createReportForm.reset();
    this.showCreateModal.set(true);
  }

  closeCreateModal(): void {
    this.showCreateModal.set(false);
  }

  submitCreateReport(): void {
    if (this.createReportForm.invalid) return;
    this.isCreating.set(true);
    // TODO: Implement real API integration for creating reports
    console.log('Create report functionality needs API integration');
    this.isCreating.set(false);
    this.closeCreateModal();
  }

  viewReport(report: ApiReport): void {
    console.log('Viewing report:', report);
    // TODO: Navigate to report details view
  }

  editReport(report: ApiReport): void {
    console.log('Editing report:', report);
    // Open edit modal or navigate to edit view
  }

  // Temporarily commented out - needs API integration
  /*
  deleteReport(report: ApiReport): void {
    if (confirm(`Are you sure you want to delete "${report.reference_number}"?`)) {
      const reports = this.allReports().filter(r => r._id !== report._id);
      this.allReports.set(reports);
    }
  }
  */

  /**
   * Utility methods
   */
  trackByReportId(index: number, report: ApiReport): string {
    return report._id || report.id || `report-${index}`;
  }

  getTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      'property_valuation': 'Property Valuation',
      'market_analysis': 'Market Analysis',
      'comparative_analysis': 'Comparative Analysis'
    };
    return labels[type] || type;
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      'draft': 'Draft',
      'in_progress': 'In Progress',
      'completed': 'Completed',
      'reviewed': 'Reviewed'
    };
    return labels[status] || status;
  }

  getUserName(userId: string): string {
    const user = this.organizationUsers().find(u => u._id === userId);
    return user ? `${user.first_name} ${user.last_name}` : 'Unknown User';
  }

  formatDate(date: string | Date): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(dateObj);
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }
}