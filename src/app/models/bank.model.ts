export interface Bank {
  _id: string;
  bankCode: string;
  bankName: string;
  bankShortName: string;
  bankType: string;
  isActive: boolean;
  headquarters?: {
    city: string;
    state: string;
    pincode: string;
  };
  branches?: BankBranch[];
  templates?: Template[];
  totalBranches?: number;
  createdAt?: string;
  updatedAt?: string;
  version?: number;
}

export interface BankBranch {
  branchId: string;
  branchName: string;
  branchCode: string;
  ifscCode: string;
  micrCode: string;
  address: {
    street: string;
    area: string;
    city: string;
    district: string;
    state: string;
    pincode: string;
    landmark: string;
  };
  contact: {
    phone: string;
    email: string;
    managerName: string;
    managerContact: string;
  };
  coordinates: {
    latitude: number;
    longitude: number;
  };
  services: string[];
  workingHours: {
    weekdays: string;
    saturday: string;
    sunday: string;
  };
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Template {
  templateId: string;
  templateCode: string;
  templateName: string;
  templateType: string;
  propertyType: string;
  description: string;
  version: string;
  isActive: boolean;
  fields: string[];
  validationRules?: {
    required_fields: string[];
    minimum_documents?: number;
  };
  allowCustomFields?: boolean;
  maxCustomFields?: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface BanksApiResponse {
  metadata: {
    generated_at: string;
    collection_name: string;
    total_documents: number;
    version: string;
    database: string;
    source_collection: string;
  };
  documents: Bank[];
}