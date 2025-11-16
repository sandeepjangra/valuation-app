import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    path: 'login',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'organization/dashboard',
    renderMode: RenderMode.Server
  },
  {
    path: 'organization/users',
    renderMode: RenderMode.Server
  },
  {
    path: 'organization/reports',
    renderMode: RenderMode.Server
  },
  {
    path: 'system/dashboard',
    renderMode: RenderMode.Server
  },
  {
    path: '**',
    renderMode: RenderMode.Prerender
  }
];
