/**
 * Organization Management Models and Interfaces
 * TypeScript interfaces for organization data, users, and API responses
 */

// Core Organization Models
export interface Organization {
  _id: string;
  org_short_name: string; // organization short name identifier (e.g., "system-administration")
  name: string; // Full organization name
  type?: 'valuation_company' | 'system' | 'enterprise';
  description?: string;
  contact_email?: string;
  phone_number?: string;
  report_reference_initials?: string; // Reference initials for report numbering
  last_reference_number?: number; // Last used reference number
  subscription_plan?: 'basic' | 'premium' | 'enterprise';
  max_users?: number;
  max_reports?: number;
  is_active: boolean;
  created_at: Date;
  updated_at: Date;
  total_users?: number;
  total_reports?: number;
  settings?: OrganizationSettings;
}

export interface OrganizationSettings {
  _id: string;
  organization_id: string;
  branding?: {
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
    company_name?: string;
  };
  report_settings?: {
    default_template?: string;
    auto_numbering?: boolean;
    require_approval?: boolean;
    watermark?: string;
  };
  user_settings?: {
    password_policy?: {
      min_length?: number;
      require_uppercase?: boolean;
      require_lowercase?: boolean;
      require_numbers?: boolean;
      require_symbols?: boolean;
    };
    session_timeout?: number;
    two_factor_required?: boolean;
  };
  notification_settings?: {
    email_notifications?: boolean;
    sms_notifications?: boolean;
    report_completed?: boolean;
    user_activity?: boolean;
  };
  is_active: boolean;
  created_at: Date;
  updated_at: Date;
}

export interface User {
  _id?: string;
  user_id: string;
  organization_id: string;
  email: string;
  full_name: string;
  first_name?: string;
  last_name?: string;
  role: string;
  roles: UserRole[];
  status: string;
  department?: string;
  phone?: string;
  phone_number?: string;
  is_active?: boolean;
  last_login?: Date;
  created_by?: string;
  created_at?: Date;
  updated_at?: Date;
  profile?: UserProfile;
  permissions: {
    can_submit_reports: boolean;
    can_manage_users: boolean;
    is_manager: boolean;
    is_admin: boolean;
  };
}

export interface UserProfile {
  _id: string;
  user_id: string;
  organization_id: string;
  avatar_url?: string;
  bio?: string;
  timezone?: string;
  language?: string;
  preferences?: {
    theme?: 'light' | 'dark';
    notifications?: boolean;
    dashboard_layout?: string;
  };
  created_at: Date;
  updated_at: Date;
}

export interface AuditLog {
  _id: string;
  organization_id: string;
  user_id: string;
  user_email: string;
  action: AuditAction;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp: Date;
  session_id?: string;
}

// Enums and Types
export type UserRole = 'system_admin' | 'manager' | 'employee';

export type AuditAction = 
  | 'create' 
  | 'read' 
  | 'update' 
  | 'delete' 
  | 'login' 
  | 'logout' 
  | 'access_denied';

// JWT and Authentication Models
export interface JwtPayload {
  sub: string;
  email: string;
  'custom:org_short_name'?: string;
  'custom:organization_id'?: string; // Backward compatibility
  'cognito:groups': UserRole[];
  iat: number;
  exp: number;
  aud?: string;
  iss?: string;
  dev_mode?: boolean;
}

export interface OrganizationContext {
  userId: string;
  email: string;
  orgShortName: string;
  organizationId: string; // Backward compatibility alias
  roles: UserRole[];
  isSystemAdmin: boolean;
  isManager: boolean;
  isEmployee: boolean;
  token: string;
  expiresAt: Date;
}

// API Response Models
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  status_code?: number;
  timestamp?: Date;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface ErrorResponse extends ApiResponse {
  success: false;
  error: string;
  validation_errors?: ValidationError[];
  status_code: number;
}

// Form Models for Components
export interface CreateUserRequest {
  email: string;
  first_name?: string;
  last_name?: string;
  roles: UserRole[];
  department?: string;
  phone_number?: string;
  send_welcome_email?: boolean;
}

export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  roles?: UserRole[];
  department?: string;
  phone_number?: string;
  is_active?: boolean;
}

export interface CreateOrganizationRequest {
  name: string;
  type?: 'valuation_company' | 'enterprise';
  description?: string;
  contact_email?: string;
  phone_number?: string;
  report_reference_initials?: string;
  subscription_plan?: 'basic' | 'premium' | 'enterprise';
  max_users?: number;
  max_reports?: number;
}

export interface UpdateOrganizationRequest {
  name?: string;
  description?: string;
  contact_email?: string;
  phone_number?: string;
  report_reference_initials?: string;
  subscription_plan?: 'basic' | 'premium' | 'enterprise';
  max_users?: number;
  max_reports?: number;
  is_active?: boolean;
}

// UI/Component Models
export interface NavigationItem {
  label: string;
  route: string;
  icon?: string;
  roles?: UserRole[];
  children?: NavigationItem[];
  disabled?: boolean;
}

export interface DashboardCard {
  title: string;
  value: number | string;
  icon?: string;
  color?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    percentage: number;
  };
  route?: string;
}

export interface DataTableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  type?: 'text' | 'date' | 'number' | 'badge' | 'actions';
  format?: string;
}

export interface FilterOption {
  key: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'checkbox';
  options?: { label: string; value: any }[];
  value?: any;
}

// Permission and Role Management
export interface Permission {
  resource: string;
  action: string;
  allowed: boolean;
}

export interface RolePermissions {
  role: UserRole;
  permissions: Permission[];
}

// Notification Models
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actions?: {
    label: string;
    action: () => void;
  }[];
}

// Constants
export const USER_ROLE_LABELS: Record<UserRole, string> = {
  system_admin: 'System Administrator',
  manager: 'Manager',
  employee: 'Employee'
};

export const AUDIT_ACTION_LABELS: Record<AuditAction, string> = {
  create: 'Created',
  read: 'Viewed',
  update: 'Updated',
  delete: 'Deleted',
  login: 'Logged In',
  logout: 'Logged Out',
  access_denied: 'Access Denied'
};

export const ORGANIZATION_TYPE_LABELS = {
  valuation_company: 'Valuation Company',
  system: 'System Organization',
  enterprise: 'Enterprise'
};

export const SUBSCRIPTION_PLAN_LABELS = {
  basic: 'Basic Plan',
  premium: 'Premium Plan',
  enterprise: 'Enterprise Plan'
};

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequireFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OmitFields<T, K extends keyof T> = Omit<T, K>;

// API Endpoint Types
export interface ApiEndpoints {
  auth: {
    login: string;
    logout: string;
    refresh: string;
    profile: string;
  };
  organizations: {
    list: string;
    get: string;
    create: string;
    update: string;
    delete: string;
  };
  users: {
    list: string;
    get: string;
    create: string;
    update: string;
    delete: string;
  };
  reports: {
    list: string;
    get: string;
    create: string;
    update: string;
    delete: string;
  };
  auditLogs: {
    list: string;
    get: string;
  };
}