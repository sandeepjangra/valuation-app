import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { LoggerService } from './logger.service';

@Injectable()
export class LoggingInterceptor implements HttpInterceptor {
  
  constructor(private logger: LoggerService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Log the request
    const requestId = this.logger.logRequest(req);
    
    return next.handle(req).pipe(
      tap(event => {
        // Log successful responses
        if (event instanceof HttpResponse) {
          this.logger.logResponse(requestId, event);
        }
      }),
      catchError((error: HttpErrorResponse) => {
        // Log error responses
        this.logger.logError(requestId, error);
        return throwError(() => error);
      })
    );
  }
}