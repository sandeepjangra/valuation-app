import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatTabsModule } from '@angular/material/tabs';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

interface CommonField {
  fieldId: string;
  fieldGroup: string;
  technicalName: string;
  uiDisplayName: string;
  fieldType: string;
  isRequired: boolean;
  placeholder?: string;
  helpText?: string;
  gridSize: number;
  sortOrder: number;
  options?: Array<{value: string, label: string}>;
  validation?: any;
}

interface Bank {
  bankCode: string;
  bankName: string;
  branches: Array<{
    branchId: string;
    branchName: string;
    ifscCode: string;
    address: any;
  }>;
}

@Component({
  selector: 'app-report-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTabsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatDividerModule,
    MatInputModule,
    MatSelectModule,
    MatFormFieldModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './report-form.component.html',
  styleUrls: ['./report-form.component.scss']
})
export class ReportFormComponent implements OnInit {
  reportForm: FormGroup;
  commonFields: CommonField[] = [];
  sortedCommonFields: CommonField[] = [];
  fieldGroups: { [key: string]: CommonField[] } = {};
  banks: Bank[] = [];
  selectedBankBranches: any[] = [];
  
  // Progress tracking
  formProgress = 15; // Demo progress

  constructor(
    private fb: FormBuilder,
    private http: HttpClient
  ) {
    this.reportForm = this.fb.group({});
  }

  ngOnInit(): void {
    this.loadCommonFields();
    this.loadBanks();
  }

  loadCommonFields(): void {
    this.http.get<CommonField[]>(`${environment.apiUrl}/common-fields`)
      .subscribe({
        next: (fields) => {
          console.log('MongoDB fields loaded:', fields.length);
          this.commonFields = fields;
          this.sortCommonFields();
          this.buildFormControls();
        },
        error: (error) => {
          console.error('Error loading common fields:', error);
          // Show error message instead of fallback
          alert('Failed to load fields from MongoDB. Please check backend connection.');
        }
      });
  }

  sortCommonFields(): void {
    // Define the custom order for field groups
    const groupOrder = [
      'basic_info',
      'bank_details', 
      'applicant_details',
      'declaration',
      'property_location',
      'property_classification',
      'valuer_details',
      'coordinates'  // Additional group found in data
    ];
    
    // Create a mapping for group priority
    const groupPriority: { [key: string]: number } = {};
    groupOrder.forEach((group, index) => {
      groupPriority[group] = index;
    });
    
    // Sort fields by custom group order first, then by sortOrder within each group
    this.sortedCommonFields = [...this.commonFields].sort((a, b) => {
      // First, sort by custom group order
      const groupA = groupPriority[a.fieldGroup] ?? 999; // Unknown groups go to end
      const groupB = groupPriority[b.fieldGroup] ?? 999;
      
      if (groupA !== groupB) {
        return groupA - groupB;
      }
      
      // Then, sort by sortOrder within the same group
      return a.sortOrder - b.sortOrder;
    });
    
    // Fix any sortOrder gaps to ensure smooth flow
    this.fixSortOrderGaps();
    
    console.log('Fields sorted by custom group order and sortOrder:', 
      this.sortedCommonFields.map(f => `${f.fieldGroup}.${f.sortOrder}: ${f.uiDisplayName}`)
    );
  }

  private fixSortOrderGaps(): void {
    // Group fields by fieldGroup
    const groupedFields: { [key: string]: CommonField[] } = {};
    this.sortedCommonFields.forEach(field => {
      if (!groupedFields[field.fieldGroup]) {
        groupedFields[field.fieldGroup] = [];
      }
      groupedFields[field.fieldGroup].push(field);
    });

    // Fix sortOrder gaps within each group
    Object.keys(groupedFields).forEach(groupName => {
      const fields = groupedFields[groupName];
      fields.sort((a, b) => a.sortOrder - b.sortOrder);
      
      // Renumber to remove gaps
      fields.forEach((field, index) => {
        field.sortOrder = index + 1;
      });
    });

    // Re-sort the entire array
    const groupOrder = ['basic_info', 'bank_details', 'applicant_details', 'declaration', 'property_location', 'property_classification', 'valuer_details', 'coordinates'];
    const groupPriority: { [key: string]: number } = {};
    groupOrder.forEach((group, index) => {
      groupPriority[group] = index;
    });

    this.sortedCommonFields.sort((a, b) => {
      const groupA = groupPriority[a.fieldGroup] ?? 999;
      const groupB = groupPriority[b.fieldGroup] ?? 999;
      
      if (groupA !== groupB) {
        return groupA - groupB;
      }
      
      return a.sortOrder - b.sortOrder;
    });
  }

