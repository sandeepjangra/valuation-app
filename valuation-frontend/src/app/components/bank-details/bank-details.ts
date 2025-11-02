import { Component, OnInit, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Bank } from '../../models/bank.model';

@Component({
  selector: 'app-bank-details',
  imports: [CommonModule],
  templateUrl: './bank-details.html',
  styleUrl: './bank-details.css',
})
export class BankDetails implements OnInit, OnDestroy {
  bank: Bank | null = null;
  loading = true;
  error = '';
  bankId = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    console.log('🚀 BankDetails component initialized');
    this.bankId = this.route.snapshot.params['id'];
    this.loadBankDetails();
  }

  ngOnDestroy() {
    console.log('🔄 BankDetails component destroyed');
  }

  loadBankDetails() {
    console.log('🔄 Loading bank details from API for:', this.bankId);
    this.loading = true;
    
    fetch(`http://localhost:8000/api/banks/${this.bankId.toUpperCase()}`)
      .then(response => {
        console.log('📡 API Response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(bankData => {
        console.log('📊 Bank data received:', bankData);
        
        this.ngZone.run(() => {
          this.bank = bankData;
          console.log('✅ Bank details loaded from API');
          this.loading = false;
          
          this.cdr.detectChanges();
        });
      })
      .catch(error => {
        console.error('❌ Error loading bank details from API:', error);
        this.ngZone.run(() => {
          this.error = 'Failed to load bank details.';
          this.loading = false;
          this.cdr.detectChanges();
        });
      });
  }

  goBack() {
    this.router.navigate(['/banks']);
  }

  goToReportForm(template: any) {
    if (this.bank) {
      const queryParams = {
        bankCode: this.bank.bankCode,
        bankName: this.bank.bankName,
        templateId: template.templateCode,
        templateName: template.templateName,
        propertyType: template.propertyType
      };
      
      console.log('🔗 Navigating to report-form with params:', queryParams);
      this.router.navigate(['/report-form'], { queryParams });
    }
  }
}