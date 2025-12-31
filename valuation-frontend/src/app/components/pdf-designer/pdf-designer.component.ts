/**
 * PDF Template Visual Designer Component
 * Microsoft Word-like interface for creating flexible PDF templates
 */

import { Component, OnInit, signal, computed, inject, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { 
  PDFTemplateDesigner, 
  PDFDesignerSection, 
  PDFDesignerElement, 
  PDFTextElement,
  PDFTableElement,
  PDFListElement,
  DesignerTool,
  DesignerState
} from '../../models/pdf-designer.model';
import { Bank } from '../../models/bank.model';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-pdf-designer',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './pdf-designer.component.html',
  styleUrls: ['./pdf-designer.component.css']
})
export class PDFDesignerComponent implements OnInit {
  @ViewChild('designCanvas', { static: false }) canvasRef!: ElementRef<HTMLDivElement>;

  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly fb = inject(FormBuilder);

  // Organization context
  private readonly currentOrgShortName = signal<string>('');
  private readonly API_BASE_URL = 'http://localhost:8000/api';

  // Template data
  template = signal<PDFTemplateDesigner | null>(null);
  templateForm: FormGroup;
  
  // Designer state
  designerState = signal<DesignerState>({
    zoomLevel: 100,
    gridEnabled: true,
    snapToGrid: true,
    gridSize: 10
  });

  // UI state
  isLoading = signal<boolean>(false);
  isSaving = signal<boolean>(false);
  error = signal<string | null>(null);
  templateId = signal<string | null>(null);
  banks = signal<Bank[]>([]);

  // Designer tools
  availableTools = signal<DesignerTool[]>([
    // Layout tools
    { id: 'section', name: 'Section', icon: '📄', type: 'section', category: 'layout', description: 'Create a new section' },
    
    // Content tools
    { id: 'text', name: 'Text', icon: '📝', type: 'element', category: 'content', description: 'Add text element' },
    { id: 'heading', name: 'Heading', icon: '📰', type: 'element', category: 'content', description: 'Add heading text' },
    
    // Data tools
    { id: 'field', name: 'Field', icon: '🔤', type: 'element', category: 'data', description: 'Add data field' },
    { id: 'table', name: 'Table', icon: '📊', type: 'element', category: 'data', description: 'Add table' },
    
    // List tools
    { id: 'list-ordered', name: 'Numbered List', icon: '🔢', type: 'element', category: 'content', description: 'Add numbered list' },
    { id: 'list-unordered', name: 'Bullet List', icon: '• ', type: 'element', category: 'content', description: 'Add bullet list' },
    { id: 'list-alpha', name: 'Alphabetical List', icon: '🔤', type: 'element', category: 'content', description: 'Add alphabetical list' }
  ]);

  // Panel visibility
  showLeftPanel = signal<boolean>(true);
  showRightPanel = signal<boolean>(true);
  activeTab = signal<string>('tools'); // tools, sections, elements, properties

  // Computed properties
  isEditMode = computed(() => !!this.templateId());
  pageTitle = computed(() => this.isEditMode() ? 'Edit PDF Template' : 'Create PDF Template');
  currentSections = computed(() => this.template()?.layout?.sections || []);
  selectedElement = computed(() => this.designerState().selectedElement);
  selectedSection = computed(() => this.designerState().selectedSection);

  constructor() {
    this.templateForm = this.fb.group({
      name: [''],
      bankCode: [''],
      propertyType: [''],
      description: ['']
    });
  }

