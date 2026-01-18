/**
 * Permission Models for RBAC System
 * Matches backend permission structure
 */

export interface PermissionTemplate {
  _id?: string;
  role: 'system_admin' | 'org_admin' | 'employee';
  displayName: string;
  description: string;
  isSystemWide: boolean;
  permissions: PermissionSet;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface PermissionSet {
  organizations: OrganizationPermissions;
  users: UserPermissions;
  reports: ReportPermissions;
  templates: TemplatePermissions;
  drafts: DraftPermissions;
  analytics: AnalyticsPermissions;
  settings: SettingsPermissions;
}

export interface OrganizationPermissions {
  viewAll: boolean;
  create: boolean;
  editAny: boolean;
  delete: boolean;
  manageSettings: boolean;
}

export interface UserPermissions {
  viewAllOrgs: boolean;
  viewOwnOrg: boolean;
  create: boolean;
  editAny: boolean;
  deleteAny: boolean;
  viewActivity: boolean;
  manageRoles: boolean;
}

export interface ReportPermissions {
  create: boolean;
  editOwn: boolean;
  editOthers: boolean;
  deleteOwn: boolean;
  deleteOthers: boolean;
  viewDrafts: boolean;
  saveDraft: boolean;
  submit: boolean;
  viewAllOrg: boolean;
  viewAllOrgs: boolean;
  export: boolean;
}

export interface TemplatePermissions {
  view: boolean;
  viewBankTemplates: boolean;
  createCustom: boolean;
  editCustom: boolean;
  deleteCustom: boolean;
  manageBankTemplates: boolean;
  shareAcrossOrgs: boolean;
}

export interface DraftPermissions {
  create: boolean;
  editOwn: boolean;
  editOthers: boolean;
  viewOwn: boolean;
  viewOthers: boolean;
  deleteOwn: boolean;
  deleteOthers: boolean;
}

export interface AnalyticsPermissions {
  viewOwnActivity: boolean;
  viewOrgActivity: boolean;
  viewAllActivity: boolean;
  exportReports: boolean;
}

export interface SettingsPermissions {
  editOrgSettings: boolean;
  editSystemSettings: boolean;
  manageIntegrations: boolean;
  viewLogs: boolean;
}

/**
 * User with permissions
 */
export interface UserWithPermissions {
  userId: string;
  email: string;
  role: 'system_admin' | 'org_admin' | 'employee';
  isSystemAdmin: boolean;
  orgShortName: string;
  permissions: PermissionSet;
  permissionOverrides?: Record<string, boolean>;
}
