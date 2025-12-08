import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class SessionTimeoutService {
  private inactivityTimer: any;
  private warningTimer: any;
  
  // Configuration (in milliseconds)
  private readonly INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes
  private readonly WARNING_TIME = 5 * 60 * 1000;        // 5 minutes warning

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  startTracking(): void {
    this.resetTimer();
    this.addEventListeners();
  }

  stopTracking(): void {
    this.clearTimers();
    this.removeEventListeners();
  }

  private resetTimer(): void {
    this.clearTimers();
    
    // Set warning timer
    this.warningTimer = setTimeout(() => {
      this.showWarning();
    }, this.INACTIVITY_TIMEOUT - this.WARNING_TIME);
    
    // Set logout timer
    this.inactivityTimer = setTimeout(() => {
      this.autoLogout();
    }, this.INACTIVITY_TIMEOUT);
  }

  private clearTimers(): void {
    if (this.inactivityTimer) clearTimeout(this.inactivityTimer);
    if (this.warningTimer) clearTimeout(this.warningTimer);
  }

  private showWarning(): void {
    const remainingTime = Math.floor(this.WARNING_TIME / 1000);
    if (confirm(`Session will expire in ${remainingTime/60} minutes. Continue?`)) {
      this.resetTimer(); // User chose to continue
    }
  }

  private autoLogout(): void {
    this.authService.logout().subscribe();
    alert('Session expired due to inactivity');
  }

  private addEventListeners(): void {
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
      document.addEventListener(event, this.resetTimer.bind(this), true);
    });
  }

  private removeEventListeners(): void {
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
      document.removeEventListener(event, this.resetTimer.bind(this), true);
    });
  }
}