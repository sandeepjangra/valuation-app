import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    RouterModule
  ],
  template: `
    <div class="dashboard-container">
      <h1>Valuation Dashboard</h1>
      
      <div class="stats-grid">
        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>account_balance</mat-icon>
              Banks
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">4</div>
            <div class="stat-label">Active Banks</div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/banks">View Banks</button>
          </mat-card-actions>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>description</mat-icon>
              Templates
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">2</div>
            <div class="stat-label">Templates Available</div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/templates">View Templates</button>
          </mat-card-actions>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>assignment</mat-icon>
              Reports
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">1</div>
            <div class="stat-label">Sample Reports</div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/reports">View Reports</button>
          </mat-card-actions>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>home</mat-icon>
              Properties
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">4</div>
            <div class="stat-label">Property Types</div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/properties">View Types</button>
          </mat-card-actions>
        </mat-card>
      </div>

      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <button mat-raised-button color="primary" routerLink="/report-form">
            <mat-icon>add</mat-icon>
            Create New Report
          </button>
          <button mat-raised-button color="warn" routerLink="/templates">
            <mat-icon>settings</mat-icon>
            Manage Templates
          </button>
          <button mat-raised-button color="accent" routerLink="/admin">
            <mat-icon>admin_panel_settings</mat-icon>
            Admin Dashboard
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    h1 {
      margin-bottom: 32px;
      color: #1976d2;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
      margin-bottom: 48px;
    }

    .stat-card {
      text-align: center;
    }

    .stat-card mat-card-title {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .stat-number {
      font-size: 3rem;
      font-weight: bold;
      color: #1976d2;
      margin: 16px 0 8px;
    }

    .stat-label {
      color: #666;
      font-size: 0.9rem;
    }

    .quick-actions {
      background: #f5f5f5;
      padding: 24px;
      border-radius: 8px;
    }

    .quick-actions h2 {
      margin-top: 0;
      margin-bottom: 24px;
    }

    .action-buttons {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .action-buttons button {
      min-width: 200px;
    }

    .action-buttons mat-icon {
      margin-right: 8px;
    }

    @media (max-width: 768px) {
      .dashboard-container {
        padding: 16px;
      }
      
      .stats-grid {
        grid-template-columns: 1fr;
      }
      
      .action-buttons {
        flex-direction: column;
      }
      
      .action-buttons button {
        width: 100%;
      }
    }
  `]
})
export class DashboardComponent {
}