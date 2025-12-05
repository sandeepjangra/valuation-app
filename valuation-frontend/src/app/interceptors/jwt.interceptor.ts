/**
 * JWT Token Interceptor for Organization Management
 * Automatically adds JWT tokens to HTTP requests and handles token refresh
 */

import { Injectable, inject } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpErrorResponse,
  HttpStatusCode
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject, of } from 'rxjs';
import { catchError, switchMap, filter, take, finalize } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { environment } from '../../environments/environment';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
  private readonly authService = inject(AuthService);
  
  // Token refresh state management
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<string | null> = new BehaviorSubject<string | null>(null);
  
  // URLs that don't need authorization headers
  private readonly excludedUrls: string[] = [
    '/auth/login',
    '/auth/register',
    '/auth/forgot-password',
    '/auth/reset-password',
    '/public/',
    '/api/pdf/',
    '/api/custom-templates',
    '/api/banks'
  ];

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip interceptor for excluded URLs
    if (this.shouldSkipInterceptor(request.url)) {
      return next.handle(request);
    }

    // Add JWT token if user is authenticated
    if (this.authService.isAuthenticated()) {
      request = this.addTokenToRequest(request);
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        // Handle 401 Unauthorized errors with token refresh
        if (error.status === HttpStatusCode.Unauthorized && this.authService.isAuthenticated()) {
          return this.handle401Error(request, next);
        }

        // Handle other errors
        return throwError(() => error);
      })
    );
  }

  /**
   * Add JWT token to request headers
   */
  private addTokenToRequest(request: HttpRequest<any>): HttpRequest<any> {
    const token = this.authService.getToken();
    
    if (token) {
      return request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
    }

    return request;
  }

  /**
   * Handle 401 Unauthorized errors with token refresh
   */
  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      return this.authService.refreshToken().pipe(
        switchMap((newToken: string) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(newToken);
          
          // Retry original request with new token
          const newRequest = this.addTokenToRequest(request);
          return next.handle(newRequest);
        }),
        catchError((error) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(null);
          
          // Refresh failed, logout user
          this.authService.logout();
          return throwError(() => error);
        }),
        finalize(() => {
          this.isRefreshing = false;
        })
      );
    } else {
      // Token refresh is in progress, wait for it to complete
      return this.refreshTokenSubject.pipe(
        filter(token => token !== null),
        take(1),
        switchMap((token) => {
          // Retry original request with refreshed token
          const newRequest = this.addTokenToRequest(request);
          return next.handle(newRequest);
        })
      );
    }
  }

  /**
   * Check if interceptor should be skipped for this URL
   */
  private shouldSkipInterceptor(url: string): boolean {
    // Skip if it's not an API call
    const apiBase = environment.apiUrl || 'http://localhost:8000/api';
    if (!url.startsWith(apiBase)) {
      return true;
    }

    // Skip for excluded URLs
    return this.excludedUrls.some(excludedUrl => url.includes(excludedUrl));
  }
}

/**
 * Error Handling Interceptor
 * Provides consistent error handling and logging for API responses
 */
