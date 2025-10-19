// User and Authentication models
export type UserRole = 'admin' | 'manager' | 'employee';

export interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  permissions: {
    canCreateReports: boolean;
    canEditReports: boolean;
    canViewReports: boolean;
    canDeleteReports: boolean;
    canSubmitReports: boolean;
    canApproveReports: boolean;
    canRejectReports: boolean;
    canViewAllReports: boolean;
    canManageTemplates: boolean;
    canManageBanks: boolean;
    canManageUsers: boolean;
    canExportReports: boolean;
    canViewDashboard: boolean;
  };
  isActive: boolean;
  createdDate: Date;
  lastLoginDate?: Date;
}

// Form and Template models
export * from './form.models';

export interface Bank {
  _id?: string;
  name: string;
  code: string;
  submissionModes: Array<'hardcopy' | 'digital'>;
  isActive: boolean;
  contact?: {
    email?: string;
    phone?: string;
    address?: string;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface PropertyType {
  _id?: string;
  name: string;
  category: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface TemplateField {
  fieldId: string;
  fieldName: string;
  fieldType: 'text' | 'number' | 'date' | 'dropdown' | 'checkbox' | 'textarea' | 'file';
  isRequired: boolean;
  validationRules?: {
    min?: number;
    max?: number;
    pattern?: string;
    maxLength?: number;
  };
  options?: string[]; // for dropdown fields
  placeholder?: string;
  defaultValue?: any;
}

export interface Template {
  _id?: string;
  bankId: string;
  propertyTypeId: string;
  templateName: string;
  version: string;
  fields: TemplateField[];
  isActive: boolean;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ValuationReport {
  _id?: string;
  templateId: string;
  userId: string;
  reportData: Record<string, any>;
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  propertyDetails: {
    address: string;
    propertyType: string;
    area: number;
    coordinates?: {
      latitude: number;
      longitude: number;
    };
  };
  valuationAmount?: number;
  submissionDate?: Date;
  approvalDate?: Date;
  rejectionReason?: string;
  createdAt: Date;
  updatedAt: Date;
}