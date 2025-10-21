import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HttpClient } from '@angular/common/http';
import { AdminService, DatabaseInfo } from '../services/admin.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    MatButtonModule, 
    MatIconModule, 
    MatCardModule, 
    MatSnackBarModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="admin-dashboard">
      <header class="admin-header">
        <h1>🛠 Admin Dashboard</h1>
        <nav class="admin-nav">
          <a routerLink="/admin/collections" routerLinkActive="active">Collections</a>
          <a routerLink="/admin/audit" routerLinkActive="active">Audit Trail</a>
        </nav>
      </header>

      <div class="admin-content">
        <aside class="admin-sidebar">
          <!-- Cache Management Section -->
          <div class="cache-management">
            <h3>🔄 Cache Management</h3>
            <mat-card class="cache-card">
              <mat-card-content>
                <p class="cache-info">
                  <strong>Common Fields Cache</strong><br>
                  Last Updated: {{ cacheLastUpdated || 'Unknown' }}<br>
                  Fields Count: {{ fieldsCount || 'N/A' }}
                </p>
                
                <div class="cache-actions">
                  <button mat-raised-button color="primary" 
                          (click)="refreshCache()" 
                          [disabled]="isRefreshing">
                    <mat-icon>refresh</mat-icon>
                    {{ isRefreshing ? 'Refreshing...' : 'Refresh Cache' }}
                  </button>
                  
                  <button mat-raised-button color="accent" 
                          (click)="downloadBackup()"
                          [disabled]="isDownloading">
                    <mat-icon>download</mat-icon>
                    {{ isDownloading ? 'Downloading...' : 'Download Backup' }}
                  </button>
                  
                  <button mat-raised-button color="warn" 
                          (click)="clearLocalStorage()">
                    <mat-icon>clear</mat-icon>
                    Clear Local Cache
                  </button>
                </div>
                
                <div class="cache-status" *ngIf="cacheStatus">
                  <div class="status-item" 
                       [ngClass]="{'status-active': cacheStatus.active, 'status-inactive': !cacheStatus.active}">
                    <mat-icon>{{ cacheStatus.active ? 'check_circle' : 'error' }}</mat-icon>
                    Active Fields: {{ cacheStatus.activeCount }}/{{ cacheStatus.totalCount }}
                  </div>
                  
                  <div class="status-item">
                    <mat-icon>schedule</mat-icon>
                    Cache Age: {{ cacheStatus.ageMinutes }}min
                  </div>
                </div>
              </mat-card-content>
            </mat-card>
          </div>

          <!-- Database Browser -->
          <div class="database-browser">
            <h3>📁 Databases</h3>
            <div class="database-list" *ngIf="databases">
              <div *ngFor="let db of databases" class="database-item">
                <h4>{{ db.name }}</h4>
                <ul class="collection-list">
                  <li *ngFor="let collection of db.collections">
                    <a [routerLink]="['/admin/collections', db.name, collection]">
                      {{ collection }}
                      <span class="collection-badge" *ngIf="collection === 'common_form_fields'">
                        📋 {{ fieldsCount || '?' }}
                      </span>
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            
            <div *ngIf="loading" class="loading">
              <mat-spinner diameter="30"></mat-spinner>
              Loading databases...
            </div>
          </div>
        </aside>

        <main class="admin-main">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .admin-dashboard {
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .admin-header {
      background: #2c3e50;
      color: white;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .admin-header h1 {
      margin: 0;
      font-size: 1.5rem;
    }

    .admin-nav a {
      color: white;
      text-decoration: none;
      margin-left: 1rem;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      transition: background-color 0.3s;
    }

    .admin-nav a:hover,
    .admin-nav a.active {
      background: #34495e;
    }

    .admin-content {
      flex: 1;
      display: flex;
    }

    .admin-sidebar {
      width: 300px;
      background: #ecf0f1;
      padding: 1rem;
      border-right: 1px solid #bdc3c7;
      overflow-y: auto;
    }

    .admin-sidebar h3 {
      margin-top: 0;
      color: #2c3e50;
    }

    .database-item {
      margin-bottom: 1rem;
    }

    .database-item h4 {
      margin: 0 0 0.5rem 0;
      color: #3498db;
      font-size: 0.9rem;
      text-transform: uppercase;
    }

    .collection-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .collection-list li {
      margin-bottom: 0.25rem;
    }

    .collection-list a {
      color: #7f8c8d;
      text-decoration: none;
      font-size: 0.85rem;
      padding: 0.25rem 0.5rem;
      display: block;
      border-radius: 3px;
      transition: all 0.3s;
    }

    .collection-list a:hover {
      color: #2c3e50;
      background: #d5dbdb;
    }

    .admin-main {
      flex: 1;
      padding: 1rem;
      overflow-y: auto;
    }

    /* Cache Management Styles */
    .cache-management {
      margin-bottom: 2rem;
    }

    .cache-card {
      margin-bottom: 1rem;
    }

    .cache-info {
      margin-bottom: 1rem;
      font-size: 0.9rem;
      line-height: 1.4;
    }

    .cache-actions {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }

    .cache-actions button {
      font-size: 0.8rem;
    }

    .cache-status {
      border-top: 1px solid #e0e0e0;
      padding-top: 1rem;
    }

    .status-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
      font-size: 0.85rem;
    }

    .status-active {
      color: #4caf50;
    }

    .status-inactive {
      color: #f44336;
    }

    .collection-badge {
      background: #3498db;
      color: white;
      padding: 0.2rem 0.4rem;
      border-radius: 10px;
      font-size: 0.7rem;
      margin-left: 0.5rem;
    }

    .database-browser {
      margin-top: 1rem;
    }

    .loading {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #666;
      font-size: 0.9rem;
    }

    /* Snackbar styles */
    ::ng-deep .snackbar-success {
      background: #4caf50 !important;
      color: white !important;
    }

    ::ng-deep .snackbar-error {
      background: #f44336 !important;
      color: white !important;
    }

    ::ng-deep .snackbar-info {
      background: #2196f3 !important;
      color: white !important;
    }

    .loading {
      text-align: center;
      color: #7f8c8d;
      font-style: italic;
    }
  `]
})
export class AdminDashboardComponent implements OnInit {
  databases: DatabaseInfo[] = [];
  loading = true;
  
  // Cache management properties
  cacheLastUpdated: string = '';
  fieldsCount: number = 0;
  isRefreshing = false;
  isDownloading = false;
  cacheStatus: any = null;

  constructor(
    private adminService: AdminService,
    private http: HttpClient,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadDatabases();
    this.loadCacheStatus();
  }

  private loadDatabases() {
    this.adminService.getDatabases().subscribe({
      next: (databases) => {
        this.databases = databases;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading databases:', error);
        this.loading = false;
        this.showMessage('Error loading databases', 'error');
      }
    });
  }

  loadCacheStatus() {
    // Get cache status from backend and local storage
    this.http.get<any>('/api/admin/cache-status').subscribe({
      next: (status) => {
        this.cacheStatus = status;
        this.fieldsCount = status.totalCount;
        this.cacheLastUpdated = status.lastUpdated ? 
          new Date(status.lastUpdated).toLocaleString() : 'Unknown';
      },
      error: (error) => {
        console.warn('Cache status not available:', error);
        this.loadLocalCacheInfo();
      }
    });
  }

  loadLocalCacheInfo() {
    // Fallback to local storage info
    const localCache = localStorage.getItem('common_form_fields_cache');
    if (localCache) {
      try {
        const cache = JSON.parse(localCache);
        this.fieldsCount = cache.fields?.length || 0;
        this.cacheLastUpdated = cache.timestamp ? 
          new Date(cache.timestamp).toLocaleString() : 'Unknown';
      } catch (e) {
        console.warn('Error parsing local cache:', e);
      }
    }
  }

  refreshCache() {
    this.isRefreshing = true;
    this.showMessage('Refreshing cache...', 'info');

    this.http.post<any>('/api/common-form-fields/refresh-cache', {}).subscribe({
      next: (response) => {
        this.isRefreshing = false;
        this.fieldsCount = response.fields?.length || 0;
        this.cacheLastUpdated = new Date().toLocaleString();
        
        // Update local storage
        localStorage.setItem('common_form_fields_cache', JSON.stringify({
          fields: response.fields,
          timestamp: new Date().toISOString(),
          source: 'manual_refresh'
        }));
        
        this.loadCacheStatus();
        this.showMessage(`Cache refreshed successfully! ${this.fieldsCount} fields loaded.`, 'success');
      },
      error: (error) => {
        this.isRefreshing = false;
        console.error('Cache refresh failed:', error);
        this.showMessage('Cache refresh failed. Check console for details.', 'error');
      }
    });
  }

  downloadBackup() {
    this.isDownloading = true;

    this.http.get<any>('/api/common-form-fields?includeInactive=true').subscribe({
      next: (response) => {
        this.isDownloading = false;
        
        const backup = {
          timestamp: new Date().toISOString(),
          totalFields: response.length,
          activeFields: response.filter((f: any) => f.isActive).length,
          fields: response
        };

        // Create and download file
        const blob = new Blob([JSON.stringify(backup, null, 2)], { 
          type: 'application/json' 
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `common_form_fields_backup_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        this.showMessage('Backup downloaded successfully!', 'success');
      },
      error: (error) => {
        this.isDownloading = false;
        console.error('Backup download failed:', error);
        this.showMessage('Backup download failed. Check console for details.', 'error');
      }
    });
  }

  clearLocalStorage() {
    localStorage.removeItem('common_form_fields_cache');
    localStorage.removeItem('common_form_fields_timestamp');
    this.showMessage('Local cache cleared successfully!', 'success');
    this.loadCacheStatus();
  }

  private showMessage(message: string, type: 'success' | 'error' | 'info' = 'info') {
    const config = {
      duration: 3000,
      panelClass: [`snackbar-${type}`]
    };
    this.snackBar.open(message, 'Close', config);
  }
}