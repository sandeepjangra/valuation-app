import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';
import { TabsField } from '../../../models/valuation-template.model';
import { FormFieldComponent } from './form-field';

@Component({
  selector: 'app-tabs-field',
  imports: [CommonModule, FormFieldComponent],
  templateUrl: './tabs-field.html',
})
export class TabsFieldComponent {
  @Input() field!: TabsField;
  @Input() form!: FormGroup;
  @Input() tableRows!: Record<string, Record<string, any>[]>;
  @Input() collapsedMap!: Record<string, boolean>;

  activeTab = 0;
}
