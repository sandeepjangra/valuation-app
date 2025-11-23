import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

interface HealthService {
  status: string;
  response_time_ms: number;
  message: string;
  details?: any;
  error?: string;
}

interface SystemResource {
  percent: number;
  status: string;
  total_gb?: number;
  used_gb?: number;
  available_gb?: number;
  free_gb?: number;
}

interface HealthData {
  overall_status: string;
  timestamp: string;
  services: {
    backend_api: HealthService;
    mongodb: HealthService;
    storage: HealthService;
  };
  system_resources: {
    cpu: SystemResource;
    memory: SystemResource;
    disk: SystemResource;
  };
  performance_metrics: {
    uptime_seconds: number;
    requests_per_minute: number;
    avg_response_time_ms: number;
    error_rate_percent: number;
  };
}

@Component({
  selector: 'app-health-check',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="health-check">
      <div class="health-header">
        <div>
          <h2>💚 System Health Check</h2>
          <p class="subtitle">Monitor backend services, database, storage, and system resources</p>
        </div>
        <div class="header-actions">
          <div class="last-updated">
            Last updated: {{ getRelativeTime(healthData()?.timestamp) }}
          </div>
          <button (click)="refreshHealth()" [disabled]="loading()" class="btn btn-primary">
            <span [class.spinning]="loading()">🔄</span> Refresh
          </button>
        </div>
      </div>

      @if (error()) {
        <div class="error-alert">
          <span>⚠️</span>
          <div>
            <strong>Error loading health data</strong>
            <p>{{ error() }}</p>
          </div>
        </div>
      }

      @if (loading() && !healthData()) {
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Loading health data...</p>
        </div>
      }

      @if (healthData()) {
        <!-- Overall Status Banner -->
        <div [class]="'status-banner status-' + healthData()!.overall_status">
          <span class="status-icon">
            {{ healthData()!.overall_status === 'healthy' ? '✅' : 
               healthData()!.overall_status === 'degraded' ? '🟡' : '🔴' }}
          </span>
          <div class="status-text">
            <h3>{{ healthData()!.overall_status === 'healthy' ? 'All Systems Operational' :
                   healthData()!.overall_status === 'degraded' ? 'System Performance Degraded' :
                   'Critical System Issues Detected' }}</h3>
            <p>{{ healthData()!.overall_status === 'healthy' ? 'All services are running normally' :
                  healthData()!.overall_status === 'degraded' ? 'Some services may be experiencing issues' :
                  'Immediate attention required' }}</p>
          </div>
        </div>

        <!-- Services Status -->
        <div class="section">
          <h3 class="section-title">🖥️ Backend Services</h3>
          <div class="services-grid">
            <!-- Backend API -->
            <div class="service-card">
              <div class="service-header">
                <div class="service-name">
                  <span class="service-icon">⚡</span>
                  <span>FastAPI Backend</span>
                </div>
                <span [class]="'badge badge-' + healthData()!.services.backend_api.status">
                  {{ healthData()!.services.backend_api.status.toUpperCase() }}
                </span>
              </div>
              <div class="service-details">
                <div class="detail-row">
                  <span class="label">Response Time:</span>
                  <span class="value">{{ healthData()!.services.backend_api.response_time_ms }}ms</span>
                </div>
                <div class="detail-row">
                  <span class="label">Message:</span>
                  <span class="value">{{ healthData()!.services.backend_api.message }}</span>
                </div>
              </div>
            </div>

            <!-- MongoDB -->
            <div class="service-card">
              <div class="service-header">
                <div class="service-name">
                  <span class="service-icon">🍃</span>
                  <span>MongoDB Database</span>
                </div>
                <span [class]="'badge badge-' + healthData()!.services.mongodb.status">
                  {{ healthData()!.services.mongodb.status.toUpperCase() }}
                </span>
              </div>
              <div class="service-details">
                <div class="detail-row">
                  <span class="label">Response Time:</span>
                  <span class="value">{{ healthData()!.services.mongodb.response_time_ms }}ms</span>
                </div>
                <div class="detail-row">
                  <span class="label">Message:</span>
                  <span class="value">{{ healthData()!.services.mongodb.message }}</span>
                </div>
                @if (healthData()!.services.mongodb.details) {
                  <div class="detail-row">
                    <span class="label">Version:</span>
                    <span class="value">{{ healthData()!.services.mongodb.details.version }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="label">Databases:</span>
                    <span class="value">{{ healthData()!.services.mongodb.details.databases_count }}</span>
                  </div>
                }
              </div>
            </div>

            <!-- Storage -->
            <div class="service-card">
              <div class="service-header">
                <div class="service-name">
                  <span class="service-icon">💾</span>
                  <span>File Storage</span>
                </div>
                <span [class]="'badge badge-' + healthData()!.services.storage.status">
                  {{ healthData()!.services.storage.status.toUpperCase() }}
                </span>
              </div>
              <div class="service-details">
                <div class="detail-row">
                  <span class="label">Status:</span>
                  <span class="value">{{ healthData()!.services.storage.message }}</span>
                </div>
                @if (healthData()!.services.storage.details) {
                  <div class="detail-row">
                    <span class="label">Total Space:</span>
                    <span class="value">{{ healthData()!.services.storage.details.total_gb }} GB</span>
                  </div>
                  <div class="detail-row">
                    <span class="label">Used:</span>
                    <span class="value">{{ healthData()!.services.storage.details.used_gb }} GB</span>
                  </div>
                  <div class="detail-row">
                    <span class="label">Free:</span>
                    <span class="value">{{ healthData()!.services.storage.details.free_gb }} GB</span>
                  </div>
                }
              </div>
            </div>
          </div>
        </div>

        <!-- System Resources -->
        <div class="section">
          <h3 class="section-title">📊 System Resources</h3>
          <div class="resources-grid">
            <!-- CPU -->
            <div class="resource-card">
              <div class="resource-header">
                <span class="resource-label">CPU Usage</span>
                <span [class]="'resource-status status-' + healthData()!.system_resources.cpu.status">
                  {{ healthData()!.system_resources.cpu.percent }}%
                </span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" 
                     [style.width.%]="healthData()!.system_resources.cpu.percent"
                     [class]="'fill-' + healthData()!.system_resources.cpu.status">
                </div>
              </div>
              <div class="resource-info">
                Status: {{ healthData()!.system_resources.cpu.status }}
              </div>
            </div>

            <!-- Memory -->
            <div class="resource-card">
              <div class="resource-header">
                <span class="resource-label">Memory Usage</span>
                <span [class]="'resource-status status-' + healthData()!.system_resources.memory.status">
                  {{ healthData()!.system_resources.memory.percent }}%
                </span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" 
                     [style.width.%]="healthData()!.system_resources.memory.percent"
                     [class]="'fill-' + healthData()!.system_resources.memory.status">
                </div>
              </div>
              <div class="resource-info">
                {{ healthData()!.system_resources.memory.used_gb }} GB / 
                {{ healthData()!.system_resources.memory.total_gb }} GB
              </div>
            </div>

            <!-- Disk -->
            <div class="resource-card">
              <div class="resource-header">
                <span class="resource-label">Disk Space</span>
                <span [class]="'resource-status status-' + healthData()!.system_resources.disk.status">
                  {{ healthData()!.system_resources.disk.percent }}%
                </span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" 
                     [style.width.%]="healthData()!.system_resources.disk.percent"
                     [class]="'fill-' + healthData()!.system_resources.disk.status">
                </div>
              </div>
              <div class="resource-info">
                {{ healthData()!.system_resources.disk.used_gb }} GB / 
                {{ healthData()!.system_resources.disk.total_gb }} GB
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Metrics -->
        <div class="section">
          <h3 class="section-title">⚡ Performance Metrics</h3>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-value">{{ formatUptime(healthData()!.performance_metrics.uptime_seconds) }}</div>
              <div class="metric-label">System Uptime</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ healthData()!.performance_metrics.requests_per_minute || 'N/A' }}</div>
              <div class="metric-label">Requests/Min</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ healthData()!.performance_metrics.avg_response_time_ms || 'N/A' }}ms</div>
              <div class="metric-label">Avg Response Time</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ healthData()!.performance_metrics.error_rate_percent || 0 }}%</div>
              <div class="metric-label">Error Rate</div>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styleUrls: ['./health-check.component.css']
})
export class HealthCheckComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly API_BASE = environment.apiUrl || 'http://localhost:8000/api';

  healthData = signal<HealthData | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);

  ngOnInit() {
    this.loadHealthData();
  }

  loadHealthData() {
    this.loading.set(true);
    this.error.set(null);

    this.http.get<any>(`${this.API_BASE}/admin/dashboard/health`).subscribe({
      next: (response) => {
        if (response.success) {
          this.healthData.set(response.data);
        } else {
          this.error.set(response.error || 'Failed to load health data');
        }
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Health check failed:', err);
        this.error.set(err.error?.error || 'Failed to connect to server');
        this.loading.set(false);
      }
    });
  }

  refreshHealth() {
    this.loadHealthData();
  }

  getRelativeTime(timestamp: string | undefined): string {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const then = new Date(timestamp);
    const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

    if (seconds < 10) return 'Just now';
    if (seconds < 60) return `${seconds} seconds ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    return `${Math.floor(seconds / 3600)} hours ago`;
  }

  formatUptime(seconds: number): string {
    if (!seconds) return 'N/A';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  }
}
