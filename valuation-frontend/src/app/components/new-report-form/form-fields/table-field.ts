import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TableField, FieldTypeDto } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-table-field',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './table-field.html',
  styles: [`
    .table-wrapper {
      margin-bottom: 24px;
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      overflow: hidden;
    }

    .table-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 18px;
      background: #f9fafb;
      border-bottom: 2px solid #8b5cf6;
    }

    .table-title {
      font-size: 15px;
      font-weight: 600;
      color: #1f2937;
      margin: 0;
    }

    .add-row-btn {
      padding: 6px 14px;
      background: linear-gradient(135deg, #10b981, #059669);
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
    }

    .add-row-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
    }

    .table-scroll {
      overflow-x: auto;
      max-width: 100%;
    }

    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }

    .data-table thead {
      background: #f9fafb;
      position: sticky;
      top: 0;
      z-index: 1;
    }

    .data-table th {
      padding: 12px;
      text-align: left;
      font-weight: 600;
      color: #374151;
      border-bottom: 2px solid #e5e7eb;
      white-space: nowrap;
    }

    .data-table td {
      padding: 8px 12px;
      border-bottom: 1px solid #f3f4f6;
    }

    .data-table tbody tr {
      transition: background 0.15s ease;
    }

    .data-table tbody tr:hover {
      background: #fafbfc;
    }

    .table-input,
    .table-select {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid #d1d5db;
      border-radius: 4px;
      font-size: 14px;
      color: #1f2937;
      background: white;
      transition: border-color 0.2s ease;
      min-width: 120px;
    }

    .table-input:focus,
    .table-select:focus {
      outline: none;
      border-color: #8b5cf6;
      box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }

    .table-input:read-only,
    .table-select:disabled {
      background: #f9fafb;
      color: #6b7280;
      cursor: not-allowed;
    }

    .action-col {
      width: 50px;
      text-align: center;
    }

    .remove-row-btn {
      padding: 4px 8px;
      background: #fee2e2;
      color: #dc2626;
      border: 1px solid #fca5a5;
      border-radius: 4px;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s ease;
      font-weight: 600;
    }

    .remove-row-btn:hover {
      background: #fecaca;
      border-color: #f87171;
    }

    .data-table tfoot {
      background: #f9fafb;
      border-top: 2px solid #e5e7eb;
      font-weight: 600;
    }

    .data-table tfoot td {
      padding: 12px;
      border-bottom: none;
    }

    .summary-cell {
      color: #059669;
      font-weight: 600;
      font-size: 13px;
    }

    @media (max-width: 768px) {
      .table-header {
        flex-direction: column;
        gap: 12px;
        align-items: flex-start;
      }

      .add-row-btn {
        width: 100%;
      }

      .table-input,
      .table-select {
        min-width: 100px;
      }
    }
  `]
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
