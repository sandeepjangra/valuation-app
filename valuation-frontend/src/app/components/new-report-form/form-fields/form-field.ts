import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';
import {
  BaseField, InputField, TabsField, SectionField, GroupField,
  TableField, AttachmentField, ContainerTypeDto
} from '../../../models/valuation-template.model';
import { InputFieldComponent }      from './input-field';
import { TableFieldComponent }      from './table-field';
import { AttachmentFieldComponent } from './attachment-field';
import { TabsFieldComponent }       from './tabs-field';
import { SectionFieldComponent }    from './section-field';
import { GroupFieldComponent }      from './group-field';

@Component({
  selector: 'app-form-field',
  imports: [
    CommonModule,
    InputFieldComponent,
    TableFieldComponent,
    AttachmentFieldComponent,
    TabsFieldComponent,
    SectionFieldComponent,
    GroupFieldComponent,
  ],
  template: `
    <ng-container [ngSwitch]="field.$type">

      <app-input-field *ngSwitchCase="'input'"
        [field]="asInput(field)" [form]="form">
      </app-input-field>

      <app-table-field *ngSwitchCase="'table'"
        [table]="asTable(field)" [rows]="tableRows[field.fieldId]">
      </app-table-field>

      <app-attachment-field *ngSwitchCase="'attachment'"
        [field]="asAttachment(field)">
      </app-attachment-field>

      <ng-container *ngSwitchCase="'container'">
        <ng-container [ngSwitch]="asContainer(field).container">

          <app-tabs-field *ngSwitchCase="ContainerTypeDto.TabGroup"
            [field]="asTabs(field)" [form]="form"
            [tableRows]="tableRows" [collapsedMap]="collapsedMap">
          </app-tabs-field>

          <app-section-field *ngSwitchCase="ContainerTypeDto.Section"
            [field]="asSection(field)" [form]="form"
            [tableRows]="tableRows" [collapsedMap]="collapsedMap">
          </app-section-field>

          <app-group-field *ngSwitchCase="ContainerTypeDto.Group"
            [field]="asGroup(field)" [form]="form"
            [tableRows]="tableRows" [collapsedMap]="collapsedMap">
          </app-group-field>

        </ng-container>
      </ng-container>

    </ng-container>
  `,
})
export class FormFieldComponent {
  @Input() field!: BaseField;
  @Input() form!: FormGroup;
  @Input() tableRows!: Record<string, Record<string, any>[]>;
  @Input() collapsedMap!: Record<string, boolean>;

  ContainerTypeDto = ContainerTypeDto;

  asInput(f: BaseField): InputField           { return f as InputField; }
  asTable(f: BaseField): TableField           { return f as TableField; }
  asAttachment(f: BaseField): AttachmentField { return f as AttachmentField; }
  asContainer(f: BaseField): any              { return f; }
  asTabs(f: BaseField): TabsField             { return f as TabsField; }
  asSection(f: BaseField): SectionField       { return f as SectionField; }
  asGroup(f: BaseField): GroupField           { return f as GroupField; }
}
