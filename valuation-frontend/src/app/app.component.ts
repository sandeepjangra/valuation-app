import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth.service';
import { SessionTimeoutService } from './services/session-timeout.service';
import { Header } from './shared/header/header';
import { NotificationComponent } from './shared/notification/notification.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, Header, NotificationComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'valuation-frontend';

  constructor(
    private authService: AuthService,
    private sessionTimeout: SessionTimeoutService
  ) {}

  ngOnInit(): void {
    // Start session tracking when user is authenticated
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.sessionTimeout.startTracking();
      } else {
        this.sessionTimeout.stopTracking();
      }
    });
  }

  ngOnDestroy(): void {
    this.sessionTimeout.stopTracking();
  }
}