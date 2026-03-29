import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';
import { InputField, FieldTypeDto } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-input-field',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './input-field.html',
})
export class InputFieldComponent {
  @Input() field!: InputField;
  @Input() form!: FormGroup;

  FieldTypeDto = FieldTypeDto;

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
