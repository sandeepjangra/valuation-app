import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, combineLatest } from 'rxjs';
import { map, debounceTime } from 'rxjs/operators';

export interface CalculationResult {
  fieldId: string;
  value: number;
  formula: string;
  inputs: { [key: string]: number };
  formattedValue: string;
  isValid: boolean;
  validationMessage?: string;
}

@Injectable({
  providedIn: 'root'
})
export class SbiCalculationService {
  // Form values tracking
  private formValues = new BehaviorSubject<{ [key: string]: any }>({});
  
  // Calculation results tracking
  private calculationResults = new BehaviorSubject<{ [key: string]: CalculationResult }>({});

  constructor() {
    // Set up real-time calculations for estimated_land_value
    this.setupEstimatedLandValueCalculation();
  }

  // Update form field value and trigger calculations
  updateFieldValue(fieldId: string, value: any): void {
    const currentValues = this.formValues.getValue();
    this.formValues.next({
      ...currentValues,
      [fieldId]: value
    });
  }

  // Get current form values
  getFormValues(): Observable<{ [key: string]: any }> {
    return this.formValues.asObservable();
  }

  // Get calculation results
  getCalculationResults(): Observable<{ [key: string]: CalculationResult }> {
    return this.calculationResults.asObservable();
  }

  // Get specific calculation result
  getCalculationResult(fieldId: string): Observable<CalculationResult | null> {
    return this.calculationResults.pipe(
      map(results => results[fieldId] || null)
    );
  }

  // Setup real-time calculation for Estimated Land Value
  private setupEstimatedLandValueCalculation(): void {
    // Watch for changes in total_extent_plot and valuation_rate
    combineLatest([
      this.formValues.pipe(map(values => values['total_extent_plot'] || 0)),
      this.formValues.pipe(map(values => values['valuation_rate'] || 0))
    ]).pipe(
      debounceTime(300) // Prevent excessive calculations
    ).subscribe(([totalExtent, valuationRate]) => {
      this.calculateEstimatedLandValue(totalExtent, valuationRate);
    });
  }

  // Calculate Estimated Land Value
  private calculateEstimatedLandValue(totalExtent: number, valuationRate: number): void {
    const calculation: CalculationResult = {
      fieldId: 'estimated_land_value',
      formula: 'total_extent_plot × valuation_rate',
      inputs: {
        total_extent_plot: totalExtent,
        valuation_rate: valuationRate
      },
      value: 0,
      formattedValue: '₹0',
      isValid: false
    };

    // Validation
    if (totalExtent <= 0) {
      calculation.validationMessage = 'Total extent must be greater than 0';
    } else if (valuationRate <= 0) {
      calculation.validationMessage = 'Valuation rate must be greater than 0';
    } else {
      // Perform calculation
      calculation.value = totalExtent * valuationRate;
      calculation.formattedValue = this.formatCurrency(calculation.value);
      calculation.isValid = true;
      
      // Auto-populate land_total field
      this.autoPopulateLandTotal(calculation.value);
    }

    // Update calculation results
    const currentResults = this.calculationResults.getValue();
    this.calculationResults.next({
      ...currentResults,
      estimated_land_value: calculation
    });
  }

  // Auto-populate land_total field in Detailed Valuation
  private autoPopulateLandTotal(estimatedValue: number): void {
    // Update the land_total field with the calculated value
    this.updateFieldValue('land_total', estimatedValue);
    
    // Create a calculation result for land_total to show it's auto-populated
    const autoPopulateResult: CalculationResult = {
      fieldId: 'land_total',
      formula: 'Auto-populated from Estimated Land Value',
      inputs: { estimated_land_value: estimatedValue },
      value: estimatedValue,
      formattedValue: this.formatCurrency(estimatedValue),
      isValid: true
    };

    const currentResults = this.calculationResults.getValue();
    this.calculationResults.next({
      ...currentResults,
      land_total: autoPopulateResult
    });
  }

  // Format currency for display
  private formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  // Get calculation display data for UI
  getCalculationDisplayData(fieldId: string): Observable<{
    showCalculation: boolean;
    formula: string;
    inputs: { label: string; value: string }[];
    result: string;
    isAutoPopulated?: boolean;
  } | null> {
    return this.getCalculationResult(fieldId).pipe(
      map(result => {
        if (!result) return null;

        if (fieldId === 'estimated_land_value') {
          return {
            showCalculation: true,
            formula: 'Total Extent × Valuation Rate',
            inputs: [
              { 
                label: 'Total Extent', 
                value: `${result.inputs.total_extent_plot} sq units` 
              },
              { 
                label: 'Valuation Rate', 
                value: this.formatCurrency(result.inputs.valuation_rate) 
              }
            ],
            result: result.formattedValue
          };
        }

        if (fieldId === 'land_total') {
          return {
            showCalculation: true,
            formula: 'Auto-populated from calculation',
            inputs: [
              { 
                label: 'Source', 
                value: 'Estimated Land Value' 
              }
            ],
            result: result.formattedValue,
            isAutoPopulated: true
          };
        }

        return null;
      })
    );
  }

  // Manual override for auto-populated fields
  overrideAutoPopulatedField(fieldId: string, newValue: number): void {
    // Update the field value
    this.updateFieldValue(fieldId, newValue);
    
    // Mark as manually overridden
    const currentResults = this.calculationResults.getValue();
    const existingResult = currentResults[fieldId];
    
    if (existingResult) {
      const overriddenResult: CalculationResult = {
        ...existingResult,
        value: newValue,
        formattedValue: this.formatCurrency(newValue),
        formula: 'Manually overridden'
      };

      this.calculationResults.next({
        ...currentResults,
        [fieldId]: overriddenResult
      });
    }
  }
}