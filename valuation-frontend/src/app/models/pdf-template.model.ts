export interface PDFTemplate {
  _id?: string;
  name: string;
  bankCode: string;
  propertyType: 'land' | 'apartment';
  description?: string;
  layout: PDFTemplateLayout;
  organizationId: string;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface PDFTemplateLayout {
  pageSize: 'A4' | 'Letter';
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  sections: PDFTemplateSection[];
}

export interface PDFTemplateSection {
  id: string;
  name: string;
  type: 'header' | 'footer' | 'content' | 'table';
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  style: {
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
    padding?: number;
  };
  fields: PDFTemplateField[];
}

export interface PDFTemplateField {
  id: string;
  fieldId: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'currency' | 'boolean';
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  style: {
    fontSize: number;
    fontWeight: 'normal' | 'bold';
    textAlign: 'left' | 'center' | 'right';
    color?: string;
    backgroundColor?: string;
  };
  required: boolean;
}

export interface PDFTemplateListItem {
  _id: string;
  name: string;
  bankCode: string;
  bankName?: string;
  propertyType: 'land' | 'apartment';
  description?: string;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}