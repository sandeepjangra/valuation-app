import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Template, TemplateField } from '../models';

@Injectable({
  providedIn: 'root'
})
export class TemplateService {
  private readonly endpoint = 'templates';

  constructor(private apiService: ApiService) {}

  getAllTemplates(): Observable<Template[]> {
    return this.apiService.get<Template[]>(this.endpoint);
  }

  getTemplateById(id: string): Observable<Template> {
    return this.apiService.get<Template>(`${this.endpoint}/${id}`);
  }

  getTemplatesByBank(bankId: string): Observable<Template[]> {
    return this.apiService.get<Template[]>(`${this.endpoint}?bankId=${bankId}`);
  }

  getTemplatesByPropertyType(propertyTypeId: string): Observable<Template[]> {
    return this.apiService.get<Template[]>(`${this.endpoint}?propertyTypeId=${propertyTypeId}`);
  }

  getTemplatesByBankAndPropertyType(bankId: string, propertyTypeId: string): Observable<Template[]> {
    return this.apiService.get<Template[]>(`${this.endpoint}?bankId=${bankId}&propertyTypeId=${propertyTypeId}`);
  }

  createTemplate(template: Partial<Template>): Observable<Template> {
    return this.apiService.post<Template>(this.endpoint, template);
  }

  updateTemplate(id: string, template: Partial<Template>): Observable<Template> {
    return this.apiService.put<Template>(`${this.endpoint}/${id}`, template);
  }

  deleteTemplate(id: string): Observable<any> {
    return this.apiService.delete(`${this.endpoint}/${id}`);
  }

  getActiveTemplates(): Observable<Template[]> {
    return this.apiService.get<Template[]>(`${this.endpoint}?active=true`);
  }
}