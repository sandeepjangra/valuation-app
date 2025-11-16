import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { 
  DynamicTableConfig, 
  DynamicTableColumn, 
  TableRow 
} from '../../models/template-field.model';

@Component({
  selector: 'app-dynamic-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dynamic-table.component.html',
  styleUrls: ['./dynamic-table.component.css']
})
export class DynamicTableComponent implements OnInit, OnDestroy {
  @Input() fieldId!: string;
  @Input() fieldLabel!: string;
  @Input() isRequired: boolean = false;
  @Input() helpText?: string;
  @Input() tableConfig?: DynamicTableConfig;
  @Input() initialData?: any;
  
  @Output() dataChange = new EventEmitter<any>();

  // Component state
  allColumns: DynamicTableColumn[] = [];
  tableRows: TableRow[] = [];
  userAddedColumns: DynamicTableColumn[] = [];
  nextColumnNumber: number = 1;
  nextRowNumber: number = 1;
  
  // Table type detection
  isColumnDynamic: boolean = false;
  isRowDynamic: boolean = false;

  ngOnInit() {
    this.initializeTable();
    console.log('🔧 DynamicTable initialized for field:', this.fieldId);
  }

  ngOnDestroy() {
    console.log('🔄 DynamicTable destroyed for field:', this.fieldId);
  }

  private initializeTable() {
    if (!this.tableConfig) {
      console.error('❌ No table config provided for dynamic table:', this.fieldId);
      return;
    }

    // Detect table type
    this.detectTableType();

    if (this.isColumnDynamic) {
      this.initializeColumnDynamicTable();
    } else if (this.isRowDynamic) {
      this.initializeRowDynamicTable();
    } else {
      console.error('❌ Unknown table type for:', this.fieldId);
      return;
    }

    // Load initial data if provided
    if (this.initialData) {
      this.loadInitialData();
    }

    console.log('📊 Dynamic table initialized:', {
      fieldId: this.fieldId,
      type: this.isColumnDynamic ? 'column_dynamic' : 'row_dynamic',
      totalColumns: this.allColumns.length,
      totalRows: this.tableRows.length
    });
  }

  private detectTableType() {
    if (!this.tableConfig) return;

    // Check for explicit tableType
    if (this.tableConfig.tableType) {
      this.isColumnDynamic = this.tableConfig.tableType === 'column_dynamic';
      this.isRowDynamic = this.tableConfig.tableType === 'row_dynamic';
      return;
    }

    // Auto-detect based on config properties
    const hasDynamicColumns = this.tableConfig.dynamicColumns && this.tableConfig.dynamicColumns.addColumnConfig;
    const hasAllowAddRows = this.tableConfig.allowAddRows === true;

    if (hasDynamicColumns && !hasAllowAddRows) {
      this.isColumnDynamic = true;
    } else if (hasAllowAddRows && !hasDynamicColumns) {
      this.isRowDynamic = true;
    } else {
      console.warn('⚠️ Could not detect table type for:', this.fieldId);
    }
  }

  private initializeColumnDynamicTable() {
    if (!this.tableConfig || !this.tableConfig.dynamicColumns) return;

    // Initialize columns: fixed + default dynamic columns
    this.allColumns = [
      ...this.tableConfig.fixedColumns,
      ...this.tableConfig.dynamicColumns.defaultColumns
    ];

    // Initialize rows from config
    this.tableRows = this.tableConfig.rows.map(row => ({ ...row }));

    // Initialize user added columns tracking
    this.userAddedColumns = [...this.tableConfig.dynamicColumns.defaultColumns];
    this.nextColumnNumber = this.userAddedColumns.length + 1;
  }

  private initializeRowDynamicTable() {
    if (!this.tableConfig) return;

    // For row dynamic, columns are fixed
    this.allColumns = [...this.tableConfig.fixedColumns];

    // Initialize with empty rows array (users will add rows)
    this.tableRows = [...(this.tableConfig.rows || [])];
    
    // Initialize row counter
    this.nextRowNumber = this.tableRows.length + 1;
  }

