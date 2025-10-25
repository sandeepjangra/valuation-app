// Template Field Models for Aggregated API Response

import { FieldType, FieldOption, FieldValidation, DataSourceConfig } from './common-field.model';

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