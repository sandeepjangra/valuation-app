import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Bank } from '../models';

@Injectable({
  providedIn: 'root'
})
export class BankService {
  private readonly endpoint = 'banks';

  constructor(private apiService: ApiService) {}

  getAllBanks(): Observable<Bank[]> {
    return this.apiService.get<Bank[]>(this.endpoint);
  }

  getBankById(id: string): Observable<Bank> {
    return this.apiService.get<Bank>(`${this.endpoint}/${id}`);
  }

  createBank(bank: Partial<Bank>): Observable<Bank> {
    return this.apiService.post<Bank>(this.endpoint, bank);
  }

  updateBank(id: string, bank: Partial<Bank>): Observable<Bank> {
    return this.apiService.put<Bank>(`${this.endpoint}/${id}`, bank);
  }

  deleteBank(id: string): Observable<any> {
    return this.apiService.delete(`${this.endpoint}/${id}`);
  }

  getActiveBanks(): Observable<Bank[]> {
    return this.apiService.get<Bank[]>(`${this.endpoint}?active=true`);
  }
}