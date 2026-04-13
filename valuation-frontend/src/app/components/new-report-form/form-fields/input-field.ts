import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';
import { InputField, FieldTypeDto } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-input-field',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './input-field.html',
  styles: [`
    .field-wrapper {
      display: flex;
      flex-direction: column;
      width: 100%;
    }

    .field-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 8px;
    }

    .field-label {
      font-size: 14px;
      font-weight: 500;
      color: #2c3e50;
      margin: 0;
    }

    .required-star {
      color: #ef4444;
      margin-left: 2px;
    }

    .field-info-icon {
      display: inline-flex;
      align-items: center;
      cursor: help;
      position: relative;
    }

    .info-icon {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background-color: #6c757d;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: bold;
      transition: all 0.2s ease;
    }

    .field-info-icon:hover .info-icon {
      background-color: #8b5cf6;
      transform: scale(1.15);
    }

    .info-tooltip {
      position: absolute;
      bottom: 120%;
      left: 50%;
      transform: translateX(-50%);
      background-color: #1f2937;
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 12px;
      white-space: normal;
      width: 200px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 1000;
      pointer-events: none;
      line-height: 1.4;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.2s ease, visibility 0.2s ease;
    }

    .field-info-icon:hover .info-tooltip {
      opacity: 1;
      visibility: visible;
    }

    .info-tooltip::after {
      content: '';
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      border: 6px solid transparent;
      border-top-color: #1f2937;
    }

    .field-input,
    .field-select,
    .field-textarea {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 14px;
      color: #1f2937;
      background: white;
      transition: all 0.2s ease;
      box-sizing: border-box;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .field-input:focus,
    .field-select:focus,
    .field-textarea:focus {
      outline: none;
      border-color: #8b5cf6;
      box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }

    .field-input.error,
    .field-select.error,
    .field-textarea.error {
      border-color: #ef4444;
    }

    .field-input.error:focus,
    .field-select.error:focus,
    .field-textarea.error:focus {
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }

    .field-input.readonly {
      background-color: #f9fafb;
      cursor: not-allowed;
      border-color: #d1d5db;
    }

    .field-select {
      cursor: pointer;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 12px center;
      padding-right: 36px;
    }

    .field-textarea {
      resize: vertical;
      min-height: 80px;
      font-family: inherit;
      line-height: 1.5;
    }

    .input-prefix-wrapper {
      position: relative;
      display: flex;
      align-items: center;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      background: white;
      transition: all 0.2s ease;
    }

    .input-prefix-wrapper:focus-within {
      border-color: #8b5cf6;
      box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }

    .input-prefix-wrapper.error {
      border-color: #ef4444;
    }

    .input-prefix-wrapper.error:focus-within {
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }

    .input-prefix {
      padding: 0 12px;
      color: #6b7280;
      font-weight: 500;
      font-size: 14px;
      user-select: none;
      border-right: 1px solid #e5e7eb;
    }

    .field-input.with-prefix {
      border: none;
      padding-left: 12px;
    }

    .field-input.with-prefix:focus {
      box-shadow: none;
    }

    /* Checkbox and Radio styles */
    .checkbox-wrapper,
    .radio-group {
      padding: 4px 0;
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      user-select: none;
    }

    .field-checkbox {
      width: 18px;
      height: 18px;
      cursor: pointer;
      accent-color: #8b5cf6;
    }

    .radio-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .radio-label {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      user-select: none;
    }

    .radio-label input[type="radio"] {
      width: 18px;
      height: 18px;
      cursor: pointer;
      accent-color: #8b5cf6;
    }

    .help-text {
      font-size: 12px;
      color: #6b7280;
      margin: 4px 0 0 0;
      line-height: 1.4;
    }

    .error-text {
      font-size: 12px;
      color: #ef4444;
      margin: 4px 0 0 0;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .error-text::before {
      content: '⚠';
    }
  `]
})
export class InputFieldComponent implements OnInit {
  @Input() field!: InputField;
  @Input() form!: FormGroup;

  FieldTypeDto = FieldTypeDto;

  ngOnInit() {
    console.log('InputField component initialized:', {
      fieldId: this.field?.fieldId,
      label: this.field?.label,
      field: this.field
    });
  }

  hasError(): boolean {
    const ctrl = this.form.get(this.field.fieldId);
    return !!(ctrl && ctrl.invalid && ctrl.touched);
  }

  getErrorMessage(): string {
    const ctrl = this.form.get(this.field.fieldId);
    if (!ctrl?.errors) return '';
    const r = this.field.validationRules;
    if (ctrl.errors['required'])  return `${this.field.label} is required`;
    if (ctrl.errors['minlength']) return `Minimum ${r?.minLength} characters required`;
    if (ctrl.errors['maxlength']) return `Maximum ${r?.maxLength} characters allowed`;
    if (ctrl.errors['min'])       return `Minimum value is ${r?.min}`;
    if (ctrl.errors['max'])       return `Maximum value is ${r?.max}`;
    if (ctrl.errors['pattern'])   return r?.errorMessage || 'Invalid format';
    return 'Invalid value';
  }
}
