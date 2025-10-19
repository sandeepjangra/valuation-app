import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AdminService, CollectionDocument } from '../services/admin.service';

@Component({
  selector: 'app-document-editor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="document-editor">
      <header class="editor-header">
        <div class="header-info">
          <h2>{{ isNewDocument ? 'Create New Document' : 'Edit Document' }}</h2>
          <div class="breadcrumb">
            <span>{{ database }}.{{ collection }}</span>
            <span *ngIf="!isNewDocument"> → {{ documentId }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" (click)="goBack()">
            ← Back
          </button>
          <button 
            class="btn btn-success" 
            (click)="saveDocument()"
            [disabled]="!isValidJson || saving"
          >
            {{ saving ? '💾 Saving...' : '💾 Save' }}
          </button>
        </div>
      </header>

      <div class="editor-content" *ngIf="!loading">
        <div class="editor-toolbar">
          <button 
            class="btn btn-format" 
            (click)="formatJson()"
            [disabled]="!isValidJson"
            title="Format JSON"
          >
            🎨 Format
          </button>
          <button 
            class="btn btn-validate" 
            (click)="validateJson()"
            title="Validate JSON"
          >
            ✅ Validate
          </button>
          <span class="validation-status" [ngClass]="{'valid': isValidJson, 'invalid': !isValidJson}">
            {{ isValidJson ? '✅ Valid JSON' : '❌ Invalid JSON' }}
          </span>
        </div>

        <div class="editor-container">
          <div class="json-editor">
            <textarea
              [(ngModel)]="documentJson"
              (input)="onJsonChange()"
              class="json-textarea"
              [class.error]="!isValidJson"
              placeholder="Enter JSON document..."
              spellcheck="false"
            ></textarea>
          </div>

          <div class="preview-panel" *ngIf="isValidJson && parsedDocument">
            <h4>Preview</h4>
            <div class="document-preview">
              <div *ngFor="let field of previewFields" class="preview-field">
                <strong>{{ field.key }}:</strong>
                <span class="field-value" [ngClass]="field.type">{{ field.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="error-panel" *ngIf="!isValidJson && jsonError">
          <h4>❌ JSON Error</h4>
          <pre>{{ jsonError }}</pre>
        </div>

        <div class="document-meta" *ngIf="originalDocument && !isNewDocument">
          <h4>Document Metadata</h4>
          <div class="meta-grid">
            <div class="meta-item">
              <strong>Document ID:</strong>
              <code>{{ originalDocument._id }}</code>
            </div>
            <div class="meta-item" *ngIf="originalDocument['createdAt']">
              <strong>Created:</strong>
              <span>{{ formatDate(originalDocument['createdAt']) }}</span>
            </div>
            <div class="meta-item" *ngIf="originalDocument['updatedAt']">
              <strong>Last Updated:</strong>
              <span>{{ formatDate(originalDocument['updatedAt']) }}</span>
            </div>
            <div class="meta-item" *ngIf="originalDocument['createdBy']">
              <strong>Created By:</strong>
              <span>{{ originalDocument['createdBy'] }}</span>
            </div>
            <div class="meta-item" *ngIf="originalDocument['version']">
              <strong>Version:</strong>
              <span>{{ originalDocument['version'] }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="loading" *ngIf="loading">
        Loading document...
      </div>
    </div>
  `,
  styles: [`
    .document-editor {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .editor-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 1rem;
      border-bottom: 2px solid #27ae60;
    }

    .header-info h2 {
      margin: 0 0 0.25rem 0;
      color: #2c3e50;
    }

    .breadcrumb {
      font-family: 'Courier New', monospace;
      font-size: 0.85rem;
      color: #7f8c8d;
    }

    .header-actions {
      display: flex;
      gap: 0.5rem;
    }

    .editor-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .editor-toolbar {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      margin-bottom: 1rem;
      padding: 0.5rem;
      background: #ecf0f1;
      border-radius: 4px;
    }

    .validation-status {
      margin-left: auto;
      font-size: 0.85rem;
      padding: 0.25rem 0.5rem;
      border-radius: 3px;
    }

    .validation-status.valid {
      background: #d5f4e6;
      color: #27ae60;
    }

    .validation-status.invalid {
      background: #fdeaea;
      color: #e74c3c;
    }

    .editor-container {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 300px;
      gap: 1rem;
      overflow: hidden;
    }

    .json-editor {
      display: flex;
      flex-direction: column;
    }

    .json-textarea {
      flex: 1;
      font-family: 'Courier New', monospace;
      font-size: 0.85rem;
      padding: 1rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      resize: none;
      outline: none;
      line-height: 1.5;
    }

    .json-textarea:focus {
      border-color: #3498db;
    }

    .json-textarea.error {
      border-color: #e74c3c;
      background: #fdeaea;
    }

    .preview-panel {
      background: #f8f9fa;
      padding: 1rem;
      border-radius: 4px;
      border: 1px solid #ecf0f1;
      overflow-y: auto;
    }

    .preview-panel h4 {
      margin-top: 0;
      color: #2c3e50;
    }

    .preview-field {
      margin-bottom: 0.5rem;
      padding: 0.25rem;
      border-radius: 3px;
      background: white;
    }

    .preview-field strong {
      color: #3498db;
      font-size: 0.8rem;
    }

    .field-value {
      display: block;
      margin-top: 0.25rem;
      font-size: 0.85rem;
      color: #2c3e50;
    }

    .field-value.string {
      color: #27ae60;
    }

    .field-value.number {
      color: #e67e22;
    }

    .field-value.boolean {
      color: #9b59b6;
    }

    .field-value.object {
      color: #34495e;
      font-style: italic;
    }

    .error-panel {
      background: #fdeaea;
      border: 1px solid #e74c3c;
      border-radius: 4px;
      padding: 1rem;
      margin-top: 1rem;
    }

    .error-panel h4 {
      margin-top: 0;
      color: #e74c3c;
    }

    .error-panel pre {
      color: #e74c3c;
      font-size: 0.85rem;
      margin: 0.5rem 0 0 0;
    }

    .document-meta {
      margin-top: 1rem;
      padding: 1rem;
      background: #f8f9fa;
      border-radius: 4px;
      border: 1px solid #ecf0f1;
    }

    .document-meta h4 {
      margin-top: 0;
      color: #2c3e50;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 0.5rem;
    }

    .meta-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
    }

    .meta-item strong {
      color: #7f8c8d;
      min-width: 80px;
    }

    .meta-item code {
      background: #ecf0f1;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
      font-size: 0.8rem;
    }

    .btn {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.85rem;
      transition: all 0.3s;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: #95a5a6;
      color: white;
    }

    .btn-secondary:hover:not(:disabled) {
      background: #7f8c8d;
    }

    .btn-success {
      background: #27ae60;
      color: white;
    }

    .btn-success:hover:not(:disabled) {
      background: #229954;
    }

    .btn-format {
      background: #3498db;
      color: white;
    }

    .btn-format:hover:not(:disabled) {
      background: #2980b9;
    }

    .btn-validate {
      background: #e67e22;
      color: white;
    }

    .btn-validate:hover:not(:disabled) {
      background: #d35400;
    }

    .loading {
      text-align: center;
      color: #7f8c8d;
      font-style: italic;
      margin-top: 2rem;
    }

    @media (max-width: 768px) {
      .editor-container {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class DocumentEditorComponent implements OnInit {
  database?: string;
  collection?: string;
  documentId?: string;
  isNewDocument = false;
  
  originalDocument?: CollectionDocument;
  documentJson = '';
  parsedDocument?: any;
  previewFields: any[] = [];
  
  isValidJson = true;
  jsonError = '';
  loading = true;
  saving = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private adminService: AdminService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.database = params['database'];
      this.collection = params['collection'];
      this.documentId = params['id'];
      this.isNewDocument = this.documentId === 'new';
      
      if (this.isNewDocument) {
        this.initNewDocument();
      } else if (this.database && this.collection && this.documentId) {
        this.loadDocument();
      }
    });
  }

  private initNewDocument() {
    this.documentJson = JSON.stringify({
      // Add some default fields based on collection
      ...(this.collection === 'banks' ? {
        bankCode: '',
        bankName: '',
        isActive: true
      } : {}),
      ...(this.collection === 'common_form_fields' ? {
        fieldId: '',
        fieldName: '',
        fieldType: 'text',
        isRequired: false,
        isActive: true
      } : {})
    }, null, 2);
    
    this.loading = false;
    this.onJsonChange();
  }

  private loadDocument() {
    if (!this.database || !this.collection || !this.documentId) return;
    
    this.adminService.getDocument(this.database, this.collection, this.documentId).subscribe({
      next: (document) => {
        this.originalDocument = document;
        this.documentJson = JSON.stringify(document, null, 2);
        this.loading = false;
        this.onJsonChange();
      },
      error: (error) => {
        console.error('Error loading document:', error);
        this.loading = false;
      }
    });
  }

  onJsonChange() {
    this.validateJson();
    if (this.isValidJson) {
      this.updatePreview();
    }
  }

  validateJson() {
    try {
      this.parsedDocument = JSON.parse(this.documentJson);
      this.isValidJson = true;
      this.jsonError = '';
    } catch (error) {
      this.isValidJson = false;
      this.jsonError = error instanceof Error ? error.message : 'Invalid JSON';
      this.parsedDocument = null;
    }
  }

  formatJson() {
    if (this.isValidJson && this.parsedDocument) {
      this.documentJson = JSON.stringify(this.parsedDocument, null, 2);
    }
  }

  updatePreview() {
    if (!this.parsedDocument) return;
    
    this.previewFields = Object.entries(this.parsedDocument)
      .slice(0, 10) // Limit preview fields
      .map(([key, value]) => ({
        key,
        value: this.formatFieldValue(value),
        type: this.getFieldType(value)
      }));
  }

  private formatFieldValue(value: any): string {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (typeof value === 'object') {
      return Array.isArray(value) ? `Array (${value.length} items)` : `Object (${Object.keys(value).length} keys)`;
    }
    if (typeof value === 'string' && value.length > 50) {
      return value.substring(0, 50) + '...';
    }
    return String(value);
  }

  private getFieldType(value: any): string {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return 'object';
    return typeof value;
  }

  saveDocument() {
    if (!this.isValidJson || !this.database || !this.collection || this.saving) return;
    
    this.saving = true;
    
    // Add metadata for new documents
    if (this.isNewDocument) {
      this.parsedDocument['createdAt'] = new Date().toISOString();
      this.parsedDocument['createdBy'] = 'admin'; // TODO: Get from auth
    } else {
      this.parsedDocument['updatedAt'] = new Date().toISOString();
      this.parsedDocument['updatedBy'] = 'admin'; // TODO: Get from auth
    }
    
    if (this.isNewDocument) {
      this.adminService.createDocument(this.database, this.collection, this.parsedDocument).subscribe({
        next: (response: any) => {
          this.saving = false;
          if (response._id) {
            // Navigate to edit mode for the new document
            this.router.navigate(['/admin/collections', this.database, this.collection, response._id]);
          } else {
            // Go back to collection browser
            this.goBack();
          }
        },
        error: (error: any) => {
          console.error('Error saving document:', error);
          this.saving = false;
          alert('Failed to save document. Please try again.');
        }
      });
    } else {
      this.adminService.updateDocument(this.database, this.collection, this.documentId!, this.parsedDocument).subscribe({
        next: (response: any) => {
          this.saving = false;
          // Go back to collection browser
          this.goBack();
        },
        error: (error: any) => {
          console.error('Error saving document:', error);
          this.saving = false;
          alert('Failed to save document. Please try again.');
        }
      });
    }
  }

  goBack() {
    this.router.navigate(['/admin/collections', this.database, this.collection]);
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString();
  }
}