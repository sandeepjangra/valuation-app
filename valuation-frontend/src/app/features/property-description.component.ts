import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DynamicFormComponent } from './forms/dynamic-form.component';
import { FormData } from '../core/models/form.models';

@Component({
  selector: 'app-property-description',
  standalone: true,
  imports: [
    CommonModule,
    DynamicFormComponent
  ],
  template: `
    <div class="property-description-page">
      <app-dynamic-form
        templateId="property-description-v1"
        (formSave)="onFormSave($event)"
        (formSubmit)="onFormSubmit($event)">
      </app-dynamic-form>
    </div>
  `,
  styles: [`
    .property-description-page {
      min-height: 100vh;
      background-color: #f8f9fa;
      padding: 20px 0;
    }
  `]
})
export class PropertyDescriptionComponent {

  onFormSave(formData: FormData): void {
    console.log('Form saved:', formData);
    // Here you would typically save to your backend/MongoDB
  }

  onFormSubmit(formData: FormData): void {
    console.log('Form submitted:', formData);
    // Here you would typically submit to your backend for processing
  }
}