export interface CommonField {
  _id: string;
  fieldId: string;
  technicalName: string;
  uiDisplayName: string;
  fieldType: FieldType;
  isRequired: boolean;
  isReadonly?: boolean;
  placeholder: string;
  helpText: string;
  validation?: FieldValidation;
  gridSize: number;
  sortOrder: number;
  isActive: boolean;
  options?: FieldOption[];
  dataSource?: string;
  dataSourceConfig?: DataSourceConfig;
  defaultValue?: string;
  createdAt?: string;
  updatedAt?: string;
  version?: number;
  createdBy?: string;
  metadata?: any;
}

export interface FieldOption {
  value: string;
  label: string;
}

export interface FieldValidation {
  pattern?: string;
  maxLength?: number;
  minLength?: number;
  maxDate?: string;
  minDate?: string;
  min?: number;
  max?: number;
}

export interface DataSourceConfig {
  collection: string;
  nestedPath?: string;
  valueField: string;
  labelField: string;
  filter?: any;
  sortBy?: string;
  dependsOn?: string;
}

export type FieldType = 
  | 'text' 
  | 'date' 
  | 'select' 
  | 'select_dynamic' 
  | 'number' 
  | 'email' 
  | 'tel' 
  | 'textarea' 
  | 'checkbox' 
  | 'radio' 
  | 'file'
  | 'currency'
  | 'group';

export interface CommonFieldsApiResponse {
  metadata: {
    generated_at: string;
    collection_name: string;
    total_documents: number;
    version: string;
    database: string;
    source_collection: string;
  };
  documents: CommonField[];
}

export interface FormFieldValue {
  fieldId: string;
  value: any;
  isValid: boolean;
  errors?: string[];
}