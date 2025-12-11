import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, forkJoin, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';

export interface DashboardReport {
  _id: string;
  report_id: string;
  property_address: string;
  bank_code: string;
  template_id: string;
  status: string;
  created_by_email: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardBank {
  _id: string;
  bankCode: string;
  bankName: string;
  description: string;
  template_count: number;
  isActive: boolean;
}

export interface DashboardTemplate {
  _id: string;
  templateName: string;
  description: string;
  bankCode: string;
  templateCode: string;
  propertyType: string;
  created_by_email: string;
  created_at: string;
  usage_count: number;
}

export interface DashboardActivity {
  _id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: any;
  timestamp: string;
  ip_address: string;
}

export interface DashboardStats {
  total_reports: number;
  pending_reports: number;
  submitted_reports: number;
  custom_templates: number;
  recent_activities: number;
  total_users: number;
}

export interface DashboardData {
  pendingReports: DashboardReport[];
  createdReports: DashboardReport[];
  banks: DashboardBank[];
  templates: DashboardTemplate[];
  recentActivities: DashboardActivity[];
  stats: DashboardStats;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  /**
   * Get HTTP headers with authorization token
   */
  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Get pending reports for dashboard
   */
  getPendingReports(limit: number = 5): Observable<DashboardReport[]> {
    const headers = this.getHeaders();
    return this.http.get<any>(`${this.baseUrl}/dashboard/pending-reports?limit=${limit}`, { headers })
      .pipe(
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching pending reports:', error);
          return of([]);
        })
      );
  }

  /**
   * Get recently created reports for dashboard
   */
  getCreatedReports(limit: number = 5): Observable<DashboardReport[]> {
    const headers = this.getHeaders();
    return this.http.get<any>(`${this.baseUrl}/dashboard/created-reports?limit=${limit}`, { headers })
      .pipe(
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching created reports:', error);
          return of([]);
        })
      );
  }

  /**
   * Get banks summary for dashboard
   */
  getBanks(limit: number = 8): Observable<DashboardBank[]> {
    const headers = this.getHeaders();
    return this.http.get<any>(`${this.baseUrl}/dashboard/banks?limit=${limit}`, { headers })
      .pipe(
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching banks:', error);
          return of([]);
        })
      );
  }

  /**
   * Get custom templates for dashboard
   */
  getTemplates(limit: number = 5): Observable<{templates: DashboardTemplate[], total: number}> {
    const headers = this.getHeaders();
    return this.http.get<any>(`${this.baseUrl}/dashboard/templates?limit=${limit}`, { headers })
      .pipe(
        map(response => ({
          templates: response.data || [],
          total: response.total || 0
        })),
        catchError(error => {
          console.error('❌ Error fetching templates:', error);
          return of({ templates: [], total: 0 });
        })
      );
  }

  /**
   * Get recent activities for dashboard
   */
  getRecentActivities(limit: number = 10): Observable<DashboardActivity[]> {
    const headers = this.getHeaders();
    return this.http.get<any>(`${this.baseUrl}/dashboard/recent-activities?limit=${limit}`, { headers })
      .pipe(
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching recent activities:', error);
          return of([]);
        })
      );
  }

  /**
   * Get dashboard statistics
   */
  getStats(): Observable<DashboardStats> {
    const headers = this.getHeaders();
    return this.http.get<any>(`${this.baseUrl}/dashboard/stats`, { headers })
      .pipe(
        map(response => response.data || {}),
        catchError(error => {
          console.error('❌ Error fetching stats:', error);
          return of({
            total_reports: 0,
            pending_reports: 0,
            submitted_reports: 0,
            custom_templates: 0,
            recent_activities: 0,
            total_users: 0
          });
        })
      );
  }

  /**
   * Get all dashboard data in a single call
   */
  getDashboardData(): Observable<DashboardData> {
    return forkJoin({
      pendingReports: this.getPendingReports(),
      createdReports: this.getCreatedReports(),
      banks: this.getBanks(),
      templates: this.getTemplates(),
      recentActivities: this.getRecentActivities(),
      stats: this.getStats()
    }).pipe(
      map(results => ({
        pendingReports: results.pendingReports,
        createdReports: results.createdReports,
        banks: results.banks,
        templates: results.templates.templates,
        recentActivities: results.recentActivities,
        stats: results.stats
      })),
      catchError(error => {
        console.error('❌ Error fetching dashboard data:', error);
        return of({
          pendingReports: [],
          createdReports: [],
          banks: [],
          templates: [],
          recentActivities: [],
          stats: {
            total_reports: 0,
            pending_reports: 0,
            submitted_reports: 0,
            custom_templates: 0,
            recent_activities: 0,
            total_users: 0
          }
        });
      })
    );
  }
}