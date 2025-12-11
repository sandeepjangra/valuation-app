import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="notification-container">
      @for (notification of notificationService.getNotifications(); track notification.id) {
        <div class="notification" [ngClass]="'notification-' + notification.type">
          <div class="notification-content">
            <span class="notification-icon">
              @switch (notification.type) {
                @case ('success') { ✓ }
                @case ('error') { ✗ }
                @case ('warning') { ⚠ }
                @case ('info') { ℹ }
              }
            </span>
            <span class="notification-message">{{ notification.message }}</span>
            <button 
              class="notification-close" 
              (click)="notificationService.remove(notification.id)"
              type="button">
              ×
            </button>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .notification-container {
      position: fixed;
      top: 80px; /* Below header */
      right: 20px;
      z-index: 1050;
      max-width: 400px;
      width: 100%;
    }

    .notification {
      margin-bottom: 10px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      animation: slideInRight 0.3s ease-out;
      border-left: 4px solid;
    }

    .notification-content {
      padding: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      background: white;
      border-radius: 8px;
    }

    .notification-icon {
      font-size: 18px;
      font-weight: bold;
      flex-shrink: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
    }

    .notification-message {
      flex: 1;
      font-size: 14px;
      line-height: 1.4;
      color: #333;
    }

    .notification-close {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      padding: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background-color 0.2s;
      color: #666;
    }

    .notification-close:hover {
      background-color: rgba(0, 0, 0, 0.1);
    }

    /* Success */
    .notification-success {
      border-left-color: #10b981;
    }

    .notification-success .notification-icon {
      background-color: #10b981;
      color: white;
    }

    /* Error */
    .notification-error {
      border-left-color: #ef4444;
    }

    .notification-error .notification-icon {
      background-color: #ef4444;
      color: white;
    }

    /* Warning */
    .notification-warning {
      border-left-color: #f59e0b;
    }

    .notification-warning .notification-icon {
      background-color: #f59e0b;
      color: white;
    }

    /* Info */
    .notification-info {
      border-left-color: #3b82f6;
    }

    .notification-info .notification-icon {
      background-color: #3b82f6;
      color: white;
    }

    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    /* Mobile responsive */
    @media (max-width: 480px) {
      .notification-container {
        top: 70px;
        right: 10px;
        left: 10px;
        max-width: none;
      }
    }
  `]
})
export class NotificationComponent {
  notificationService = inject(NotificationService);
}