// Template Field Models for Aggregated API Response

import { FieldType, FieldOption, FieldValidation, DataSourceConfig } from './common-field.model';

// Calculation metadata interfaces
export interface CalculationTarget {
  fieldId: string;
  templateId?: string;
  condition: string;
  mode: string;
}

export interface CalculationMetadata {
  isCalculatedField?: boolean;
  isCalculationInput?: boolean;
  formula?: string;
  dependencies?: string[];
  usedInFormulas?: string[];
  calculationTriggers?: string[];
  realTimeUpdate?: boolean;
  showCalculation?: boolean;
  calculationDisplay?: {
    showFormula?: boolean;
    formulaText?: string;
    showSteps?: boolean;
    showResult?: boolean;
  };
  formatting?: {
    currency?: boolean;
    decimalPlaces?: number;
    thousandSeparator?: boolean;
  };
  autoPopulate?: {
    enabled?: boolean;
    targetFields?: CalculationTarget[];
  };
  validationRules?: {
    required?: boolean;
    type?: string;
    min?: number;
    max?: number;
    message?: string;
  };
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
  formula?: string; // For calculated fields
  displayFormat?: string; // For calculated fields
  columns?: TableColumn[]; // For table fields
  rows?: TableRow[]; // For table fields
  tableConfig?: DynamicTableConfig; // For dynamic_table fields
  calculationMetadata?: CalculationMetadata; // For calculated fields
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
  formula?: string; // For calculated fields
  displayFormat?: string; // For calculated fields
  columns?: TableColumn[]; // For table fields
  rows?: TableRow[]; // For table fields
  tableConfig?: DynamicTableConfig; // For dynamic_table fields
  calculationMetadata?: CalculationMetadata; // For calculated fields
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

export interface DocumentType {
  documentId: string;
  documentName: string;
  technicalName: string;
  fieldType: string;
  description: string;
  applicablePropertyTypes: string[];
  applicableBanks: string[];
  isRequired: boolean;
  isActive: boolean;
  sortOrder: number;
  validation?: any;
  helpText?: string;
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
  documentTypes: DocumentType[];
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