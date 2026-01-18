import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import {
  ActivityLogEntry,
  LogActivityRequest,
  ActivityLogResponse,
  ActionType,
  CommonActions
} from '../models/activity-log.model';

@Injectable({
  providedIn: 'root'
})
export class ActivityLoggingService {
  private apiUrl = `${environment.apiUrl}/activity-logs`;

  constructor(private http: HttpClient) {}

  /**
   * Log a user activity (fire-and-forget, doesn't block UI)
   */
  logActivity(
    userId: string,
    orgShortName: string,
    action: string,
    actionType: ActionType | string,
    description: string,
    entityType?: string,
    entityId?: string,
    metadata?: Record<string, any>
  ): void {
    const request: LogActivityRequest = {
      userId,
      orgShortName,
      action,
      actionType,
      description,
      entityType,
      entityId,
      metadata
    };

    // Fire and forget - don't wait for response, don't block UI
    this.http.post<ActivityLogResponse>(this.apiUrl, request)
      .pipe(
        catchError(error => {
          console.error('Error logging activity:', error);
          return of({ success: false, data: { id: '' }, message: 'Failed to log activity' });
        })
      )
      .subscribe();
  }

  /**
   * Log authentication activity (login, logout, etc.)
   */
  logAuthActivity(
    userId: string,
    orgShortName: string,
    action: string,
    description: string,
    metadata?: Record<string, any>
  ): void {
    this.logActivity(
      userId,
      orgShortName,
      action,
      ActionType.AUTHENTICATION,
      description,
      undefined,
      undefined,
      metadata
    );
  }

  /**
   * Log organization activity
   */
  logOrgActivity(
    userId: string,
    orgShortName: string,
    action: string,
    description: string,
    orgId?: string,
    metadata?: Record<string, any>
  ): void {
    this.logActivity(
      userId,
      orgShortName,
      action,
      ActionType.ORGANIZATION,
      description,
      'organization',
      orgId,
      metadata
    );
  }

  /**
   * Log user management activity
   */
  logUserActivity(
    userId: string,
    orgShortName: string,
    action: string,
    description: string,
    targetUserId?: string,
    metadata?: Record<string, any>
  ): void {
    this.logActivity(
      userId,
      orgShortName,
      action,
      ActionType.USER_MANAGEMENT,
      description,
      'user',
      targetUserId,
      metadata
    );
  }

  /**
   * Log report activity
   */
  logReportActivity(
    userId: string,
    orgShortName: string,
    action: string,
    description: string,
    reportId?: string,
    metadata?: Record<string, any>
  ): void {
    this.logActivity(
      userId,
      orgShortName,
      action,
      ActionType.REPORT,
      description,
      'report',
      reportId,
      metadata
    );
  }

  /**
   * Log template activity
   */
  logTemplateActivity(
    userId: string,
    orgShortName: string,
    action: string,
    description: string,
    templateId?: string,
    metadata?: Record<string, any>
  ): void {
    this.logActivity(
      userId,
      orgShortName,
      action,
      ActionType.TEMPLATE,
      description,
      'template',
      templateId,
      metadata
    );
  }

  /**
   * Log draft activity
   */
  logDraftActivity(
    userId: string,
    orgShortName: string,
    action: string,
    description: string,
    draftId?: string,
    metadata?: Record<string, any>
  ): void {
    this.logActivity(
      userId,
      orgShortName,
      action,
      ActionType.DRAFT,
      description,
      'draft',
      draftId,
      metadata
    );
  }

  /**
   * Log settings activity
   */
  logSettingsActivity(
    userId: string,
    orgShortName: string,
    action: string,
    description: string,
    metadata?: Record<string, any>
  ): void {
    this.logActivity(
      userId,
      orgShortName,
      action,
      ActionType.SETTINGS,
      description,
      undefined,
      undefined,
      metadata
    );
  }

  /**
   * Get activities for a specific user
   */
  getUserActivity(userId: string, limit: number = 100, skip: number = 0): Observable<ActivityLogResponse> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('skip', skip.toString());

