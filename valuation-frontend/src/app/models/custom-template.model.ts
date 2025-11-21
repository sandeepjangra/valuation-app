/**
 * Custom Template Models
 * Interfaces for custom template management system
 */

export interface CustomTemplate {
  _id: string;
  templateName: string;
  description?: string;
  bankCode: string;
  bankName: string;
  propertyType: 'land' | 'apartment';
  fieldValues: Record<string, any>;
  createdBy: string;
  createdByName: string;
  organizationId: string;
  isActive: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date;
  deletedBy?: string;
  clonedFrom?: string;
}

export interface CustomTemplateListItem {
  _id: string;
  templateName: string;
  description?: string;
  bankCode: string;
  bankName: string;
  propertyType: 'land' | 'apartment';
  createdBy: string;
  createdByName: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateCustomTemplateRequest {
  templateName: string;
  description?: string;
  bankCode: string;
  propertyType: 'land' | 'apartment';
  fieldValues: Record<string, any>;
}

export interface UpdateCustomTemplateRequest {
  templateName?: string;
  description?: string;
  fieldValues?: Record<string, any>;
}

export interface CloneCustomTemplateRequest {
  newTemplateName: string;
  description?: string;
}

export interface CustomTemplateFieldsResponse {
  success: boolean;
  bankCode: string;
  propertyType: string;
  templateInfo: {
    templateId: string;
    templateCode: string;
    templateName: string;
    bankCode: string;
    bankName: string;
    propertyType: string;
  };
  commonFields: any[];
  bankSpecificTabs: any[];
}

export interface CustomTemplatesListResponse {
  success: boolean;
  message: string;
  data: CustomTemplateListItem[];
  count: {
    total: number;
    filtered: number;
  };
}

export interface CustomTemplateResponse {
  success: boolean;
  message: string;
  data: CustomTemplate;
}

export interface CustomTemplateCreateResponse {
  success: boolean;
  message: string;
  data: {
    template_id: string;
    template: CustomTemplate;
  };
}

export interface AutoFillStrategy {
  type: 'fill_empty' | 'replace_all' | 'cancel';
  label: string;
  description: string;
}

export const AUTO_FILL_STRATEGIES: AutoFillStrategy[] = [
  {
    type: 'fill_empty',
    label: 'Fill Empty Fields Only',
    description: 'Only fill fields that are currently empty. Your existing data will be preserved.'
  },
  {
    type: 'replace_all',
    label: 'Replace All Fields',
    description: 'Replace all field values with template data. Warning: This will overwrite your current data.'
  },
  {
    type: 'cancel',
    label: 'Cancel',
    description: 'Do not apply the template.'
  }
];
