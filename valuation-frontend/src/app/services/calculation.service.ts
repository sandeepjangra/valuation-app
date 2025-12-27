import { Injectable } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { CalculatedFieldConfig, BankSpecificField, TemplateField } from '../models/template-field.model';

@Injectable({
  providedIn: 'root'
})
export class CalculationService {

  constructor() { }

  /**
   * Evaluates a calculated field based on its configuration
   * @param config - The calculated field configuration
   * @param formGroup - The form group containing the field values
   * @returns The calculated value
   */
  evaluateCalculatedField(config: CalculatedFieldConfig, formGroup: FormGroup): number {
    if (!config || !config.sourceFields || config.sourceFields.length === 0) {
      return 0;
    }

    const values = this.getFieldValues(config.sourceFields, formGroup);

    switch (config.type) {
      case 'sum':
        return this.calculateSum(values);
      case 'product':
        return this.calculateProduct(values);
      case 'average':
        return this.calculateAverage(values);
      case 'custom':
        // For future custom formula implementation
        return this.evaluateCustomFormula(config.customFormula || '', values);
      default:
        console.warn(`Unknown calculation type: ${config.type}`);
        return 0;
    }
  }

  /**
   * Retrieves field values from the form group
   * Handles nested fields (e.g., group.subfield)
   */
  private getFieldValues(fieldIds: string[], formGroup: FormGroup): number[] {
    const values: number[] = [];

    for (const fieldId of fieldIds) {
      const value = this.getNestedFieldValue(fieldId, formGroup);
      
      // Convert to number, handle null/undefined/empty
      const numericValue = this.parseNumericValue(value);
      values.push(numericValue);
    }

    return values;
  }

  /**
   * Gets value from potentially nested form control
   * Handles patterns like: 'extra_items.portico', 'building_total'
   */
  private getNestedFieldValue(fieldPath: string, formGroup: FormGroup): any {
    const parts = fieldPath.split('.');
    let control: any = formGroup;

    for (const part of parts) {
      if (control && control.get) {
        control = control.get(part);
      } else {
        return null;
      }
    }

    return control ? control.value : null;
  }

  /**
   * Parses a value to numeric, handling currency strings and null values
   */
  private parseNumericValue(value: any): number {
    if (value === null || value === undefined || value === '') {
      return 0;
    }

    // If already a number
    if (typeof value === 'number') {
      return value;
    }

    // If string, remove currency symbols and commas
    if (typeof value === 'string') {
      const cleaned = value.replace(/[₹$,\s]/g, '');
      const parsed = parseFloat(cleaned);
      return isNaN(parsed) ? 0 : parsed;
    }

    return 0;
  }

  /**
   * Calculates the sum of values
   */
  private calculateSum(values: number[]): number {
    return values.reduce((sum, val) => sum + val, 0);
  }

  /**
   * Calculates the product of values
   */
  private calculateProduct(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((product, val) => product * val, 1);
  }

