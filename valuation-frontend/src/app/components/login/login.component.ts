/**
 * Login Component for Organization Management
 * Simple login interface for development and production authentication
 */

import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserRole } from '../../models/organization.model';
import { AuthService } from '../../services/auth.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>Valuation App</h1>
          <p>Organization Management System</p>
        </div>

        <!-- Development Mode Quick Login -->
        <div *ngIf="isDevelopmentMode" class="dev-login-section">
          <h2>🧪 Development Quick Login</h2>
          <p>Choose a role to test with development credentials:</p>
          
          <div class="dev-login-buttons">
            <button 
              class="btn btn-dev system-admin"
              (click)="devLogin('system_admin')"
              [disabled]="isLoading()">
              <div class="btn-content">
                <span class="btn-icon">👑</span>
                <div>
                  <div class="btn-title">System Admin</div>
                  <div class="btn-subtitle">admin@system.com</div>
                </div>
              </div>
            </button>

            <button 
              class="btn btn-dev manager"
              (click)="devLogin('manager')"
              [disabled]="isLoading()">
              <div class="btn-content">
                <span class="btn-icon">👔</span>
                <div>
                  <div class="btn-title">Manager</div>
                  <div class="btn-subtitle">manager@demo.com</div>
                </div>
              </div>
            </button>

            <button 
              class="btn btn-dev employee"
              (click)="devLogin('employee')"
              [disabled]="isLoading()">
              <div class="btn-content">
                <span class="btn-icon">👤</span>
                <div>
                  <div class="btn-title">Employee</div>
                  <div class="btn-subtitle">employee@demo.com</div>
                </div>
              </div>
            </button>
          </div>

          <div class="dev-divider">
            <span>or use traditional login</span>
          </div>
        </div>

        <!-- Traditional Login Form -->
        <form [formGroup]="loginForm" (ngSubmit)="submitLogin()" class="login-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input 
              id="email"
              type="email" 
              formControlName="email"
              placeholder="Enter your email"
              class="form-input"
              [class.error]="loginForm.get('email')?.invalid && loginForm.get('email')?.touched">
            <div *ngIf="loginForm.get('email')?.errors?.['required'] && loginForm.get('email')?.touched" 
                 class="error-text">
              Email is required
            </div>
            <div *ngIf="loginForm.get('email')?.errors?.['email'] && loginForm.get('email')?.touched" 
                 class="error-text">
              Please enter a valid email
            </div>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <div class="password-input-wrapper">
              <input 
                id="password"
                [type]="showPassword() ? 'text' : 'password'"
                formControlName="password"
                placeholder="Enter your password"
                class="form-input"
                [class.error]="loginForm.get('password')?.invalid && loginForm.get('password')?.touched">
              <button 
                type="button" 
                class="password-toggle"
                (click)="togglePasswordVisibility()">
                {{ showPassword() ? '🙈' : '👁️' }}
              </button>
            </div>
            <div *ngIf="loginForm.get('password')?.errors?.['required'] && loginForm.get('password')?.touched" 
                 class="error-text">
              Password is required
            </div>
          </div>

          <div class="form-group">
            <div class="checkbox-group">
              <input 
                type="checkbox" 
                id="rememberMe"
                formControlName="rememberMe">
              <label for="rememberMe">Remember me</label>
            </div>
          </div>

          <!-- Error Message -->
          <div *ngIf="error()" class="error-message">
            {{ error() }}
          </div>

          <button 
            type="submit" 
            class="btn btn-primary btn-full"
            [disabled]="loginForm.invalid || isLoading()">
            <span *ngIf="isLoading()" class="btn-spinner"></span>
            {{ isLoading() ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <div class="login-footer">
          <p>Don't have an account? <a href="#" class="link">Contact your administrator</a></p>
          <p><a href="#" class="link">Forgot your password?</a></p>
        </div>

        <!-- Version Info -->
        <div class="version-info">
          <small>Version 1.0.0 | {{ isDevelopmentMode ? 'Development' : 'Production' }} Mode</small>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .login-card {
      background: white;
      border-radius: 16px;
      padding: 40px;
      width: 100%;
      max-width: 450px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }

    .login-header {
      text-align: center;
      margin-bottom: 30px;
    }

    .login-header h1 {
      margin: 0 0 8px 0;
      font-size: 2rem;
      font-weight: 700;
      color: #1f2937;
    }

    .login-header p {
      margin: 0;
      color: #6b7280;
      font-size: 1rem;
    }

    .dev-login-section {
      margin-bottom: 30px;
      padding: 20px;
      background: #fef3c7;
      border-radius: 12px;
      border: 2px solid #fbbf24;
    }

    .dev-login-section h2 {
      margin: 0 0 8px 0;
      font-size: 1.25rem;
      color: #92400e;
    }

    .dev-login-section p {
      margin: 0 0 20px 0;
      color: #92400e;
      font-size: 0.875rem;
    }

    .dev-login-buttons {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .btn-dev {
      padding: 16px;
      border: 2px solid transparent;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: left;
      font-weight: 600;
      width: 100%;
    }

    .btn-dev:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.1);
    }

    .btn-dev.system-admin {
      background: #fef3c7;
      color: #92400e;
      border-color: #fbbf24;
    }

    .btn-dev.manager {
      background: #dbeafe;
      color: #1e40af;
      border-color: #3b82f6;
    }

    .btn-dev.employee {
      background: #d1fae5;
      color: #065f46;
      border-color: #10b981;
    }

    .btn-content {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .btn-icon {
      font-size: 1.5rem;
    }

    .btn-title {
      font-size: 1rem;
      font-weight: 600;
    }

    .btn-subtitle {
      font-size: 0.875rem;
      opacity: 0.8;
    }

    .dev-divider {
      text-align: center;
      margin: 20px 0;
      position: relative;
    }

    .dev-divider::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 1px;
      background: #d1d5db;
    }

    .dev-divider span {
      background: white;
      padding: 0 16px;
      color: #6b7280;
      font-size: 0.875rem;
    }

    .login-form {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .form-group label {
      font-weight: 600;
      color: #374151;
      font-size: 0.875rem;
    }

    .form-input {
      padding: 12px 16px;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      font-size: 1rem;
      transition: border-color 0.2s ease;
    }

    .form-input:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    .form-input.error {
      border-color: #ef4444;
    }

    .password-input-wrapper {
      position: relative;
    }

    .password-toggle {
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1rem;
      color: #6b7280;
    }

    .checkbox-group {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .checkbox-group input[type="checkbox"] {
      width: 16px;
      height: 16px;
    }

    .checkbox-group label {
      cursor: pointer;
      font-weight: 500;
    }

    .error-text {
      color: #ef4444;
      font-size: 0.75rem;
      font-weight: 500;
    }

    .error-message {
      background: #fee2e2;
      border: 1px solid #fecaca;
      border-radius: 8px;
      padding: 12px;
      color: #dc2626;
      font-size: 0.875rem;
    }

    .btn {
      padding: 12px 20px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-primary {
      background: #3b82f6;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #2563eb;
      transform: translateY(-1px);
    }

    .btn-full {
      width: 100%;
    }

    .btn-spinner {
      width: 16px;
      height: 16px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .login-footer {
      margin-top: 30px;
      text-align: center;
    }

    .login-footer p {
      margin: 8px 0;
      color: #6b7280;
      font-size: 0.875rem;
    }

    .link {
      color: #3b82f6;
      text-decoration: none;
      font-weight: 600;
    }

    .link:hover {
      text-decoration: underline;
    }

    .version-info {
      margin-top: 20px;
      text-align: center;
      color: #9ca3af;
    }

    @media (max-width: 480px) {
      .login-container {
        padding: 10px;
      }

      .login-card {
        padding: 30px 20px;
      }

      .login-header h1 {
        font-size: 1.5rem;
      }
    }
  `]
})
export class LoginComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);

  // Component state
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);
  readonly showPassword = signal<boolean>(false);

  // Environment configuration
  readonly isDevelopmentMode = environment.developmentMode;

  // Login form
  loginForm: FormGroup;

  constructor() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false]
    });

    // Redirect if already authenticated
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/organization/dashboard']);
    }
  }

  /**
   * Development login with predefined roles
   */
  devLogin(role: UserRole): void {
    this.isLoading.set(true);
    this.error.set(null);

    const credentials = this.getDevCredentials(role);
    
    this.authService.loginWithDevToken(credentials.email, credentials.organizationId, role).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.redirectAfterLogin();
      },
      error: (error) => {
        console.error('Development login failed:', error);
        this.error.set('Development login failed. Please try again.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Traditional login form submission
   */
  submitLogin(): void {
    if (this.loginForm.invalid) return;

    this.isLoading.set(true);
    this.error.set(null);

    const credentials = this.loginForm.value;
    
    this.authService.login(credentials).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.redirectAfterLogin();
      },
      error: (error) => {
        console.error('Login failed:', error);
        this.error.set(error.message || 'Login failed. Please check your credentials.');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Toggle password visibility
   */
  togglePasswordVisibility(): void {
    this.showPassword.set(!this.showPassword());
  }

  /**
   * Redirect after successful login
   */
  private redirectAfterLogin(): void {
    // Check for attempted URL in session storage
    const attemptedUrl = sessionStorage.getItem('attempted_url');
    if (attemptedUrl) {
      sessionStorage.removeItem('attempted_url');
      this.router.navigateByUrl(attemptedUrl);
    } else {
      // Default redirect based on role
      const orgContext = this.authService.getOrganizationContext();
      if (orgContext?.isSystemAdmin) {
        this.router.navigate(['/system/dashboard']);
      } else {
        this.router.navigate(['/organization/dashboard']);
      }
    }
  }

  /**
   * Get development credentials for role
   */
  private getDevCredentials(role: UserRole) {
    const credentials = {
      system_admin: {
        email: 'admin@system.com',
        organizationId: 'system_admin'
      },
      manager: {
        email: 'manager@demo.com',
        organizationId: 'demo_org_001'
      },
      employee: {
        email: 'employee@demo.com',
        organizationId: 'demo_org_001'
      }
    };

    return credentials[role];
  }
}