export interface ValuationReport {
  _id?: string;
  reportReferenceNumber: string;
  bankCode: string;
  bankName: string;
  bankBranch: string;
  templateId?: string;
  templateName?: string;
  propertyType?: string;
  
  // Common fields
  valuationDate: Date;
  inspectionDate: Date;
  valuationPurpose: string;
  applicantName: string;
  
  // Form data
  commonFieldsData: { [fieldId: string]: any };
  templateFieldsData: { [fieldId: string]: any };
  
  // Status
  status: ReportStatus;
  isDraft: boolean;
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  version: number;
}

export type ReportStatus = 
  | 'draft' 
  | 'in_progress' 
  | 'under_review' 
  | 'completed' 
  | 'approved' 
  | 'rejected';

export interface ReportFormData {
  bankCode: string;
  bankName: string;
  templateId?: string;
  templateName?: string;
  propertyType?: string;
  formValues: { [fieldId: string]: any };
  isValid: boolean;
  isDraft: boolean;
}

export interface NavigationParams {
  bankCode: string;
  bankName: string;
  templateId?: string;
  templateName?: string;
  propertyType?: string;
}