  /**
   * Calculates the average of values
   */
  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    const sum = this.calculateSum(values);
    return sum / values.length;
  }

  /**
   * Evaluates a custom formula (placeholder for future implementation)
   */
  private evaluateCustomFormula(formula: string, values: number[]): number {
    // TODO: Implement safe formula evaluation
    // For now, return 0
    console.warn('Custom formula evaluation not yet implemented:', formula);
    return 0;
  }

  /**
   * Gets all calculated fields from template data
   * @param fields - Array of template or bank-specific fields
   * @returns Array of field IDs that are calculated
   */
  getCalculatedFields(fields: (TemplateField | BankSpecificField)[]): Map<string, CalculatedFieldConfig> {
    const calculatedFieldsMap = new Map<string, CalculatedFieldConfig>();

    const processFields = (fieldList: (TemplateField | BankSpecificField)[]) => {
      for (const field of fieldList) {
        // Check if field has calculated configuration
        if (field.calculatedField) {
          calculatedFieldsMap.set(field.fieldId, field.calculatedField);
        }
        // Also check for fieldType === 'calculated' (legacy support)
        else if (field.fieldType === 'calculated' && field.formula) {
          // Create calculatedField config from legacy format
          const dependencies = this.extractDependenciesFromFormula(field.formula);
          const calcType = this.determineCalculationType(field.formula, dependencies);
          
          const config: CalculatedFieldConfig = {
            type: calcType,
            sourceFields: dependencies,
            dependencies: dependencies,
            outputFormat: field.displayFormat === 'currency' ? 'currency' : 'number'
          };
          
          if (calcType === 'custom') {
            config.customFormula = field.formula;
          }
          
          calculatedFieldsMap.set(field.fieldId, config);
        }

        // Recursively process subFields (for group fields)
        if (field.subFields && field.subFields.length > 0) {
          processFields(field.subFields);
        }
      }
    };

    processFields(fields);
    return calculatedFieldsMap;
  }

  /**
   * Gets field dependencies for a calculated field
   * Returns all field IDs that when changed, should trigger recalculation
   */
  getFieldDependencies(config: CalculatedFieldConfig): string[] {
    return config.dependencies || config.sourceFields || [];
  }

  /**
   * Checks if a field is calculated
   */
  isCalculatedField(fieldId: string, calculatedFieldsMap: Map<string, CalculatedFieldConfig>): boolean {
    return calculatedFieldsMap.has(fieldId);
  }

  /**
   * Extracts field dependencies from a formula string
   */
  private extractDependenciesFromFormula(formula: string): string[] {
    if (!formula) return [];
    
    // Extract variable names using regex
    const matches = formula.match(/\b[a-zA-Z_][a-zA-Z0-9_]*\b/g) || [];
    
    // Filter out common math functions and operators
    const filtered = matches.filter(dep => 
      !['Math', 'min', 'max', 'round', 'ceil', 'floor', 'parseFloat', 'parseInt'].includes(dep)
    );
    
    // Remove duplicates
    return [...new Set(filtered)];
  }

  /**
   * Determines calculation type based on formula and dependencies
   */
  private determineCalculationType(formula: string, dependencies: string[]): 'sum' | 'product' | 'average' | 'custom' {
    if (!formula || dependencies.length === 0) return 'custom';
    
    // Check for multiplication
    if (formula.includes('*') && dependencies.length === 2) {
      return 'product';
    }
    
    // Check for addition (sum)
    if (formula.includes('+') && dependencies.length >= 2) {
      return 'sum';
    }
    
    // Check for division or other complex operations
    if (formula.includes('/') || formula.includes('-') || formula.includes('(') || formula.includes(')')) {
      return 'custom';
    }
    
    // Default to custom for complex formulas
    return 'custom';
  }

  /**
   * Gets the sum of subfields within a group field
   * Useful for fields like extra_items_total (sum of all subfields in extra_items group)
   */
  calculateGroupFieldSum(groupFieldId: string, formGroup: FormGroup): number {
    const groupControl = formGroup.get(groupFieldId);
    
    if (!groupControl || !(groupControl instanceof FormGroup)) {
      return 0;
    }

    const values: number[] = [];
    
    // Iterate through all controls in the group
    Object.keys(groupControl.controls).forEach(key => {
      const control = groupControl.get(key);
      if (control) {
        const numericValue = this.parseNumericValue(control.value);
        values.push(numericValue);
      }
    });

    return this.calculateSum(values);
  }

  /**
   * Formats a number as Indian currency (₹1,23,456.00)
   */
  formatCurrency(value: number): string {
    if (isNaN(value) || value === null || value === undefined) {
      return '₹0.00';
    }

    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  /**
   * Parses currency string back to number
   */
  parseCurrency(currencyString: string): number {
    if (!currencyString || typeof currencyString !== 'string') {
      return 0;
    }

    // Remove currency symbols, commas, and spaces
    const cleaned = currencyString.replace(/[₹$,\s]/g, '');
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
  }

  /**
   * Auto-detects sum fields for group fields
   * For example, extra_items_total should sum all fields in extra_items group
   */
  detectGroupSumFields(groupFieldId: string, formGroup: FormGroup): string[] {
    const groupControl = formGroup.get(groupFieldId);
    
    if (!groupControl || !(groupControl instanceof FormGroup)) {
      return [];
    }

    // Return all control keys in the group
    return Object.keys(groupControl.controls).map(key => `${groupFieldId}.${key}`);
  }
}
