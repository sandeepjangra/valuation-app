import { Component, OnInit, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Bank } from '../../models/bank.model';

@Component({
  selector: 'app-banks',
  imports: [CommonModule],
  templateUrl: './banks.html',
  styleUrl: './banks.css',
})
export class Banks implements OnInit, OnDestroy {
  banks: Bank[] = [];
  loading = true;
  error = '';

  constructor(
    private router: Router,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    // Ensure we start fresh
    console.log('🚀 Banks component initialized');
    this.resetComponent();
    this.loadBanks();
  }

  ngOnDestroy() {
    console.log('🔄 Banks component destroyed');
    // Cleanup if needed
  }

  resetComponent() {
    this.banks = [];
    this.loading = true;
    this.error = '';
  }

  loadBanks() {
    // Load banks data dynamically from API
    console.log('🔄 Loading banks data from API...');
    this.loading = true;
    
    // Use fetch to get banks data from API with proper error handling
    fetch('http://localhost:8000/api/banks')
      .then(response => {
        console.log('📡 API Response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(banksData => {
        console.log('📊 Raw banks data received:', banksData.length);
        
        // Run in NgZone to ensure change detection
        this.ngZone.run(() => {
          this.banks = banksData;
          console.log('✅ Banks loaded from API:', this.banks.length);
          this.loading = false;
          
          // Force change detection
          this.cdr.detectChanges();
        });
      })
      .catch(error => {
        console.error('❌ Error loading banks from API:', error);
        this.ngZone.run(() => {
          console.log('🔄 Using fallback data...');
          this.loadBanksFallback();
          this.loading = false;
          this.cdr.detectChanges();
        });
      });
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }

  private loadBanksFallback() {
    // Fallback data - kept for emergency fallback only
    const banksData = [
      {
        _id: "68f3ebdea9483cef5ac839a8",
        bankCode: "SBI",
        bankName: "State Bank of India",
        bankShortName: "SBI",
        bankType: "public_sector",
        isActive: true,
        headquarters: {
          city: "Mumbai",
          state: "Maharashtra",
          pincode: "400001"
        }
      },
      {
        _id: "68f3ebdea9483cef5ac839aa",
        bankCode: "HDFC",
        bankName: "HDFC Bank Limited",
        bankShortName: "HDFC Bank",
        bankType: "private_sector",
        isActive: true,
        headquarters: {
          city: "Mumbai",
          state: "Maharashtra",
          pincode: "400020"
        }
      }
    ];

    this.banks = banksData;
    console.log('🔄 Fallback banks loaded:', this.banks.length);
  }

  retryLoad() {
    this.resetComponent();
    this.loadBanks();
  }

  viewBankDetails(bank: Bank) {
    this.router.navigate(['/bank-details', bank.bankCode]);
  }
}
