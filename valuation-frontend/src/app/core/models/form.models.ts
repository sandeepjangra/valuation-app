export interface FormField {
  id: string;
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'date' | 'number' | 'email' | 'tel' | 'checkbox' | 'radio' | 'coordinates';
  required: boolean;
  placeholder?: string;
  validation?: {
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    min?: number;
    max?: number;
  };
  options?: Array<{
    value: string;
    label: string;
  }>;
  defaultValue?: any;
  gridSize: 1 | 2 | 3 | 4 | 6 | 12; // Material Grid system (1-12)
  order: number;
  visible: boolean;
  readonly?: boolean;
  dependsOn?: {
    fieldId: string;
    value: any;
    condition: 'equals' | 'not_equals' | 'greater_than' | 'less_than';
  };
}

export interface FormSection {
  id: string;
  title: string;
  description?: string;
  order: number;
  collapsible: boolean;
  expanded: boolean;
  fields: FormField[];
  visible: boolean;
}

export interface FormTemplate {
  id: string;
  name: string;
  description: string;
  version: string;
  bankId?: string; // Optional - for bank-specific templates
  category: 'general' | 'residential' | 'commercial' | 'industrial';
  sections: FormSection[];
  isActive: boolean;
  createdBy: string;
  createdDate: Date;
  updatedBy?: string;
  updatedDate?: Date;
}

// For storing actual form data
export interface FormData {
  id: string;
  templateId: string;
  templateVersion: string;
  reportId?: string;
  userId: string;
  bankId?: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  data: { [fieldId: string]: any };
  createdDate: Date;
  updatedDate: Date;
  submittedDate?: Date;
  approvedDate?: Date;
}

// Property Description specific interfaces
export interface PropertyDescription {
  reportDate: Date;
  bankDetails: {
    bankName: string;
    branchName: string;
    branchCode: string;
  };
  purpose: string;
  inspectionDate: Date;
  valuerDetails: {
    name: string;
    qualification: string;
    registrationNumber: string;
    sealUploaded: boolean;
  };
  borrowerDetails: {
    name: string;
    fatherName: string;
    address: string;
    contactNumber: string;
    email?: string;
  };
  ownerDetails: {
    name: string;
    relationship: string;
    address: string;
  };
  declarationNoConflict: boolean;
  propertyAddress: {
    fullAddress: string;
    plotNumber: string;
    village: string;
    sector: string;
    district: string;
    state: string;
    pincode: string;
  };
  propertyType: 'residential' | 'commercial' | 'industrial';
  tenure: 'freehold' | 'leasehold';
  locationDetails: {
    plotNo: string;
    village: string;
    sector: string;
    district: string;
    nearbyLandmarks: string[];
  };
  areaClassification: 'urban' | 'semi-urban' | 'rural';
  municipalJurisdiction: string;
  coordinates: {
    latitude: number;
    longitude: number;
    accuracy?: string;
  };
}