export interface PDFTemplateDesigner {
  _id?: string;
  name: string;
  bankCode: string;
  propertyType: 'land' | 'apartment';
  description?: string;
  layout: PDFDesignerLayout;
  organizationId: string;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface PDFDesignerLayout {
  pageSize: 'A4' | 'Letter';
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  sections: PDFDesignerSection[];
}

export interface PDFDesignerSection {
  id: string;
  name: string;
  type: 'header' | 'content' | 'footer' | 'custom';
  order: number;
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
    borderStyle?: 'solid' | 'dashed' | 'dotted' | 'none';
    padding: number;
    margin: number;
  };
  elements: PDFDesignerElement[];
}

export interface PDFDesignerElement {
  id: string;
  type: 'text' | 'table' | 'list' | 'field' | 'image';
  order: number;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  content: any; // Will be specific to element type
  style: PDFDesignerElementStyle;
}

export interface PDFDesignerElementStyle {
  fontSize: number;
  fontWeight: 'normal' | 'bold' | '100' | '200' | '300' | '400' | '500' | '600' | '700' | '800' | '900';
  fontStyle: 'normal' | 'italic';
  textAlign: 'left' | 'center' | 'right' | 'justify';
  textDecoration: 'none' | 'underline' | 'line-through';
  color: string;
  backgroundColor?: string;
  borderColor?: string;
  borderWidth?: number;
  borderStyle?: 'solid' | 'dashed' | 'dotted' | 'none';
  padding: number;
  margin: number;
  lineHeight: number;
}

// Specific element types
export interface PDFTextElement extends PDFDesignerElement {
  type: 'text';
  content: {
    text: string;
    placeholder?: string;
    isEditable: boolean;
    formatting: {
      bold: boolean;
      italic: boolean;
      underline: boolean;
    };
  };
}

export interface PDFTableElement extends PDFDesignerElement {
  type: 'table';
  content: {
    rows: number;
    columns: number;
    headers: string[];
    data: PDFTableCell[][];
    styling: {
      headerStyle: PDFDesignerElementStyle;
      cellStyle: PDFDesignerElementStyle;
      borderCollapse: boolean;
      alternateRowColors: boolean;
      alternateColor?: string;
    };
  };
}

export interface PDFTableCell {
  value: string;
  colSpan?: number;
  rowSpan?: number;
  style?: Partial<PDFDesignerElementStyle>;
  isHeader?: boolean;
}

export interface PDFListElement extends PDFDesignerElement {
  type: 'list';
  content: {
    listType: 'ordered' | 'unordered' | 'alphabetical' | 'roman';
    orderingStyle: 'numeric' | 'alphabetic-lower' | 'alphabetic-upper' | 'roman-lower' | 'roman-upper';
    items: PDFListItem[];
    indentation: number;
    spacing: number;
  };
}

export interface PDFListItem {
  id: string;
  text: string;
  level: number;
  children?: PDFListItem[];
  style?: Partial<PDFDesignerElementStyle>;
}

export interface PDFFieldElement extends PDFDesignerElement {
  type: 'field';
  content: {
    fieldId: string;
    fieldName: string;
    fieldType: 'text' | 'number' | 'date' | 'currency' | 'boolean';
    defaultValue?: any;
    placeholder?: string;
    validation?: {
      required: boolean;
      minLength?: number;
      maxLength?: number;
      pattern?: string;
    };
  };
}

// Designer tool interfaces
export interface DesignerTool {
  id: string;
  name: string;
  icon: string;
  type: 'section' | 'element';
  category: 'layout' | 'content' | 'data' | 'formatting';
  description: string;
}

export interface DesignerState {
  selectedElement?: PDFDesignerElement;
  selectedSection?: PDFDesignerSection;
  draggedElement?: PDFDesignerElement;
  clipboard?: PDFDesignerElement[];
  zoomLevel: number;
  gridEnabled: boolean;
  snapToGrid: boolean;
  gridSize: number;
}