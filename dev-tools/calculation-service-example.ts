/**
 * Enhanced Calculation Service for SBI Land Template
 * Handles real-time calculations and auto-population
 */

export interface CalculationField {
  fieldId: string;
  formula: string;
  dependencies: string[];
  displayFormat: string;
  precision: number;
  realTimeUpdate: boolean;
  calculationDisplay: {
    showFormula: boolean;
    formulaTemplate: string;
    showInRealTime: boolean;
    highlightOnUpdate: boolean;
  };
  autoPopulate?: {
    targetField: string;
    targetSection?: string;
    targetCategory?: string;
    enabled: boolean;
    triggerOnChange: boolean;
  };
}

export interface AutoPopulateField {
  fieldId: string;
  sourceField: string;
  sourceCategory?: string;
  enabled: boolean;
  allowManualOverride: boolean;
  showSourceInfo: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class CalculationService {
  
  constructor() {}

  /**
   * Calculate estimated land value
   * Formula: Total Extent × Valuation Rate
   */
  calculateEstimatedLandValue(totalExtent: number, valuationRate: number): number {
    if (!totalExtent || !valuationRate) {
      return 0;
    }
    return totalExtent * valuationRate;
  }

  /**
   * Format calculation display for UI
   */
  formatCalculationDisplay(
    totalExtent: number, 
    valuationRate: number, 
    result: number,
    template: string = '{total_extent_plot} × {valuation_rate} = ₹{result}'
  ): string {
    return template
      .replace('{total_extent_plot}', this.formatNumber(totalExtent))
      .replace('{valuation_rate}', this.formatCurrency(valuationRate))
      .replace('{result}', this.formatCurrency(result));
  }

  /**
   * Format number for display
   */
  formatNumber(value: number): string {
    if (value === null || value === undefined) return '0';
    return new Intl.NumberFormat('en-IN').format(value);
  }

  /**
   * Format currency for display
   */
  formatCurrency(value: number): string {
    if (value === null || value === undefined) return '₹0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(value);
  }

  /**
   * Check if all dependencies are satisfied for calculation
   */
  canCalculate(dependencies: string[], formData: any): boolean {
    return dependencies.every(dep => {
      const value = this.getFieldValue(dep, formData);
      return value !== null && value !== undefined && value !== '' && !isNaN(Number(value));
    });
  }

  /**
   * Get field value from form data
   */
  getFieldValue(fieldId: string, formData: any): any {
    return formData[fieldId]?.value || formData[fieldId] || null;
  }

  /**
   * Perform calculation based on field configuration
   */
  performCalculation(field: CalculationField, formData: any): {
    result: number;
    displayText: string;
    canCalculate: boolean;
  } {
    const canCalc = this.canCalculate(field.dependencies, formData);
    
    if (!canCalc) {
      return {
        result: 0,
        displayText: 'Calculation pending...',
        canCalculate: false
      };
    }

    let result = 0;
    
    // Handle different calculation types
    if (field.formula === 'total_extent_plot * valuation_rate') {
      const totalExtent = Number(this.getFieldValue('total_extent_plot', formData));
      const valuationRate = Number(this.getFieldValue('valuation_rate', formData));
      result = this.calculateEstimatedLandValue(totalExtent, valuationRate);
    }

    const displayText = this.formatCalculationDisplay(
      Number(this.getFieldValue('total_extent_plot', formData)),
      Number(this.getFieldValue('valuation_rate', formData)),
      result,
      field.calculationDisplay.formulaTemplate
    );

    return {
      result: Number(result.toFixed(field.precision || 2)),
      displayText,
      canCalculate: true
    };
  }
}

/**
 * Enhanced Report Form Component with Calculation Support
 */
@Component({
  // ... existing component code
})
export class ReportFormComponent implements OnInit, OnDestroy {
  
  calculatedFields: Map<string, CalculationField> = new Map();
  autoPopulateFields: Map<string, AutoPopulateField> = new Map();
  
  constructor(
    private calculationService: CalculationService,
    // ... other dependencies
  ) {}

