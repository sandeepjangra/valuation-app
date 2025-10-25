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
  bankSpecificFields: BankSpecificField[];
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

export interface ProcessedTemplateData {
  templateInfo: TemplateInfo;
  commonFieldGroups: FieldGroup[];
  bankSpecificFieldGroups: FieldGroup[];
  allFields: (TemplateField | BankSpecificField)[];
  totalFieldCount: number;
}