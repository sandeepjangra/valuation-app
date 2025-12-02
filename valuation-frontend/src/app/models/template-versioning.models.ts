/**
 * Template Versioning Models for Frontend
 * Models that match the backend Pydantic models for template versioning system
 */

export interface TemplateField {
  fieldId: string;
  technicalName?: string;
  uiDisplayName: string;
  fieldType: 'text' | 'textarea' | 'number' | 'currency' | 'select' | 'date' | 'group' | 'table' | 'dynamic_table';
  isRequired?: boolean;
  defaultValue?: string;
  placeholder?: string;
  helpText?: string;
  sortOrder: number;
  includeInCustomTemplate?: boolean;
  
  // Field type specific properties
  options?: Array<{ value: string; label: string; }>;
  units?: string[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  
  // Group field properties
  subFields?: TemplateField[];
  
  // Table field properties
  columns?: TemplateColumn[];
  rows?: Record<string, any>[];
  tableConfig?: TableConfig;
  
  // Conditional logic
  conditionalLogic?: {
    field: string;
    operator: '==' | '!=' | '>' | '<' | 'contains';
    value: any;
  };
  
  // Calculation metadata
  formula?: string;
  displayFormat?: string;
  isReadonly?: boolean;
  calculationMetadata?: {
    isCalculatedField?: boolean;
    isCalculationInput?: boolean;
    formula?: string;
    dependencies?: string[];
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
      targetFields?: Array<{
        fieldId: string;
        templateId?: string;
        condition?: string;
        mode?: string;
      }>;
    };
    validationRules?: {
      required?: boolean;
      type?: string;
      message?: string;
    };
    usedInFormulas?: string[];
  };
}

export interface TemplateColumn {
  columnId: string;
  columnName: string;
  fieldType: string;
  isRequired?: boolean;
  isEditable?: boolean;
  isReadonly?: boolean;
  sortOrder?: number;
}

export interface TableConfig {
  tableType?: 'static' | 'row_dynamic' | 'column_dynamic';
  fixedColumns?: TemplateColumn[];
  dynamicColumns?: {
    columnType?: string;
    defaultColumns?: TemplateColumn[];
    addColumnConfig?: {
      buttonText?: string;
      columnNamePattern?: string;
      maxColumns?: number;
    };
  };
  maxRows?: number;
  addRowConfig?: {
    buttonText?: string;
  };
  rows?: Record<string, any>[];
}

export interface TemplateSection {
  sectionId: string;
  sectionName: string;
  sortOrder: number;
  description?: string;
  fields: TemplateField[];
}

export interface TemplateDocument {
  documentId: string;
  documentName: string;
  uiName: string;
  templateId: string;
  templateName: string;
  bankCode: string;
  propertyType: string;
  templateCategory: string;
  sections: TemplateSection[];
  isActive: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface TemplateSnapshot {
  snapshotId: string;
  templateId: string;
  version: string;
  bankCode: string;
  propertyType: string;
  templateCategory: string;
  contentHash: string;
  template: TemplateDocument;
  createdAt: string;
  isLatest: boolean;
  changes?: {
    added?: string[];
    modified?: string[];
    removed?: string[];
  };
}

export interface TemplateVersion {
  templateId: string;
  version: string;
  bankCode: string;
  propertyType: string;
  templateCategory: string;
  isLatest: boolean;
  createdAt: string;
  fieldCount: number;
  sectionCount: number;
}

export interface ValuationReport {
  reportId?: string;
  templateSnapshot: TemplateSnapshot;
  propertyId?: string;
  bankCode: string;
  propertyType: string;
  reportType: string;
  data: Record<string, any>;
  status: 'DRAFT' | 'SUBMITTED' | 'REVIEWED' | 'APPROVED' | 'REJECTED';
  createdBy?: string;
  createdAt?: string;
  updatedAt?: string;
  submittedAt?: string;
  reviewedAt?: string;
  comments?: string;
  calculations?: {
    fieldId: string;
    formula: string;
    result: number;
    inputs: Record<string, number>;
  }[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface CreateReportRequest {
  templateId: string;
  propertyId?: string;
  bankCode: string;
  propertyType: string;
  reportType: string;
  initialData?: Record<string, any>;
}

export interface UpdateReportRequest {
  data: Record<string, any>;
  status?: 'DRAFT' | 'SUBMITTED';
  comments?: string;
}

export interface TemplateVersionsResponse {
  templates: TemplateVersion[];
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  database: {
    status: string;
    database: string;
    collections: number;
    dataSize: number;
    indexSize: number;
    timestamp: string;
  };
  template_versioning: {
    template_versions: number;
    template_snapshots: number;
    total_reports: number;
    status: string;
  };
  features: {
    template_versioning: boolean;
    dynamic_forms: boolean;
    real_time_calculations: boolean;
    multi_bank_support: boolean;
    role_based_access: boolean;
  };
}