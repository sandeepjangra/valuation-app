import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService, LoginRequest } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  error = '';
  returnUrl = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rememberMe: [false]
    });
  }

  ngOnInit(): void {
    // Get return URL from route parameters or default to dashboard
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';

    // Redirect if already logged in
    if (this.authService.isAuthenticated()) {
      this.router.navigate([this.returnUrl]);
    }
  }

  get f() {
    return this.loginForm.controls;
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    const loginRequest: LoginRequest = {
      email: this.f['email'].value,
      password: this.f['password'].value,
      remember_me: this.f['rememberMe'].value
    };

    this.authService.login(loginRequest).subscribe({
      next: (response) => {
        if (response.success) {
          // Redirect based on user role
          const user = response.data.user;
          
          console.log('Login successful, user:', user);
          
          // Get organization short name from user data
          const orgShortName = user.org_short_name || 'system-administration';
          
          // Redirect based on user role and organization
          if (user.permissions?.is_admin || user.is_system_admin || user.role === 'admin') {
            // System admin goes to admin dashboard
            this.router.navigate(['/admin']);
          } else if (user.permissions?.is_manager || user.role === 'manager') {
            // Manager goes to their organization dashboard
            this.router.navigate([`/org/${orgShortName}/dashboard`]);
          } else {
            // Regular user goes to their organization dashboard
            this.router.navigate([`/org/${orgShortName}/dashboard`]);
          }
        }
      },
      error: (error) => {
        this.loading = false;
        
        console.error('Full login error:', error);
        console.error('Error status:', error.status);
        console.error('Error message:', error.message);
        console.error('Error details:', error.error);
        
        if (error.status === 401) {
          this.error = 'Invalid email or password';
        } else if (error.error?.detail) {
          this.error = error.error.detail;
        } else {
          this.error = 'Login failed. Please try again.';
        }
      }
    });
  }

  // Development login helpers (remove in production)
  loginAsAdmin(): void {
    this.loginForm.patchValue({
      email: 'admin@system.com',
      password: 'admin123'
    });
    this.onSubmit();
  }

  loginAsManager(): void {
    this.loginForm.patchValue({
      email: 'manager@test.com',
      password: 'manager123'
    });
    this.onSubmit();
  }

  loginAsEmployee(): void {
    this.loginForm.patchValue({
      email: 'employee@test.com',
      password: 'employee123'
    });
    this.onSubmit();
  }
}