  ngOnInit(): void {
    // Get organization context from route
    this.route.parent?.params.subscribe(params => {
      const orgShortName = params['orgShortName'];
      if (orgShortName) {
        this.currentOrgShortName.set(orgShortName);
        console.log('📍 PDF Designer - Current organization:', orgShortName);
      }
    });

    // Check permissions
    if (!this.authService.isManager() && !this.authService.isSystemAdmin()) {
      this.error.set('You do not have permission to use the PDF designer.');
      setTimeout(() => this.router.navigate(['/dashboard']), 2000);
      return;
    }

    // Load banks
    this.loadBanks();

    // Check if editing existing template
    this.route.params.subscribe(params => {
      const id = params['id'];
      if (id) {
        this.templateId.set(id);
        this.loadTemplate(id);
      } else {
        this.initializeNewTemplate();
      }
    });

    // Set query parameters for create mode
    this.route.queryParams.subscribe(params => {
      if (params['bankCode']) {
        this.templateForm.patchValue({ bankCode: params['bankCode'] });
      }
      if (params['propertyType']) {
        this.templateForm.patchValue({ propertyType: params['propertyType'] });
      }
    });
  }

  loadBanks(): void {
    fetch(`${this.API_BASE_URL}/banks`)
      .then(response => response.json())
      .then((banks: Bank[]) => {
        this.banks.set(banks);
      })
      .catch(error => {
        console.error('❌ Error loading banks:', error);
        this.notificationService.error('Failed to load banks');
      });
  }