@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  private readonly authService = inject(AuthService);

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An unexpected error occurred';
        let shouldLogout = false;

        switch (error.status) {
          case HttpStatusCode.BadRequest:
            errorMessage = this.extractErrorMessage(error, 'Invalid request data');
            break;

          case HttpStatusCode.Unauthorized:
            errorMessage = 'Authentication required';
            shouldLogout = true;
            break;

          case HttpStatusCode.Forbidden:
            errorMessage = 'Access denied - insufficient permissions';
            break;

          case HttpStatusCode.NotFound:
            errorMessage = 'Resource not found';
            break;

          case HttpStatusCode.Conflict:
            errorMessage = this.extractErrorMessage(error, 'Data conflict occurred');
            break;

          case HttpStatusCode.UnprocessableEntity:
            errorMessage = this.extractErrorMessage(error, 'Validation failed');
            break;

          case HttpStatusCode.TooManyRequests:
            errorMessage = 'Too many requests - please try again later';
            break;

          case HttpStatusCode.InternalServerError:
            errorMessage = 'Server error - please try again';
            break;

          case HttpStatusCode.BadGateway:
          case HttpStatusCode.ServiceUnavailable:
          case HttpStatusCode.GatewayTimeout:
            errorMessage = 'Service temporarily unavailable';
            break;

          default:
            if (error.error instanceof ErrorEvent) {
              // Client-side network error
              errorMessage = `Network error: ${error.error.message}`;
            } else {
              // Server-side error
              errorMessage = this.extractErrorMessage(error, errorMessage);
            }
        }

        // Log error details for debugging
        console.error('🚫 HTTP Error:', {
          status: error.status,
          statusText: error.statusText,
          message: errorMessage,
          url: request.url,
          method: request.method,
          timestamp: new Date().toISOString()
        });

        // Logout on unauthorized errors
        if (shouldLogout && this.authService.isAuthenticated()) {
          this.authService.logout();
        }

        // Create enhanced error object
        const enhancedError = new Error(errorMessage);
        (enhancedError as any).status = error.status;
        (enhancedError as any).statusText = error.statusText;
        (enhancedError as any).originalError = error;

        return throwError(() => enhancedError);
      })
    );
  }

  /**
   * Extract meaningful error message from HTTP error response
   */
  private extractErrorMessage(error: HttpErrorResponse, fallback: string): string {
    if (error.error) {
      // Try to extract error message from various response formats
      if (typeof error.error === 'string') {
        return error.error;
      }

      if (error.error.message) {
        return error.error.message;
      }

      if (error.error.error) {
        return error.error.error;
      }

      if (error.error.detail) {
        return error.error.detail;
      }

      // Handle validation errors
      if (error.error.validation_errors && Array.isArray(error.error.validation_errors)) {
        const validationMessages = error.error.validation_errors
          .map((ve: any) => `${ve.field}: ${ve.message}`)
          .join(', ');
        return `Validation errors: ${validationMessages}`;
      }
    }

    return fallback;
  }
}

/**
 * Loading Interceptor
 * Shows/hides loading indicator for HTTP requests
 */
@Injectable()
export class LoadingInterceptor implements HttpInterceptor {
  private activeRequests = 0;
  private loadingSubject = new BehaviorSubject<boolean>(false);
  
  // Observable for components to subscribe to loading state
  public loading$ = this.loadingSubject.asObservable();

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip loading indicator for certain requests
    if (this.shouldSkipLoading(request)) {
      return next.handle(request);
    }

    // Increment active requests and show loading
    this.activeRequests++;
    this.updateLoadingState();

    return next.handle(request).pipe(
      finalize(() => {
        // Decrement active requests and update loading state
        this.activeRequests--;
        this.updateLoadingState();
      })
    );
  }

  private updateLoadingState(): void {
    this.loadingSubject.next(this.activeRequests > 0);
  }

  private shouldSkipLoading(request: HttpRequest<any>): boolean {
    // Skip loading for background requests or polling
    return (
      request.headers.has('skip-loading') ||
      request.url.includes('/health') ||
      request.url.includes('/ping') ||
      request.method === 'HEAD'
    );
  }

  /**
   * Get current loading state
   */
  isLoading(): boolean {
    return this.loadingSubject.value;
  }
}

/**
 * Organization Context Interceptor
 * Adds organization context headers to requests
 */
@Injectable()
export class OrganizationInterceptor implements HttpInterceptor {
  private readonly authService = inject(AuthService);

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const orgContext = this.authService.getOrganizationContext();
    
    if (orgContext && !this.shouldSkipOrganizationHeaders(request.url)) {
      const modifiedRequest = request.clone({
        setHeaders: {
          'X-Organization-Short-Name': orgContext.orgShortName,
          'X-Organization-ID': orgContext.organizationId, // Backward compatibility
          'X-User-Roles': orgContext.roles.join(',')
        }
      });
      
      console.log('📤 Adding organization headers:', {
        orgShortName: orgContext.orgShortName,
        roles: orgContext.roles,
        url: request.url
      });
      
      return next.handle(modifiedRequest);
    }

    return next.handle(request);
  }

  private shouldSkipOrganizationHeaders(url: string): boolean {
    const skipPaths = ['/auth/', '/public/', '/system/'];
    return skipPaths.some(path => url.includes(path));
  }
}