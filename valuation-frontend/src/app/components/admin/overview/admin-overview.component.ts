import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-admin-overview',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="overview-container">
      <h2>Admin Dashboard Overview</h2>
      <p class="subtitle">System Administration Portal</p>
    </div>
  `,
  styles: [`
    .overview-container {
      padding: 2rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    h2 {
      color: #333;
      margin-bottom: 0.5rem;
      font-size: 2rem;
    }

    .subtitle {
      color: #666;
      margin-bottom: 2rem;
      font-size: 1.1rem;
    }

    .overview-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .overview-card {
      background: white;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      text-align: center;
    }

    .overview-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      border-color: #007bff;
    }

    .card-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }

    .overview-card h3 {
      color: #333;
      margin-bottom: 0.5rem;
      font-size: 1.25rem;
    }

    .overview-card p {
      color: #666;
      font-size: 0.95rem;
      margin: 0;
    }

    .info-section {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 1.5rem;
      margin-top: 2rem;
    }

    .info-section h3 {
      color: #333;
      margin-bottom: 1rem;
    }

    .coming-soon {
      color: #666;
      font-style: italic;
    }
  `]
})
export class AdminOverviewComponent {}
