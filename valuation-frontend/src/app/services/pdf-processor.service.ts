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
    const formData = new FormData();
    formData.append('file', file);

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
    const formData: {[key: string]: any} = {};
    
    // Common field mappings
    const fieldMappings: {[key: string]: string} = {
      'reportReferenceNumber': 'reference_number',
      'applicantName': 'applicant_name',
      'propertyAddress': 'property_address',
      'inspectionDate': 'inspection_date',
      'valuationDate': 'valuation_date',
      'propertyType': 'property_type',
      'marketValue': 'market_value'
    };

    // Map extracted fields to form fields
    Object.entries(fieldMappings).forEach(([formField, extractedField]) => {
      const value = extractedFields[extractedField];
      if (value && value.trim()) {
        // Convert dates to proper format if needed
        if (formField.includes('Date') && value.includes('.')) {
          // Convert DD.MM.YYYY to YYYY-MM-DD for date inputs
          const parts = value.split('.');
          if (parts.length === 3) {
            const [day, month, year] = parts;
            formData[formField] = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
          } else {
            formData[formField] = value;
          }
        } else {
          formData[formField] = value;
        }
      }
    });

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