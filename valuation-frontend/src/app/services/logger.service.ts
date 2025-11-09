import { Injectable } from '@angular/core';
import { HttpRequest, HttpResponse, HttpErrorResponse } from '@angular/common/http';

export interface LogEntry {
  id: string;
  timestamp: string;
  type: 'request' | 'response' | 'error';
  method?: string;
  url?: string;
  requestHeaders?: any;
  requestBody?: any;
  responseStatus?: number;
  responseHeaders?: any;
  responseBody?: any;
  error?: any;
  processingTime?: number;
}

@Injectable({
  providedIn: 'root'
})
export class LoggerService {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Keep last 1000 log entries
  private requestStartTimes = new Map<string, number>();
  
  constructor() {
    // Try to load existing logs from localStorage
    this.loadLogsFromStorage();
  }

  /**
   * Generate a unique request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Log HTTP request
   */
  logRequest(request: HttpRequest<any>): string {
    const requestId = this.generateRequestId();
    const timestamp = new Date().toISOString();
    
    // Store start time for calculating processing time
    this.requestStartTimes.set(requestId, Date.now());
    
    const logEntry: LogEntry = {
      id: requestId,
      timestamp,
      type: 'request',
      method: request.method,
      url: request.url,
      requestHeaders: this.sanitizeHeaders(request.headers),
      requestBody: request.body
    };

    this.addLog(logEntry);
    
    // Console log for development
    console.log(`🔄 [${timestamp}] REQUEST ${request.method} ${request.url}`, {
      id: requestId,
      headers: logEntry.requestHeaders,
      body: request.body
    });

    return requestId;
  }

  /**
   * Log HTTP response
   */
  logResponse(requestId: string, response: HttpResponse<any>): void {
    const timestamp = new Date().toISOString();
    const startTime = this.requestStartTimes.get(requestId);
    const processingTime = startTime ? Date.now() - startTime : undefined;
    
    // Clean up start time
    this.requestStartTimes.delete(requestId);
    
    const logEntry: LogEntry = {
      id: requestId,
      timestamp,
      type: 'response',
      responseStatus: response.status,
      responseHeaders: this.sanitizeHeaders(response.headers),
      responseBody: response.body,
      processingTime
    };

    this.addLog(logEntry);
    
    // Console log for development
    const logLevel = response.status >= 400 ? 'error' : 'info';
    const emoji = response.status >= 400 ? '❌' : '✅';
    
    console[logLevel](`${emoji} [${timestamp}] RESPONSE ${response.status} (${processingTime}ms)`, {
      id: requestId,
      status: response.status,
      headers: logEntry.responseHeaders,
      body: response.body,
      processingTime: `${processingTime}ms`
    });
  }

  /**
   * Log HTTP error
   */
  logError(requestId: string, error: HttpErrorResponse): void {
    const timestamp = new Date().toISOString();
    const startTime = this.requestStartTimes.get(requestId);
    const processingTime = startTime ? Date.now() - startTime : undefined;
    
    // Clean up start time
    this.requestStartTimes.delete(requestId);
    
    const logEntry: LogEntry = {
      id: requestId,
      timestamp,
      type: 'error',
      responseStatus: error.status,
      error: {
        name: error.name,
        message: error.message,
        status: error.status,
        statusText: error.statusText,
        error: error.error
      },
      processingTime
    };

    this.addLog(logEntry);
    
    // Console log for development
    console.error(`❌ [${timestamp}] ERROR ${error.status} ${error.statusText} (${processingTime}ms)`, {
      id: requestId,
      error: error.error,
      message: error.message,
      processingTime: `${processingTime}ms`
    });
  }

  /**
   * Add log entry and manage storage
   */
  private addLog(logEntry: LogEntry): void {
    this.logs.unshift(logEntry);
    
    // Keep only the last maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs);
    }
    
    // Save to localStorage
    this.saveLogsToStorage();
  }

  /**
   * Sanitize headers (remove sensitive information)
   */
  private sanitizeHeaders(headers: any): any {
    if (!headers) return null;
    
    const sanitized: any = {};
    const sensitiveHeaders = ['authorization', 'cookie', 'x-api-key'];
    
    if (headers.keys) {
      // Angular HttpHeaders
      headers.keys().forEach((key: string) => {
        const lowerKey = key.toLowerCase();
        if (!sensitiveHeaders.includes(lowerKey)) {
          sanitized[key] = headers.get(key);
        }
      });
    } else {
      // Plain object
      Object.keys(headers).forEach(key => {
        const lowerKey = key.toLowerCase();
        if (!sensitiveHeaders.includes(lowerKey)) {
          sanitized[key] = headers[key];
        }
      });
    }
    
    return sanitized;
  }

  /**
   * Get all logs
   */
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Get logs filtered by type
   */
  getLogsByType(type: 'request' | 'response' | 'error'): LogEntry[] {
    return this.logs.filter(log => log.type === type);
  }

  /**
   * Get logs for a specific time range
   */
  getLogsByTimeRange(startTime: Date, endTime: Date): LogEntry[] {
    return this.logs.filter(log => {
      const logTime = new Date(log.timestamp);
      return logTime >= startTime && logTime <= endTime;
    });
  }

  /**
   * Clear all logs
   */
  clearLogs(): void {
    this.logs = [];
    this.requestStartTimes.clear();
    localStorage.removeItem('valuation_app_frontend_logs');
    console.log('🗑️ Frontend logs cleared');
  }

  /**
   * Export logs as JSON
   */
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  /**
   * Export logs as CSV
   */
  exportLogsAsCSV(): string {
    const headers = ['ID', 'Timestamp', 'Type', 'Method', 'URL', 'Status', 'Processing Time (ms)', 'Error'];
    const csvRows = [headers.join(',')];
    
    this.logs.forEach(log => {
      const row = [
        log.id,
        log.timestamp,
        log.type,
        log.method || '',
        log.url || '',
        log.responseStatus || '',
        log.processingTime || '',
        log.error?.message || ''
      ];
      csvRows.push(row.join(','));
    });
    
    return csvRows.join('\n');
  }

  /**
   * Save logs to localStorage
   */
  private saveLogsToStorage(): void {
    try {
      const logsToSave = this.logs.slice(0, 100); // Save only last 100 logs to localStorage
      localStorage.setItem('valuation_app_frontend_logs', JSON.stringify(logsToSave));
    } catch (error) {
      console.warn('Failed to save logs to localStorage:', error);
    }
  }

  /**
   * Load logs from localStorage
   */
  private loadLogsFromStorage(): void {
    try {
      const savedLogs = localStorage.getItem('valuation_app_frontend_logs');
      if (savedLogs) {
        this.logs = JSON.parse(savedLogs);
        console.log(`📂 Loaded ${this.logs.length} logs from localStorage`);
      }
    } catch (error) {
      console.warn('Failed to load logs from localStorage:', error);
      this.logs = [];
    }
  }

  /**
   * Get statistics about logs
   */
  getLogStats() {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    
    const lastHour = this.getLogsByTimeRange(oneHourAgo, now);
    const lastDay = this.getLogsByTimeRange(oneDayAgo, now);
    
    return {
      total: this.logs.length,
      lastHour: lastHour.length,
      lastDay: lastDay.length,
      errors: this.getLogsByType('error').length,
      requests: this.getLogsByType('request').length,
      responses: this.getLogsByType('response').length
    };
  }
}