  getFieldSizeClass(field: CommonField): string {
    // Use gridSize from MongoDB instead of hardcoded logic
    const gridSize = field.gridSize || 6; // Default to 6 if not specified
    
    // Convert gridSize to CSS class
    // MongoDB uses 12-column grid system (like Bootstrap)
    // gridSize 12 = full width, gridSize 6 = half width, gridSize 4 = third width, etc.
    
    if (gridSize >= 12) {
      return 'size-full';     // Full width (100%)
    } else if (gridSize >= 8) {
      return 'size-large';    // Large width (~66%)
    } else if (gridSize >= 6) {
      return 'size-normal';   // Normal width (~50%)
    } else if (gridSize >= 4) {
      return 'size-medium';   // Medium width (~33%)
    } else {
      return 'size-small';    // Small width (~25%)
    }
  }

  trackByFieldId(index: number, field: CommonField): string {
    return field.fieldId;
  }

  handleDynamicFieldChange(field: CommonField, value: any): void {
    if (field.technicalName === 'bank_code') {
      this.onBankSelectionChange(value);
    } else if (field.technicalName === 'branch_details') {
      this.onBranchSelectionChange(value);
    }
  }

  loadBanks(): void {
    this.http.get<Bank[]>(`${environment.apiUrl}/banks`)
      .subscribe({
        next: (banks) => {
          console.log('MongoDB banks loaded:', banks.length);
          this.banks = banks;
        },
        error: (error) => {
          console.error('Error loading banks:', error);
          // Show error message instead of fallback
          alert('Failed to load banks from MongoDB. Please check backend connection.');
        }
      });
  }

  buildFormControls(): void {
    const formControls: { [key: string]: any } = {};
    
    this.sortedCommonFields.forEach(field => {
      formControls[field.technicalName] = [''];
    });
    
    this.reportForm = this.fb.group(formControls);
  }

  onBankSelectionChange(bankCode: string): void {
    const selectedBank = this.banks.find(bank => bank.bankCode === bankCode);
    this.selectedBankBranches = selectedBank ? selectedBank.branches : [];
    
    // Reset branch selection
    this.reportForm.get('branch_details')?.setValue('');
    this.reportForm.get('branch_ifsc')?.setValue('');
    this.reportForm.get('branch_address')?.setValue('');
  }

  onBranchSelectionChange(branchId: string): void {
    const branch = this.selectedBankBranches.find(b => b.branchId === branchId);
    if (branch) {
      // Set the branch name instead of ID for better readability
      this.reportForm.get('branch_details')?.setValue(branch.branchName);
      this.reportForm.get('branch_ifsc')?.setValue(branch.ifscCode);
      // You can format the address here
      const addressText = `${branch.address?.street || ''}, ${branch.address?.city || ''}, ${branch.address?.state || ''} - ${branch.address?.pincode || ''}`;
      this.reportForm.get('branch_address')?.setValue(addressText);
    }
  }

  getFieldGridClass(gridSize: number): string {
    const colClass = Math.round((gridSize / 12) * 12); // Convert to 12-column grid
    return `col-md-${colClass}`;
  }

  onSaveProgress(): void {
    console.log('Saving progress...', this.reportForm.value);
    // Implement save logic
  }

  onSubmitReport(): void {
    if (this.reportForm.valid) {
      console.log('Submitting report...', this.reportForm.value);
      // Implement submit logic
    } else {
      console.log('Form is invalid');
    }
  }

  onPreviewReport(): void {
    console.log('Previewing report...', this.reportForm.value);
    // Implement preview logic
  }
}