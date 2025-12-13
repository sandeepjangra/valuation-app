import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, forkJoin, of, throwError, timer } from 'rxjs';
import { map, catchError, timeout, timeoutWith } from 'rxjs/operators';
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
   * Extract organization from token for debugging
   */
  private extractOrgFromToken(authHeader: string): string {
    try {
      const token = authHeader.replace('Bearer ', '');
      // Dev tokens have format: dev_admin_system.com_ORGNAME_role
      const parts = token.split('_');
      if (parts.length >= 4) {
        return parts[3]; // Organization name is the 4th part
      }
      return 'unknown';
    } catch (error) {
      return 'parse-error';
    }
  }

  /**
   * Get pending reports for dashboard
   */
  getPendingReports(limit: number = 5): Observable<DashboardReport[]> {
    const headers = this.getHeaders();
    console.log('🔄 Fetching pending reports...');
    
    return this.http.get<any>(`${this.baseUrl}/dashboard/pending-reports?limit=${limit}`, { headers })
      .pipe(
        timeout(30000), // 30 second timeout
        map(response => {
          console.log('✅ Pending reports response:', response);
          return response.data || [];
        }),
        catchError(error => {
          console.error('❌ Error fetching pending reports:', error);
          if (error.name === 'TimeoutError') {
            console.error('❌ Pending reports request timed out');
          }
          return of([]);
        })
      );
  }

  /**
   * Get recently created reports for dashboard
   */
  getCreatedReports(limit: number = 5): Observable<DashboardReport[]> {
    console.log('🔄 DashboardService.getCreatedReports called with limit:', limit);
    const headers = this.getHeaders();
    const url = `${this.baseUrl}/dashboard/created-reports?limit=${limit}`;
    
    return this.http.get<any>(url, { headers })
      .pipe(
        timeout(10000),
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching created reports:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
          });
          return of([]);
        })
      );
  }

  /**
   * Get banks summary for dashboard
   */
  getBanks(limit: number = 8): Observable<DashboardBank[]> {
    console.log('🔄 DashboardService.getBanks called with limit:', limit);
    const headers = this.getHeaders();
    const url = `${this.baseUrl}/dashboard/banks?limit=${limit}`;
    
    return this.http.get<any>(url, { headers })
      .pipe(
        timeout(10000),
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching banks:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
          });
          return of([]);
        })
      );
  }

  /**
   * Get custom templates for dashboard
   */
  getTemplates(limit: number = 5): Observable<{templates: DashboardTemplate[], total: number}> {
    console.log('🔄 DashboardService.getTemplates called with limit:', limit);
    const headers = this.getHeaders();
    const url = `${this.baseUrl}/dashboard/templates?limit=${limit}`;
    const currentToken = headers.get('Authorization');
    console.log('🔑 DashboardService: Using token for templates:', currentToken?.substring(0, 50) + '...');
    
    // CRITICAL: Log what organization this token is for
    if (currentToken) {
      console.log('🏢 DashboardService: Token organization context:', this.extractOrgFromToken(currentToken));
    }
    
    return this.http.get<any>(url, { headers })
      .pipe(
        timeout(10000),
        map(response => ({
          templates: response.data || [],
          total: response.total || 0
        })),
        catchError(error => {
          console.error('❌ Error fetching templates:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
          });
          return of({ templates: [], total: 0 });
        })
      );
  }

  /**
   * Get recent activities for dashboard
   */
  getRecentActivities(limit: number = 10): Observable<DashboardActivity[]> {
    console.log('🔄 DashboardService.getRecentActivities called with limit:', limit);
    const headers = this.getHeaders();
    const url = `${this.baseUrl}/dashboard/recent-activities?limit=${limit}`;
    
    return this.http.get<any>(url, { headers })
      .pipe(
        timeout(10000),
        map(response => response.data || []),
        catchError(error => {
          console.error('❌ Error fetching recent activities:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
          });
          return of([]);
        })
      );
  }

  /**
   * Get dashboard statistics
   */
  getStats(): Observable<DashboardStats> {
    console.log('🔄 DashboardService.getStats called');
    const headers = this.getHeaders();
    const url = `${this.baseUrl}/dashboard/stats`;
    
    return this.http.get<any>(url, { headers })
      .pipe(
        timeout(10000),
        map(response => response.data || {}),
        catchError(error => {
          console.error('❌ Error fetching stats:', {
            status: error.status,
            message: error.message,
            url: url,
            isTimeout: error.name === 'TimeoutError'
          });
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
   * Get all dashboard data in a single call with timeout
   */
  getDashboardData(): Observable<DashboardData> {
    console.log('🔄 Starting dashboard data fetch...');
    
    return forkJoin({
      pendingReports: this.getPendingReports(),
      createdReports: this.getCreatedReports(), 
      banks: this.getBanks(),
      templates: this.getTemplates(),
      recentActivities: this.getRecentActivities(),
      stats: this.getStats()
    }).pipe(
      map(results => {
        console.log('✅ Dashboard data fetch completed:', results);
        return {
          pendingReports: results.pendingReports,
          createdReports: results.createdReports,
          banks: results.banks,
          templates: results.templates.templates,
          recentActivities: results.recentActivities,
          stats: results.stats
        };
      }),
      catchError(error => {
        console.error('❌ Error fetching dashboard data:', error);
        console.error('❌ Error details:', {
          message: error.message,
          status: error.status,
          url: error.url
        });
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