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
                  <td class="actions-cell">
                    <button class="btn btn-sm btn-edit" (click)="editUser(user)" title="Edit user details">
                      ✏️ Edit
                    </button>
                    @if (user.status === 'active') {
                      <button class="btn btn-sm btn-warning" (click)="toggleUserStatus(user)" title="Deactivate user">
                        🚫 Deactivate
                      </button>
                    } @else {
                      <button class="btn btn-sm btn-success" (click)="toggleUserStatus(user)" title="Activate user">
                        ✅ Activate
                      </button>
                    }
                    <button class="btn btn-sm btn-danger" (click)="confirmDeleteUser(user)" title="Delete user permanently">
                      🗑️ Delete
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

    <!-- Add/Edit User Dialog -->
    @if (showDialog()) {
      <div class="dialog-overlay" (click)="closeDialog()">
        <div class="dialog" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h2>{{ editingUser() ? 'Edit User' : 'Add New User' }}</h2>
            <button class="close-btn" (click)="closeDialog()">✕</button>
          </div>

          <form (ngSubmit)="submitUser()" class="dialog-content">
            <div class="form-group">
              <label>Full Name *</label>
              <input type="text" [(ngModel)]="userForm.full_name" name="full_name" required
                     [disabled]="!!editingUser()"
                     placeholder="John Doe">
              @if (editingUser()) {
                <small class="help-text">Name cannot be changed after creation</small>
              }
            </div>

            <div class="form-group">
              <label>Email Address *</label>
              <input type="email" [(ngModel)]="userForm.email" name="email" required
                     [disabled]="!!editingUser()"
                     placeholder="john.doe@company.com">
              @if (editingUser()) {
                <small class="help-text">Email cannot be changed after creation</small>
              }
            </div>

            <div class="form-group">
              <label>Phone</label>
              <input type="tel" [(ngModel)]="userForm.phone" name="phone"
                     placeholder="+1-555-0123">
            </div>

            @if (!editingUser()) {
              <div class="form-group">
                <label>Password *</label>
                <input type="password" [(ngModel)]="userForm.password" name="password" required
                       placeholder="Minimum 8 characters">
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
                {{ submitting() ? 'Saving...' : (editingUser() ? 'Update User' : 'Add User') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- Delete Confirmation Dialog -->
    @if (showDeleteConfirm()) {
      <div class="dialog-overlay" (click)="cancelDelete()">
        <div class="dialog delete-dialog" (click)="$event.stopPropagation()">
          <div class="dialog-header">
            <h2>⚠️ Confirm Delete</h2>
            <button class="close-btn" (click)="cancelDelete()">✕</button>
          </div>

          <div class="dialog-content">
            <div class="warning-box">
              <p><strong>Are you sure you want to delete this user?</strong></p>
              <p class="user-details">
                <strong>Name:</strong> {{ userToDelete()?.name }}<br>
                <strong>Email:</strong> {{ userToDelete()?.email }}
              </p>
              <p class="warning-text">
                ⚠️ This action cannot be undone. The user will be permanently removed from the organization.
              </p>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-secondary" (click)="cancelDelete()">
                Cancel
              </button>
              <button type="button" class="btn btn-danger" (click)="deleteUser()" [disabled]="deleting()">
                {{ deleting() ? 'Deleting...' : 'Delete User' }}
              </button>
            </div>
          </div>
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
      margin-right: 6px;
    }

    .btn-sm:hover {
      background: #e5e7eb;
    }

    .btn-sm.btn-edit {
      background: #3b82f6;
      color: white;
    }

    .btn-sm.btn-edit:hover {
      background: #2563eb;
    }

    .btn-sm.btn-warning {
      background: #f59e0b;
      color: white;
    }

    .btn-sm.btn-warning:hover {
      background: #d97706;
    }

    .btn-sm.btn-success {
      background: #10b981;
      color: white;
    }

    .btn-sm.btn-success:hover {
      background: #059669;
    }

    .btn-sm.btn-danger {
      background: #ef4444;
      color: white;
    }

    .btn-sm.btn-danger:hover {
      background: #dc2626;
    }

    .btn.btn-danger {
      background: #ef4444;
      color: white;
    }

    .btn.btn-danger:hover:not(:disabled) {
      background: #dc2626;
    }

    .actions-cell {
      white-space: nowrap;
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

    .form-group input:disabled {
      background: #f3f4f6;
      cursor: not-allowed;
      color: #6b7280;
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

    .delete-dialog .dialog {
      max-width: 500px;
    }

    .warning-box {
      background: #fef2f2;
      border: 2px solid #fca5a5;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
    }

    .warning-box p {
      margin: 0 0 12px 0;
      color: #991b1b;
    }

    .warning-box p:last-child {
      margin-bottom: 0;
    }

    .user-details {
      background: white;
      padding: 12px;
      border-radius: 6px;
      margin: 12px 0;
      color: #374151 !important;
    }

    .warning-text {
      font-weight: 600;
      font-size: 14px;
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
  showDeleteConfirm = signal(false);
  deleting = signal(false);
  userToDelete = signal<User | null>(null);

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
    this.resetForm();
    this.showDialog.set(true);
  }

  editUser(user: User) {
    this.editingUser.set(user);
    this.userForm.full_name = user.name;
    this.userForm.email = user.email;
    this.userForm.phone = user._id; // Will get phone from backend
    this.userForm.role = user.role;
    this.userForm.password = ''; // Not needed for edit
    this.showDialog.set(true);
  }

  editUserRole(user: User) {
    this.editUser(user);
  }

  closeDialog() {
    this.showDialog.set(false);
    this.resetForm();
  }

  submitUser() {
    this.submitting.set(true);

    if (this.editingUser()) {
      // Update user
      const userId = this.editingUser()!.user_id;
      const updateData = {
        phone: this.userForm.phone,
        role: this.userForm.role
      };
      
      this.http.put<any>(
        `${this.API_BASE}/admin/organizations/${this.organizationId()}/users/${userId}`,
        updateData
      ).subscribe({
        next: (response) => {
          if (response.success) {
            console.log('✅ User updated:', response.data);
            alert(`User "${this.editingUser()!.name}" has been updated successfully.`);
            this.loadUsers(this.organizationId());
            this.closeDialog();
          }
          this.submitting.set(false);
        },
        error: (err) => {
          console.error('Failed to update user:', err);
          const errorMessage = err.error?.detail || err.error?.error || 'Failed to update user. Please try again.';
          alert(errorMessage);
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
            alert(`User "${this.userForm.email}" has been added successfully.`);
            this.loadUsers(this.organizationId());
            this.closeDialog();
          }
          this.submitting.set(false);
        },
        error: (err) => {
          console.error('Failed to add user:', err);
          const errorMessage = err.error?.detail || err.error?.error || 'Failed to add user. Please try again.';
          alert(errorMessage);
          this.submitting.set(false);
        }
      });
    }
  }

  toggleUserStatus(user: User) {
    const action = user.status === 'active' ? 'deactivate' : 'activate';
    const confirmMsg = user.status === 'active' 
      ? `Are you sure you want to deactivate ${user.name}? They will not be able to access the system.`
      : `Are you sure you want to activate ${user.name}?`;
    
    if (!confirm(confirmMsg)) return;

    this.http.put<any>(
      `${this.API_BASE}/admin/organizations/${this.organizationId()}/users/${user.user_id}/status`,
      { is_active: user.status !== 'active' }
    ).subscribe({
      next: (response) => {
        if (response.success) {
          console.log(`✅ User ${action}d:`, response.data);
          alert(`User "${user.name}" has been ${action}d successfully.`);
          this.loadUsers(this.organizationId());
        }
      },
      error: (err) => {
        console.error(`Failed to ${action} user:`, err);
        const errorMessage = err.error?.detail || err.error?.error || `Failed to ${action} user. Please try again.`;
        alert(errorMessage);
      }
    });
  }

  confirmDeleteUser(user: User) {
    this.userToDelete.set(user);
    this.showDeleteConfirm.set(true);
  }

  cancelDelete() {
    this.showDeleteConfirm.set(false);
    this.userToDelete.set(null);
  }

  deleteUser() {
    const user = this.userToDelete();
    if (!user) return;

    this.deleting.set(true);

    this.http.delete<any>(
      `${this.API_BASE}/admin/organizations/${this.organizationId()}/users/${user.user_id}`
    ).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('✅ User deleted:', response.data);
          alert(`User "${user.name}" has been deleted successfully.`);
          this.loadUsers(this.organizationId());
          this.cancelDelete();
        }
        this.deleting.set(false);
      },
      error: (err) => {
        console.error('Failed to delete user:', err);
        const errorMessage = err.error?.detail || err.error?.error || 'Failed to delete user. Please try again.';
        alert(errorMessage);
        this.deleting.set(false);
      }
    });
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
