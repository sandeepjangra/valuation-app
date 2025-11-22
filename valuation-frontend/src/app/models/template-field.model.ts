// Template Field Models for Aggregated API Response

import { FieldType, FieldOption, FieldValidation, DataSourceConfig } from './common-field.model';

// Calculated Field Configuration
export interface CalculatedFieldConfig {
  type: 'sum' | 'product' | 'average' | 'custom'; // Formula type
  sourceFields: string[]; // Field IDs to use in calculation
  customFormula?: string; // For complex calculations (optional)
  dependencies?: string[]; // Fields that trigger recalculation
}

// Table field interfaces
export interface TableColumn {
  columnId: string;
  columnName: string;
  fieldType: string;
  isRequired?: boolean;
  isEditable?: boolean;
  isReadonly?: boolean;
  placeholder?: string;
}

export interface TableRow {
  [key: string]: any; // Dynamic properties based on column IDs
  isReadonly?: boolean; // For readonly rows
}

// Dynamic Table field interfaces
export interface DynamicTableColumn {
  columnId: string;
  columnName: string;
  fieldType: string;
  isRequired?: boolean;
  isEditable?: boolean;
  isReadonly?: boolean;
  placeholder?: string;
  isUserAdded?: boolean; // Track if column was added by user
  canDelete?: boolean; // Track if column can be deleted
}

export interface DynamicColumnConfig {
  columnType: string; // 'floor', 'unit', etc.
  defaultColumns: DynamicTableColumn[];
  addColumnConfig: {
    buttonText: string;
    columnNamePattern: string; // 'Floor {number}', 'Unit {number}'
    maxColumns: number;
  };
}

export interface DynamicRowConfig {
  buttonText: string;
  maxRows: number;
  rowTemplate: { [key: string]: any }; // Template for new rows
}

export interface DynamicTableConfig {
  // Table type identifier
  tableType?: 'column_dynamic' | 'row_dynamic';
  
  // Column definitions (always present)
  fixedColumns: DynamicTableColumn[];
  
  // Column-dynamic specific properties
  dynamicColumns?: DynamicColumnConfig;
  
  // Row-dynamic specific properties
  allowAddRows?: boolean;
  maxRows?: number;
  addRowConfig?: DynamicRowConfig;
  
  // Table data (rows)
  rows: TableRow[];
}

export interface TemplateField {
  _id: string;
  fieldId: string;
  technicalName: string;
  uiDisplayName: string;
  fieldType: FieldType;
  fieldGroup?: string;
  isRequired: boolean;
  isReadonly?: boolean;
  placeholder?: string;
  helpText?: string;
  validation?: FieldValidation;
  gridSize: number;
  sortOrder: number;
  isActive: boolean;
  options?: FieldOption[];
  dataSource?: string;
  dataSourceConfig?: DataSourceConfig;
  defaultValue?: string;
  metadata?: any;
  subFields?: TemplateField[]; // For group fields
  
  // Enhanced field properties
  prefix?: string; // For currency fields
  suffix?: string; // For currency fields
  formula?: string; // For calculated fields (deprecated, use calculatedField)
  calculatedField?: CalculatedFieldConfig; // For calculated fields
  displayFormat?: string; // For calculated fields
  columns?: TableColumn[]; // For table fields
  rows?: TableRow[]; // For table fields
  tableConfig?: DynamicTableConfig; // For dynamic_table fields
}

export interface BankSpecificField {
  _id: string;
  fieldId: string;
  technicalName: string;
  uiDisplayName: string;
  fieldType: FieldType;
  fieldGroup?: string;
  section?: string; // Added for section support (e.g., 'part_a', 'part_b')
  isRequired: boolean;
  isReadonly?: boolean;
  placeholder?: string;
  helpText?: string;
  validation?: FieldValidation;
  gridSize: number;
  sortOrder: number;
  isActive: boolean;
  options?: FieldOption[];
  dataSource?: string;
  dataSourceConfig?: DataSourceConfig;
  defaultValue?: string;
  metadata?: any;
  subFields?: BankSpecificField[]; // For group fields
  
  // Enhanced field properties
  prefix?: string; // For currency fields
  suffix?: string; // For currency fields
  formula?: string; // For calculated fields (deprecated, use calculatedField)
  calculatedField?: CalculatedFieldConfig; // For calculated fields
  displayFormat?: string; // For calculated fields
  columns?: TableColumn[]; // For table fields
  rows?: TableRow[]; // For table fields
  tableConfig?: DynamicTableConfig; // For dynamic_table fields
}

export interface BankSpecificSection {
  sectionId: string;
  sectionName: string;
  sortOrder: number;
  description?: string;
  fields: BankSpecificField[];
}

export interface BankSpecificTab {
  tabId: string;
  tabName: string;
  sortOrder: number;
  hasSections: boolean;
  description?: string;
  fields: BankSpecificField[];
  sections?: BankSpecificSection[];
}

export interface AggregatedTemplateResponse {
  templateInfo: {
    templateId: string;
    templateName: string;
    propertyType: string;
    bankCode: string;
    bankName: string;
    version: string;
  };
  commonFields: TemplateField[];
  bankSpecificTabs: BankSpecificTab[];
  aggregatedAt: string;
}

export interface TemplateInfo {
  templateId: string;
  templateName: string;
  propertyType: string;
  bankCode: string;
  bankName: string;
  version: string;
}

export interface FieldGroup {
  groupName: string;
  displayName: string;
  fields: (TemplateField | BankSpecificField)[];
  sortOrder?: number;
}

export interface FieldGroupSection {
  id: string;
  name: string;
  fields: BankSpecificField[];
}

export interface FieldGroupTab {
  id: string;
  name: string;
  fields: BankSpecificField[];
  sections?: FieldGroupSection[];
}

export interface ProcessedTemplateData {
  templateInfo: TemplateInfo;
  commonFieldGroups: FieldGroup[];
  bankSpecificTabs: BankSpecificTab[];
  allFields: (TemplateField | BankSpecificField)[];
  totalFieldCount: number;
}