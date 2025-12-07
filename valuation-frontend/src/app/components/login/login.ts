/**
 * Login Component for Valuation App
 * Clean login interface with admin access
 */

import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);

  // Component state
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);
  readonly showPassword = signal<boolean>(false);

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
      this.router.navigate(['/dashboard']);
    }
  }

  ngOnInit(): void {
    // Clear form to prevent autofill
    setTimeout(() => {
      this.loginForm.reset({
        email: '',
        password: '',
        rememberMe: false
      });
    }, 100);
  }

  /**
   * Admin quick login
   */
  adminLogin(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.authService.loginWithDevToken('admin@system.com', 'system-administration', 'system_admin').subscribe({
      next: () => {
        this.isLoading.set(false);
        this.redirectAfterLogin();
      },
      error: (error) => {
        console.error('Admin login failed:', error);
        this.error.set('Admin login failed. Please try again.');
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
      // Get user's organization context for proper redirect
      const orgContext = this.authService.getOrganizationContext();
      
      if (orgContext) {
        // For system admin, redirect to admin dashboard
        if (orgContext.isSystemAdmin) {
          console.log('🔄 Redirecting System Admin to /admin');
          this.router.navigate(['/admin']);
        } else {
          // For regular users, redirect to org dashboard
          const orgShortName = orgContext.orgShortName;
          console.log(`🔄 Redirecting to /org/${orgShortName}/dashboard`);
          this.router.navigate(['/org', orgShortName, 'dashboard']);
        }
      } else {
        // Fallback to login if no context
        console.error('❌ No organization context found after login');
        this.router.navigate(['/login']);
      }
    }
  }
}