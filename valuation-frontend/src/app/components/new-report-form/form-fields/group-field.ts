import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';
import { GroupField } from '../../../models/valuation-template.model';
import { FormFieldComponent } from './form-field';

@Component({
  selector: 'app-group-field',
  imports: [CommonModule, FormFieldComponent],
  templateUrl: './group-field.html',
})
export class GroupFieldComponent {
  @Input() field!: GroupField;
  @Input() form!: FormGroup;
  @Input() tableRows!: Record<string, Record<string, any>[]>;
  @Input() collapsedMap!: Record<string, boolean>;

  get collapsed(): boolean { return !!this.collapsedMap[this.field.fieldId]; }

  toggle() {
    if (this.field.isCollapsible) {
      this.collapsedMap[this.field.fieldId] = !this.collapsed;
    }
  }
}
