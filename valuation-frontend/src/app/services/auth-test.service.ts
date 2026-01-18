import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthTestService {
  private readonly http = inject(HttpClient);
  private readonly API_BASE_URL = environment.apiUrl;

  /**
   * Test authentication with a simple authenticated endpoint
   */
  testAuth(): Observable<any> {
    console.log('🧪 Testing authentication...');
    
    // Check what's in localStorage
    const authData = localStorage.getItem('auth_data');
    const accessToken = localStorage.getItem('access_token');
    
    console.log('🔍 Auth data in localStorage:', {
      hasAuthData: !!authData,
      hasAccessToken: !!accessToken,
      authDataPreview: authData ? authData.substring(0, 100) + '...' : null,
      tokenPreview: accessToken ? accessToken.substring(0, 50) + '...' : null
    });

    return this.http.get(`${this.API_BASE_URL}/auth/me`);
  }

  /**
   * Test organization-specific endpoint
   */
  testOrgEndpoint(orgShortName: string): Observable<any> {
    console.log('🧪 Testing org endpoint for:', orgShortName);
    return this.http.get(`${this.API_BASE_URL}/organizations/${orgShortName}/next-reference-number`);
  }
}