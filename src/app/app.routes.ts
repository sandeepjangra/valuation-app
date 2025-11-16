import { Routes } from '@angular/router';
import { Login } from './components/login/login';
import { Dashboard } from './components/dashboard/dashboard';
import { NewReport } from './components/new-report/new-report';
import { ReportForm } from './components/report-form/report-form';
import { Admin } from './components/admin/admin';
import { Reports } from './components/reports/reports';
import { Banks } from './components/banks/banks';
import { BankDetails } from './components/bank-details/bank-details';
import { LogViewerComponent } from './components/log-viewer.component';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'login', component: Login },
  { path: 'dashboard', component: Dashboard },
  { path: 'new-report', component: NewReport },
  { path: 'report-form', component: ReportForm },
  { path: 'admin', component: Admin },
  { path: 'reports', component: Reports },
  { path: 'banks', component: Banks },
  { path: 'bank-details/:id', component: BankDetails },
  { path: 'logs', component: LogViewerComponent },
];
