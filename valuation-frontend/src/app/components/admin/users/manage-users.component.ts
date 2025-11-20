/**
 * Manage Users Component
 * View and manage users for a specific organization
 */

import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { environment } from '../../../../environments/environment';

interface User {
  _id: string;
  user_id: string;
  name: string;
  email: string;
  role: 'manager' | 'employee';
  status: string;
  created_at: string;
}

@Component({
  selector: 'app-manage-users',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="admin-container">
      <div class="header">
        <div>
          <button class="back-btn" (click)="goBack()">← Back to Organizations</button>
          <h1>👥 User Management</h1>
          @if (organizationId()) {
            <p class="org-info">Organization: <strong>{{ organizationId() }}</strong></p>
          }
        </div>
        <button class="btn btn-primary" (click)="showAddUserDialog()">
          ➕ Add User
        </button>
      </div>

      @if (loading()) {
        <div class="loading">
          <div class="spinner"></div>
          <p>Loading users...</p>
        </div>
      }

      @if (error()) {
        <div class="error-message">
          {{ error() }}
        </div>
      }

      @if (!loading() && users().length > 0) {
        <div class="users-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              @for (user of users(); track user._id) {
                <tr>
                  <td>{{ user.name }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span class="role-badge" [class.manager]="user.role === 'manager'">
                      {{ user.role === 'manager' ? '👔 Manager' : '👤 Employee' }}
                    </span>
                  </td>
                  <td>
                    <span class="status-badge" [class.active]="user.status === 'active'">
                      {{ user.status }}
                    </span>
                  </td>
                  <td>{{ formatDate(user.created_at) }}</td>
                  <td>
                    <button class="btn btn-sm" (click)="editUserRole(user)">
                      ✏️ Edit Role
                    </button>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }

      @if (!loading() && users().length === 0 && !error()) {
        <div class="empty-state">
          <p>No users found for this organization.</p>
          <button class="btn btn-primary" (click)="showAddUserDialog()">
            Add First User
          </button>
        </div>
      }
    </div>

    <!-- Add User Dialog -->
    @if (showDialog()) {
      <div class="dialog-overlay" (click)="closeDialog()">
        <div class="dialog" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h2>{{ editingUser() ? 'Edit User Role' : 'Add New User' }}</h2>
            <button class="close-btn" (click)="closeDialog()">✕</button>
          </div>

          <form (ngSubmit)="submitUser()" class="dialog-content">
            @if (!editingUser()) {
              <div>
                <div class="form-group">
                  <label>Full Name *</label>
                  <input type="text" [(ngModel)]="userForm.full_name" name="full_name" required
                         placeholder="John Doe">
                </div>

                <div class="form-group">
                  <label>Email Address *</label>
                  <input type="email" [(ngModel)]="userForm.email" name="email" required
                         placeholder="john.doe@company.com">
                </div>

                <div class="form-group">
                  <label>Phone (Optional)</label>
                  <input type="tel" [(ngModel)]="userForm.phone" name="phone"
                         placeholder="+1-555-0123">
                </div>

                <div class="form-group">
                  <label>Password *</label>
                  <input type="password" [(ngModel)]="userForm.password" name="password" required
                         placeholder="Minimum 8 characters">
                </div>
              </div>
            }

            @if (editingUser()) {
              <div class="user-info">
                <p><strong>Name:</strong> {{ editingUser()?.name }}</p>
                <p><strong>Email:</strong> {{ editingUser()?.email }}</p>
              </div>
            }

            <div class="form-group">
              <label>Role *</label>
              <select [(ngModel)]="userForm.role" name="role" required>
                <option value="manager">👔 Manager (Can submit reports & view logs)</option>
                <option value="employee">👤 Employee (Can create/edit reports only)</option>
              </select>
              <small class="help-text">
                Managers have full access. Employees cannot submit reports or view activity logs.
              </small>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-secondary" (click)="closeDialog()">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="submitting()">
                {{ submitting() ? 'Saving...' : (editingUser() ? 'Update Role' : 'Add User') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    }
  `,
  styles: [`
    .admin-container {
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 32px;
    }

    .header h1 {
      margin: 8px 0 4px 0;
      font-size: 28px;
      color: #1f2937;
    }

    .back-btn {
      background: none;
      border: none;
      color: #3b82f6;
      font-size: 14px;
      cursor: pointer;
      padding: 0;
      margin-bottom: 8px;
    }

    .back-btn:hover {
      text-decoration: underline;
    }

    .org-info {
      margin: 0;
      color: #6b7280;
      font-size: 14px;
    }

    .users-table {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      overflow: hidden;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    thead {
      background: #f9fafb;
    }

    th {
      text-align: left;
      padding: 16px;
      font-weight: 600;
      color: #374151;
      font-size: 14px;
      border-bottom: 2px solid #e5e7eb;
    }

    td {
      padding: 16px;
      border-bottom: 1px solid #f3f4f6;
      font-size: 14px;
    }

    tr:last-child td {
      border-bottom: none;
    }

    tbody tr:hover {
      background: #f9fafb;
    }

    .role-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      background: #dbeafe;
      color: #1e40af;
    }

    .role-badge.manager {
      background: #fef3c7;
      color: #92400e;
    }

    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      background: #fee2e2;
      color: #991b1b;
    }

    .status-badge.active {
      background: #d1fae5;
      color: #065f46;
    }

    .btn {
      padding: 10px 20px;
      border-radius: 8px;
      font-weight: 600;
      border: none;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 14px;
    }

    .btn-primary {
      background: #3b82f6;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #2563eb;
    }

    .btn-secondary {
      background: #f3f4f6;
      color: #374151;
    }

    .btn-secondary:hover {
      background: #e5e7eb;
    }

    .btn-sm {
      padding: 6px 12px;
      font-size: 13px;
      background: #f3f4f6;
      color: #374151;
    }

    .btn-sm:hover {
      background: #e5e7eb;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .loading {
      text-align: center;
      padding: 60px 20px;
    }

    .spinner {
      width: 48px;
      height: 48px;
      border: 4px solid #e5e7eb;
      border-top-color: #3b82f6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 16px;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-message {
      background: #fee2e2;
      color: #991b1b;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 24px;
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #6b7280;
    }

    .dialog-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .dialog {
      background: white;
      border-radius: 12px;
      width: 90%;
      max-width: 500px;
      max-height: 90vh;
      overflow-y: auto;
    }

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24px;
      border-bottom: 1px solid #e5e7eb;
    }

    .dialog-header h2 {
      margin: 0;
      font-size: 24px;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: #6b7280;
      padding: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .close-btn:hover {
      color: #111827;
    }

    .dialog-content {
      padding: 24px;
    }

    .user-info {
      background: #f9fafb;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 20px;
    }

    .user-info p {
      margin: 8px 0;
      color: #374151;
    }

    .form-group {
      margin-bottom: 20px;
    }

    .form-group label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
      color: #374151;
    }

    .form-group input,
    .form-group select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 14px;
    }

    .form-group input:focus,
    .form-group select:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .help-text {
      display: block;
      margin-top: 6px;
      color: #6b7280;
      font-size: 13px;
    }

    .dialog-actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #e5e7eb;
    }
  `]
})
export class ManageUsersComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly API_BASE = environment.apiUrl || 'http://localhost:8000/api';

  organizationId = signal<string>('');
  users = signal<User[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);
  showDialog = signal(false);
  submitting = signal(false);
  editingUser = signal<User | null>(null);

  userForm = {
    full_name: '',
    email: '',
    password: '',
    role: 'employee' as 'manager' | 'employee',
    phone: ''
  };

  ngOnInit() {
    this.route.params.subscribe(params => {
      const orgId = params['orgId'];
      if (orgId) {
        this.organizationId.set(orgId);
        this.loadUsers(orgId);
      }
    });
  }

  loadUsers(orgId: string) {
    this.loading.set(true);
    this.error.set(null);

    this.http.get<any>(`${this.API_BASE}/admin/organizations/${orgId}/users`).subscribe({
      next: (response) => {
        if (response.success) {
          this.users.set(response.data);
        }
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load users:', err);
        this.error.set('Failed to load users. Please try again.');
        this.loading.set(false);
      }
    });
  }

  showAddUserDialog() {
    this.editingUser.set(null);
    this.showDialog.set(true);
  }

  editUserRole(user: User) {
    this.editingUser.set(user);
    this.userForm.role = user.role;
    this.showDialog.set(true);
  }

  closeDialog() {
    this.showDialog.set(false);
    this.resetForm();
  }

  submitUser() {
    this.submitting.set(true);

    if (this.editingUser()) {
      // Update role
      const userId = this.editingUser()!.user_id;
      this.http.put<any>(
        `${this.API_BASE}/admin/users/${userId}/role`,
        { role: this.userForm.role }
      ).subscribe({
        next: (response) => {
          if (response.success) {
            console.log('✅ User role updated:', response.data);
            this.loadUsers(this.organizationId());
            this.closeDialog();
          }
          this.submitting.set(false);
        },
        error: (err) => {
          console.error('Failed to update role:', err);
          alert('Failed to update user role. Please try again.');
          this.submitting.set(false);
        }
      });
    } else {
      // Add new user
      this.http.post<any>(
        `${this.API_BASE}/admin/organizations/${this.organizationId()}/users`,
        this.userForm
      ).subscribe({
        next: (response) => {
          if (response.success) {
            console.log('✅ User added:', response.data);
            this.loadUsers(this.organizationId());
            this.closeDialog();
          }
          this.submitting.set(false);
        },
        error: (err) => {
          console.error('Failed to add user:', err);
          alert('Failed to add user. Please try again.');
          this.submitting.set(false);
        }
      });
    }
  }

  goBack() {
    this.router.navigate(['/admin/organizations']);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  private resetForm() {
    this.userForm = {
      full_name: '',
      email: '',
      password: '',
      role: 'employee',
      phone: ''
    };
    this.editingUser.set(null);
  }
}
