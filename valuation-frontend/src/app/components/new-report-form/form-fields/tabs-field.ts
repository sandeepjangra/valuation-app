import { Component, Input, Type, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';
import { TabsField } from '../../../models/valuation-template.model';

@Component({
  selector: 'app-tabs-field',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './tabs-field.html',
  styles: [`
    .tabs-wrapper {
      margin: 32px 0;
    }

    .tab-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      padding: 8px;
      background: linear-gradient(to bottom, #f9fafb, #ffffff);
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      overflow-x: auto;
      scrollbar-width: thin;
      scrollbar-color: #e5e7eb transparent;
    }

    .tab-bar::-webkit-scrollbar {
      height: 6px;
    }

    .tab-bar::-webkit-scrollbar-track {
      background: transparent;
    }

    .tab-bar::-webkit-scrollbar-thumb {
      background: #e5e7eb;
      border-radius: 3px;
    }

    .tab-btn {
      position: relative;
      flex: 1;
      min-width: 180px;
      padding: 16px 24px;
      border: 2px solid #d1d5db;
      border-radius: 12px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      background: white;
      color: #6b7280;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .tab-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
      color: #374151;
      border-color: #9ca3af;
    }

    .tab-btn.active {
      background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%);
      color: white;
      border: 2px solid #7c3aed;
      box-shadow: 0 8px 20px rgba(139, 92, 246, 0.35);
      transform: translateY(-2px);
    }

    .tab-btn.active::before {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 0;
      height: 0;
      border-left: 8px solid transparent;
      border-right: 8px solid transparent;
      border-top: 8px solid #8b5cf6;
    }

    .tab-btn:nth-child(1).active {
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
      border: 2px solid #1e40af;
      box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
    }

    .tab-btn:nth-child(1).active::before {
      border-top-color: #3b82f6;
    }

    .tab-btn:nth-child(2).active {
      background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
      border: 2px solid #065f46;
      box-shadow: 0 8px 20px rgba(16, 185, 129, 0.35);
    }

    .tab-btn:nth-child(2).active::before {
      border-top-color: #10b981;
    }

    .tab-btn:nth-child(3).active {
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #b45309 100%);
      border: 2px solid #92400e;
      box-shadow: 0 8px 20px rgba(245, 158, 11, 0.35);
    }

    .tab-btn:nth-child(3).active::before {
      border-top-color: #f59e0b;
    }

    .tab-btn:nth-child(4).active {
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%);
      border: 2px solid #991b1b;
      box-shadow: 0 8px 20px rgba(239, 68, 68, 0.35);
    }

    .tab-btn:nth-child(4).active::before {
      border-top-color: #ef4444;
    }

    .tab-btn:nth-child(5).active {
      background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%);
      border: 2px solid #5b21b6;
      box-shadow: 0 8px 20px rgba(139, 92, 246, 0.35);
    }

    .tab-btn:nth-child(5).active::before {
      border-top-color: #8b5cf6;
    }

    .tab-panels {
      background: white;
      border-radius: 16px;
      padding: 32px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
      border: 2px solid #f3f4f6;
      min-height: 400px;
    }

    .tab-panel {
      animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @media (max-width: 768px) {
      .tab-bar {
        flex-wrap: nowrap;
        overflow-x: auto;
        gap: 8px;
        padding: 6px;
      }

      .tab-btn {
        min-width: 140px;
        padding: 12px 16px;
        font-size: 14px;
      }

      .tab-panels {
        padding: 20px;
      }
    }
  `]
})
export class TabsFieldComponent implements OnInit {
  @Input() field!: TabsField;
  @Input() form!: FormGroup;
  @Input() tableRows!: Record<string, Record<string, any>[]>;
  @Input() collapsedMap!: Record<string, boolean>;

  activeTab = 0;
  formFieldComponent!: Type<any>;

  constructor(private cdr: ChangeDetectorRef) {}

  async ngOnInit() {
    // Dynamically import FormFieldComponent to avoid circular dependency
    const { FormFieldComponent } = await import('./form-field');
    this.formFieldComponent = FormFieldComponent;
    this.cdr.detectChanges();
  }
}
