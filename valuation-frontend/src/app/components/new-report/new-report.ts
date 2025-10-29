import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Bank, Template } from '../../models';

@Component({
  selector: 'app-new-report',
  imports: [CommonModule],
  templateUrl: './new-report.html',
  styleUrl: './new-report.css',
})
export class NewReport implements OnInit {
  
  banks: Bank[] = [];
  selectedBank: Bank | null = null;
  selectedTemplate: Template | null = null;
  availableTemplates: Template[] = [];
  isLoading = false; // Set to false since we're loading data synchronously
  step = 1; // 1: Select Bank, 2: Select Template, 3: Ready to proceed

  constructor(private router: Router) {}

  ngOnInit() {
    this.loadBanksData();
  }

  loadBanksData() {
    // Load banks data dynamically from API
    this.isLoading = true;
    
    // Use fetch to get banks data from API
    fetch('http://localhost:8000/api/banks')
      .then(response => response.json())
      .then(banksData => {
        // Filter only active banks
        this.banks = banksData.filter((bank: Bank) => bank.isActive);
        console.log('✅ Banks loaded from API:', this.banks.length);
        console.log('🏦 Available banks:', this.banks.map(b => `${b.bankCode} (${b.templates?.length || 0} templates)`));
        this.isLoading = false;
      })
      .catch(error => {
        console.error('❌ Error loading banks from API, using fallback data:', error);
        this.loadBanksFallback();
        this.isLoading = false;
      });
  }

  private loadBanksFallback() {
    // Fallback data - kept for emergency fallback only
    const banksData = {
      documents: [
        {
          _id: "68f3ebdea9483cef5ac839a8",
          bankCode: "SBI",
          bankName: "State Bank of India",
          bankShortName: "SBI",
          bankType: "public_sector",
          isActive: true,
          templates: [
            {
              templateId: "SBI_LAND_REF_001",
              templateCode: "land",
              templateName: "Land Property Valuation",
              templateType: "property_valuation",
              propertyType: "land",
              description: "Template for land property valuation as per SBI guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_description", "location_details", "land_area", "boundaries", "legal_documents", "market_analysis", "valuation_method", "final_valuation"]
            },
            {
              templateId: "SBI_APARTMENT_REF_001",
              templateCode: "apartment",
              templateName: "Apartment/Flat Property Valuation",
              templateType: "property_valuation",
              propertyType: "apartment",
              description: "Template for apartment/flat property valuation as per SBI guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_description", "location_details", "built_area", "carpet_area", "floor_details", "amenities", "legal_documents", "market_comparison", "valuation_method", "final_valuation"]
            }
          ]
        },
        {
          _id: "68f3ebdea9483cef5ac839aa",
          bankCode: "HDFC",
          bankName: "HDFC Bank Limited",
          bankShortName: "HDFC Bank",
          bankType: "private_sector",
          isActive: true,
          templates: [
            {
              templateId: "HDFC_ALL_REF_001",
              templateCode: "all",
              templateName: "HDFC Property Valuation",
              templateType: "property_valuation",
              propertyType: "all",
              description: "Unified template for all property types",
              version: "2.0",
              isActive: true,
              fields: ["property_description", "location_details", "property_area", "construction_details", "legal_documents", "market_analysis", "valuation_method", "final_valuation"]
            }
          ]
        }
      ]
    };

    // Filter only active banks from fallback data
    this.banks = banksData.documents.filter((bank: Bank) => bank.isActive);
    console.log('🔄 Fallback banks loaded:', this.banks.length);
  }

  selectBank(bank: Bank) {
    this.selectedBank = bank;
    this.selectedTemplate = null;
    this.availableTemplates = bank.templates || [];
    
    if (this.availableTemplates.length > 0) {
      this.step = 2;
    } else {
      // No templates available for this bank
      this.step = 3;
    }
  }

  selectTemplate(template: Template) {
    this.selectedTemplate = template;
    this.step = 3;
  }

  goBack() {
    if (this.step === 2) {
      this.step = 1;
      this.selectedBank = null;
      this.selectedTemplate = null;
      this.availableTemplates = [];
    } else if (this.step === 3) {
      if (this.availableTemplates.length > 0) {
        this.step = 2;
        this.selectedTemplate = null;
      } else {
        this.step = 1;
        this.selectedBank = null;
        this.selectedTemplate = null;
        this.availableTemplates = [];
      }
    }
  }

  proceedToForm() {
    if (this.selectedBank) {
      // Navigate to report form with bank and template info
      const queryParams: any = {
        bankCode: this.selectedBank.bankCode,
        bankName: this.selectedBank.bankName
      };
      
      if (this.selectedTemplate) {
        queryParams.templateId = this.selectedTemplate.templateCode; // Use templateCode for URL
        queryParams.templateName = this.selectedTemplate.templateName;
        queryParams.propertyType = this.selectedTemplate.propertyType;
      }
      
      this.router.navigate(['/report-form'], { queryParams });
    }
  }

  cancelAndGoBack() {
    this.router.navigate(['/dashboard']);
  }

  getBankIcon(bankCode: string): string {
    const icons: { [key: string]: string } = {
      'SBI': '🏛️',
      'HDFC': '🏢',
      'PNB': '🏦',
      'ICICI': '🏪',
      'UNION': '🏛️',
      'BOB': '🏦',
      'UCO': '🏛️',
      'CBI': '🏢'
    };
    return icons[bankCode] || '🏦';
  }

  getPropertyTypeIcon(propertyType: string): string {
    const icons: { [key: string]: string } = {
      'land': '🏞️',
      'apartment': '🏠',
      'all': '🏘️',
      'standard': '📋'
    };
    return icons[propertyType] || '🏘️';
  }
}
