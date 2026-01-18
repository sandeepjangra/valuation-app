import { Component, OnInit, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Bank, Template } from '../../models';
import { CustomTemplateService } from '../../services/custom-template.service';
import { CustomTemplateListItem } from '../../models/custom-template.model';
import { PdfProcessorService } from '../../services/pdf-processor.service';

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
  step = 1; // 1: Select Bank, 2: Select Template, 3: PDF Upload, 4: Ready to proceed
  
  // New properties for redesigned flow
  selectedStartOption: 'template' | 'blank' | 'pdf' | null = null;
  selectedPropertyType: 'land' | 'apartment' | null = null;
  
  // PDF Upload properties
  uploadedPdf: File | null = null;
  isProcessingPdf = false;
  processingStatus = '';
  extractedFields: { [key: string]: any } | null = null;
  
  currentOrgShortName = '';
  
  // Expose Object for template
  Object = Object;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone,
    private customTemplateService: CustomTemplateService,
    private pdfProcessorService: PdfProcessorService
  ) {}

  ngOnInit() {
    // Ensure we start fresh
    console.log('🚀 NewReport component initialized');
    
    // Test PDF API connectivity
    this.testPdfApi();
    
    // Get organization context from route
    this.route.parent?.params.subscribe(params => {
      this.currentOrgShortName = params['orgShortName'] || '';
      console.log('📍 Current organization:', this.currentOrgShortName);
    });
    
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

  selectTemplate(template: Template): void {
    console.log('📋 Selected template:', template.templateName);
    this.selectedTemplate = template;
    this.selectedCustomTemplate = null; // Reset custom template selection
    
    // When template is selected from the new flow, go directly to form
    if (this.selectedStartOption === 'template') {
      console.log('➡️ Template selected in new flow - going directly to form');
      this.proceedToForm();
    } else {
      // Legacy behavior - skip PDF upload and go directly to final step
      this.step = 4; // Skip PDF upload and go directly to final step
      console.log('➡️ Template selected - skipping PDF upload, going to step 4');
    }
    
    // Force change detection
    this.cdr.detectChanges();
  }

  // New methods for redesigned flow
  selectStartOption(option: 'template' | 'blank' | 'pdf') {
    this.selectedStartOption = option;
    this.selectedPropertyType = null;
    this.selectedCustomTemplate = null;
    this.customTemplates = [];
    
    console.log('🎯 Start option selected:', option);
    this.cdr.detectChanges();
  }

  selectPropertyType(propertyType: 'land' | 'apartment') {
    this.selectedPropertyType = propertyType;
    console.log('🏠 Property type selected:', propertyType);
    
    // If template option is selected, load custom templates for this bank and property type
    if (this.selectedStartOption === 'template' && this.selectedBank) {
      this.loadCustomTemplates(this.selectedBank.bankCode, propertyType);
    }
    
    this.cdr.detectChanges();
  }

  canProceedFromStep2(): boolean {
    if (!this.selectedStartOption || !this.selectedPropertyType) {
      return false;
    }
    
    // If template option is selected, must have a template selected
    if (this.selectedStartOption === 'template') {
      return this.selectedCustomTemplate !== null;
    }
    
    // For blank and PDF options, property type selection is enough
    return true;
  }

  continueFromStep2() {
    console.log('🔵 continueFromStep2() called');
    console.log('📊 Current state:', {
      step: this.step,
      selectedStartOption: this.selectedStartOption,
      selectedPropertyType: this.selectedPropertyType,
      selectedBank: this.selectedBank?.bankCode,
      selectedTemplate: this.selectedTemplate?.templateCode,
      currentOrgShortName: this.currentOrgShortName
    });
    
    if (!this.canProceedFromStep2()) {
      console.warn('⚠️ Cannot proceed - canProceedFromStep2() returned false');
      return;
    }

    // Set the template based on property type for blank and PDF options
    if (this.selectedStartOption !== 'template') {
      // Find the bank template for the selected property type
      this.selectedTemplate = this.availableTemplates.find(
        t => t.propertyType === this.selectedPropertyType
      ) || null;
      console.log('📋 Auto-selected template for property type:', this.selectedTemplate?.templateCode);
    }

    if (this.selectedStartOption === 'pdf') {
      console.log('➡️ PDF option - going to step 3');
      this.step = 3; // Go to PDF upload step
    } else if (this.selectedStartOption === 'blank') {
      // For blank template, go directly to form (skip confirmation step)
      console.log('➡️ Blank template selected - going directly to form');
      console.log('🔍 Before calling proceedToForm:');
      console.log('  - selectedBank:', this.selectedBank);
      console.log('  - currentOrgShortName:', this.currentOrgShortName);
      this.proceedToForm();
      console.log('✅ proceedToForm() completed');
      return;
    } else {
      console.log('➡️ Template option - going to step 4');
      this.step = 4; // Go to final confirmation step (for custom template)
    }
    
    console.log('➡️ Continuing from step 2 to step:', this.step);
    this.cdr.detectChanges();
  }

  formatDate(date: Date | string): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
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
      
      // If we're in the new flow with template option, go directly to form
      if (this.selectedStartOption === 'template') {
        console.log('➡️ Custom template selected in new flow - going directly to form');
        this.proceedToForm();
        return;
      }
    } else {
      console.log('❌ No custom template selected');
    }
    
    // Legacy behavior - go to step 4
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
      this.selectedStartOption = null;
      this.selectedPropertyType = null;
      this.availableTemplates = [];
      this.customTemplates = [];
    } else if (this.step === 3) {
      this.step = 2;
      // Keep the selections from step 2, just go back
      this.uploadedPdf = null;
      this.extractedFields = null;
    } else if (this.step === 4) {
      // Determine where to go back based on selected start option
      if (this.selectedStartOption === 'pdf') {
        this.step = 3; // Back to PDF upload
      } else {
        this.step = 2; // Back to template selection
      }
    }
  }

  proceedToForm() {
    console.log('🔵 proceedToForm() called');
    console.log('🔍 Validation check:');
    console.log('  - selectedBank:', this.selectedBank);
    console.log('  - currentOrgShortName:', this.currentOrgShortName);
    
    if (this.selectedBank && this.currentOrgShortName) {
      console.log('✅ Validation passed - proceeding with navigation');
      console.log('🚀 Proceeding to form with bank:', this.selectedBank.bankCode);
      console.log('📍 Organization:', this.currentOrgShortName);
      
      // Navigate to organization-aware report creation form
      const queryParams: any = {
        bankCode: this.selectedBank.bankCode,
        bankName: this.selectedBank.bankName
      };
      
      // Add property type from our selection
      if (this.selectedPropertyType) {
        queryParams.propertyType = this.selectedPropertyType;
        console.log('🏠 Property type:', this.selectedPropertyType);
      }
      
      if (this.selectedTemplate) {
        console.log('📋 Including template:', this.selectedTemplate.templateCode);
        queryParams.templateId = this.selectedTemplate.templateCode; // Use templateCode for URL
        queryParams.templateName = this.selectedTemplate.templateName;
        if (!queryParams.propertyType) {
          queryParams.propertyType = this.selectedTemplate.propertyType;
        }
      }

      // Add custom template ID if selected
      if (this.selectedCustomTemplate) {
        console.log('📝 Including custom template:', this.selectedCustomTemplate._id);
        queryParams.customTemplateId = this.selectedCustomTemplate._id;
        queryParams.customTemplateName = this.selectedCustomTemplate.templateName;
        
        // IMPORTANT: When using custom template, we still need base templateId 
        // ReportForm expects templateId to load the base template structure
        if (this.selectedPropertyType && !queryParams.templateId) {
          // Set base template based on property type for the selected bank
          const baseTemplate = this.availableTemplates.find(
            t => t.propertyType === this.selectedPropertyType
          );
          if (baseTemplate) {
            queryParams.templateId = baseTemplate.templateCode;
            queryParams.templateName = baseTemplate.templateName;
            console.log('📋 Added base template for custom template:', baseTemplate.templateCode);
          } else {
            console.error('❌ No base template found for property type:', this.selectedPropertyType);
          }
        }
      }

      // Add start option for form initialization
      if (this.selectedStartOption) {
        queryParams.startOption = this.selectedStartOption;
        console.log('🎯 Start option:', this.selectedStartOption);
      }

      // Add extracted PDF fields if available
      if (this.extractedFields && Object.keys(this.extractedFields).length > 0) {
        console.log('📄 Including extracted PDF fields:', this.extractedFields);
        queryParams.pdfFields = JSON.stringify(this.extractedFields);
      }
      
      // Navigate to organization-aware create route
      const createRoute = `/org/${this.currentOrgShortName}/reports/create`;
      console.log('🔗 Navigating to organization-aware route:', createRoute);
      console.log('📋 Query params:', queryParams);
      
      this.router.navigate([createRoute], { queryParams })
        .then(success => {
          console.log('✅ Navigation result:', success);
        })
        .catch(error => {
          console.error('❌ Navigation error:', error);
        });
    } else {
      console.error('❌ Validation failed - cannot proceed');
      console.error('Bank:', this.selectedBank);
      console.error('Organization:', this.currentOrgShortName);
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

  // PDF Upload Methods

  skipPdfUpload() {
    console.log('📝 Skipping PDF upload - proceeding with empty form');
    this.uploadedPdf = null;
    this.extractedFields = null;
    this.step = 4; // Go to final step
  }

  onUploadAreaClick() {
    console.log('🖱️ Upload area clicked - triggering file input');
  }

  // Debug method to test API connectivity
  testPdfApi() {
    console.log('🧪 Testing PDF API connectivity...');
    
    this.pdfProcessorService.checkHealth().subscribe({
      next: (result) => {
        console.log('✅ PDF API Health Check Success:', result);
      },
      error: (error) => {
        console.error('❌ PDF API Health Check Failed:', error);
      }
    });
  }

  onFileSelected(event: Event) {
    console.log('🎯 File selection event triggered:', event);
    const input = event.target as HTMLInputElement;
    console.log('🎯 Input element:', input);
    console.log('🎯 Files found:', input.files?.length || 0);
    if (input.files && input.files[0]) {
      console.log('📄 PDF file selected:', input.files[0].name, 'Size:', input.files[0].size);
      this.handlePdfFile(input.files[0]);
    } else {
      console.log('❌ No file selected');
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    
    const files = event.dataTransfer?.files;
    if (files && files[0]) {
      this.handlePdfFile(files[0]);
    }
  }

  private handlePdfFile(file: File) {
    console.log('🚀 handlePdfFile called with:', { name: file.name, size: file.size, type: file.type });
    
    // Validate file type
    if (file.type !== 'application/pdf') {
      console.error('❌ Invalid file type:', file.type);
      return;
    }

    // Validate file size (15MB max - updated to match backend)
    if (file.size > 15 * 1024 * 1024) {
      console.error('❌ File too large:', file.size);
      return;
    }

    console.log('✅ File validation passed');
    console.log('📄 PDF file selected:', file.name);
    this.uploadedPdf = file;
    this.processPdf(file);
  }

  private processPdf(file: File) {
    console.log('🚀 processPdf called with file:', file.name);
    
    // Validate file first
    const validation = this.pdfProcessorService.validatePdfFile(file);
    
    if (!validation.valid) {
      console.error('File validation failed:', validation.errors);
      this.uploadedPdf = null;
      return;
    }

    console.log('✅ File validation passed, starting processing...');
    this.isProcessingPdf = true;
    this.processingStatus = 'Uploading and processing PDF...';
    
    console.log('📤 Processing PDF:', file.name);
    console.log('🔍 PDF file details:', { name: file.name, size: file.size, type: file.type });
    
    // Process with real API
    console.log('🌐 Calling PDF service...');
    
    this.pdfProcessorService.extractFieldsFromPdf(file).subscribe({
      next: (result) => {
        if (result.success) {
          console.log('✅ PDF processed successfully:', result);
          console.log('🔍 Raw result.fields:', result.fields);
          console.log('🔍 Result metadata:', result.metadata);
          
          // Map extracted fields to our form format
          this.extractedFields = this.pdfProcessorService.mapExtractedFieldsToForm(result.fields);
          console.log('📋 Mapped extracted fields:', this.extractedFields);
          
          this.processingStatus = `Successfully extracted ${result.metadata.fields_extracted} fields`;
          
          console.log('🔄 Current step before change:', this.step);
          
          // Reset processing flags first
          this.isProcessingPdf = false;
          
          // Then change step
          this.step = 4; // Go to final step
          console.log('🔄 Step changed to:', this.step);
          
          // Check step 4 display conditions
          console.log('🔍 Step 4 conditions check:');
          console.log('  - isLoading:', this.isLoading);
          console.log('  - step === 4:', this.step === 4);
          console.log('  - selectedTemplate:', this.selectedTemplate);
          console.log('  - isProcessingPdf:', this.isProcessingPdf);
          
          // Force change detection
          this.cdr.detectChanges();
          console.log('🔄 Change detection triggered');
        } else {
          throw new Error(result.error || 'PDF processing failed');
        }
      },
      error: (error) => {
        console.error('❌ Error processing PDF:', error);
        console.error('❌ Full error object:', JSON.stringify(error, null, 2));
        this.uploadedPdf = null;
        this.isProcessingPdf = false;
      },
      complete: () => {
        this.isProcessingPdf = false;
      }
    });
  }



  getExtractedFieldsArray(): Array<{ label: string, value: string }> {
    if (!this.extractedFields) return [];
    
    const fieldLabels: { [key: string]: string } = {
      'applicant_name': 'Applicant Name',
      'inspection_date': 'Inspection Date',
      'valuation_date': 'Valuation Date',
      'valuation_purpose': 'Valuation Purpose',
      'property_address': 'Property Address'
    };

    return Object.entries(this.extractedFields).map(([key, value]) => ({
      label: fieldLabels[key] || key,
      value: String(value)
    }));
  }
}
