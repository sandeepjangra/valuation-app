import { Component, OnInit, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Bank, Template } from '../../models';
import { CustomTemplateService } from '../../services/custom-template.service';
import { CustomTemplateListItem } from '../../models/custom-template.model';

@Component({
  selector: 'app-new-report',
  imports: [CommonModule],
  templateUrl: './new-report.html',
  styleUrl: './new-report.css',
})
export class NewReport implements OnInit, OnDestroy {
  
  banks: Bank[] = [];
  selectedBank: Bank | null = null;
  selectedTemplate: Template | null = null;
  availableTemplates: Template[] = [];
  customTemplates: CustomTemplateListItem[] = [];
  selectedCustomTemplate: CustomTemplateListItem | null = null;
  isLoading = true; // Start with loading state
  isLoadingCustomTemplates = false;
  step = 1; // 1: Select Bank, 2: Select Template, 3: Optional Custom Template, 4: Ready to proceed

  constructor(
    private router: Router,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone,
    private customTemplateService: CustomTemplateService
  ) {}

  ngOnInit() {
    // Ensure we start fresh
    console.log('🚀 NewReport component initialized');
    this.loadBanksData();
  }

  ngOnDestroy() {
    console.log('🔄 NewReport component destroyed');
    // Cleanup if needed
  }

  loadBanksData() {
    // Load banks data dynamically from API
    console.log('🔄 Loading banks data from API...');
    this.isLoading = true;
    
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
          // Filter only active banks
          this.banks = banksData.filter((bank: Bank) => bank.isActive);
          console.log('✅ Banks loaded from API:', this.banks.length);
          console.log('🏦 Available banks:', this.banks.map(b => `${b.bankCode} (${b.templates?.length || 0} templates)`));
          this.isLoading = false;
          
          // Force change detection
          this.cdr.detectChanges();
        });
      })
      .catch(error => {
        console.error('❌ Error loading banks from API:', error);
        this.ngZone.run(() => {
          console.log('🔄 Using fallback data...');
          this.loadBanksFallback();
          this.isLoading = false;
          this.cdr.detectChanges();
        });
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
    console.log('🏦 Bank selected:', bank.bankCode, bank.bankName);
    this.selectedBank = bank;
    this.selectedTemplate = null;
    this.availableTemplates = bank.templates || [];
    
    console.log('📋 Available templates for bank:', this.availableTemplates.length);
    
    if (this.availableTemplates.length > 0) {
      this.step = 2;
      console.log('➡️ Moving to step 2: Template selection');
    } else {
      // No templates available for this bank
      this.step = 3;
      console.log('➡️ Moving to step 3: No templates available');
    }
    
    // Force change detection
    this.cdr.detectChanges();
  }

  selectTemplate(template: Template) {
    console.log('📋 Template selected:', template.templateCode, template.templateName);
    this.selectedTemplate = template;
    this.selectedCustomTemplate = null; // Reset custom template selection
    
    // Load custom templates for this bank and property type
    this.loadCustomTemplates(this.selectedBank!.bankCode, template.propertyType);
    
    this.step = 3;
    console.log('➡️ Moving to step 3: Optional custom template selection');
    
    // Force change detection
    this.cdr.detectChanges();
  }

  loadCustomTemplates(bankCode: string, propertyType: string): void {
    this.isLoadingCustomTemplates = true;
    this.customTemplateService.getTemplates(bankCode, propertyType as 'land' | 'apartment').subscribe({
      next: (response) => {
        this.customTemplates = response.data;
        console.log(`✅ Loaded ${this.customTemplates.length} custom templates`);
        this.isLoadingCustomTemplates = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('❌ Failed to load custom templates:', error);
        this.customTemplates = [];
        this.isLoadingCustomTemplates = false;
        this.cdr.detectChanges();
      }
    });
  }

  selectCustomTemplate(customTemplate: CustomTemplateListItem | null): void {
    this.selectedCustomTemplate = customTemplate;
    if (customTemplate) {
      console.log('📝 Custom template selected:', customTemplate.templateName);
    } else {
      console.log('❌ No custom template selected');
    }
    this.step = 4;
    this.cdr.detectChanges();
  }

  skipCustomTemplate(): void {
    this.selectedCustomTemplate = null;
    this.step = 4;
    this.cdr.detectChanges();
  }

  goBack() {
    if (this.step === 2) {
      this.step = 1;
      this.selectedBank = null;
      this.selectedTemplate = null;
      this.selectedCustomTemplate = null;
      this.availableTemplates = [];
      this.customTemplates = [];
    } else if (this.step === 3) {
      this.step = 2;
      this.selectedTemplate = null;
      this.selectedCustomTemplate = null;
      this.customTemplates = [];
    } else if (this.step === 4) {
      this.step = 3;
      this.selectedCustomTemplate = null;
    }
  }

  proceedToForm() {
    if (this.selectedBank) {
      console.log('🚀 Proceeding to form with bank:', this.selectedBank.bankCode);
      
      // Navigate to report form with bank and template info
      const queryParams: any = {
        bankCode: this.selectedBank.bankCode,
        bankName: this.selectedBank.bankName
      };
      
      if (this.selectedTemplate) {
        console.log('📋 Including template:', this.selectedTemplate.templateCode);
        queryParams.templateId = this.selectedTemplate.templateCode; // Use templateCode for URL
        queryParams.templateName = this.selectedTemplate.templateName;
        queryParams.propertyType = this.selectedTemplate.propertyType;
      }

      // Add custom template ID if selected
      if (this.selectedCustomTemplate) {
        console.log('📝 Including custom template:', this.selectedCustomTemplate._id);
        queryParams.customTemplateId = this.selectedCustomTemplate._id;
        queryParams.customTemplateName = this.selectedCustomTemplate.templateName;
      }
      
      console.log('🔗 Navigating to report-form with params:', queryParams);
      this.router.navigate(['/report-form'], { queryParams });
    } else {
      console.error('❌ No bank selected - cannot proceed');
    }
  }

  cancelAndGoBack() {
    this.router.navigate(['/dashboard']);
  }

  getBankThemeColor(bankCode: string): string {
    const colors: { [key: string]: string } = {
      'SBI': '#22409A',      // SBI Blue
      'PNB': '#E31E24',      // PNB Red
      'BOB': '#ED8B00',      // BOB Orange
      'UBI': '#D32F2F',      // UBI Red
      'BOI': '#0066B3',      // BOI Blue
      'CBI': '#1A237E',      // CBI Dark Blue
      'IOB': '#00796B',      // IOB Teal
      'CANARA': '#D32F2F',   // Canara Red
      'UCO': '#6A1B9A',      // UCO Purple
      'HDFC': '#004C8F',     // HDFC Blue
      'ICICI': '#F37021',    // ICICI Orange
      'AXIS': '#800080'      // Axis Purple
    };
    return colors[bankCode] || '#6b7280';
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