  private loadInitialData() {
    if (this.initialData.columns) {
      // Restore user-added columns
      const savedUserColumns = this.initialData.columns.filter((col: any) => col.isUserAdded);
      this.userAddedColumns.push(...savedUserColumns);
      this.allColumns.push(...savedUserColumns);
      
      // Update next column number
      this.nextColumnNumber = this.userAddedColumns.length + 1;
    }

    if (this.initialData.rows) {
      // Restore row data
      this.tableRows = this.initialData.rows.map((row: any) => ({ ...row }));
    }

    console.log('📥 Initial data loaded for table:', this.fieldId);
  }

  canAddColumn(): boolean {
    if (!this.tableConfig || !this.isColumnDynamic || !this.tableConfig.dynamicColumns) return false;
    const currentDynamicCount = this.userAddedColumns.length;
    const maxColumns = this.tableConfig.dynamicColumns.addColumnConfig.maxColumns;
    return currentDynamicCount < maxColumns;
  }

  canAddRow(): boolean {
    if (!this.tableConfig || !this.isRowDynamic) return false;
    const currentRowCount = this.tableRows.length;
    const maxRows = this.tableConfig.maxRows || 0;
    return currentRowCount < maxRows;
  }

  addColumn() {
    if (!this.canAddColumn() || !this.tableConfig?.dynamicColumns?.addColumnConfig) {
      console.warn('⚠️ Cannot add column - either limit reached or no config available');
      return;
    }

    const config = this.tableConfig.dynamicColumns.addColumnConfig;
    const newColumnName = config.columnNamePattern.replace('{number}', this.nextColumnNumber.toString());
    
    const newColumn: DynamicTableColumn = {
      columnId: `user_column_${Date.now()}`, // Unique ID
      columnName: newColumnName,
      fieldType: 'textarea',
      isRequired: false,
      isEditable: true,
      isReadonly: false,
      isUserAdded: true,
      canDelete: true,
      placeholder: `Enter ${newColumnName.toLowerCase()} details`
    };

    // Add column to arrays
    this.allColumns.push(newColumn);
    this.userAddedColumns.push(newColumn);

    // Initialize column data in all rows
    this.tableRows.forEach(row => {
      row[newColumn.columnId] = '';
    });

    // Update counter
    this.nextColumnNumber++;

    // Emit data change
    this.emitDataChange();

    console.log('➕ Column added:', newColumn.columnName, 'Total columns:', this.allColumns.length);
  }

  addRow() {
    if (!this.canAddRow() || !this.tableConfig) {
      console.warn('⚠️ Cannot add row - either limit reached or no config available');
      return;
    }

    // Create new row with empty values or from template
    const newRow: TableRow = {};
    
    if (this.tableConfig.addRowConfig?.rowTemplate) {
      // Use template if provided
      Object.assign(newRow, this.tableConfig.addRowConfig.rowTemplate);
    } else {
      // Initialize with empty values for all columns
      this.allColumns.forEach(column => {
        newRow[column.columnId] = '';
      });
    }

    // Set row number if sr_no column exists
    const srNoColumn = this.allColumns.find(col => col.columnId === 'sr_no');
    if (srNoColumn) {
      newRow['sr_no'] = `${this.nextRowNumber}.`;
    }

    // Add row to table
    this.tableRows.push(newRow);
    this.nextRowNumber++;

    // Emit data change
    this.emitDataChange();

    console.log('➕ Row added:', this.nextRowNumber - 1, 'Total rows:', this.tableRows.length);
  }

