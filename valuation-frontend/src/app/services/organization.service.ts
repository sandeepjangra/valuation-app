/**
 * Angular Organization Service
 * Handles organization management API calls (shared endpoints, not org-scoped)
 * 
 * NOTE: User and Report management methods are deprecated.
 * Use UserService and ReportsService instead for org-scoped operations.
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import {
  Organization,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  ApiResponse
} from '../models/organization.model';
import { AuthService } from './auth.service';
import { OrganizationContextService } from './organization-context.service';

@Injectable({
  providedIn: 'root'
})
export class OrganizationService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly orgContext = inject(OrganizationContextService);

  constructor() {}

  /**
   * Transform .NET backend response (camelCase) to frontend model (snake_case)
   */
  private transformOrganization(backendOrg: any): Organization {
    return {
      _id: backendOrg.id || backendOrg._id,
      org_short_name: backendOrg.shortName || backendOrg.org_short_name,
      name: backendOrg.fullName || backendOrg.name,
      type: 'valuation_company',
      description: backendOrg.description,
      contact_email: backendOrg.contactEmail || backendOrg.contact_email,
      phone_number: backendOrg.contactPhone || backendOrg.phone_number,
      report_reference_initials: backendOrg.reportReferenceInitials || backendOrg.report_reference_initials,
      last_reference_number: backendOrg.lastReferenceNumber || backendOrg.last_reference_number || 0,
      subscription_plan: 'basic',
      max_users: 25,
      max_reports: 100,
      is_active: backendOrg.isActive !== undefined ? backendOrg.isActive : true,
      created_at: new Date(backendOrg.createdAt || backendOrg.created_at),
      updated_at: new Date(backendOrg.updatedAt || backendOrg.updated_at),
      total_users: backendOrg.userCount || backendOrg.total_users || 0,
      total_reports: backendOrg.reportCount || backendOrg.total_reports || 0
    };
  }

  getCurrentOrganization(): Observable<Organization> {
    const orgShortName = this.orgContext.getOrganization();
    if (!orgShortName) {
      return throwError(() => new Error('No organization context available'));
    }
    return this.getOrganizationByShortName(orgShortName);
  }

  getAllOrganizations(): Observable<Organization[]> {
    const url = this.orgContext.getSharedApiUrl('organizations');
    return this.http.get<any>(url).pipe(
      map((response: any) => {
        if (response.success && response.data) {
          const orgs = Array.isArray(response.data) ? response.data : [response.data];
          return orgs.map((org: any) => this.transformOrganization(org));
        }
        return [];
      }),
      catchError(this.handleError.bind(this))
    );
  }

  getOrganizationByShortName(shortName: string): Observable<Organization> {
    const url = this.orgContext.getSharedApiUrl(`organizations/${shortName}`);
    return this.http.get<any>(url).pipe(
      map(response => {
        if (response.success && response.data) {
          return this.transformOrganization(response.data);
        }
        return this.transformOrganization(response);
      }),
      catchError(this.handleError.bind(this))
    );
  }

  getOrganizationById(id: string): Observable<Organization> {
    const url = this.orgContext.getSharedApiUrl(`organizations/${id}`);
    return this.http.get<any>(url).pipe(
      map(response => {
        if (response.success && response.data) {
          return this.transformOrganization(response.data);
        }
        return this.transformOrganization(response);
      }),
      catchError(this.handleError.bind(this))
    );
  }

  createOrganization(organizationData: CreateOrganizationRequest): Observable<string> {
    const url = this.orgContext.getSharedApiUrl('organizations');
    return this.http.post<any>(url, organizationData).pipe(
      map(response => {
        if (!response.success || !response.data) {
          throw new Error(response.message || 'Failed to create organization');
        }
        return response.data.organization_id || response.data.id;
      }),
      catchError(this.handleError.bind(this))
    );
  }

  updateOrganization(organizationId: string, updates: UpdateOrganizationRequest): Observable<boolean> {
    const url = this.orgContext.getSharedApiUrl(`organizations/${organizationId}`);
    return this.http.put<any>(url, updates).pipe(
      map(response => response.success),
      catchError(this.handleError.bind(this))
    );
  }

  deleteOrganization(organizationId: string): Observable<boolean> {
    const url = this.orgContext.getSharedApiUrl(`organizations/${organizationId}`);
    return this.http.delete<any>(url).pipe(
      map(response => response.success),
      catchError(this.handleError.bind(this))
    );
  }

  getNextReferenceNumber(orgShortName?: string): Observable<any> {
    const org = orgShortName || this.orgContext.getOrganization();
    if (!org) {
      return throwError(() => new Error('No organization context available'));
    }
    const url = this.orgContext.getOrgApiUrl('next-reference-number');
    if (!url) {
      return throwError(() => new Error('Failed to build org URL'));
    }
    return this.http.get<any>(url).pipe(
      map(response => {
        if (!response.success || !response.data) {
          throw new Error(response.message || 'Failed to get reference number');
        }
        return response.data;
      }),
      catchError(this.handleError.bind(this))
    );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      if (error.error?.message) {
        errorMessage = error.error.message;
      } else if (error.error?.errors) {
        const validationErrors = Object.values(error.error.errors).flat();
        errorMessage = validationErrors.join(', ');
      } else {
        errorMessage = `Server Error: ${error.status} - ${error.message}`;
      }
    }
    console.error('❌ OrganizationService Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
