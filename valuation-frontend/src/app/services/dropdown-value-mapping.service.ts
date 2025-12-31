import { Injectable } from '@angular/core';
import { TemplateField } from '../models/template-field.model';

@Injectable({
  providedIn: 'root'
})
export class DropdownValueMappingService {

  /**
   * Convert technical values (stored in DB) to display labels for form population
   * @param fieldValue The value from database (e.g., "cc_road")
   * @param field The template field configuration
   * @returns The corresponding label (e.g., "CC Road") or original value if no mapping found
   */
  convertValueToLabel(fieldValue: any, field: TemplateField): any {
    if (field.fieldType !== 'select' || !field.options || !fieldValue) {
      return fieldValue;
    }

    // Find the option that matches the stored value
    const matchingOption = field.options.find(option => option.value === fieldValue);
    
    if (matchingOption) {
      console.log(`🔄 Converting DB value "${fieldValue}" to label "${matchingOption.label}" for field ${field.fieldId}`);
      return matchingOption.label;
    }

    // If no matching option found, return original value
    console.warn(`⚠️ No matching option found for value "${fieldValue}" in field ${field.fieldId}`);
    return fieldValue;
  }

  /**
   * Convert display labels back to technical values for form control population
   * @param displayValue The label shown to user (e.g., "CC Road")  
   * @param field The template field configuration
   * @returns The corresponding technical value (e.g., "cc_road") or original value if no mapping found
   */
  convertLabelToValue(displayValue: any, field: TemplateField): any {
    if (field.fieldType !== 'select' || !field.options || !displayValue) {
      return displayValue;
    }

    // Find the option that matches the display label
    const matchingOption = field.options.find(option => option.label === displayValue);
    
    if (matchingOption) {
      console.log(`🔄 Converting label "${displayValue}" to form value "${matchingOption.value}" for field ${field.fieldId}`);
      return matchingOption.value;
    }

    // If no matching option found, try to find by value (backward compatibility)
    const valueMatch = field.options.find(option => option.value === displayValue);
    if (valueMatch) {
      console.log(`🔄 Value "${displayValue}" already in correct format for field ${field.fieldId}`);
      return displayValue;
    }

    // If no match found, return original value
    console.warn(`⚠️ No matching option found for display value "${displayValue}" in field ${field.fieldId}`);
    return displayValue;
  }

  /**
   * Convert form values (technical codes) to display labels for storage
   * @param formValue The value from form control (e.g., "cc_road")
   * @param field The template field configuration  
   * @returns The corresponding label (e.g., "CC Road") for storage
   */
  convertFormValueToStorageLabel(formValue: any, field: TemplateField): any {
    if (field.fieldType !== 'select' || !field.options || !formValue) {
      return formValue;
    }

    // Find the option that matches the form value
    const matchingOption = field.options.find(option => option.value === formValue);
    
    if (matchingOption) {
      console.log(`💾 Converting form value "${formValue}" to storage label "${matchingOption.label}" for field ${field.fieldId}`);
      return matchingOption.label;
    }

    // If no matching option found, return original value
    console.warn(`⚠️ No matching option found for form value "${formValue}" in field ${field.fieldId}`);
    return formValue;
  }

  /**
   * Get all field mappings for a template (for debugging)
   * @param templateFields Array of template fields
   * @returns Mapping object for debugging
   */
  getFieldMappings(templateFields: TemplateField[]): Record<string, any> {
    const mappings: Record<string, any> = {};
    
    templateFields.forEach(field => {
      if (field.fieldType === 'select' && field.options) {
        mappings[field.fieldId] = {
          fieldType: field.fieldType,
          valueToLabel: {},
          labelToValue: {}
        };
        
        field.options.forEach(option => {
          mappings[field.fieldId].valueToLabel[option.value] = option.label;
          mappings[field.fieldId].labelToValue[option.label] = option.value;
        });
      }
    });
    
    return mappings;
  }
}