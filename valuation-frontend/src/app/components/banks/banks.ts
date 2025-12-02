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
        headquarters: { city: "Mumbai", state: "Maharashtra", pincode: "400001" }
      },
      {
        _id: "68f3ebdea9483cef5ac839aa",
        bankCode: "HDFC",
        bankName: "HDFC Bank Limited",
        bankShortName: "HDFC Bank",
        bankType: "private_sector",
        isActive: true,
        headquarters: { city: "Mumbai", state: "Maharashtra", pincode: "400020" }
      },
      {
        _id: "68f3ebdea9483cef5ac839ab",
        bankCode: "ICICI",
        bankName: "ICICI Bank Limited",
        bankShortName: "ICICI Bank",
        bankType: "private_sector",
        isActive: true,
        headquarters: { city: "Mumbai", state: "Maharashtra", pincode: "400051" }
      },
      {
        _id: "68f3ebdea9483cef5ac839ac",
        bankCode: "PNB",
        bankName: "Punjab National Bank",
        bankShortName: "PNB",
        bankType: "public_sector",
        isActive: true,
        headquarters: { city: "New Delhi", state: "Delhi", pincode: "110001" }
      },
      {
        _id: "68f3ebdea9483cef5ac839ad",
        bankCode: "BOB",
        bankName: "Bank of Baroda",
        bankShortName: "BOB",
        bankType: "public_sector",
        isActive: true,
        headquarters: { city: "Vadodara", state: "Gujarat", pincode: "390007" }
      },
      {
        _id: "68f3ebdea9483cef5ac839ae",
        bankCode: "CANARA",
        bankName: "Canara Bank",
        bankShortName: "Canara Bank",
        bankType: "public_sector",
        isActive: true,
        headquarters: { city: "Bengaluru", state: "Karnataka", pincode: "560002" }
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

  createNewReport(bank: Bank) {
    console.log('Creating new report for bank:', bank.bankCode);
    this.router.navigate(['/new-report'], { 
      queryParams: { selectedBank: bank.bankCode } 
    });
  }

  getBankLogo(bankCode: string): string {
    const logos: { [key: string]: string } = {
      'SBI': '🏛️',
      'HDFC': '🏢',
      'ICICI': '🏦',
      'AXIS': '🏪',
      'PNB': '🏛️',
      'BOB': '🏦',
      'CANARA': '🏢',
      'UBI': '🏪',
      'IOB': '🏛️',
      'UNION': '🏦'
    };
    return logos[bankCode] || '🏦';
  }

  getBankThemeColor(bankCode: string): string {
    const colors: { [key: string]: string } = {
      'SBI': 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
      'HDFC': 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)',
      'ICICI': 'linear-gradient(135deg, #ea580c 0%, #f97316 100%)',
      'AXIS': 'linear-gradient(135deg, #7c2d12 0%, #a16207 100%)',
      'PNB': 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
      'BOB': 'linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%)',
      'CANARA': 'linear-gradient(135deg, #be123c 0%, #e11d48 100%)',
      'UBI': 'linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)',
      'IOB': 'linear-gradient(135deg, #4338ca 0%, #6366f1 100%)',
      'UNION': 'linear-gradient(135deg, #059669 0%, #10b981 100%)'
    };
    return colors[bankCode] || 'linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)';
  }

  getTemplateCount(bankCode: string): number {
    // Use actual template data from API
    const bank = this.banks.find(b => b.bankCode === bankCode);
    if (bank && (bank as any).templates) {
      const count = (bank as any).templates.length;
      console.log(`📊 ${bankCode} template count: ${count}`);
      return count;
    }
    // Fallback to 0 if no templates found
    console.log(`⚠️ No templates found for bank: ${bankCode}`);
    return 0;
  }

  getBankType(bankCode: string): string {
    const types: { [key: string]: string } = {
      'SBI': 'Public Sector',
      'HDFC': 'Private Sector', 
      'ICICI': 'Private Sector',
      'AXIS': 'Private Sector',
      'PNB': 'Public Sector',
      'BOB': 'Public Sector',
      'CANARA': 'Public Sector',
      'UBI': 'Public Sector',
      'IOB': 'Public Sector',
      'UNION': 'Public Sector'
    };
    return types[bankCode] || 'Unknown';
  }

  getBankHeadquarters(bankCode: string): string {
    const headquarters: { [key: string]: string } = {
      'SBI': 'Mumbai, Maharashtra',
      'HDFC': 'Mumbai, Maharashtra',
      'ICICI': 'Mumbai, Maharashtra',
      'AXIS': 'Mumbai, Maharashtra',
      'PNB': 'New Delhi, Delhi',
      'BOB': 'Mumbai, Maharashtra',
      'CANARA': 'Bengaluru, Karnataka',
      'UBI': 'Kolkata, West Bengal',
      'IOB': 'Chennai, Tamil Nadu',
      'UNION': 'Mumbai, Maharashtra'
    };
    return headquarters[bankCode] || 'Unknown';
  }

  getBankLogoPath(bankCode: string): string {
    // Return path to bank logo in assets folder
    return `assets/images/banks/${bankCode.toLowerCase()}.svg`;
  }

  onImageError(event: any, bankCode: string): void {
    console.log(`Failed to load SVG logo for bank: ${bankCode}, trying PNG...`);
    
    // If SVG fails, try PNG
    const currentSrc = event.target.src;
    if (currentSrc.includes('.svg')) {
      event.target.src = `assets/images/banks/${bankCode.toLowerCase()}.png`;
    } else {
      // If PNG also fails, use default
      console.log(`Failed to load PNG logo for bank: ${bankCode}, using default`);
      event.target.src = 'assets/images/banks/default-bank.svg';
    }
  }
}
