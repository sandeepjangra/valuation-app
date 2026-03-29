import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AttachmentField } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-attachment-field',
  imports: [CommonModule],
  templateUrl: './attachment-field.html',
})
export class AttachmentFieldComponent {
  @Input() field!: AttachmentField;

  formatFileSize(bytes: number): string {
    return bytes >= 1048576 ? `${(bytes / 1048576).toFixed(0)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
  }
}