  ngOnInit() {
    // Initialize calculation fields from template metadata
    this.initializeCalculationFields();
    
    // Set up form value change listeners for real-time calculation
    this.setupCalculationListeners();
    
    // ... existing initialization code
  }

  /**
   * Initialize calculation fields from template
   */
  initializeCalculationFields() {
    // Extract calculation fields from template
    this.templateData.sections?.forEach(section => {
      section.fields?.forEach(field => {
        if (field.fieldType === 'calculated' && field.calculation) {
          this.calculatedFields.set(field.fieldId, {
            fieldId: field.fieldId,
            formula: field.calculation.formula,
            dependencies: field.calculation.dependencies,
            displayFormat: field.calculation.displayFormat,
            precision: field.calculation.precision,
            realTimeUpdate: field.calculation.realTimeUpdate,
            calculationDisplay: field.calculation.calculationDisplay,
            autoPopulate: field.autoPopulate
          });
        }
        
        if (field.autoPopulated) {
          this.autoPopulateFields.set(field.fieldId, {
            fieldId: field.fieldId,
            sourceField: field.autoPopulated.sourceField,
            sourceCategory: field.autoPopulated.sourceCategory,
            enabled: field.autoPopulated.enabled,
            allowManualOverride: field.autoPopulated.allowManualOverride,
            showSourceInfo: field.autoPopulated.showSourceInfo
          });
        }
      });
    });
  }

  /**
   * Set up listeners for real-time calculations
   */
  setupCalculationListeners() {
    // Listen to form changes for calculation triggers
    this.reportForm.valueChanges.pipe(
      debounceTime(300), // Debounce for performance
      takeUntil(this.destroy$)
    ).subscribe(formData => {
      this.performAllCalculations(formData);
    });
  }

  /**
   * Perform all active calculations
   */
  performAllCalculations(formData: any) {
    this.calculatedFields.forEach((calcField, fieldId) => {
      if (calcField.realTimeUpdate) {
        const calculation = this.calculationService.performCalculation(calcField, formData);
        
        // Update the calculated field
        this.updateCalculatedField(fieldId, calculation);
        
        // Handle auto-population if configured
        if (calcField.autoPopulate?.enabled && calculation.canCalculate) {
          this.handleAutoPopulation(calcField, calculation.result);
        }
      }
    });
  }

  /**
   * Update calculated field in the form
   */
  updateCalculatedField(fieldId: string, calculation: any) {
    const control = this.reportForm.get(fieldId);
    if (control) {
      control.setValue(calculation.result, { emitEvent: false });
      
      // Update UI display
      const fieldElement = document.querySelector(`[data-field-id="${fieldId}"]`);
      if (fieldElement) {
        const displayElement = fieldElement.querySelector('.calculation-display');
        if (displayElement) {
          displayElement.textContent = calculation.displayText;
          
          // Add highlight animation
          if (calculation.canCalculate) {
            displayElement.classList.add('calculation-updated');
            setTimeout(() => {
              displayElement.classList.remove('calculation-updated');
            }, 1000);
          }
        }
      }
    }
  }

  /**
   * Handle auto-population to other fields
   */
  handleAutoPopulation(calcField: CalculationField, value: number) {
    const autoPopConfig = calcField.autoPopulate;
    if (!autoPopConfig) return;

    // Find target field in different tab/section
    const targetControl = this.reportForm.get(autoPopConfig.targetField);
    if (targetControl) {
      // Only auto-populate if field is empty or user hasn't manually entered value
      const currentValue = targetControl.value;
      const shouldPopulate = !currentValue || currentValue === 0 || 
                           targetControl.hasError('autoPopulated');

      if (shouldPopulate) {
        targetControl.setValue(value);
        targetControl.markAsTouched();
        
        // Add visual indicator that this was auto-populated
        const targetElement = document.querySelector(`[data-field-id="${autoPopConfig.targetField}"]`);
        if (targetElement) {
          targetElement.classList.add('auto-populated');
          
          // Show source reference tooltip
          const tooltip = targetElement.querySelector('.auto-populate-tooltip');
          if (tooltip) {
            tooltip.textContent = `Auto-calculated from ${calcField.fieldId}`;
          }
        }
      }
    }
  }
}