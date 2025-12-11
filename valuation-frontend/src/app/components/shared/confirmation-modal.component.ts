import { Component, Input, Output, EventEmitter, OnInit, OnDestroy, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ConfirmationModalData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'warning' | 'danger' | 'info' | 'success';
  icon?: string;
}

@Component({
  selector: 'app-confirmation-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="modal-overlay" 
         [class.show]="isVisible"
         (click)="onOverlayClick($event)"
         #modalOverlay>
      <div class="modal-container" 
           [class.show]="isVisible"
           [ngClass]="'modal-' + (data?.type || 'warning')"
           #modalContainer>
        
        <!-- Modal Header -->
        <div class="modal-header" [ngClass]="'header-' + (data?.type || 'warning')">
          <div class="modal-icon">
            @switch (data?.type || 'warning') {
              @case ('danger') {
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              }
              @case ('warning') {
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              }
              @case ('info') {
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              }
              @case ('success') {
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              }
            }
          </div>
          <h3 class="modal-title">{{ data?.title || 'Confirm Action' }}</h3>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <p class="modal-message">{{ data?.message || 'Are you sure you want to proceed?' }}</p>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button type="button" 
                  class="btn btn-secondary"
                  (click)="onCancel()"
                  #cancelButton>
            {{ data?.cancelText || 'Cancel' }}
          </button>
          <button type="button" 
                  class="btn btn-confirm"
                  [ngClass]="'btn-' + (data?.type || 'warning')"
                  (click)="onConfirm()"
                  #confirmButton>
            {{ data?.confirmText || 'Confirm' }}
          </button>
        </div>
      </div>
    </div>
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
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.3s ease, visibility 0.3s ease;
    }

    .modal-overlay.show {
      opacity: 1;
      visibility: visible;
    }

    .modal-container {
      background: white;
      border-radius: 12px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      max-width: 500px;
      width: 90%;
      max-height: 90vh;
      overflow: hidden;
      transform: scale(0.9) translateY(-20px);
      transition: transform 0.3s ease, opacity 0.3s ease;
      opacity: 0;
    }

    .modal-container.show {
      transform: scale(1) translateY(0);
      opacity: 1;
    }

    .modal-header {
      padding: 24px 24px 16px 24px;
      border-bottom: 1px solid #e5e7eb;
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .modal-header.header-danger {
      background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
      border-bottom-color: #fca5a5;
    }

    .modal-header.header-warning {
      background: linear-gradient(135deg, #fffbeb 0%, #fed7aa 100%);
      border-bottom-color: #fdba74;
    }

    .modal-header.header-info {
      background: linear-gradient(135deg, #eff6ff 0%, #bfdbfe 100%);
      border-bottom-color: #93c5fd;
    }

    .modal-header.header-success {
      background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%);
      border-bottom-color: #86efac;
    }

    .modal-icon {
      flex-shrink: 0;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .modal-danger .modal-icon {
      background: #fee2e2;
      color: #dc2626;
    }

    .modal-warning .modal-icon {
      background: #fef3c7;
      color: #d97706;
    }

    .modal-info .modal-icon {
      background: #dbeafe;
      color: #2563eb;
    }

    .modal-success .modal-icon {
      background: #dcfce7;
      color: #16a34a;
    }

    .modal-icon .icon {
      width: 24px;
      height: 24px;
      stroke-width: 2;
    }

    .modal-title {
      font-size: 18px;
      font-weight: 600;
      margin: 0;
      color: #111827;
    }

    .modal-body {
      padding: 20px 24px;
    }

    .modal-message {
      font-size: 14px;
      line-height: 1.6;
      color: #6b7280;
      margin: 0;
      white-space: pre-line;
    }

    .modal-footer {
      padding: 16px 24px 24px 24px;
      display: flex;
      gap: 12px;
      justify-content: flex-end;
    }

    .btn {
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid transparent;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 80px;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: #f9fafb;
      color: #374151;
      border-color: #d1d5db;
    }

    .btn-secondary:hover:not(:disabled) {
      background: #f3f4f6;
      border-color: #9ca3af;
    }

    .btn-confirm.btn-danger {
      background: #dc2626;
      color: white;
    }

    .btn-confirm.btn-danger:hover:not(:disabled) {
      background: #b91c1c;
    }

    .btn-confirm.btn-warning {
      background: #d97706;
      color: white;
    }

    .btn-confirm.btn-warning:hover:not(:disabled) {
      background: #b45309;
    }

    .btn-confirm.btn-info {
      background: #2563eb;
      color: white;
    }

    .btn-confirm.btn-info:hover:not(:disabled) {
      background: #1d4ed8;
    }

    .btn-confirm.btn-success {
      background: #16a34a;
      color: white;
    }

    .btn-confirm.btn-success:hover:not(:disabled) {
      background: #15803d;
    }

    /* Animation keyframes */
    @keyframes modalSlideIn {
      from {
        transform: scale(0.9) translateY(-20px);
        opacity: 0;
      }
      to {
        transform: scale(1) translateY(0);
        opacity: 1;
      }
    }

    @keyframes modalSlideOut {
      from {
        transform: scale(1) translateY(0);
        opacity: 1;
      }
      to {
        transform: scale(0.9) translateY(-20px);
        opacity: 0;
      }
    }

    /* Focus styles for accessibility */
    .btn:focus {
      outline: 2px solid #3b82f6;
      outline-offset: 2px;
    }
  `]
})
export class ConfirmationModalComponent implements OnInit, OnDestroy {
  @Input() data: ConfirmationModalData | null = null;
  @Input() isVisible: boolean = false;
  
  @Output() confirmed = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  @ViewChild('modalOverlay') modalOverlay!: ElementRef;
  @ViewChild('modalContainer') modalContainer!: ElementRef;
  @ViewChild('cancelButton') cancelButton!: ElementRef;
  @ViewChild('confirmButton') confirmButton!: ElementRef;

  ngOnInit() {
    if (this.isVisible) {
      this.focusConfirmButton();
    }
  }

  ngOnDestroy() {
    // Cleanup if needed
  }

  onOverlayClick(event: MouseEvent): void {
    // Close modal if clicking on overlay (outside modal container)
    if (event.target === this.modalOverlay.nativeElement) {
      this.onCancel();
    }
  }

  onConfirm(): void {
    this.confirmed.emit();
  }

  onCancel(): void {
    this.cancelled.emit();
  }

  private focusConfirmButton(): void {
    // Focus the confirm button for accessibility
    setTimeout(() => {
      if (this.confirmButton) {
        this.confirmButton.nativeElement.focus();
      }
    }, 100);
  }
}