import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AdminService, DatabaseInfo } from '../services/admin.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
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
          <h3>Databases</h3>
          <div class="database-list" *ngIf="databases">
            <div *ngFor="let db of databases" class="database-item">
              <h4>{{ db.name }}</h4>
              <ul class="collection-list">
                <li *ngFor="let collection of db.collections">
                  <a [routerLink]="['/admin/collections', db.name, collection]">
                    {{ collection }}
                  </a>
                </li>
              </ul>
            </div>
          </div>
          
          <div *ngIf="loading" class="loading">
            Loading databases...
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

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.loadDatabases();
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
      }
    });
  }
}