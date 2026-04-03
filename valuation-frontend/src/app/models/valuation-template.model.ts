// Enums

export enum FieldTypeDto {
  // Inputs
  Text = 0,
  Number = 1,
  Date = 2,
  Dropdown = 3,
  FileUpload = 4,
  Currency = 5,
  Textarea = 6,
  Checkbox = 7,
  Radio = 8,
  // Structure
  Container = 9,
  // Complex
  Table = 10,
  // Individual tab panel (TabField)
  Tab = 11
}

export enum ContainerTypeDto {
  TabGroup = 0,   // TabsField  — the tab bar wrapper, children are TabField[]
  Tab = 1,        // TabField   — a single tab panel, children are BaseField[]
  Group = 2,      // GroupField — dashed card grouping inputs
  Section = 3     // SectionField — titled collapsible card
}

export enum PropertyTypeDto {
  House = 0,
  Flat = 1,
  Apartment = 2,
  Land = 3,
  Commercial = 4,
  Other = 5
}

export enum AttachmentCategoryDto {
  PropertyPhoto = 0,
  LegalDocument = 1,
  MapOrSketch = 2,
  MarketComparison = 3,
  ValuerSignature = 4,
  Other = 5
}

export enum AggregateTypeDto {
  Sum = 0,
  Average = 1,
  Min = 2,
  Max = 3,
  Count = 4
}

export enum OperatorTypeDto {
  Equals = 0,
  NotEquals = 1,
  GreaterThan = 2,
  LessThan = 3,
  Contains = 4
}

// Supporting models

export interface BankDto {
  bankName: string;
  bankCode: string;
}

export interface InputValidationRulesDto {
  min?: number;
  max?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  errorMessage?: string;
}

export interface VisibilityRule {
  sourceFieldId: string;
  operator: OperatorTypeDto;
  targetValue?: string;
}

export interface TableColumnDto {
  fieldId: string;
  label: string;
  fieldType: FieldTypeDto;
  width?: string;
  isReadonly: boolean;
  options?: string[];
  validationRules?: InputValidationRulesDto;
}

export interface TableSummary {
  columnFieldId: string;
  operation: AggregateTypeDto;
  label?: string;
  summaryFieldId: string;
}

export interface CalculationRule {
  ruleId: string;
  triggerFieldIds: string[];
  formula: string;
  targetFieldId: string;
}

// ── Polymorphic field hierarchy ───────────────────────────────────────────────
// $type discriminator matches C# [JsonDerivedType] values

export interface BaseField {
  $type: 'input' | 'table' | 'container' | 'attachment';
  fieldId: string;
  label: string;
  displayOrder: number;
  fieldType: FieldTypeDto;
  isVisible: boolean;
  visibility?: VisibilityRule;
}

// input — maps to C# InputField
export interface InputField extends BaseField {
  $type: 'input';
  specificType: FieldTypeDto;
  defaultValue?: string;
  isRequired: boolean;
  isReadonly: boolean;
  helpText?: string;
  placeholderText?: string;
  options?: string[];
  validationRules?: InputValidationRulesDto;
}

// container — base for all container types, discriminated further by containerType
export interface ContainerField extends BaseField {
  $type: 'container';
  container: ContainerTypeDto;
}

// TabsField — containerType = TabGroup
// Children are TabField[] (the individual tab panels)
export interface TabsField extends ContainerField {
  container: ContainerTypeDto.TabGroup;
  children: TabField[];
}

// TabField — containerType = Tab
// Children are any BaseField (inputs, tables, groups, sections, nested tabs…)
export interface TabField extends ContainerField {
  container: ContainerTypeDto.Tab;
  children: BaseField[];
}

// SectionField — containerType = Section
export interface SectionField extends ContainerField {
  container: ContainerTypeDto.Section;
  children: BaseField[];
  isCollapsible: boolean;
  isCollapsed: boolean;
}

// GroupField — containerType = Group
export interface GroupField extends ContainerField {
  container: ContainerTypeDto.Group;
  children: BaseField[];
  isCollapsible: boolean;
  isCollapsed: boolean;
}

// table — maps to C# TableField
export interface TableField extends BaseField {
  $type: 'table';
  columns: TableColumnDto[];
  rows?: Record<string, any>[]; // ⭐ Add rows property for pre-filled data from API
  summaries: TableSummary[];
  minRows: number;
  maxRows?: number;
  allowAddRows: boolean;
  allowDeleteRows: boolean;
  showFooter: boolean;
}

// attachment — maps to C# AttachmentField
export interface AttachmentField extends BaseField {
  $type: 'attachment';
  allowedExtensions?: string[];
  maxFileSize: number;
  allowMultiple: boolean;
  category: AttachmentCategoryDto;
}

// Main template model
export interface ValuationTemplate {
  templateId: string;
  templateName: string;
  templateDescription: string;
  bankDetails: BankDto;
  propertyType: PropertyTypeDto;
  elements: BaseField[];
  calculationRules: CalculationRule[];
  version?: string;
  status?: string;
  isActive: boolean;
  createdAt?: string;
  updatedAt?: string;
}
