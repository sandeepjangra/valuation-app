import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PDFUploadResult {
  success: boolean;
  message?: string;
  data?: {
    filename: string;
    validation: {
      valid: boolean;
      errors: string[];
      size_mb: number;
    };
    extracted_fields: {[key: string]: any};
    form_fields: {[key: string]: string};
    processing_info: {
      fields_found: number;
      text_length: number;
      timestamp: string;
    };
  };
  error?: string;
}

export interface PDFFieldExtractionResult {
  success: boolean;
  fields: {[key: string]: string};
  metadata: {
    filename: string;
    fields_extracted: number;
    extraction_timestamp: string;
  };
  error?: string;
}

export interface SupportedField {
  description: string;
  form_field: string;
  example: string;
}

export interface SupportedFieldsResult {
  success: boolean;
  supported_fields: {[key: string]: SupportedField};
  processing_info: {
    max_file_size_mb: number;
    supported_extensions: string[];
    extraction_method: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class PdfProcessorService {
  private apiUrl = 'http://localhost:8000/api/pdf';

  constructor(private http: HttpClient) { }

  /**
   * Upload PDF file and extract all field data
   */
  uploadPdf(file: File): Observable<PDFUploadResult> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<PDFUploadResult>(`${this.apiUrl}/upload`, formData);
  }

  /**
   * Extract only form fields from PDF for direct integration
   */
  extractFieldsFromPdf(file: File): Observable<PDFFieldExtractionResult> {
    console.log('🔗 PDF Service: Starting extraction for file:', file.name);
    console.log('🔗 PDF Service: API URL:', `${this.apiUrl}/extract-fields`);
    
    const formData = new FormData();
    formData.append('file', file);

    console.log('🔗 PDF Service: Making HTTP request...');
    return this.http.post<PDFFieldExtractionResult>(`${this.apiUrl}/extract-fields`, formData);
  }

  /**
   * Get list of supported fields that can be extracted
   */
  getSupportedFields(): Observable<SupportedFieldsResult> {
    return this.http.get<SupportedFieldsResult>(`${this.apiUrl}/supported-fields`);
  }

  /**
   * Check PDF service health
   */
  checkHealth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }

  /**
   * Validate file before upload
   */
  validatePdfFile(file: File): {valid: boolean, errors: string[]} {
    const errors: string[] = [];
    
    // Check file type
    if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
      errors.push('Please select a PDF file');
    }
    
    // Check file size (15MB limit to match backend)
    const maxSizeMB = 15;
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      errors.push(`File size (${fileSizeMB.toFixed(1)}MB) exceeds limit of ${maxSizeMB}MB`);
    }
    
    // Check filename
    if (!file.name || file.name.trim().length === 0) {
      errors.push('Invalid filename');
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Get field mapping for form pre-fill
   */
  mapExtractedFieldsToForm(extractedFields: {[key: string]: string}): {[key: string]: any} {
    console.log('🔄 mapExtractedFieldsToForm input:', extractedFields);
    const formData: {[key: string]: any} = {};
    
    // The API already returns the correct field names, so we can use them directly
    // Just need to process dates and handle special formatting
    Object.entries(extractedFields).forEach(([fieldName, value]) => {
      if (value && typeof value === 'string' && value.trim()) {
        // Convert dates to proper format if needed
        if (fieldName.includes('Date') && value.includes('.')) {
          // Convert DD.MM.YYYY to YYYY-MM-DD for date inputs
          const parts = value.split('.');
          if (parts.length === 3) {
            const [day, month, year] = parts;
            formData[fieldName] = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
            console.log(`📅 Converted date ${fieldName}: ${value} → ${formData[fieldName]}`);
          } else {
            formData[fieldName] = value;
          }
        } else {
          formData[fieldName] = value;
          console.log(`📝 Mapped field ${fieldName}: ${value}`);
        }
      }
    });

    console.log('✅ Final mapped form data:', formData);
    return formData;
  }

  /**
   * Get extraction summary for display
   */
  getExtractionSummary(result: PDFUploadResult): string {
    if (!result.success || !result.data) {
      return 'PDF processing failed';
    }

    const fieldsFound = result.data.processing_info.fields_found;
    const filename = result.data.filename;
    
    return `Successfully extracted ${fieldsFound} fields from ${filename}`;
  }
}