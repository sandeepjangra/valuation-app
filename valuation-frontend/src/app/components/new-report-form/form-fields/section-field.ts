import { Component, Input, Type, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';
import { SectionField } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-section-field',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './section-field.html',
  styles: [`
    .section-wrapper {
      margin-bottom: 24px;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 18px;
      background: #f9fafb;
      border-radius: 8px 8px 0 0;
      border: 1px solid #e5e7eb;
      border-bottom: 2px solid #8b5cf6;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .section-header:hover {
      background: #f3f4f6;
    }

    .section-title {
      font-size: 15px;
      font-weight: 600;
      color: #1f2937;
      margin: 0;
    }

    .toggle-icon {
      font-size: 14px;
      color: #8b5cf6;
      transition: transform 0.3s ease;
    }

    .toggle-icon.collapsed {
      transform: rotate(-90deg);
    }

    .section-body {
      padding: 20px;
      background: white;
      border: 1px solid #e5e7eb;
      border-top: none;
      border-radius: 0 0 8px 8px;
    }

    .fields-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      align-items: start;
    }

    .field-item {
      min-width: 0;
    }

    /* Table fields always take full width */
    .field-item.table-field {
      grid-column: 1 / -1;
    }

    @media (max-width: 1200px) {
      .fields-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 768px) {
      .fields-grid {
        grid-template-columns: 1fr;
      }
      
      .section-body {
        padding: 16px;
      }
    }
  `]
})
export class SectionFieldComponent implements OnInit {
  @Input() field!: SectionField;
  @Input() form!: FormGroup;
  @Input() tableRows!: Record<string, Record<string, any>[]>;
  @Input() collapsedMap!: Record<string, boolean>;

  formFieldComponent!: Type<any>;

  constructor(private cdr: ChangeDetectorRef) {}

  get collapsed(): boolean { return !!this.collapsedMap[this.field.fieldId]; }

  toggle() {
    if (this.field.isCollapsible) {
      this.collapsedMap[this.field.fieldId] = !this.collapsed;
    }
  }

  async ngOnInit() {
    const { FormFieldComponent } = await import('./form-field');
    this.formFieldComponent = FormFieldComponent;
    this.cdr.detectChanges();
  }
}
