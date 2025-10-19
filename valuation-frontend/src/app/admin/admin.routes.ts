import { Routes } from '@angular/router';
import { AdminDashboardComponent } from './components/admin-dashboard.component';
import { CollectionBrowserComponent } from './components/collection-browser.component';
import { DocumentEditorComponent } from './components/document-editor.component';
import { AuditTrailComponent } from './components/audit-trail.component';

export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminDashboardComponent,
    children: [
      { path: '', redirectTo: 'collections', pathMatch: 'full' },
      { path: 'collections', component: CollectionBrowserComponent },
      { path: 'collections/:database/:collection', component: CollectionBrowserComponent },
      { path: 'collections/:database/:collection/:id', component: DocumentEditorComponent },
      { path: 'audit', component: AuditTrailComponent }
    ]
  }
];