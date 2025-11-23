import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

interface ServerLog {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
  raw: string;
}

interface ServerLogsData {
  logs: ServerLog[];
  total: number;
  error_count: number;
  warning_count: number;
  log_file: string;
  showing: number;
}

@Component({
  selector: 'app-server-logs',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="server-logs-container">
      <div class="header">
        <div>
          <h1>📝 Server Logs</h1>
          <p class="subtitle">Monitor server errors and warnings</p>
        </div>
        <button class="btn btn-refresh" (click)="refresh()">
          🔄 Refresh
        </button>
      </div>

      <!-- Filters -->
      <div class="filters-card">
        <div class="filter-row">
          <div class="filter-group">
            <label for="logType">Log Source:</label>
            <select id="logType" [(ngModel)]="logType" (change)="applyFilters()" class="filter-select">
              <option value="backend">Backend</option>
              <option value="frontend">Frontend</option>
              <option value="api_server">API Server</option>
              <option value="backend_nohup">Backend (Nohup)</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="level">Log Level:</label>
            <select id="level" [(ngModel)]="selectedLevel" (change)="applyFilters()" class="filter-select">
              <option value="">All Errors & Warnings</option>
              <option value="ERROR">ERROR Only</option>
              <option value="WARNING">WARNING Only</option>
              <option value="CRITICAL">CRITICAL Only</option>
              <option value="INFO">INFO</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="limit">Show:</label>
            <select id="limit" [(ngModel)]="limit" (change)="applyFilters()" class="filter-select">
              <option [value]="50">50 entries</option>
              <option [value]="100">100 entries</option>
              <option [value]="200">200 entries</option>
              <option [value]="500">500 entries</option>
            </select>
          </div>

          <div class="filter-group" style="flex: 1;">
            <label for="search">Search:</label>
            <input 
              type="text" 
              id="search"
              [(ngModel)]="searchTerm" 
              (keyup.enter)="applyFilters()"
              placeholder="Search in log messages..."
              class="filter-input"
            />
          </div>

          <button class="btn btn-secondary" (click)="clearFilters()">
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Stats Card -->
      @if (logsData()) {
        <div class="stats-card">
          <div class="stat">
            <div class="stat-label">Total Issues</div>
            <div class="stat-value">{{ logsData()!.total }}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Errors</div>
            <div class="stat-value error">{{ logsData()!.error_count }}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Warnings</div>
            <div class="stat-value warning">{{ logsData()!.warning_count }}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Showing</div>
            <div class="stat-value">{{ logsData()!.showing }}</div>
          </div>
          <div class="stat-file">
            <div class="stat-label">Log File:</div>
            <div class="stat-file-path">{{ logsData()!.log_file }}</div>
          </div>
        </div>
      }

      <!-- Loading State -->
      @if (loading()) {
        <div class="loading">
          <div class="spinner"></div>
          <p>Loading server logs...</p>
        </div>
      }

      <!-- Error State -->
      @if (error()) {
        <div class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ error() }}</span>
        </div>
      }

      <!-- Logs List -->
      @if (!loading() && logsData() && logsData()!.logs.length > 0) {
        <div class="logs-list">
          @for (log of logsData()!.logs; track $index) {
            <div class="log-entry" [class]="'log-level-' + log.level.toLowerCase()">
              <div class="log-header">
                <span [class]="'log-badge log-badge-' + log.level.toLowerCase()">
                  {{ log.level }}
                </span>
                <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
                @if (log.logger) {
                  <span class="log-logger">{{ log.logger }}</span>
                }
                <button class="btn-expand" (click)="toggleExpanded($index)">
                  {{ expandedLogs.has($index) ? '▼ Collapse' : '▶ Expand' }}
                </button>
              </div>
              
              <div class="log-message">
                {{ getPreviewMessage(log.message) }}
              </div>

              @if (expandedLogs.has($index)) {
                <div class="log-details">
                  <div class="log-full-message">
                    <pre>{{ log.message }}</pre>
                  </div>
                  <div class="log-raw">
                    <strong>Raw Log:</strong>
                    <pre>{{ log.raw }}</pre>
                  </div>
                </div>
              }
            </div>
          }
        </div>
      }

      <!-- No Logs State -->
      @if (!loading() && logsData() && logsData()!.logs.length === 0) {
        <div class="no-logs">
          <div class="no-logs-icon">✅</div>
          <h3>No Server Issues Found</h3>
          <p>
            @if (selectedLevel() || searchTerm()) {
              No logs match your current filters. Try adjusting your search criteria.
            } @else {
              No errors or warnings have been logged. Your server is running smoothly!
            }
          </p>
          @if (selectedLevel() || searchTerm()) {
            <button class="btn btn-primary" (click)="clearFilters()">
              Clear Filters
            </button>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .server-logs-container {
      padding: 24px;
      max-width: 1600px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
    }

    .header h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
      color: #111827;
    }

    .subtitle {
      margin: 0;
      color: #6b7280;
      font-size: 14px;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-refresh {
      background: #3b82f6;
      color: white;
    }

    .btn-refresh:hover {
      background: #2563eb;
    }

    .btn-secondary {
      background: #e5e7eb;
      color: #374151;
    }

    .btn-secondary:hover {
      background: #d1d5db;
    }

    .btn-primary {
      background: #3b82f6;
      color: white;
    }

    .filters-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .filter-row {
      display: flex;
      gap: 16px;
      align-items: flex-end;
      flex-wrap: wrap;
    }

    .filter-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
      min-width: 150px;
    }

    .filter-group label {
      font-size: 12px;
      font-weight: 600;
      color: #6b7280;
      text-transform: uppercase;
    }

    .filter-select, .filter-input {
      padding: 8px 12px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 14px;
    }

    .filter-input {
      width: 100%;
    }

    .stats-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 20px;
      color: white;
    }

    .stat {
      text-align: center;
    }

    .stat-label {
      font-size: 12px;
      opacity: 0.9;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .stat-value {
      font-size: 32px;
      font-weight: 700;
    }

    .stat-value.error {
      color: #fca5a5;
    }

    .stat-value.warning {
      color: #fde047;
    }

    .stat-file {
      grid-column: 1 / -1;
      text-align: center;
      margin-top: 12px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stat-file-path {
      font-family: monospace;
      font-size: 12px;
      opacity: 0.8;
      margin-top: 4px;
    }

    .loading {
      text-align: center;
      padding: 64px 24px;
    }

    .spinner {
      width: 48px;
      height: 48px;
      margin: 0 auto 16px;
      border: 4px solid #f3f4f6;
      border-top-color: #3b82f6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-message {
      background: #fee2e2;
      border: 1px solid #fecaca;
      border-radius: 8px;
      padding: 16px;
      color: #991b1b;
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }

    .error-icon {
      font-size: 24px;
    }

    .logs-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .log-entry {
      background: white;
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border-left: 4px solid #d1d5db;
    }

    .log-entry.log-level-error,
    .log-entry.log-level-critical {
      border-left-color: #ef4444;
      background: #fef2f2;
    }

    .log-entry.log-level-warning {
      border-left-color: #f59e0b;
      background: #fffbeb;
    }

    .log-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .log-badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .log-badge-error,
    .log-badge-critical {
      background: #fee2e2;
      color: #991b1b;
    }

    .log-badge-warning {
      background: #fef3c7;
      color: #92400e;
    }

    .log-badge-info {
      background: #dbeafe;
      color: #1e40af;
    }

    .log-timestamp {
      font-size: 13px;
      color: #6b7280;
      font-family: monospace;
    }

    .log-logger {
      font-size: 12px;
      color: #9ca3af;
      background: #f3f4f6;
      padding: 2px 8px;
      border-radius: 4px;
      font-family: monospace;
    }

    .btn-expand {
      margin-left: auto;
      padding: 4px 12px;
      background: #f3f4f6;
      border: none;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      color: #374151;
    }

    .btn-expand:hover {
      background: #e5e7eb;
    }

    .log-message {
      color: #374151;
      line-height: 1.6;
      font-size: 14px;
    }

    .log-details {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #e5e7eb;
    }

    .log-full-message {
      margin-bottom: 16px;
    }

    .log-full-message pre,
    .log-raw pre {
      background: #f9fafb;
      padding: 12px;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 12px;
      line-height: 1.5;
      margin: 8px 0 0 0;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .log-raw strong {
      font-size: 12px;
      color: #6b7280;
      text-transform: uppercase;
    }

    .no-logs {
      text-align: center;
      padding: 64px 24px;
      background: #f9fafb;
      border-radius: 12px;
      border: 2px dashed #d1d5db;
    }

    .no-logs-icon {
      font-size: 64px;
      margin-bottom: 16px;
    }

    .no-logs h3 {
      margin: 0 0 12px 0;
      color: #111827;
    }

    .no-logs p {
      margin: 0 0 24px 0;
      color: #6b7280;
      max-width: 500px;
      margin-left: auto;
      margin-right: auto;
    }
  `]
})
export class ServerLogsComponent implements OnInit {
  logsData = signal<ServerLogsData | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);
  
  // Filters
  logType = 'backend';
  selectedLevel = signal<string>('');
  limit = 100;
  searchTerm = signal<string>('');
  
  // Expanded logs tracking
  expandedLogs = new Set<number>();

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadLogs();
  }

  loadLogs() {
    this.loading.set(true);
    this.error.set(null);
    
    const params: any = {
      log_type: this.logType,
      limit: this.limit.toString()
    };
    
    if (this.selectedLevel()) {
      params.level = this.selectedLevel();
    }
    
    if (this.searchTerm()) {
      params.search = this.searchTerm();
    }
    
    const url = `${environment.apiUrl}/admin/server-logs`;
    
    this.http.get<{ success: boolean; data: ServerLogsData }>(url, { params }).subscribe({
      next: (response) => {
        this.logsData.set(response.data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading server logs:', err);
        this.error.set(err.error?.detail || 'Failed to load server logs');
        this.loading.set(false);
      }
    });
  }

  refresh() {
    this.expandedLogs.clear();
    this.loadLogs();
  }

  applyFilters() {
    this.expandedLogs.clear();
    this.loadLogs();
  }

  clearFilters() {
    this.selectedLevel.set('');
    this.searchTerm.set('');
    this.limit = 100;
    this.expandedLogs.clear();
    this.loadLogs();
  }

  toggleExpanded(index: number) {
    if (this.expandedLogs.has(index)) {
      this.expandedLogs.delete(index);
    } else {
      this.expandedLogs.add(index);
    }
  }

  formatTimestamp(timestamp: string): string {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp.replace(',', '.'));
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  }

  getPreviewMessage(message: string): string {
    const lines = message.split('\n');
    if (lines.length > 1) {
      return lines[0] + ' ...';
    }
    return message.length > 200 ? message.substring(0, 200) + '...' : message;
  }
}
