import { Injectable, signal } from '@angular/core';

export interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notifications = signal<Notification[]>([]);

  getNotifications = this.notifications.asReadonly();

  show(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', duration: number = 4000) {
    const id = Math.random().toString(36).substr(2, 9);
    const notification: Notification = { id, message, type, duration };
    
    this.notifications.update(notifications => [...notifications, notification]);

    if (duration > 0) {
      setTimeout(() => this.remove(id), duration);
    }

    return id;
  }

  success(message: string, duration?: number) {
    return this.show(message, 'success', duration);
  }

  error(message: string, duration?: number) {
    return this.show(message, 'error', duration);
  }

  warning(message: string, duration?: number) {
    return this.show(message, 'warning', duration);
  }

  info(message: string, duration?: number) {
    return this.show(message, 'info', duration);
  }

  remove(id: string) {
    this.notifications.update(notifications => 
      notifications.filter(n => n.id !== id)
    );
  }

  clear() {
    this.notifications.set([]);
  }
}