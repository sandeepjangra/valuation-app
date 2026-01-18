/**
 * HasPermission Directive
 * Shows/hides elements based on user permissions
 * Usage: *hasPermission="'reports.create'"
 * Usage: *hasPermission="['reports.create', 'reports.editOwn']" mode="all"
 */

import { 
  Directive, 
  Input, 
  TemplateRef, 
  ViewContainerRef,
  OnInit,
  OnDestroy,
  inject
} from '@angular/core';
import { PermissionsService } from '../services/permissions.service';

@Directive({
  selector: '[hasPermission]',
  standalone: true
})
export class HasPermissionDirective implements OnInit, OnDestroy {
  private readonly templateRef = inject(TemplateRef<any>);
  private readonly viewContainer = inject(ViewContainerRef);
  private readonly permissionsService = inject(PermissionsService);

  private permissions: string[] = [];
  private mode: 'all' | 'any' = 'all';
  private hasView = false;

  @Input()
  set hasPermission(value: string | string[]) {
    this.permissions = Array.isArray(value) ? value : [value];
    this.updateView();
  }

  @Input()
  set hasPermissionMode(value: 'all' | 'any') {
    this.mode = value;
    this.updateView();
  }

  ngOnInit(): void {
    this.updateView();
  }

  ngOnDestroy(): void {
    this.viewContainer.clear();
  }

  private updateView(): void {
    const hasPermission = this.checkPermissions();

    if (hasPermission && !this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (!hasPermission && this.hasView) {
      this.viewContainer.clear();
      this.hasView = false;
    }
  }

  private checkPermissions(): boolean {
    if (this.permissions.length === 0) {
      return true; // No permissions specified, show by default
    }

    if (this.mode === 'all') {
      return this.permissionsService.hasAllPermissions(this.permissions);
    } else {
      return this.permissionsService.hasAnyPermission(this.permissions);
    }
  }
}