  initializeNewTemplate(): void {
    const newTemplate: PDFTemplateDesigner = {
      name: 'New PDF Template',
      bankCode: '',
      propertyType: 'land',
      description: '',
      layout: {
        pageSize: 'A4',
        orientation: 'portrait',
        margins: { top: 20, right: 20, bottom: 20, left: 20 },
        sections: []
      },
      organizationId: this.authService.getOrganizationContext()?.organizationId || '',
      createdBy: 'current-user',
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.template.set(newTemplate);
    this.templateForm.patchValue({
      name: newTemplate.name,
      bankCode: newTemplate.bankCode,
      propertyType: newTemplate.propertyType,
      description: newTemplate.description
    });
  }

  loadTemplate(templateId: string): void {
    this.isLoading.set(true);
    // For now, initialize with empty template - will implement API call later
    this.initializeNewTemplate();
    this.isLoading.set(false);
  }

  // Section Management
  addSection(type: 'header' | 'content' | 'footer' | 'custom' = 'content'): void {
    const template = this.template();
    if (!template) return;

    const newSection: PDFDesignerSection = {
      id: `section_${Date.now()}`,
      name: `${type.charAt(0).toUpperCase() + type.slice(1)} Section`,
      type,
      order: template.layout.sections.length,
      position: { x: 0, y: 0, width: 100, height: 10 }, // Percentage based
      style: {
        backgroundColor: 'transparent',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        borderStyle: 'solid',
        padding: 10,
        margin: 5
      },
      elements: []
    };

    const updatedTemplate = {
      ...template,
      layout: {
        ...template.layout,
        sections: [...template.layout.sections, newSection]
      }
    };

    this.template.set(updatedTemplate);
    this.selectSection(newSection);
    this.notificationService.success(`${type.charAt(0).toUpperCase() + type.slice(1)} section added`);
  }

  selectSection(section: PDFDesignerSection): void {
    const currentState = this.designerState();
    this.designerState.set({
      ...currentState,
      selectedSection: section,
      selectedElement: undefined
    });
    this.activeTab.set('properties');
  }

  deleteSection(sectionId: string): void {
    const template = this.template();
    if (!template) return;

    const confirmed = confirm('Are you sure you want to delete this section and all its elements?');
    if (!confirmed) return;

    const updatedSections = template.layout.sections.filter(s => s.id !== sectionId);
    const updatedTemplate = {
      ...template,
      layout: {
        ...template.layout,
        sections: updatedSections
      }
    };

    this.template.set(updatedTemplate);
    
    // Clear selection if deleted section was selected
    const currentState = this.designerState();
    if (currentState.selectedSection?.id === sectionId) {
      this.designerState.set({
        ...currentState,
        selectedSection: undefined,
        selectedElement: undefined
      });
    }

    this.notificationService.success('Section deleted');
  }

  // Element Management
  addElement(tool: DesignerTool, sectionId?: string): void {
    const template = this.template();
    if (!template || template.layout.sections.length === 0) {
      this.notificationService.warning('Please add a section first');
      return;
    }

    // Use selected section or first available section
    const targetSectionId = sectionId || this.selectedSection()?.id || template.layout.sections[0].id;
    const section = template.layout.sections.find(s => s.id === targetSectionId);
    
    if (!section) {
      this.notificationService.error('No valid section found');
      return;
    }

    const newElement = this.createElementFromTool(tool);
    if (!newElement) return;

    // Add element to section
    const updatedSection = {
      ...section,
      elements: [...section.elements, newElement]
    };

    const updatedSections = template.layout.sections.map(s => 
      s.id === targetSectionId ? updatedSection : s
    );

    const updatedTemplate = {
      ...template,
      layout: {
        ...template.layout,
        sections: updatedSections
      }
    };

    this.template.set(updatedTemplate);
    this.selectElement(newElement);
    this.notificationService.success(`${tool.name} element added`);
  }

  createElementFromTool(tool: DesignerTool): PDFDesignerElement | null {
    const baseElement = {
      id: `element_${Date.now()}`,
      order: 0,
      position: { x: 10, y: 10, width: 50, height: 5 }, // Percentage based
      style: {
        fontSize: 12,
        fontWeight: 'normal' as const,
        fontStyle: 'normal' as const,
        textAlign: 'left' as const,
        textDecoration: 'none' as const,
        color: '#000000',
        padding: 5,
        margin: 2,
        lineHeight: 1.4
      }
    };

    switch (tool.id) {
      case 'text':
        return {
          ...baseElement,
          type: 'text',
          content: {
            text: 'Sample text',
            placeholder: 'Enter your text here',
            isEditable: true,
            formatting: { bold: false, italic: false, underline: false }
          }
        } as PDFTextElement;

      case 'heading':
        return {
          ...baseElement,
          type: 'text',
          style: { ...baseElement.style, fontSize: 16, fontWeight: 'bold' },
          content: {
            text: 'Heading Text',
            placeholder: 'Enter heading text',
            isEditable: true,
            formatting: { bold: true, italic: false, underline: false }
          }
        } as PDFTextElement;

      case 'table':
        return {
          ...baseElement,
          type: 'table',
          position: { x: 10, y: 10, width: 80, height: 20 },
          content: {
            rows: 3,
            columns: 3,
            headers: ['Column 1', 'Column 2', 'Column 3'],
            data: [
              [
                { value: 'Row 1, Col 1' },
                { value: 'Row 1, Col 2' },
                { value: 'Row 1, Col 3' }
              ],
              [
                { value: 'Row 2, Col 1' },
                { value: 'Row 2, Col 2' },
                { value: 'Row 2, Col 3' }
              ]
            ],
            styling: {
              headerStyle: { ...baseElement.style, fontWeight: 'bold', backgroundColor: '#f7fafc' },
              cellStyle: baseElement.style,
              borderCollapse: true,
              alternateRowColors: false
            }
          }
        } as PDFTableElement;

      case 'list-ordered':
      case 'list-unordered':
      case 'list-alpha':
        const listType = tool.id === 'list-unordered' ? 'unordered' : 'ordered';
        const orderingStyle = tool.id === 'list-alpha' ? 'alphabetic-lower' : 'numeric';
        
        return {
          ...baseElement,
          type: 'list',
          content: {
            listType,
            orderingStyle,
            items: [
              { id: 'item1', text: 'First item', level: 0 },
              { id: 'item2', text: 'Second item', level: 0 },
              { id: 'item3', text: 'Third item', level: 0 }
            ],
            indentation: 20,
            spacing: 5
          }
        } as PDFListElement;

      default:
        this.notificationService.error(`Element type ${tool.id} not yet implemented`);
        return null;
    }
  }

  selectElement(element: PDFDesignerElement): void {
    const currentState = this.designerState();
    this.designerState.set({
      ...currentState,
      selectedElement: element,
      selectedSection: undefined
    });
    this.activeTab.set('properties');
  }

  // UI Methods
  toggleLeftPanel(): void {
    this.showLeftPanel.set(!this.showLeftPanel());
  }

  toggleRightPanel(): void {
    this.showRightPanel.set(!this.showRightPanel());
  }

  setActiveTab(tab: string): void {
    this.activeTab.set(tab);
  }

  // Save and Navigation
  saveTemplate(): void {
    const template = this.template();
    if (!template) return;

    // Update template with form data
    const formData = this.templateForm.value;
    const updatedTemplate = {
      ...template,
      name: formData.name || template.name,
      bankCode: formData.bankCode || template.bankCode,
      propertyType: formData.propertyType || template.propertyType,
      description: formData.description || template.description,
      updatedAt: new Date()
    };

    this.isSaving.set(true);
    
    // Simulate save for now
    setTimeout(() => {
      this.template.set(updatedTemplate);
      this.isSaving.set(false);
      this.notificationService.success('Template saved successfully!');
    }, 1000);
  }

  goBack(): void {
    const orgShortName = this.currentOrgShortName();
    if (orgShortName) {
      this.router.navigate(['/org', orgShortName, 'pdf-templates']);
    } else {
      const authOrgContext = this.authService.getOrganizationContext();
      if (authOrgContext?.orgShortName) {
        this.router.navigate(['/org', authOrgContext.orgShortName, 'pdf-templates']);
      } else {
        this.router.navigate(['/pdf-templates']);
      }
    }
  }

  // Property Update Methods
  updateElementProperty(propertyPath: string, value: any): void {
    const template = this.template();
    const selectedElement = this.selectedElement();
    
    if (!template || !selectedElement) return;

    // Find and update the element
    const updatedSections = template.layout.sections.map(section => {
      const updatedElements = section.elements.map(element => {
        if (element.id === selectedElement.id) {
          const updatedElement = { ...element };
          
          // Handle nested property updates
          const pathParts = propertyPath.split('.');
          let target = updatedElement as any;
          
          for (let i = 0; i < pathParts.length - 1; i++) {
            if (!target[pathParts[i]]) {
              target[pathParts[i]] = {};
            }
            target = target[pathParts[i]];
          }
          
          target[pathParts[pathParts.length - 1]] = value;
          return updatedElement;
        }
        return element;
      });
      
      return { ...section, elements: updatedElements };
    });

    const updatedTemplate = {
      ...template,
      layout: {
        ...template.layout,
        sections: updatedSections
      }
    };

    this.template.set(updatedTemplate);
    
    // Update selected element reference
    const updatedSelectedElement = updatedSections
      .flatMap(s => s.elements)
      .find(e => e.id === selectedElement.id);
    
    if (updatedSelectedElement) {
      const currentState = this.designerState();
      this.designerState.set({
        ...currentState,
        selectedElement: updatedSelectedElement
      });
    }
  }

  updateSectionProperty(propertyPath: string, value: any): void {
    const template = this.template();
    const selectedSection = this.selectedSection();
    
    if (!template || !selectedSection) return;

    // Find and update the section
    const updatedSections = template.layout.sections.map(section => {
      if (section.id === selectedSection.id) {
        const updatedSection = { ...section };
        
        // Handle nested property updates
        const pathParts = propertyPath.split('.');
        let target = updatedSection as any;
        
        for (let i = 0; i < pathParts.length - 1; i++) {
          if (!target[pathParts[i]]) {
            target[pathParts[i]] = {};
          }
          target = target[pathParts[i]];
        }
        
        target[pathParts[pathParts.length - 1]] = value;
        return updatedSection;
      }
      return section;
    });

    const updatedTemplate = {
      ...template,
      layout: {
        ...template.layout,
        sections: updatedSections
      }
    };

    this.template.set(updatedTemplate);
    
    // Update selected section reference
    const updatedSelectedSection = updatedSections.find(s => s.id === selectedSection.id);
    
    if (updatedSelectedSection) {
      const currentState = this.designerState();
      this.designerState.set({
        ...currentState,
        selectedSection: updatedSelectedSection
      });
    }
  }

  // UI Helper Methods for Template
  zoomIn(): void {
    const currentState = this.designerState();
    this.designerState.set({
      ...currentState,
      zoomLevel: Math.min(200, currentState.zoomLevel + 25)
    });
  }

  zoomOut(): void {
    const currentState = this.designerState();
    this.designerState.set({
      ...currentState,
      zoomLevel: Math.max(25, currentState.zoomLevel - 25)
    });
  }

  toggleGrid(): void {
    const currentState = this.designerState();
    this.designerState.set({
      ...currentState,
      gridEnabled: !currentState.gridEnabled
    });
  }

  toggleSnapToGrid(): void {
    const currentState = this.designerState();
    this.designerState.set({
      ...currentState,
      snapToGrid: !currentState.snapToGrid
    });
  }

  // TrackBy Functions for ngFor
  trackByIndex(index: number, item: any): number {
    return index;
  }

  trackById(index: number, item: any): string {
    return item.id;
  }

  // Event Handler Helper Methods
  onTextAreaInput(event: Event, propertyPath: string): void {
    const target = event.target as HTMLTextAreaElement;
    if (target) {
      this.updateElementProperty(propertyPath, target.value);
    }
  }

  onNumberInput(event: Event, propertyPath: string): void {
    const target = event.target as HTMLInputElement;
    if (target) {
      this.updateElementProperty(propertyPath, +target.value);
    }
  }

  onSelectChange(event: Event, propertyPath: string): void {
    const target = event.target as HTMLSelectElement;
    if (target) {
      this.updateElementProperty(propertyPath, target.value);
    }
  }

  onSectionTextInput(event: Event, propertyPath: string): void {
    const target = event.target as HTMLInputElement;
    if (target) {
      this.updateSectionProperty(propertyPath, target.value);
    }
  }

  onSectionSelectChange(event: Event, propertyPath: string): void {
    const target = event.target as HTMLSelectElement;
    if (target) {
      this.updateSectionProperty(propertyPath, target.value);
    }
  }

  onSectionColorInput(event: Event, propertyPath: string): void {
    const target = event.target as HTMLInputElement;
    if (target) {
      this.updateSectionProperty(propertyPath, target.value);
    }
  }

  // Helper methods for template
  getElementContentText(): string {
    const element = this.selectedElement();
    if (element && element.type === 'text') {
      return (element as any)?.content?.text || '';
    }
    return '';
  }

  getElementHeaders(): string[] {
    const element = this.selectedElement();
    if (element && element.type === 'table') {
      return (element as any)?.content?.headers || ['Col 1', 'Col 2', 'Col 3'];
    }
    return [];
  }

  getElementData(): any[][] {
    const element = this.selectedElement();
    if (element && element.type === 'table') {
      return (element as any)?.content?.data || [[{value:'Data'}, {value:'Data'}, {value:'Data'}]];
    }
    return [];
  }

  getElementItems(): any[] {
    const element = this.selectedElement();
    if (element && element.type === 'list') {
      return (element as any)?.content?.items || [{text: 'Item 1'}, {text: 'Item 2'}];
    }
    return [];
  }

  isOrderedList(element: any): boolean {
    return element?.content?.listType === 'ordered';
  }

  // Display helper methods for template rendering
  getElementTextForDisplay(element: any): string {
    return element?.content?.text || 'Sample text';
  }

  getElementHeadersForDisplay(element: any): string[] {
    return element?.content?.headers || ['Col 1', 'Col 2', 'Col 3'];
  }

  getElementDataForDisplay(element: any): any[][] {
    return element?.content?.data || [[{value:'Data'}, {value:'Data'}, {value:'Data'}]];
  }

  getElementItemsForDisplay(element: any): any[] {
    return element?.content?.items || [{text: 'Item 1'}, {text: 'Item 2'}];
  }

  isOrderedListForDisplay(element: any): boolean {
    return element?.content?.listType === 'ordered';
  }
}