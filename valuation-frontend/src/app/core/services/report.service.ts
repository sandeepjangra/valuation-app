import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ValuationReport } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private readonly endpoint = 'reports';

  constructor(private apiService: ApiService) {}

  getAllReports(): Observable<ValuationReport[]> {
    return this.apiService.get<ValuationReport[]>(this.endpoint);
  }

  getReportById(id: string): Observable<ValuationReport> {
    return this.apiService.get<ValuationReport>(`${this.endpoint}/${id}`);
  }

  getReportsByUser(userId: string): Observable<ValuationReport[]> {
    return this.apiService.get<ValuationReport[]>(`${this.endpoint}?userId=${userId}`);
  }

  getReportsByTemplate(templateId: string): Observable<ValuationReport[]> {
    return this.apiService.get<ValuationReport[]>(`${this.endpoint}?templateId=${templateId}`);
  }

  getReportsByStatus(status: string): Observable<ValuationReport[]> {
    return this.apiService.get<ValuationReport[]>(`${this.endpoint}?status=${status}`);
  }

  createReport(report: Partial<ValuationReport>): Observable<ValuationReport> {
    return this.apiService.post<ValuationReport>(this.endpoint, report);
  }

  updateReport(id: string, report: Partial<ValuationReport>): Observable<ValuationReport> {
    return this.apiService.put<ValuationReport>(`${this.endpoint}/${id}`, report);
  }

  deleteReport(id: string): Observable<any> {
    return this.apiService.delete(`${this.endpoint}/${id}`);
  }

  submitReport(id: string): Observable<ValuationReport> {
    return this.apiService.put<ValuationReport>(`${this.endpoint}/${id}/submit`, {});
  }

  approveReport(id: string): Observable<ValuationReport> {
    return this.apiService.put<ValuationReport>(`${this.endpoint}/${id}/approve`, {});
  }

  rejectReport(id: string, reason: string): Observable<ValuationReport> {
    return this.apiService.put<ValuationReport>(`${this.endpoint}/${id}/reject`, { reason });
  }
}