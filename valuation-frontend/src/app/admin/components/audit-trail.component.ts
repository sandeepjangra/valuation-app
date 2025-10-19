import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, AuditLogEntry } from '../services/admin.service';

@Component({
  selector: 'app-audit-trail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="audit-trail">
      <header class="audit-header">
        <h2>📋 Audit Trail</h2>
        <div class="header-filters">
          <select [(ngModel)]="selectedDatabase" (change)="onFilterChange()" class="filter-select">
            <option value="">All Databases</option>
            <option value="admin">Admin Database</option>
            <option value="main">Main Database</option>
            <option value="reports">Reports Database</option>
          </select>
          
          <select [(ngModel)]="selectedCollection" (change)="onFilterChange()" class="filter-select">
            <option value="">All Collections</option>
            <option *ngFor="let collection of availableCollections" [value]="collection">
              {{ collection }}
            </option>
          </select>
          
          <button class="btn btn-refresh" (click)="refreshLogs()">
            🔄 Refresh
          </button>
        </div>
      </header>

      <div class="audit-stats" *ngIf="totalLogs > 0">
        <div class="stat-card">
          <span class="stat-number">{{ totalLogs }}</span>
          <span class="stat-label">Total Changes</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">{{ getOperationCount('CREATE') }}</span>
          <span class="stat-label">Created</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">{{ getOperationCount('UPDATE') }}</span>
          <span class="stat-label">Updated</span>
        </div>
        <div class="stat-card">
          <span class="stat-number">{{ getOperationCount('DELETE') }}</span>
          <span class="stat-label">Deleted</span>
        </div>
      </div>

      <div class="audit-logs" *ngIf="!loading">
        <div *ngFor="let log of auditLogs" class="audit-log-entry" [ngClass]="'op-' + log.operation.toLowerCase()">
          <div class="log-header">
            <div class="log-operation">
              <span class="operation-badge" [ngClass]="'op-' + log.operation.toLowerCase()">
                {{ getOperationIcon(log.operation) }} {{ log.operation }}
              </span>
              <span class="log-target">
                {{ log.database }}.{{ log.collection }}
              </span>
            </div>
            <div class="log-meta">
              <span class="log-time">{{ formatDate(log.timestamp) }}</span>
              <span class="log-user">by {{ log.userName || log.userId }}</span>
            </div>
          </div>

          <div class="log-details">
            <div class="document-id">
              <strong>Document ID:</strong>
              <code>{{ log.documentId }}</code>
            </div>

            <div class="changes-section" *ngIf="log.changes && hasChanges(log.changes)">
              <h5>Changes Made:</h5>
              <div class="changes-grid">
                <div *ngFor="let change of getChangesList(log.changes)" class="change-item">
                  <span class="field-name">{{ change.field }}:</span>
                  <div class="change-values">
                    <span class="old-value" *ngIf="change.oldValue !== undefined">
                      <em>was:</em> {{ formatValue(change.oldValue) }}
                    </span>
                    <span class="new-value">
                      <em>now:</em> {{ formatValue(change.newValue) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="previous-version" *ngIf="log.previousVersion && expandedLogs.has(log._id)">
              <h5>Previous Version:</h5>
              <pre class="json-preview">{{ formatJson(log.previousVersion) }}</pre>
            </div>
          </div>

          <div class="log-actions">
            <button 
              class="btn-expand" 
              (click)="toggleExpand(log._id)"
              *ngIf="log.previousVersion"
            >
              {{ expandedLogs.has(log._id) ? '▲ Hide Previous Version' : '▼ Show Previous Version' }}
            </button>
          </div>
        </div>

        <div class="pagination" *ngIf="totalPages > 1">
          <button 
            class="btn btn-page" 
            [disabled]="currentPage <= 1"
            (click)="goToPage(currentPage - 1)"
          >
            ← Previous
          </button>
          
          <span class="page-info">
            Page {{ currentPage }} of {{ totalPages }} ({{ totalLogs }} total logs)
          </span>
          
          <button 
            class="btn btn-page"
            [disabled]="currentPage >= totalPages"
            (click)="goToPage(currentPage + 1)"
          >
            Next →
          </button>
        </div>
      </div>

      <div class="loading" *ngIf="loading">
        Loading audit logs...
      </div>

      <div class="no-logs" *ngIf="!loading && auditLogs.length === 0">
        <h3>No audit logs found</h3>
        <p>No changes have been tracked yet, or your current filters don't match any logs.</p>
      </div>
    </div>
  `,
  styles: [`
    .audit-trail {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .audit-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 1rem;
      border-bottom: 2px solid #9b59b6;
    }

    .audit-header h2 {
      margin: 0;
      color: #2c3e50;
    }

    .header-filters {
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }

    .filter-select {
      padding: 0.5rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      font-size: 0.85rem;
    }

    .audit-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .stat-card {
      background: #ecf0f1;
      padding: 1rem;
      border-radius: 6px;
      text-align: center;
    }

    .stat-number {
      display: block;
      font-size: 1.5rem;
      font-weight: bold;
      color: #2c3e50;
    }

    .stat-label {
      display: block;
      font-size: 0.8rem;
      color: #7f8c8d;
      margin-top: 0.25rem;
    }

    .audit-logs {
      flex: 1;
      overflow-y: auto;
    }

    .audit-log-entry {
      background: white;
      border: 1px solid #ecf0f1;
      border-radius: 6px;
      margin-bottom: 1rem;
      padding: 1rem;
      transition: all 0.3s;
    }

    .audit-log-entry:hover {
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .audit-log-entry.op-create {
      border-left: 4px solid #27ae60;
    }

    .audit-log-entry.op-update {
      border-left: 4px solid #3498db;
    }

    .audit-log-entry.op-delete {
      border-left: 4px solid #e74c3c;
    }

    .log-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.75rem;
    }

    .log-operation {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .operation-badge {
      display: inline-block;
      padding: 0.25rem 0.5rem;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: bold;
      text-transform: uppercase;
    }

    .operation-badge.op-create {
      background: #d5f4e6;
      color: #27ae60;
    }

    .operation-badge.op-update {
      background: #d6eaf8;
      color: #3498db;
    }

    .operation-badge.op-delete {
      background: #fdeaea;
      color: #e74c3c;
    }

    .log-target {
      font-family: 'Courier New', monospace;
      font-size: 0.85rem;
      color: #7f8c8d;
    }

    .log-meta {
      text-align: right;
      font-size: 0.8rem;
      color: #95a5a6;
    }

    .log-time {
      display: block;
    }

    .log-user {
      display: block;
      margin-top: 0.25rem;
    }

    .log-details {
      margin-bottom: 0.75rem;
    }

    .document-id {
      margin-bottom: 0.75rem;
      font-size: 0.85rem;
    }

    .document-id code {
      background: #ecf0f1;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
      font-size: 0.8rem;
    }

    .changes-section h5 {
      margin: 0 0 0.5rem 0;
      color: #2c3e50;
      font-size: 0.9rem;
    }

    .changes-grid {
      display: grid;
      gap: 0.5rem;
    }

    .change-item {
      background: #f8f9fa;
      padding: 0.5rem;
      border-radius: 4px;
      border-left: 3px solid #3498db;
    }

    .field-name {
      font-weight: bold;
      color: #2c3e50;
      font-size: 0.85rem;
    }

    .change-values {
      margin-top: 0.25rem;
      font-size: 0.8rem;
    }

    .old-value,
    .new-value {
      display: block;
      margin-top: 0.2rem;
    }

    .old-value {
      color: #e74c3c;
    }

    .old-value em {
      color: #95a5a6;
    }

    .new-value {
      color: #27ae60;
    }

    .new-value em {
      color: #95a5a6;
    }

    .previous-version h5 {
      margin: 1rem 0 0.5rem 0;
      color: #2c3e50;
      font-size: 0.9rem;
    }

    .json-preview {
      background: #f8f9fa;
      padding: 0.75rem;
      border-radius: 4px;
      border: 1px solid #ecf0f1;
      font-size: 0.75rem;
      max-height: 200px;
      overflow-y: auto;
      color: #2c3e50;
    }

    .log-actions {
      text-align: center;
      padding-top: 0.5rem;
      border-top: 1px solid #ecf0f1;
    }

    .btn-expand {
      background: none;
      border: none;
      color: #3498db;
      cursor: pointer;
      font-size: 0.8rem;
      padding: 0.25rem 0.5rem;
      border-radius: 3px;
      transition: background-color 0.3s;
    }

    .btn-expand:hover {
      background: #ecf0f1;
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 1rem;
      padding: 1rem;
      border-top: 1px solid #ecf0f1;
      margin-top: 1rem;
    }

    .page-info {
      color: #7f8c8d;
      font-size: 0.9rem;
    }

    .btn {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.85rem;
      transition: all 0.3s;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-refresh {
      background: #3498db;
      color: white;
    }

    .btn-refresh:hover {
      background: #2980b9;
    }

    .btn-page {
      background: #ecf0f1;
      color: #2c3e50;
    }

    .btn-page:hover:not(:disabled) {
      background: #d5dbdb;
    }

    .loading,
    .no-logs {
      text-align: center;
      color: #7f8c8d;
      font-style: italic;
      margin-top: 2rem;
    }

    .no-logs h3 {
      color: #95a5a6;
    }
  `]
})
export class AuditTrailComponent implements OnInit {
  auditLogs: AuditLogEntry[] = [];
  currentPage = 1;
  totalPages = 1;
  totalLogs = 0;
  loading = true;
  
  selectedDatabase = '';
  selectedCollection = '';
  availableCollections = ['banks', 'common_form_fields', 'valuation_reports'];
  
  expandedLogs = new Set<string>();

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.loadAuditLogs();
  }

  private loadAuditLogs() {
    this.loading = true;
    
    this.adminService.getAuditLogs(
      this.selectedDatabase || undefined,
      this.selectedCollection || undefined,
      this.currentPage
    ).subscribe({
      next: (response) => {
        this.auditLogs = response.logs;
        this.totalLogs = response.total;
        this.totalPages = Math.ceil(response.total / 50);
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading audit logs:', error);
        this.loading = false;
      }
    });
  }

  onFilterChange() {
    this.currentPage = 1;
    this.loadAuditLogs();
  }

  refreshLogs() {
    this.currentPage = 1;
    this.loadAuditLogs();
  }

  goToPage(page: number) {
    this.currentPage = page;
    this.loadAuditLogs();
  }

  toggleExpand(logId: string) {
    if (this.expandedLogs.has(logId)) {
      this.expandedLogs.delete(logId);
    } else {
      this.expandedLogs.add(logId);
    }
  }

  getOperationIcon(operation: string): string {
    switch (operation) {
      case 'CREATE': return '➕';
      case 'UPDATE': return '✏️';
      case 'DELETE': return '🗑️';
      default: return '📝';
    }
  }

  getOperationCount(operation: string): number {
    return this.auditLogs.filter(log => log.operation === operation).length;
  }

  hasChanges(changes: any): boolean {
    return changes && Object.keys(changes).length > 0;
  }

  getChangesList(changes: any): any[] {
    if (!changes) return [];
    
    return Object.entries(changes).map(([field, change]: [string, any]) => ({
      field,
      oldValue: change.from,
      newValue: change.to
    }));
  }

  formatValue(value: any): string {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    if (typeof value === 'string' && value.length > 100) {
      return value.substring(0, 100) + '...';
    }
    return String(value);
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString();
  }

  formatJson(obj: any): string {
    return JSON.stringify(obj, null, 2);
  }
}