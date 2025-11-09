import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-admin',
  imports: [CommonModule],
  templateUrl: './admin.html',
  styleUrl: './admin.css',
})
export class Admin implements OnInit {
  backendOnline = false;
  databaseOnline = false;

  constructor(private router: Router, private http: HttpClient) {}

  ngOnInit() {
    this.checkSystemStatus();
  }

  // Navigation Methods
  navigateToLogs() {
    // Navigate to log viewer component
    this.router.navigate(['/logs']);
  }

  navigateToBanks() {
    this.router.navigate(['/banks']);
  }

  viewReports() {
    this.router.navigate(['/reports']);
  }

  // System Status Methods
  checkSystemStatus() {
    // Check backend status
    this.http.get('http://localhost:8000/api/banks').subscribe({
      next: (response) => {
        this.backendOnline = true;
        this.databaseOnline = true; // If banks API works, database is connected
      },
      error: (error) => {
        console.log('Backend or database offline:', error);
        this.backendOnline = false;
        this.databaseOnline = false;
      }
    });
  }

  refreshStatus() {
    this.checkSystemStatus();
  }

  // Log Testing Methods
  openLogTest() {
    // Open log testing page in new window
    window.open('http://localhost:8080/test_frontend_logging.html', '_blank');
  }

  // Placeholder methods for future implementation
  viewCollections() {
    alert('Collections view coming soon! This will show MongoDB collection statistics.');
  }

  exportData() {
    alert('Export functionality coming soon! This will allow exporting logs and data.');
  }
}
