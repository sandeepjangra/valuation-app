export interface ActivityLogEntry {
  id?: string;
  userId: string;
  orgShortName: string;
  action: string;
  actionType: string;
  description: string;
  entityType?: string;
  entityId?: string;
  metadata?: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  timestamp?: string;
  createdAt?: string;
}

export interface LogActivityRequest {
  userId: string;
  orgShortName: string;
  action: string;
  actionType: string;
  description: string;
  entityType?: string;
  entityId?: string;
  metadata?: Record<string, any>;
}

export interface ActivityLogResponse {
  success: boolean;
  data: ActivityLogEntry[] | ActivityLogEntry | { id: string };
  message?: string;
}

/**
 * Action types for activity logging
 */
export enum ActionType {
  AUTHENTICATION = 'authentication',
  ORGANIZATION = 'organization',
  USER_MANAGEMENT = 'user_management',
  REPORT = 'report',
  TEMPLATE = 'template',
  DRAFT = 'draft',
  SETTINGS = 'settings',
  ANALYTICS = 'analytics'
}

/**
 * Common actions for each action type
 */
export const CommonActions = {
  AUTHENTICATION: {
    LOGIN: 'login',
    LOGOUT: 'logout',
    TOKEN_REFRESH: 'token_refresh',
    PASSWORD_CHANGE: 'password_change'
  },
  ORGANIZATION: {
    CREATE: 'create_organization',
    UPDATE: 'update_organization',
    DELETE: 'delete_organization',
    VIEW: 'view_organization'
  },
  USER: {
    CREATE: 'create_user',
    UPDATE: 'update_user',
    DELETE: 'delete_user',
    ACTIVATE: 'activate_user',
    DEACTIVATE: 'deactivate_user',
    CHANGE_ROLE: 'change_user_role',
    VIEW: 'view_user'
  },
  REPORT: {
    CREATE: 'create_report',
    UPDATE: 'update_report',
    DELETE: 'delete_report',
    SUBMIT: 'submit_report',
    EXPORT: 'export_report',
    VIEW: 'view_report'
  },
  TEMPLATE: {
    CREATE: 'create_template',
    UPDATE: 'update_template',
    DELETE: 'delete_template',
    VIEW: 'view_template'
  },
  DRAFT: {
    CREATE: 'create_draft',
    UPDATE: 'update_draft',
    DELETE: 'delete_draft',
    VIEW: 'view_draft'
  },
  SETTINGS: {
    UPDATE_ORG: 'update_org_settings',
    UPDATE_SYSTEM: 'update_system_settings',
    VIEW: 'view_settings'
  },
  ANALYTICS: {
    VIEW_DASHBOARD: 'view_analytics_dashboard',
    EXPORT_REPORT: 'export_analytics_report'
  }
};
