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
    // Sort fields by sortOrder from MongoDB, then by fieldGroup if needed
    this.sortedCommonFields = [...this.commonFields].sort((a, b) => {
      if (a.sortOrder !== b.sortOrder) {
        return a.sortOrder - b.sortOrder;
      }
      return a.fieldGroup.localeCompare(b.fieldGroup);
    });
  }

  getFieldSizeClass(field: CommonField): string {
    const fieldName = field.technicalName.toLowerCase();
    const fieldType = field.fieldType;
    const uiName = field.uiDisplayName.toLowerCase();
    
    // Content-based sizing logic
    if (fieldType === 'textarea' || uiName.includes('address') || uiName.includes('description')) {
      return 'size-full'; // Full width
    } else if (fieldName.includes('pin') || fieldName.includes('ifsc') || uiName.includes('code')) {
      return 'size-small'; // ~120px
    } else if (fieldName.includes('phone') || fieldName.includes('contact') || fieldName.includes('registration')) {
      return 'size-medium'; // ~180px
    } else if (fieldType === 'date' || fieldType === 'select' || fieldType === 'select_dynamic') {
      return 'size-medium'; // ~180px
    } else {
      return 'size-normal'; // ~250px
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