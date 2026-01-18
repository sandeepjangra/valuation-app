import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PDFTemplate, PDFTemplateListItem } from '../models/pdf-template.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PDFTemplateService {
  private readonly http = inject(HttpClient);
  private readonly API_BASE_URL = environment.apiUrl;

  /**
   * Get all PDF templates for an organization
   */
  getPDFTemplates(organizationId: string): Observable<PDFTemplateListItem[]> {
    return this.http.get<PDFTemplateListItem[]>(`${this.API_BASE_URL}/pdf-templates`, {
      params: { organizationId }
    });
  }

  /**
   * Get a specific PDF template by ID
   */
  getPDFTemplate(templateId: string): Observable<PDFTemplate> {
    return this.http.get<PDFTemplate>(`${this.API_BASE_URL}/pdf-templates/${templateId}`);
  }

  /**
   * Create a new PDF template
   */
  createPDFTemplate(template: Omit<PDFTemplate, '_id' | 'createdAt' | 'updatedAt'>): Observable<PDFTemplate> {
    return this.http.post<PDFTemplate>(`${this.API_BASE_URL}/pdf-templates`, template);
  }

  /**
   * Update an existing PDF template
   */
  updatePDFTemplate(templateId: string, template: Partial<PDFTemplate>): Observable<PDFTemplate> {
    return this.http.put<PDFTemplate>(`${this.API_BASE_URL}/pdf-templates/${templateId}`, template);
  }

  /**
   * Delete a PDF template
   */
  deletePDFTemplate(templateId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_BASE_URL}/pdf-templates/${templateId}`);
  }

  /**
   * Generate PDF from template
   */
  generatePDF(templateId: string, data: any): Observable<Blob> {
    return this.http.post(`${this.API_BASE_URL}/pdf-templates/${templateId}/generate`, data, {
      responseType: 'blob'
    });
  }
}