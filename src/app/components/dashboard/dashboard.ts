import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  
  // Mock user data - will be replaced with actual service later
  isAdmin = true; // Toggle this to test different views
  currentCompany = 'TechCorp Valuations';
  showCollectiveView = false; // Toggle for admin view
  
  // Statistics data - will be populated from services later
  companyStats = {
    pendingReports: 12,
    createdReports: 145,
    totalBanks: 8
  };
  
  // Mock collective stats for admin
  collectiveStats = {
    pendingReports: 47,
    createdReports: 523,
    totalBanks: 8,
    totalCompanies: 4
  };
  
  // Recent activity for last 5 business days
  recentActivity = [
    { date: '2025-10-24', type: 'created', count: 3, company: 'TechCorp Valuations' },
    { date: '2025-10-23', type: 'pending', count: 2, company: 'Global Properties' },
    { date: '2025-10-22', type: 'created', count: 5, company: 'TechCorp Valuations' },
    { date: '2025-10-21', type: 'pending', count: 1, company: 'Metro Appraisals' },
    { date: '2025-10-18', type: 'created', count: 4, company: 'City Valuations' }
  ];

  constructor(private router: Router) {}

  ngOnInit() {
    // Initialize dashboard data
    this.loadDashboardData();
  }

  loadDashboardData() {
    // This will be replaced with actual API calls
    console.log('Loading dashboard data for:', this.currentCompany);
  }

  toggleAdminView() {
    this.showCollectiveView = !this.showCollectiveView;
  }

  navigateToReports() {
    this.router.navigate(['/reports']);
  }

  navigateToBanks() {
    this.router.navigate(['/banks']);
  }

  createNewReport() {
    this.router.navigate(['/new-report']);
  }

  getDisplayStats() {
    return this.isAdmin && this.showCollectiveView ? this.collectiveStats : this.companyStats;
  }
}
