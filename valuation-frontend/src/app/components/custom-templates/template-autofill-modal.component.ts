/**
 * Template Auto-Fill Modal Component
 * Displays modal with options for applying template values to form
 */

import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AUTO_FILL_STRATEGIES, AutoFillStrategy } from '../../models/custom-template.model';

export interface AutoFillChoice {
  strategy: 'fill_empty' | 'replace_all' | 'cancel';
  confirmed: boolean;
}

@Component({
  selector: 'app-template-autofill-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    @if (isOpen()) {
      <div class="modal-overlay" (click)="onOverlayClick()">
        <div class="modal-container" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h2>Apply Template: {{ templateName() }}</h2>
            <button 
              type="button" 
              class="close-button"
              (click)="onCancel()"
              aria-label="Close modal">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <p class="modal-description">
              Choose how you want to apply this template to your form:
            </p>

            <div class="strategy-options">
              @for (strategy of strategies; track strategy.type) {
                <label 
                  class="strategy-option"
                  [class.selected]="selectedStrategy() === strategy.type">
                  <input 
                    type="radio" 
                    name="strategy" 
                    [value]="strategy.type"
                    [(ngModel)]="selectedStrategyValue"
                    (change)="onStrategyChange(strategy.type)"
                    class="strategy-radio">
                  <div class="strategy-content">
                    <div class="strategy-header">
                      <svg class="strategy-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        @if (strategy.type === 'fill_empty') {
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        }
                        @if (strategy.type === 'replace_all') {
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                        }
                        @if (strategy.type === 'cancel') {
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        }
                      </svg>
                      <span class="strategy-label">{{ strategy.label }}</span>
                    </div>
                    <p class="strategy-description">{{ strategy.description }}</p>
                  </div>
                </label>
              }
            </div>
          </div>

          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary"
              (click)="onCancel()">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              (click)="onConfirm()"
              [disabled]="!selectedStrategy()">
              Apply
            </button>
          </div>
        </div>
      </div>
    }
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      animation: fadeIn 0.2s;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .modal-container {
      background: white;
      border-radius: 0.75rem;
      width: 90%;
      max-width: 600px;
      max-height: 90vh;
      overflow: hidden;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      animation: slideUp 0.3s;
    }

    @keyframes slideUp {
      from { 
        opacity: 0;
        transform: translateY(20px);
      }
      to { 
        opacity: 1;
        transform: translateY(0);
      }
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem;
      border-bottom: 1px solid #e2e8f0;
    }

    .modal-header h2 {
      font-size: 1.25rem;
      font-weight: 700;
      color: #1a202c;
      margin: 0;
    }

    .close-button {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 2rem;
      height: 2rem;
      padding: 0;
      border: none;
      background: transparent;
      color: #718096;
      border-radius: 0.375rem;
      cursor: pointer;
      transition: all 0.2s;
    }

    .close-button:hover {
      background: #f7fafc;
      color: #2d3748;
    }

    .close-button svg {
      width: 1.5rem;
      height: 1.5rem;
    }

    .modal-body {
      padding: 1.5rem;
      max-height: calc(90vh - 200px);
      overflow-y: auto;
    }

    .modal-description {
      font-size: 0.9375rem;
      color: #4a5568;
      margin: 0 0 1.5rem 0;
    }

    .strategy-options {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .strategy-option {
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      padding: 1rem;
      border: 2px solid #e2e8f0;
      border-radius: 0.5rem;
      cursor: pointer;
      transition: all 0.2s;
    }

    .strategy-option:hover {
      border-color: #cbd5e0;
      background: #f7fafc;
    }

    .strategy-option.selected {
      border-color: #4299e1;
      background: #ebf8ff;
    }

    .strategy-radio {
      margin-top: 0.25rem;
      cursor: pointer;
    }

    .strategy-content {
      flex: 1;
    }

    .strategy-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }

    .strategy-icon {
      width: 1.5rem;
      height: 1.5rem;
      flex-shrink: 0;
    }

    .strategy-option.selected .strategy-icon {
      color: #4299e1;
    }

    .strategy-label {
      font-size: 1rem;
      font-weight: 600;
      color: #2d3748;
    }

    .strategy-description {
      font-size: 0.875rem;
      color: #718096;
      margin: 0;
      line-height: 1.5;
    }

    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: 1rem;
      padding: 1.5rem;
      border-top: 1px solid #e2e8f0;
      background: #f7fafc;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.625rem 1.25rem;
      font-size: 0.9375rem;
      font-weight: 600;
      border-radius: 0.5rem;
      border: none;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-primary {
      background: #4299e1;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #3182ce;
    }

    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: white;
      color: #2d3748;
      border: 1px solid #e2e8f0;
    }

    .btn-secondary:hover {
      background: #f7fafc;
    }

    @media (max-width: 640px) {
      .modal-container {
        width: 95%;
        max-height: 95vh;
      }

      .modal-footer {
        flex-direction: column-reverse;
      }

      .btn {
        width: 100%;
      }
    }
  `]
})
export class TemplateAutofillModalComponent {
  @Input() set show(value: boolean) {
    this.isOpen.set(value);
  }
  
  @Input() set template(value: string) {
    this.templateName.set(value);
  }

  @Output() choice = new EventEmitter<AutoFillChoice>();

  isOpen = signal<boolean>(false);
  templateName = signal<string>('');
  selectedStrategy = signal<'fill_empty' | 'replace_all' | 'cancel' | null>(null);
  selectedStrategyValue: string = '';

  strategies = AUTO_FILL_STRATEGIES;

  onStrategyChange(strategy: 'fill_empty' | 'replace_all' | 'cancel'): void {
    this.selectedStrategy.set(strategy);
  }

  onOverlayClick(): void {
    this.onCancel();
  }

  onCancel(): void {
    this.choice.emit({
      strategy: 'cancel',
      confirmed: false
    });
    this.reset();
  }

  onConfirm(): void {
    const strategy = this.selectedStrategy();
    if (!strategy) return;

    this.choice.emit({
      strategy: strategy === 'cancel' ? 'cancel' : strategy,
      confirmed: strategy !== 'cancel'
    });
    this.reset();
  }

  private reset(): void {
    this.isOpen.set(false);
    this.selectedStrategy.set(null);
    this.selectedStrategyValue = '';
  }
}
