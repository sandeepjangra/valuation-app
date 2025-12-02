import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

export interface SaveTemplateDialogData {
  bankCode: string;
  bankName: string;
  templateCode: string;
  propertyType: string;
  fieldValues: Record<string, any>;
}

export interface SaveTemplateDialogResult {
  templateName: string;
  description: string | null;
}

@Component({
  selector: 'app-save-template-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  template: `
    <div class="modal-overlay" *ngIf="isOpen()" (click)="onOverlayClick($event)">
      <div class="modal-dialog" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h2>💾 Save as Custom Template</h2>
          <button type="button" class="close-button" (click)="onCancel()" [disabled]="isSaving()">
            ×
          </button>
        </div>
        
        <div class="modal-body">
          <div class="dialog-info">
            <p class="info-text">
              Create a reusable template from this report form. 
              Only filled bank-specific fields will be saved.
            </p>
            
            <div class="template-context">
              <div class="context-item">
                <span class="label">Bank:</span>
                <span class="value">{{ data.bankName }} ({{ data.bankCode }})</span>
              </div>
              <div class="context-item">
                <span class="label">Property Type:</span>
                <span class="value">{{ data.propertyType }}</span>
              </div>
              <div class="context-item">
                <span class="label">Fields with values:</span>
                <span class="value">{{ nonEmptyFieldCount() }}</span>
              </div>
            </div>
          </div>

          <form [formGroup]="templateForm" class="template-form">
            <div class="form-group">
              <label for="templateName" class="form-label">
                Template Name <span class="required">*</span>
              </label>
              <input
                id="templateName"
                type="text"
                formControlName="templateName"
                class="form-control"
                [class.error]="templateForm.get('templateName')?.invalid && templateForm.get('templateName')?.touched"
                placeholder="e.g., Standard Land Valuation"
                maxlength="100"
              />
              <div class="form-hint">
                {{ templateForm.get('templateName')?.value?.length || 0 }}/100 characters
              </div>
              <div class="form-error" *ngIf="templateForm.get('templateName')?.hasError('required') && templateForm.get('templateName')?.touched">
                Template name is required
              </div>
              <div class="form-error" *ngIf="templateForm.get('templateName')?.hasError('minlength')">
                Minimum 3 characters required
              </div>
            </div>

            <div class="form-group">
              <label for="description" class="form-label">
                Description (Optional)
              </label>
              <textarea
                id="description"
                formControlName="description"
                class="form-control"
                placeholder="Describe when to use this template..."
                rows="3"
                maxlength="500"
              ></textarea>
              <div class="form-hint">
                {{ templateForm.get('description')?.value?.length || 0 }}/500 characters
              </div>
            </div>
          </form>

          <div class="warning-message" *ngIf="nonEmptyFieldCount() === 0">
            ⚠️ No filled fields found. Please fill in at least one bank-specific field before saving as template.
          </div>

          <div class="error-message" *ngIf="errorMessage()">
            ❌ {{ errorMessage() }}
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            (click)="onCancel()"
            [disabled]="isSaving()"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-primary"
            (click)="onSave()"
            [disabled]="!templateForm.valid || isSaving() || nonEmptyFieldCount() === 0"
          >
            <span *ngIf="!isSaving()">💾 Save Template</span>
            <span *ngIf="isSaving()" class="loading-text">
              <span class="spinner"></span> Saving...
            </span>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      animation: fadeIn 0.2s ease-in-out;
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
      }
      to {
        opacity: 1;
      }
    }

    .modal-dialog {
      background: white;
      border-radius: 8px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      min-width: 500px;
      max-width: 600px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      animation: slideDown 0.3s ease-out;
    }

    @keyframes slideDown {
      from {
        transform: translateY(-50px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 8px 8px 0 0;
    }

    .modal-header h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }

    .close-button {
      background: none;
      border: none;
      color: white;
      font-size: 32px;
      line-height: 1;
      cursor: pointer;
      padding: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      transition: background 0.2s;
    }

    .close-button:hover:not(:disabled) {
      background: rgba(255, 255, 255, 0.1);
    }

    .close-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .modal-body {
      padding: 24px;
      overflow-y: auto;
      flex: 1;
    }

    .dialog-info {
      margin-bottom: 24px;
    }

    .info-text {
      color: #666;
      font-size: 14px;
      margin: 0 0 16px 0;
      line-height: 1.5;
    }

    .template-context {
      background: #f5f7fa;
      border-radius: 8px;
      padding: 16px;
      border-left: 4px solid #667eea;
    }

    .context-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 14px;
    }

    .context-item:last-child {
      margin-bottom: 0;
    }

    .context-item .label {
      font-weight: 500;
      color: #666;
    }

    .context-item .value {
      font-weight: 600;
      color: #333;
    }

    .template-form {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
    }

    .form-label {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 8px;
    }

    .form-label .required {
      color: #dc3545;
    }

    .form-control {
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 14px;
      transition: all 0.2s;
      font-family: inherit;
    }

    .form-control:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .form-control.error {
      border-color: #dc3545;
    }

    .form-control.error:focus {
      box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
    }

    textarea.form-control {
      resize: vertical;
      min-height: 80px;
    }

    .form-hint {
      font-size: 12px;
      color: #6b7280;
      margin-top: 4px;
    }

    .form-error {
      font-size: 12px;
      color: #dc3545;
      margin-top: 4px;
    }

    .warning-message {
      background: #fff3cd;
      border: 1px solid #ffc107;
      border-radius: 6px;
      padding: 12px;
      color: #856404;
      font-size: 14px;
      margin-top: 16px;
    }

    .error-message {
      background: #f8d7da;
      border: 1px solid #dc3545;
      border-radius: 6px;
      padding: 12px;
      color: #721c24;
      font-size: 14px;
      margin-top: 16px;
    }

    .modal-footer {
      padding: 16px 24px;
      background: #f9fafb;
      border-top: 1px solid #e5e7eb;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      border-radius: 0 0 8px 8px;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      min-width: 120px;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: #6b7280;
      color: white;
    }

    .btn-secondary:hover:not(:disabled) {
      background: #4b5563;
    }

    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .loading-text {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  `]
})
export class SaveTemplateDialogComponent {
  @Input() data!: SaveTemplateDialogData;
  @Output() save = new EventEmitter<SaveTemplateDialogResult>();
  @Output() cancel = new EventEmitter<void>();

  isOpen = signal(false);
  isSaving = signal(false);
  errorMessage = signal<string | null>(null);
  templateForm: FormGroup;

  constructor(private fb: FormBuilder) {
    // Initialize form with validation
    this.templateForm = this.fb.group({
      templateName: ['', [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(100)
      ]],
      description: ['', [
        Validators.maxLength(500)
      ]]
    });
  }

  /**
   * Open the dialog
   */
  open(): void {
    this.isOpen.set(true);
    this.isSaving.set(false);
    this.errorMessage.set(null);
    this.templateForm.reset();

    console.log('💾 SaveTemplateDialog opened with data:', {
      bankCode: this.data.bankCode,
      bankName: this.data.bankName,
      propertyType: this.data.propertyType,
      totalFields: Object.keys(this.data.fieldValues || {}).length,
      nonEmptyFields: this.nonEmptyFieldCount()
    });
  }

  /**
   * Close the dialog
   */
  close(): void {
    this.isOpen.set(false);
    this.isSaving.set(false);
    this.errorMessage.set(null);
  }

  /**
   * Set saving state
   */
  setSaving(saving: boolean): void {
    this.isSaving.set(saving);
  }

  /**
   * Set error message
   */
  setError(message: string | null): void {
    this.errorMessage.set(message);
  }

  /**
   * Count non-empty field values
   */
  nonEmptyFieldCount(): number {
    if (!this.data || !this.data.fieldValues) {
      return 0;
    }

    let count = 0;
    for (const [key, value] of Object.entries(this.data.fieldValues)) {
      // Skip empty values
      if (value === null || value === undefined || value === '') {
        continue;
      }

      // Skip empty arrays
      if (Array.isArray(value) && value.length === 0) {
        continue;
      }

      // Skip empty objects
      if (typeof value === 'object' && !Array.isArray(value) && Object.keys(value).length === 0) {
        continue;
      }
      
      // Skip whitespace-only strings
      if (typeof value === 'string' && !value.trim()) {
        continue;
      }

      count++;
    }

    return count;
  }

  /**
   * Handle overlay click (close dialog)
   */
  onOverlayClick(event: MouseEvent): void {
    if (!this.isSaving()) {
      this.onCancel();
    }
  }

  /**
   * Handle save button click
   */
  onSave(): void {
    if (this.templateForm.invalid) {
      console.warn('⚠️ Form is invalid, cannot save');
      this.templateForm.markAllAsTouched();
      return;
    }

    if (this.nonEmptyFieldCount() === 0) {
      console.warn('⚠️ No filled fields, cannot save template');
      this.setError('No filled fields found. Please fill in at least one bank-specific field.');
      return;
    }

    const result: SaveTemplateDialogResult = {
      templateName: this.templateForm.get('templateName')?.value?.trim() || '',
      description: this.templateForm.get('description')?.value?.trim() || null
    };

    console.log('✅ Emitting save event with:', result);
    this.save.emit(result);
  }

  /**
   * Handle cancel button click
   */
  onCancel(): void {
    console.log('❌ Template save cancelled');
    this.cancel.emit();
    this.close();
  }
}
