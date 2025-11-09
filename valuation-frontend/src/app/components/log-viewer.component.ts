import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LoggerService, LogEntry } from '../services/logger.service';

@Component({
  selector: 'app-log-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="log-viewer">
      <div class="log-header">
        <h3>Frontend API Logs</h3>
        <div class="log-actions">
          <button (click)="refreshLogs()" class="btn btn-refresh">🔄 Refresh</button>
          <button (click)="clearLogs()" class="btn btn-clear">🗑️ Clear</button>
          <button (click)="exportLogs()" class="btn btn-export">📄 Export JSON</button>
          <button (click)="exportCSV()" class="btn btn-export">📊 Export CSV</button>
        </div>
      </div>
      
      <div class="log-stats">
        <span class="stat">Total: {{ stats.total }}</span>
        <span class="stat">Requests: {{ stats.requests }}</span>
        <span class="stat">Responses: {{ stats.responses }}</span>
        <span class="stat error">Errors: {{ stats.errors }}</span>
        <span class="stat">Last Hour: {{ stats.lastHour }}</span>
      </div>
      
      <div class="log-filters">
        <label>
          <input type="checkbox" [(ngModel)]="showRequests" (change)="filterLogs()"> Requests
        </label>
        <label>
          <input type="checkbox" [(ngModel)]="showResponses" (change)="filterLogs()"> Responses
        </label>
        <label>
          <input type="checkbox" [(ngModel)]="showErrors" (change)="filterLogs()"> Errors
        </label>
      </div>
      
      <div class="log-entries">
        @for (log of filteredLogs; track log.id) {
          <div class="log-entry" [ngClass]="'log-' + log.type">
            <div class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</div>
            <div class="log-content">
              @if (log.type === 'request') {
                <div class="log-method">{{ log.method }}</div>
                <div class="log-url">{{ log.url }}</div>
                @if (log.requestBody) {
                  <div class="log-body">
                    <strong>Request Body:</strong>
                    <pre>{{ formatJSON(log.requestBody) }}</pre>
                  </div>
                }
              }
              @else if (log.type === 'response') {
                <div class="log-status" [ngClass]="getStatusClass(log.responseStatus!)">
                  {{ log.responseStatus }}
                </div>
                @if (log.processingTime) {
                  <div class="log-time">{{ log.processingTime }}ms</div>
                }
                @if (log.responseBody) {
                  <div class="log-body">
                    <strong>Response Body:</strong>
                    <pre>{{ formatJSON(log.responseBody) }}</pre>
                  </div>
                }
              }
              @else if (log.type === 'error') {
                <div class="log-error">
                  <strong>Error {{ log.responseStatus }}:</strong> {{ log.error?.message }}
                </div>
                @if (log.processingTime) {
                  <div class="log-time">{{ log.processingTime }}ms</div>
                }
              }
            </div>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    .log-viewer {
      font-family: 'Courier New', monospace;
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 1rem;
      border-radius: 4px;
      max-height: 600px;
      overflow-y: auto;
    }
    
    .log-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #333;
    }
    
    .log-header h3 {
      margin: 0;
      color: #569cd6;
    }
    
    .log-actions {
      display: flex;
      gap: 0.5rem;
    }
    
    .btn {
      padding: 0.25rem 0.5rem;
      border: 1px solid #555;
      background: #2d2d30;
      color: #d4d4d4;
      border-radius: 3px;
      cursor: pointer;
      font-size: 0.8rem;
    }
    
    .btn:hover {
      background: #3e3e42;
    }
    
    .log-stats {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
      padding: 0.5rem;
      background: #252526;
      border-radius: 3px;
    }
    
    .stat {
      font-size: 0.8rem;
      padding: 0.2rem 0.5rem;
      background: #007acc;
      color: white;
      border-radius: 3px;
    }
    
    .stat.error {
      background: #f14c4c;
    }
    
    .log-filters {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
      padding: 0.5rem;
      background: #252526;
      border-radius: 3px;
    }
    
    .log-filters label {
      display: flex;
      align-items: center;
      gap: 0.3rem;
      font-size: 0.8rem;
      cursor: pointer;
    }
    
    .log-entries {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .log-entry {
      padding: 0.5rem;
      border-radius: 3px;
      border-left: 3px solid transparent;
    }
    
    .log-entry.log-request {
      background: #0e2f44;
      border-left-color: #007acc;
    }
    
    .log-entry.log-response {
      background: #1e3a1e;
      border-left-color: #4ec9b0;
    }
    
    .log-entry.log-error {
      background: #3d1a1a;
      border-left-color: #f14c4c;
    }
    
    .log-timestamp {
      font-size: 0.7rem;
      color: #808080;
      margin-bottom: 0.3rem;
    }
    
    .log-content {
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
    }
    
    .log-method {
      font-weight: bold;
      color: #dcdcaa;
    }
    
    .log-url {
      color: #9cdcfe;
      word-break: break-all;
    }
    
    .log-status {
      font-weight: bold;
      padding: 0.2rem 0.5rem;
      border-radius: 3px;
      display: inline-block;
    }
    
    .log-status.success {
      background: #4ec9b0;
      color: white;
    }
    
    .log-status.error {
      background: #f14c4c;
      color: white;
    }
    
    .log-time {
      font-size: 0.7rem;
      color: #808080;
    }
    
    .log-body {
      margin-top: 0.5rem;
    }
    
    .log-body pre {
      background: #0c0c0c;
      padding: 0.5rem;
      border-radius: 3px;
      overflow-x: auto;
      font-size: 0.7rem;
      max-height: 200px;
      overflow-y: auto;
    }
    
    .log-error {
      color: #f14c4c;
    }
  `]
})
export class LogViewerComponent implements OnInit {
  logs: LogEntry[] = [];
  filteredLogs: LogEntry[] = [];
  stats: any = {};
  
  showRequests = true;
  showResponses = true;
  showErrors = true;
  
  constructor(private logger: LoggerService) {}
  
  ngOnInit() {
    this.refreshLogs();
  }
  
  refreshLogs() {
    this.logs = this.logger.getLogs();
    this.stats = this.logger.getLogStats();
    this.filterLogs();
  }
  
  filterLogs() {
    this.filteredLogs = this.logs.filter(log => {
      if (log.type === 'request' && !this.showRequests) return false;
      if (log.type === 'response' && !this.showResponses) return false;
      if (log.type === 'error' && !this.showErrors) return false;
      return true;
    });
  }
  
  clearLogs() {
    this.logger.clearLogs();
    this.refreshLogs();
  }
  
  exportLogs() {
    const data = this.logger.exportLogs();
    this.downloadFile(data, 'frontend-logs.json', 'application/json');
  }
  
  exportCSV() {
    const data = this.logger.exportLogsAsCSV();
    this.downloadFile(data, 'frontend-logs.csv', 'text/csv');
  }
  
  private downloadFile(data: string, filename: string, type: string) {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  }
  
  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }
  
  formatJSON(obj: any): string {
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  }
  
  getStatusClass(status: number): string {
    if (status >= 200 && status < 300) return 'success';
    if (status >= 400) return 'error';
    return '';
  }
}