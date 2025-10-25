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
    // Mock data for fast loading - replace with actual data structure from banks.json
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
          templates: []
        },
        {
          _id: "68f3ebdea9483cef5ac839a9",
          bankCode: "PNB",
          bankName: "Punjab National Bank",
          bankShortName: "PNB",
          bankType: "public_sector",
          isActive: true,
          templates: [
            {
              templateId: "PNB_STANDARD_001",
              templateCode: "standard",
              templateName: "Standard Property Valuation",
              templateType: "property_valuation",
              propertyType: "all",
              description: "Standard template for all property types as per PNB guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_description", "location_details", "property_area", "construction_details", "legal_documents", "market_analysis", "valuation_method", "final_valuation"]
            }
          ]
        },
        {
          _id: "68fa36cd5bb6b9cffed41371",
          bankCode: "UNION",
          bankName: "Union Bank of India",
          bankShortName: "Union Bank",
          bankType: "public_sector",
          isActive: true,
          templates: [
            {
              templateId: "UNION_LAND_001",
              templateCode: "land",
              templateName: "Land Property Valuation",
              templateType: "property_valuation",
              propertyType: "land",
              description: "Template for land property valuation as per Union Bank guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_description", "location_details", "land_area", "survey_details", "boundaries", "legal_documents", "market_analysis", "valuation_method", "final_valuation"]
            },
            {
              templateId: "UNION_APARTMENT_001",
              templateCode: "apartment",
              templateName: "Apartment/Flat Property Valuation",
              templateType: "property_valuation",
              propertyType: "apartment",
              description: "Template for apartment/flat property valuation as per Union Bank guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_description", "location_details", "built_area", "super_area", "floor_details", "parking", "amenities", "legal_documents", "market_comparison", "valuation_method", "final_valuation"]
            }
          ]
        },
        {
          _id: "68fa37eeb2357c7d7163ff9f",
          bankCode: "BOB",
          bankName: "Bank of Baroda",
          bankShortName: "BOB",
          bankType: "public_sector",
          isActive: true,
          templates: [
            {
              templateId: "BOB_STANDARD_001",
              templateCode: "standard",
              templateName: "Standard Property Valuation",
              templateType: "property_valuation",
              propertyType: "all",
              description: "Standard template for all property types as per Bank of Baroda guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_description", "location_details", "property_area", "construction_quality", "legal_documents", "market_comparison", "valuation_approach", "final_valuation"]
            }
          ]
        },
        {
          _id: "68fa37efb2357c7d7163ffa0",
          bankCode: "UCO",
          bankName: "UCO Bank",
          bankShortName: "UCO Bank",
          bankType: "public_sector",
          isActive: true,
          templates: [
            {
              templateId: "UCO_STANDARD_001",
              templateCode: "standard",
              templateName: "Standard Property Valuation",
              templateType: "property_valuation",
              propertyType: "all",
              description: "Standard template for all property types as per UCO Bank guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_details", "geographical_location", "area_measurements", "construction_specifications", "documentation", "comparative_analysis", "valuation_process", "concluded_value"]
            }
          ]
        },
        {
          _id: "68fa37efb2357c7d7163ffa1",
          bankCode: "CBI",
          bankName: "Central Bank of India",
          bankShortName: "Central Bank",
          bankType: "public_sector",
          isActive: true,
          templates: [
            {
              templateId: "CBI_STANDARD_001",
              templateCode: "standard",
              templateName: "Standard Property Valuation",
              templateType: "property_valuation",
              propertyType: "all",
              description: "Standard template for all property types as per Central Bank of India guidelines",
              version: "1.0",
              isActive: true,
              fields: ["property_details", "geographical_location", "area_measurements", "construction_specifications", "documentation", "comparative_analysis", "valuation_process", "concluded_value"]
            }
          ]
        }
      ]
    };

    // Filter only active banks
    this.banks = banksData.documents.filter((bank: Bank) => bank.isActive);
    console.log('Banks loaded instantly:', this.banks.length);
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
