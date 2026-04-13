import { Component, Input, Type, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';
import { GroupField } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-group-field',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './group-field.html',
  styles: [`
    .group-wrapper {
      background: #fafbfc;
      border: 1px dashed #cbd5e0;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }

    .group-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e5e7eb;
      cursor: pointer;
      transition: background 0.2s ease;
    }

    .group-header:hover {
      background: rgba(139, 92, 246, 0.05);
      border-radius: 4px;
      padding: 4px 8px;
      margin: 0 -8px 12px -8px;
    }

    .group-title {
      font-size: 14px;
      font-weight: 600;
      color: #374151;
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

    .group-body {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .field-item {
      width: 100%;
    }

    @media (max-width: 768px) {
      .group-wrapper {
        padding: 12px;
      }
    }
  `]
})
export class GroupFieldComponent implements OnInit {
  @Input() field!: GroupField;
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
