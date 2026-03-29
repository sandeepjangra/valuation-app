import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableField, FieldTypeDto } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-table-field',
  imports: [CommonModule, FormsModule],
  templateUrl: './table-field.html',
})
export class TableFieldComponent {
  @Input() table!: TableField;
  @Input() rows!: Record<string, any>[];

  FieldTypeDto = FieldTypeDto;

  addRow() {
    this.rows.push(Object.fromEntries(this.table.columns.map(c => [c.fieldId, ''])));
  }

  removeRow(index: number) {
    if (this.rows.length > 1) this.rows.splice(index, 1);
  }

  getColumnSum(colId: string): number {
    return this.rows.reduce((sum, row) => sum + (parseFloat(row[colId]) || 0), 0);
  }
}