    return this.http.get<ActivityLogResponse>(`${this.apiUrl}/user/${userId}`, { params })
      .pipe(
        tap(response => console.log('User activity retrieved:', response)),
        catchError(error => {
          console.error('Error getting user activity:', error);
          return of({ success: false, data: [], message: 'Failed to retrieve user activity' });
        })
      );
  }

  /**
   * Get activities for an organization
   */
  getOrgActivity(orgShortName: string, limit: number = 100, skip: number = 0): Observable<ActivityLogResponse> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('skip', skip.toString());

    return this.http.get<ActivityLogResponse>(`${this.apiUrl}/org/${orgShortName}`, { params })
      .pipe(
        tap(response => console.log('Organization activity retrieved:', response)),
        catchError(error => {
          console.error('Error getting organization activity:', error);
          return of({ success: false, data: [], message: 'Failed to retrieve organization activity' });
        })
      );
  }

  /**
   * Get all activities (system admin only)
   */
  getAllActivity(limit: number = 100, skip: number = 0): Observable<ActivityLogResponse> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('skip', skip.toString());

    return this.http.get<ActivityLogResponse>(`${this.apiUrl}/all`, { params })
      .pipe(
        tap(response => console.log('All activity retrieved:', response)),
        catchError(error => {
          console.error('Error getting all activity:', error);
          return of({ success: false, data: [], message: 'Failed to retrieve all activity' });
        })
      );
  }

  /**
   * Get activities by action type
   */
  getActivitiesByType(actionType: ActionType | string, limit: number = 100, skip: number = 0): Observable<ActivityLogResponse> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('skip', skip.toString());

    return this.http.get<ActivityLogResponse>(`${this.apiUrl}/type/${actionType}`, { params })
      .pipe(
        tap(response => console.log('Activities by type retrieved:', response)),
        catchError(error => {
          console.error('Error getting activities by type:', error);
          return of({ success: false, data: [], message: 'Failed to retrieve activities by type' });
        })
      );
  }

  /**
   * Get activities for a specific entity
   */
  getEntityActivity(entityType: string, entityId: string, limit: number = 100, skip: number = 0): Observable<ActivityLogResponse> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('skip', skip.toString());

    return this.http.get<ActivityLogResponse>(`${this.apiUrl}/entity/${entityType}/${entityId}`, { params })
      .pipe(
        tap(response => console.log('Entity activity retrieved:', response)),
        catchError(error => {
          console.error('Error getting entity activity:', error);
          return of({ success: false, data: [], message: 'Failed to retrieve entity activity' });
        })
      );
  }

  /**
   * Get activities by date range
   */
  getActivitiesByDateRange(
    startDate: Date,
    endDate: Date,
    orgShortName?: string,
    limit: number = 100,
    skip: number = 0
  ): Observable<ActivityLogResponse> {
    let params = new HttpParams()
      .set('startDate', startDate.toISOString())
      .set('endDate', endDate.toISOString())
      .set('limit', limit.toString())
      .set('skip', skip.toString());

    if (orgShortName) {
      params = params.set('orgShortName', orgShortName);
    }

    return this.http.get<ActivityLogResponse>(`${this.apiUrl}/date-range`, { params })
      .pipe(
        tap(response => console.log('Activities by date range retrieved:', response)),
        catchError(error => {
          console.error('Error getting activities by date range:', error);
          return of({ success: false, data: [], message: 'Failed to retrieve activities by date range' });
        })
      );
  }

  /**
   * Get activity counts by type for analytics
   */
  getActivityCountsByType(orgShortName?: string, days: number = 30): Observable<{ success: boolean; data: Record<string, number> }> {
    let params = new HttpParams().set('days', days.toString());

    if (orgShortName) {
      params = params.set('orgShortName', orgShortName);
    }

    return this.http.get<{ success: boolean; data: Record<string, number> }>(`${this.apiUrl}/analytics/counts`, { params })
      .pipe(
        tap(response => console.log('Activity counts retrieved:', response)),
        catchError(error => {
          console.error('Error getting activity counts:', error);
          return of({ success: false, data: {} });
        })
      );
  }

  /**
   * Expose CommonActions for convenience
   */
  get actions() {
    return CommonActions;
  }
}
