import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AdminService, CollectionDocument } from '../services/admin.service';

@Component({
  selector: 'app-collection-browser',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="collection-browser">
      <header class="browser-header" *ngIf="database && collection">
        <h2>{{ database }}.{{ collection }}</h2>
        <div class="header-actions">
          <button class="btn btn-primary" (click)="createNewDocument()">
            ➕ Add New Document
          </button>
          <button class="btn btn-secondary" (click)="refreshDocuments()">
            🔄 Refresh
          </button>
        </div>
      </header>

      <div class="search-bar" *ngIf="database && collection">
        <input 
          type="text" 
          placeholder="Search documents... (JSON query or text)"
          [(ngModel)]="searchQuery"
          (keyup.enter)="searchDocuments()"
          class="search-input"
        >
        <button class="btn btn-search" (click)="searchDocuments()">Search</button>
        <button class="btn btn-clear" (click)="clearSearch()" *ngIf="isSearchActive">Clear</button>
      </div>

      <div class="collection-stats" *ngIf="stats">
        <span class="stat-item">📊 {{ stats.count }} documents</span>
        <span class="stat-item">💾 {{ formatBytes(stats.size) }}</span>
        <span class="stat-item">📏 {{ formatBytes(stats.avgObjSize) }} avg</span>
      </div>

      <div class="documents-container" *ngIf="database && collection">
        <div class="documents-grid">
          <div 
            *ngFor="let doc of documents" 
            class="document-card"
            (click)="editDocument(doc._id)"
          >
            <div class="document-header">
              <span class="document-id">{{ doc._id }}</span>
              <div class="document-actions" (click)="$event.stopPropagation()">
                <button class="btn-icon" (click)="editDocument(doc._id)" title="Edit">✏️</button>
                <button class="btn-icon" (click)="deleteDocument(doc._id)" title="Delete">🗑️</button>
              </div>
            </div>
            <div class="document-preview">
              <pre>{{ getDocumentPreview(doc) }}</pre>
            </div>
            <div class="document-meta" *ngIf="doc['createdAt'] || doc['updatedAt']">
              <small *ngIf="doc['createdAt']">Created: {{ formatDate(doc['createdAt']) }}</small>
              <small *ngIf="doc['updatedAt']">Updated: {{ formatDate(doc['updatedAt']) }}</small>
            </div>
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
            Page {{ currentPage }} of {{ totalPages }} ({{ totalDocuments }} total)
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

      <div class="welcome-message" *ngIf="!database || !collection">
        <h3>Welcome to Admin Dashboard</h3>
        <p>Select a collection from the sidebar to browse documents.</p>
      </div>

      <div class="loading" *ngIf="loading">
        Loading documents...
      </div>
    </div>
  `,
  styles: [`
    .collection-browser {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .browser-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 1rem;
      border-bottom: 2px solid #3498db;
    }

    .browser-header h2 {
      margin: 0;
      color: #2c3e50;
      font-family: 'Courier New', monospace;
    }

    .header-actions {
      display: flex;
      gap: 0.5rem;
    }

    .search-bar {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      align-items: center;
    }

    .search-input {
      flex: 1;
      padding: 0.5rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
    }

    .collection-stats {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
      padding: 0.5rem;
      background: #ecf0f1;
      border-radius: 4px;
    }

    .stat-item {
      font-size: 0.85rem;
      color: #7f8c8d;
    }

    .documents-container {
      flex: 1;
      overflow-y: auto;
    }

    .documents-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .document-card {
      border: 1px solid #bdc3c7;
      border-radius: 6px;
      padding: 1rem;
      background: white;
      cursor: pointer;
      transition: all 0.3s;
    }

    .document-card:hover {
      border-color: #3498db;
      box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
    }

    .document-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .document-id {
      font-family: 'Courier New', monospace;
      font-size: 0.8rem;
      color: #7f8c8d;
      background: #ecf0f1;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
    }

    .document-actions {
      display: flex;
      gap: 0.25rem;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      padding: 0.2rem;
      border-radius: 3px;
      transition: background-color 0.3s;
    }

    .btn-icon:hover {
      background: #ecf0f1;
    }

    .document-preview {
      background: #f8f9fa;
      padding: 0.5rem;
      border-radius: 4px;
      margin-bottom: 0.5rem;
      max-height: 150px;
      overflow: hidden;
    }

    .document-preview pre {
      margin: 0;
      font-size: 0.75rem;
      color: #2c3e50;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .document-meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.7rem;
      color: #95a5a6;
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 1rem;
      padding: 1rem;
      border-top: 1px solid #ecf0f1;
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

    .btn-primary {
      background: #3498db;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #2980b9;
    }

    .btn-secondary {
      background: #95a5a6;
      color: white;
    }

    .btn-secondary:hover:not(:disabled) {
      background: #7f8c8d;
    }

    .btn-search {
      background: #27ae60;
      color: white;
    }

    .btn-search:hover {
      background: #229954;
    }

    .btn-clear {
      background: #e74c3c;
      color: white;
    }

    .btn-clear:hover {
      background: #c0392b;
    }

    .btn-page {
      background: #ecf0f1;
      color: #2c3e50;
    }

    .btn-page:hover:not(:disabled) {
      background: #d5dbdb;
    }

    .welcome-message {
      text-align: center;
      color: #7f8c8d;
      margin-top: 2rem;
    }

    .loading {
      text-align: center;
      color: #7f8c8d;
      font-style: italic;
      margin-top: 2rem;
    }
  `]
})
export class CollectionBrowserComponent implements OnInit {
  database?: string;
  collection?: string;
  documents: CollectionDocument[] = [];
  currentPage = 1;
  totalPages = 1;
  totalDocuments = 0;
  loading = false;
  searchQuery = '';
  isSearchActive = false;
  stats?: any;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private adminService: AdminService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.database = params['database'];
      this.collection = params['collection'];
      
      if (this.database && this.collection) {
        this.loadDocuments();
        this.loadStats();
      }
    });
  }

  private loadDocuments() {
    if (!this.database || !this.collection) return;
    
    this.loading = true;
    this.adminService.getDocuments(this.database, this.collection, this.currentPage).subscribe({
      next: (response) => {
        this.documents = response.documents;
        this.totalPages = response.totalPages;
        this.totalDocuments = response.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading documents:', error);
        this.loading = false;
      }
    });
  }

  private loadStats() {
    if (!this.database || !this.collection) return;
    
    this.adminService.getCollectionStats(this.database, this.collection).subscribe({
      next: (stats) => {
        this.stats = stats;
      },
      error: (error) => {
        console.error('Error loading stats:', error);
      }
    });
  }

  refreshDocuments() {
    this.currentPage = 1;
    this.loadDocuments();
    this.loadStats();
  }

  createNewDocument() {
    if (this.database && this.collection) {
      this.router.navigate(['/admin/collections', this.database, this.collection, 'new']);
    }
  }

  editDocument(id: string) {
    if (this.database && this.collection) {
      this.router.navigate(['/admin/collections', this.database, this.collection, id]);
    }
  }

  deleteDocument(id: string) {
    if (!this.database || !this.collection) return;
    
    if (confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      this.adminService.deleteDocument(this.database, this.collection, id).subscribe({
        next: () => {
          this.loadDocuments();
        },
        error: (error) => {
          console.error('Error deleting document:', error);
          alert('Failed to delete document. Please try again.');
        }
      });
    }
  }

  searchDocuments() {
    if (!this.database || !this.collection || !this.searchQuery.trim()) return;
    
    this.loading = true;
    this.isSearchActive = true;
    
    let query: any;
    try {
      // Try to parse as JSON query
      query = JSON.parse(this.searchQuery);
    } catch {
      // Fallback to text search across common fields
      query = {
        $or: [
          { name: { $regex: this.searchQuery, $options: 'i' } },
          { title: { $regex: this.searchQuery, $options: 'i' } },
          { description: { $regex: this.searchQuery, $options: 'i' } },
          { code: { $regex: this.searchQuery, $options: 'i' } }
        ]
      };
    }
    
    this.adminService.searchDocuments(this.database, this.collection, query, this.currentPage).subscribe({
      next: (response) => {
        this.documents = response.documents;
        this.totalDocuments = response.total;
        this.totalPages = Math.ceil(response.total / 20);
        this.loading = false;
      },
      error: (error) => {
        console.error('Error searching documents:', error);
        this.loading = false;
      }
    });
  }

  clearSearch() {
    this.searchQuery = '';
    this.isSearchActive = false;
    this.currentPage = 1;
    this.loadDocuments();
  }

  goToPage(page: number) {
    this.currentPage = page;
    if (this.isSearchActive) {
      this.searchDocuments();
    } else {
      this.loadDocuments();
    }
  }

  getDocumentPreview(doc: any): string {
    const preview = { ...doc };
    delete preview._id;
    
    // Limit preview size
    const previewStr = JSON.stringify(preview, null, 2);
    return previewStr.length > 300 ? previewStr.substring(0, 300) + '...' : previewStr;
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString();
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}