  removeColumn(columnIndex: number) {
    const column = this.allColumns[columnIndex];
    
    if (!column.canDelete) {
      console.warn('⚠️ Cannot delete fixed column:', column.columnName);
      return;
    }

    // Remove column from arrays
    this.allColumns.splice(columnIndex, 1);
    
    // Remove from user added columns
    const userColumnIndex = this.userAddedColumns.findIndex(col => col.columnId === column.columnId);
    if (userColumnIndex > -1) {
      this.userAddedColumns.splice(userColumnIndex, 1);
    }

    // Remove column data from all rows
    this.tableRows.forEach(row => {
      delete row[column.columnId];
    });

    // Emit data change
    this.emitDataChange();

    console.log('➖ Column removed:', column.columnName, 'Remaining columns:', this.allColumns.length);
  }

  removeRow(rowIndex: number) {
    if (rowIndex < 0 || rowIndex >= this.tableRows.length) {
      console.warn('⚠️ Invalid row index:', rowIndex);
      return;
    }

    // Remove row from array
    this.tableRows.splice(rowIndex, 1);

    // Update row numbers in remaining rows if sr_no column exists
    const srNoColumn = this.allColumns.find(col => col.columnId === 'sr_no');
    if (srNoColumn) {
      this.tableRows.forEach((row, index) => {
        row['sr_no'] = `${index + 1}.`;
      });
      this.nextRowNumber = this.tableRows.length + 1;
    }

    // Emit data change
    this.emitDataChange();

    console.log('➖ Row removed at index:', rowIndex, 'Remaining rows:', this.tableRows.length);
  }

  updateColumnName(columnIndex: number, event: any) {
    const newName = event.target.value;
    if (newName && newName.trim()) {
      this.allColumns[columnIndex].columnName = newName.trim();
      this.emitDataChange();
      console.log('✏️ Column renamed:', this.allColumns[columnIndex].columnId, 'to:', newName);
    }
  }

  updateCellValue(rowIndex: number, columnId: string, event: any) {
    const newValue = event.target.value;
    this.tableRows[rowIndex][columnId] = newValue;
    this.emitDataChange();
  }

  getCellInputType(fieldType: string): string {
    switch (fieldType) {
      case 'number':
        return 'number';
      case 'currency':
        return 'number';
      case 'email':
        return 'email';
      case 'date':
        return 'date';
      case 'url':
        return 'url';
      default:
        return 'text';
    }
  }

  getCellValue(rowIndex: number, columnId: string): any {
    return this.tableRows[rowIndex]?.[columnId] || '';
  }

  private emitDataChange() {
    const tableData = {
      fieldId: this.fieldId,
      columns: this.allColumns,
      rows: this.tableRows,
      userAddedColumns: this.userAddedColumns,
      nextColumnNumber: this.nextColumnNumber
    };
    
    this.dataChange.emit(tableData);
  }

  // Helper methods for template
  isColumnEditable(column: DynamicTableColumn): boolean {
    return column.isEditable !== false && !column.isReadonly;
  }

  isColumnRequired(column: DynamicTableColumn): boolean {
    return column.isRequired === true;
  }

  getAddColumnButtonText(): string {
    return this.tableConfig?.dynamicColumns?.addColumnConfig?.buttonText || 'Add Column';
  }

  getAddRowButtonText(): string {
    return this.tableConfig?.addRowConfig?.buttonText || 'Add Row';
  }

  getRemainingColumns(): number {
    if (!this.tableConfig?.dynamicColumns?.addColumnConfig) return 0;
    const currentCount = this.userAddedColumns.length;
    const maxCount = this.tableConfig.dynamicColumns.addColumnConfig.maxColumns;
    return maxCount - currentCount;
  }

  getRemainingRows(): number {
    if (!this.tableConfig || !this.isRowDynamic) return 0;
    const currentCount = this.tableRows.length;
    const maxCount = this.tableConfig.maxRows || 0;
    return maxCount - currentCount;
  }

  // Check if row can be removed
  canRemoveRow(rowIndex: number): boolean {
    return this.isRowDynamic && this.tableRows.length > 0;
  }
}