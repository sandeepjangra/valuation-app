/**
 * User Management Component
 * Component for managing organization users with role-based permissions (manager/admin only)
 */

import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { 
  User, 
  CreateUserRequest, 
  UpdateUserRequest, 
  UserRole,
  USER_ROLE_LABELS,
  DataTableColumn,
  PaginatedResponse
} from '../../models/organization.model';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { UserService } from '../../services/user.service';

interface UserFormData {
  email: string;
  first_name: string;
  last_name: string;
  roles: UserRole[];
  department: string;
  phone_number: string;
  send_welcome_email: boolean;
}

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `
    <div class="user-management">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>Employee Activities</h1>
          <p>View and manage employee activities and profiles</p>
        </div>
        <div class="header-actions">
          <button 
            *ngIf="canCreateUsers()" 
            class="btn btn-primary"
            (click)="openCreateUserModal()">
            <span class="btn-icon">👤</span>
            Add User
          </button>
          <button 
            class="btn btn-outline"
            (click)="refreshUsers()"
            [disabled]="isLoading()">
            <span class="btn-icon">🔄</span>
            Refresh
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filters-row">
          <div class="filter-group">
            <label for="search">Search Users</label>
            <input 
              id="search"
              type="text" 
              placeholder="Search by email or name..."
              [(ngModel)]="searchQuery"
              (ngModelChange)="onSearchChange()"
              class="form-input">
          </div>
          
          <div class="filter-group">
            <label for="roleFilter">Filter by Role</label>
            <select 
              id="roleFilter"
              [(ngModel)]="roleFilter"
              (ngModelChange)="onFilterChange()"
              class="form-select">
              <option value="">All Roles</option>
              <option *ngFor="let role of availableRoles()" [value]="role.value">
                {{ role.label }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="statusFilter">Filter by Status</label>
            <select 
              id="statusFilter"
              [(ngModel)]="statusFilter"
              (ngModelChange)="onFilterChange()"
              class="form-select">
              <option value="">All Users</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div *ngIf="isLoading()" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading users...</p>
      </div>

      <!-- Error State -->
      <div *ngIf="error()" class="error-container">
        <div class="error-message">
          <h3>⚠️ Error Loading Users</h3>
          <p>{{ error() }}</p>
          <button class="btn btn-primary" (click)="refreshUsers()">
            Try Again
          </button>
        </div>
      </div>

      <!-- Users Table -->
      <div *ngIf="!isLoading() && !error()" class="table-container">
        <div *ngIf="users().length === 0" class="empty-state">
          <div class="empty-icon">👥</div>
          <h3>No Users Found</h3>
          <p *ngIf="hasActiveFilters()">
            Try adjusting your filters or search criteria.
          </p>
          <p *ngIf="!hasActiveFilters() && canCreateUsers()">
            Get started by adding your first team member.
          </p>
          <p *ngIf="!hasActiveFilters() && !canCreateUsers()">
            Contact your System Administrator to add new users to your organization.
          </p>
          <button 
            *ngIf="canCreateUsers()" 
            class="btn btn-primary"
            (click)="openCreateUserModal()">
            Add First User
          </button>
        </div>

        <div *ngIf="users().length > 0" class="users-table-wrapper">
          <table class="users-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Roles</th>
                <th>Department</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let user of users(); trackBy: trackByUserId" 
                  class="user-row"
                  [class.inactive]="!user.is_active">
                <td class="user-cell">
                  <div class="user-info">
                    <div class="user-avatar">
                      {{ getUserInitials(user) }}
                    </div>
                    <div class="user-details">
                      <div class="user-name">
                        {{ getUserDisplayName(user) }}
                      </div>
                      <div class="user-email">{{ user.email }}</div>
                    </div>
                  </div>
                </td>
                
                <td class="roles-cell">
                  <div class="roles-list">
                    <span *ngFor="let role of user.roles" 
                          class="role-badge"
                          [class]="getRoleBadgeClass(role)">
                      {{ getRoleLabel(role) }}
                    </span>
                  </div>
                </td>
                
                <td class="department-cell">
                  {{ user.department || '-' }}
                </td>
                
                <td class="status-cell">
                  <span class="status-badge"
                        [class.active]="user.is_active"
                        [class.inactive]="!user.is_active">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                
                <td class="last-login-cell">
                  {{ formatDate(user.last_login) }}
                </td>
                
                <td class="actions-cell">
                  <div class="action-buttons">
                    <button 
                      class="btn-icon-small"
                      (click)="viewUser(user)"
                      title="View User">
                      👁️
                    </button>
                    <button 
                      *ngIf="canEditUser(user)"
                      class="btn-icon-small"
                      (click)="editUser(user)"
                      title="Edit User">
                      ✏️
                    </button>
                    <button 
                      *ngIf="canToggleUserStatus(user)"
                      class="btn-icon-small"
                      [class.danger]="user.is_active"
                      [class.success]="!user.is_active"
                      (click)="toggleUserStatus(user)"
                      [title]="user.is_active ? 'Deactivate User' : 'Activate User'">
                      {{ user.is_active ? '🚫' : '✅' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div *ngIf="pagination()" class="pagination-container">
          <div class="pagination-info">
            Showing {{ getPaginationStart() }} - {{ getPaginationEnd() }} of {{ pagination()!.total }} users
          </div>
          <div class="pagination-controls">
            <button 
              class="btn btn-outline btn-small"
              [disabled]="!pagination()!.has_prev"
              (click)="previousPage()">
              Previous
            </button>
            
            <span class="page-info">
              Page {{ pagination()!.page }} of {{ pagination()!.total_pages }}
            </span>
            
            <button 
              class="btn btn-outline btn-small"
              [disabled]="!pagination()!.has_next"
              (click)="nextPage()">
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- Create/Edit User Modal -->
      <div *ngIf="showUserModal()" class="modal-overlay" (click)="closeUserModal()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h2>{{ isEditMode() ? 'Edit User' : 'Create New User' }}</h2>
            <button class="modal-close" (click)="closeUserModal()">×</button>
          </div>
          
          <form [formGroup]="userForm" (ngSubmit)="submitUserForm()" class="user-form">
            <div class="form-grid">
              <div class="form-group">
                <label for="email">Email Address *</label>
                <input 
                  id="email"
                  type="email" 
                  formControlName="email"
                  [readonly]="isEditMode()"
                  class="form-input"
                  [class.error]="userForm.get('email')?.invalid && userForm.get('email')?.touched">
                <div *ngIf="userForm.get('email')?.errors?.['required'] && userForm.get('email')?.touched" 
                     class="error-text">
                  Email is required
                </div>
                <div *ngIf="userForm.get('email')?.errors?.['email'] && userForm.get('email')?.touched" 
                     class="error-text">
                  Please enter a valid email
                </div>
              </div>

              <div class="form-group">
                <label for="firstName">First Name</label>
                <input 
                  id="firstName"
                  type="text" 
                  formControlName="first_name"
                  class="form-input">
              </div>

              <div class="form-group">
                <label for="lastName">Last Name</label>
                <input 
                  id="lastName"
                  type="text" 
                  formControlName="last_name"
                  class="form-input">
              </div>

              <div class="form-group">
                <label for="department">Department</label>
                <input 
                  id="department"
                  type="text" 
                  formControlName="department"
                  class="form-input">
              </div>

              <div class="form-group">
                <label for="phone">Phone Number</label>
                <input 
                  id="phone"
                  type="tel" 
                  formControlName="phone_number"
                  class="form-input">
              </div>

              <div class="form-group full-width">
                <label>Roles *</label>
                <div class="roles-checkboxes">
                  <div *ngFor="let role of availableRoles()" class="checkbox-group">
                    <input 
                      type="checkbox" 
                      [id]="'role-' + role.value"
                      [value]="role.value"
                      (change)="onRoleChange($event)"
                      [checked]="isRoleSelected(role.value)">
                    <label [for]="'role-' + role.value">{{ role.label }}</label>
                  </div>
                </div>
                <div *ngIf="!hasSelectedRoles() && userForm.touched" class="error-text">
                  At least one role is required
                </div>
              </div>

              <div *ngIf="!isEditMode()" class="form-group full-width">
                <div class="checkbox-group">
                  <input 
                    type="checkbox" 
                    id="sendWelcome"
                    formControlName="send_welcome_email">
                  <label for="sendWelcome">Send welcome email to new user</label>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-outline" (click)="closeUserModal()">
                Cancel
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                [disabled]="userForm.invalid || isSubmitting() || !hasSelectedRoles()">
                <span *ngIf="isSubmitting()" class="btn-spinner"></span>
                {{ isEditMode() ? 'Update User' : 'Create User' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./user-management.component.css']
})
export class UserManagementComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly organizationService = inject(OrganizationService);
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);

  // Component state
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);
  readonly users = signal<User[]>([]);
  readonly pagination = signal<PaginatedResponse<User>['pagination'] | null>(null);
  readonly showUserModal = signal<boolean>(false);
  readonly isEditMode = signal<boolean>(false);
  readonly isSubmitting = signal<boolean>(false);

  // Form and filters
  userForm: FormGroup;
  searchQuery = '';
  roleFilter = '';
  statusFilter = '';
  selectedRoles: UserRole[] = [];
  currentEditUser: User | null = null;

  // Filter debounce
  private searchTimeout?: ReturnType<typeof setTimeout>;

  // Available roles based on user permissions
  readonly availableRoles = computed(() => {
    const currentUserRoles = this.authService.userRoles();
    
    // System admin can assign any role
    if (this.authService.isSystemAdmin()) {
      return [
        { value: 'system_admin' as UserRole, label: USER_ROLE_LABELS.system_admin },
        { value: 'manager' as UserRole, label: USER_ROLE_LABELS.manager },
        { value: 'employee' as UserRole, label: USER_ROLE_LABELS.employee }
      ];
    }
    
    // Manager can assign manager and employee roles
    if (this.authService.isManager()) {
      return [
        { value: 'manager' as UserRole, label: USER_ROLE_LABELS.manager },
        { value: 'employee' as UserRole, label: USER_ROLE_LABELS.employee }
      ];
    }
    
    return [];
  });

  constructor() {
    this.userForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      first_name: [''],
      last_name: [''],
      department: [''],
      phone_number: [''],
      send_welcome_email: [true]
    });
  }

  ngOnInit(): void {
    // Check permissions
    if (!this.canViewUsers()) {
      this.router.navigate(['/access-denied']);
      return;
    }

    this.loadUsers();
  }

  /**
   * Load users with current filters
   */
  loadUsers(page: number = 1): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.isLoading.set(true);
    this.error.set(null);
    
    this.userService.getUsers(page, 20).subscribe({
      next: (response) => {
        this.users.set(response.data?.users as any || []);
        this.pagination.set(response.data?.pagination as any || null);
        this.isLoading.set(false);
      },
      error: (error: any) => {
        console.error('Error loading users:', error);
        this.error.set('Failed to load users');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Refresh users list
   */
  refreshUsers(): void {
    this.loadUsers(this.pagination()?.page || 1);
  }

  /**
   * Handle search input change
   */
  onSearchChange(): void {
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }
    
    this.searchTimeout = setTimeout(() => {
      this.loadUsers(1);
    }, 500);
  }

  /**
   * Handle filter changes
   */
  onFilterChange(): void {
    this.loadUsers(1);
  }

  /**
   * Check if filters are active
   */
  hasActiveFilters(): boolean {
    return !!(this.searchQuery || this.roleFilter || this.statusFilter);
  }

  /**
   * Pagination methods
   */
  previousPage(): void {
    const currentPage = this.pagination()?.page || 1;
    if (currentPage > 1) {
      this.loadUsers(currentPage - 1);
    }
  }

  nextPage(): void {
    const pagination = this.pagination();
    if (pagination?.has_next) {
      this.loadUsers(pagination.page + 1);
    }
  }

  getPaginationStart(): number {
    const pagination = this.pagination();
    if (!pagination) return 0;
    return (pagination.page - 1) * pagination.limit + 1;
  }

  getPaginationEnd(): number {
    const pagination = this.pagination();
    if (!pagination) return 0;
    return Math.min(pagination.page * pagination.limit, pagination.total);
  }

  /**
   * User modal methods
   */
  openCreateUserModal(): void {
    if (!this.canCreateUsers()) return;
    
    this.isEditMode.set(false);
    this.currentEditUser = null;
    this.selectedRoles = [];
    this.userForm.reset({
      email: '',
      first_name: '',
      last_name: '',
      department: '',
      phone_number: '',
      send_welcome_email: true
    });
    this.showUserModal.set(true);
  }

  editUser(user: User): void {
    if (!this.canEditUser(user)) return;
    
    this.isEditMode.set(true);
    this.currentEditUser = user;
    this.selectedRoles = [...user.roles];
    this.userForm.patchValue({
      email: user.email,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      department: user.department || '',
      phone_number: user.phone_number || ''
    });
    this.showUserModal.set(true);
  }

  closeUserModal(): void {
    this.showUserModal.set(false);
    this.isEditMode.set(false);
    this.currentEditUser = null;
    this.selectedRoles = [];
    this.userForm.reset();
  }

  /**
   * Handle role selection
   */
  onRoleChange(event: Event): void {
    const checkbox = event.target as HTMLInputElement;
    const role = checkbox.value as UserRole;
    
    if (checkbox.checked) {
      this.selectedRoles.push(role);
    } else {
      this.selectedRoles = this.selectedRoles.filter(r => r !== role);
    }
  }

  isRoleSelected(role: UserRole): boolean {
    return this.selectedRoles.includes(role);
  }

  hasSelectedRoles(): boolean {
    return this.selectedRoles.length > 0;
  }

  /**
   * Submit user form
   */
  submitUserForm(): void {
    if (this.userForm.invalid || !this.hasSelectedRoles()) return;
    
    this.isSubmitting.set(true);
    const formValue = this.userForm.value as UserFormData;
    
    if (this.isEditMode()) {
      // Update existing user
      const updateData: UpdateUserRequest = {
        first_name: formValue.first_name,
        last_name: formValue.last_name,
        department: formValue.department,
        phone_number: formValue.phone_number,
        roles: this.selectedRoles
      };
      
      this.userService.updateUser(this.currentEditUser!.user_id, updateData).subscribe({
        next: () => {
          this.closeUserModal();
          this.refreshUsers();
          this.isSubmitting.set(false);
        },
        error: (error: any) => {
          console.error('Error updating user:', error);
          this.error.set('Failed to update user');
          this.isSubmitting.set(false);
        }
      });
    } else {
      // Create new user
      const createData: any = {
        email: formValue.email,
        fullName: `${formValue.first_name} ${formValue.last_name}`,
        password: 'Temp@123', // Temporary password - should be changed on first login
        roles: this.selectedRoles,
        department: formValue.department,
        phoneNumber: formValue.phone_number,
      };
      
      this.userService.createUser(createData).subscribe({
        next: () => {
          this.closeUserModal();
          this.refreshUsers();
          this.isSubmitting.set(false);
        },
        error: (error: any) => {
          console.error('Error creating user:', error);
          this.error.set('Failed to create user');
          this.isSubmitting.set(false);
        }
      });
    }
  }

  /**
   * Toggle user active status
   */
  toggleUserStatus(user: User): void {
    if (!this.canToggleUserStatus(user)) return;
    
    const newStatus = !user.is_active;
    
    // Use deactivateUser if setting to inactive
    if (!newStatus && user.user_id) {
      this.userService.deactivateUser(user.user_id).subscribe({
        next: () => {
          // Update local user data
          const updatedUsers = this.users().map(u => 
            u.user_id === user.user_id ? { ...u, is_active: newStatus } : u
          );
          this.users.set(updatedUsers);
        },
        error: (error: any) => {
          console.error('Error deactivating user:', error);
          this.error.set('Failed to update user status');
        }
      });
    } else {
      // For reactivation, we'd need an updateUser call
      console.warn('User reactivation not yet implemented');
      this.error.set('User reactivation not yet implemented');
    }
  }

  /**
   * View user details
   */
  viewUser(user: User): void {
    // Navigate to user detail page or open view modal
    this.router.navigate(['/organization/users', user.user_id]);
  }

  /**
   * Permission methods
   */
  canViewUsers(): boolean {
    return this.authService.hasPermission('users', 'read');
  }

  canCreateUsers(): boolean {
    return this.authService.hasPermission('users', 'create');
  }

  canEditUser(user: User): boolean {
    // Can edit if has update permission and not editing system admin (unless current user is system admin)
    const hasUpdatePermission = this.authService.hasPermission('users', 'update');
    const isTargetSystemAdmin = user.roles.includes('system_admin');
    const isCurrentSystemAdmin = this.authService.isSystemAdmin();
    
    return hasUpdatePermission && (!isTargetSystemAdmin || isCurrentSystemAdmin);
  }

  canToggleUserStatus(user: User): boolean {
    // Same logic as edit, plus can't deactivate self
    const currentUser = this.authService.currentUser();
    const isSelf = currentUser?.user_id === user.user_id;
    
    return this.canEditUser(user) && !isSelf;
  }

  /**
   * Utility methods
   */
  trackByUserId(index: number, user: User): string {
    return user.user_id;
  }

  getUserInitials(user: User): string {
    const firstName = user.first_name || user.email.split('@')[0];
    const lastName = user.last_name || '';
    return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase();
  }

  getUserDisplayName(user: User): string {
    if (user.first_name || user.last_name) {
      return `${user.first_name || ''} ${user.last_name || ''}`.trim();
    }
    return user.email.split('@')[0];
  }

  getRoleLabel(role: UserRole): string {
    return USER_ROLE_LABELS[role] || role;
  }

  getRoleBadgeClass(role: UserRole): string {
    const classes: Record<UserRole, string> = {
      'system_admin': 'role-system-admin',
      'manager': 'role-manager',
      'employee': 'role-employee'
    };
    return classes[role] || '';
  }

  formatDate(date: Date | string | undefined): string {
    if (!date) return 'Never';
    const d = new Date(date);
    return d.toLocaleDateString();
  }
}