// Template Field Models for Aggregated API Response

import { FieldType, FieldOption, FieldValidation, DataSourceConfig } from './common-field.model';

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