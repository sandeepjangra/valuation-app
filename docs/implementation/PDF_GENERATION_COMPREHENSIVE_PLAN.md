# PDF Document Generation for Bank-Specific Valuation Reports

## Current System Analysis

### ✅ **Existing Capabilities**:
- PDF field extraction (`extractedPdfFields` in report-form.ts)
- PyPDF2 library available for PDF manipulation
- Template system with bank-specific fields
- Form data structure for SBI Land Property valuations

## 🎯 **PDF Generation Implementation Options**

### **Option 1: HTML-to-PDF with Customizable Templates (RECOMMENDED)**

**Technology Stack**: 
- **Frontend**: Angular + HTML/CSS templating
- **Backend**: FastAPI + WeasyPrint/Puppeteer
- **Storage**: MongoDB for template configs

**Architecture**:
```
UI Template Builder → Template Config → HTML Generation → PDF Output
     ↓                    ↓               ↓              ↓
Angular Component → MongoDB Storage → Server Rendering → Download/Email
```

**Benefits**:
- ✅ **User-friendly**: Visual template builder in UI
- ✅ **Flexible**: Full CSS styling capabilities
- ✅ **Responsive**: Different layouts for different banks
- ✅ **Maintainable**: HTML templates are easy to modify
- ✅ **Professional**: High-quality PDF output

### **Option 2: Fillable PDF Forms**

**Technology Stack**:
- **Templates**: Pre-designed PDF forms with fillable fields
- **Backend**: PyPDF2/PDFtk for field population
- **Storage**: PDF template files per bank

**Benefits**:
- ✅ **Exact formatting**: Pixel-perfect bank layouts
- ✅ **Fast generation**: Direct field mapping
- ✅ **Bank compliance**: Match official formats

**Limitations**:
- ❌ Limited customization without recreating PDFs
- ❌ Requires PDF design software for changes

### **Option 3: Programmatic PDF Creation**

**Technology Stack**:
- **Backend**: ReportLab (Python) or jsPDF (JavaScript)
- **Templates**: Code-based layout definitions

**Benefits**:
- ✅ **Full control**: Precise positioning and formatting
- ✅ **Dynamic**: Conditional sections and layouts

**Limitations**:
- ❌ **Complex**: Requires programming for design changes
- ❌ **Time-intensive**: More development effort

## 🏗️ **RECOMMENDED IMPLEMENTATION: Option 1 - HTML-to-PDF**

### **Phase 1: Core PDF Generation System**

#### **1.1 Backend PDF Service**

```python
# backend/services/pdf_generator.py
from weasyprint import HTML, CSS
from jinja2 import Template
import json

class PDFGenerator:
    def __init__(self):
        self.template_path = "templates/pdf/"
        
    async def generate_report_pdf(self, bank_code: str, property_type: str, 
                                form_data: dict, template_config: dict = None):
        """Generate PDF from form data using bank-specific template"""
        
        # Load template configuration
        template_config = template_config or await self.get_template_config(bank_code, property_type)
        
        # Load HTML template
        html_template = self.load_html_template(bank_code, property_type)
        
        # Render with data
        rendered_html = self.render_template(html_template, form_data, template_config)
        
        # Generate PDF
        pdf_bytes = HTML(string=rendered_html).write_pdf()
        
        return pdf_bytes
        
    async def get_template_config(self, bank_code: str, property_type: str):
        """Get PDF template configuration from database"""
        # Query: valuation_admin.pdf_templates collection
        pass
        
    def render_template(self, html_template: str, form_data: dict, config: dict):
        """Render Jinja2 template with form data"""
        template = Template(html_template)
        return template.render(
            report_data=form_data,
            config=config,
            bank_info=self.get_bank_info(form_data.get('bank_code')),
            calculated_fields=self.calculate_derived_values(form_data)
        )
```

#### **1.2 API Endpoints**

```python
# Add to backend/main.py

@app.post("/api/reports/{report_id}/generate-pdf")
async def generate_pdf_report(
    report_id: str,
    request: Request,
    template_config: Optional[Dict] = None
):
    """Generate PDF for a specific report"""
    
    # Get report data
    report_data = await get_report_by_id(report_id)
    
    # Generate PDF
    pdf_generator = PDFGenerator()
    pdf_bytes = await pdf_generator.generate_report_pdf(
        bank_code=report_data['bank_code'],
        property_type=report_data['property_type'],
        form_data=report_data['form_data'],
        template_config=template_config
    )
    
    # Return PDF
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{report_id}.pdf"
        }
    )

@app.get("/api/pdf-templates/{bank_code}/{property_type}")
async def get_pdf_template_config(bank_code: str, property_type: str):
    """Get PDF template configuration for customization"""
    pass

@app.put("/api/pdf-templates/{bank_code}/{property_type}")
async def save_pdf_template_config(bank_code: str, property_type: str, config: Dict):
    """Save customized PDF template configuration"""
    pass
```

### **Phase 2: UI Template Builder**

#### **2.1 PDF Template Manager Component**

```typescript
// valuation-frontend/src/app/components/pdf-template-manager/

@Component({
  selector: 'app-pdf-template-manager',
  templateUrl: './pdf-template-manager.component.html',
  styleUrls: ['./pdf-template-manager.component.css']
})
export class PdfTemplateManagerComponent {
  
  selectedBank: string = '';
  selectedPropertyType: string = '';
  templateConfig: PdfTemplateConfig = {};
  previewUrl: string = '';
  
  // Template customization options
  layoutOptions = {
    pageSize: 'A4',
    orientation: 'portrait',
    margins: { top: 20, right: 20, bottom: 20, left: 20 },
    headerHeight: 80,
    footerHeight: 40
  };
  
  sectionConfig = {
    sections: [
      { id: 'header', name: 'Header', enabled: true, fields: [] },
      { id: 'property_details', name: 'Property Details', enabled: true, fields: [] },
      { id: 'valuation_summary', name: 'Valuation Summary', enabled: true, fields: [] },
      { id: 'calculations', name: 'Calculations', enabled: true, fields: [] },
      { id: 'footer', name: 'Footer', enabled: true, fields: [] }
    ]
  };
  
  async loadTemplateConfig() {
    const config = await this.pdfService.getTemplateConfig(
      this.selectedBank, 
      this.selectedPropertyType
    );
    this.templateConfig = config;
  }
  
  async saveTemplate() {
    await this.pdfService.saveTemplateConfig(
      this.selectedBank,
      this.selectedPropertyType, 
      this.templateConfig
    );
  }
  
  async generatePreview() {
    // Generate preview with sample data
    const sampleData = this.generateSampleData();
    this.previewUrl = await this.pdfService.generatePreview(
      this.selectedBank,
      this.selectedPropertyType,
      sampleData,
      this.templateConfig
    );
  }
}
```

#### **2.2 Drag-and-Drop Field Manager**

```html
<!-- PDF Template Builder UI -->
<div class="pdf-template-builder">
  
  <!-- Bank & Template Selection -->
  <div class="template-selector">
    <select [(ngModel)]="selectedBank" (change)="loadTemplateConfig()">
      <option value="SBI">State Bank of India</option>
      <option value="HDFC">HDFC Bank</option>
      <!-- ... other banks -->
    </select>
    
    <select [(ngModel)]="selectedPropertyType" (change)="loadTemplateConfig()">
      <option value="LAND_PROPERTY">Land Property</option>
      <option value="APARTMENT">Apartment</option>
      <!-- ... other property types -->
    </select>
  </div>
  
  <!-- Layout Configuration -->
  <div class="layout-config">
    <h3>Layout Settings</h3>
    
    <div class="form-row">
      <label>Page Size:</label>
      <select [(ngModel)]="layoutOptions.pageSize">
        <option value="A4">A4</option>
        <option value="Letter">Letter</option>
      </select>
      
      <label>Orientation:</label>
      <select [(ngModel)]="layoutOptions.orientation">
        <option value="portrait">Portrait</option>
        <option value="landscape">Landscape</option>
      </select>
    </div>
    
    <!-- Margin controls -->
    <div class="margins-config">
      <h4>Margins (mm)</h4>
      <input type="number" [(ngModel)]="layoutOptions.margins.top" placeholder="Top">
      <input type="number" [(ngModel)]="layoutOptions.margins.right" placeholder="Right">
      <input type="number" [(ngModel)]="layoutOptions.margins.bottom" placeholder="Bottom">
      <input type="number" [(ngModel)]="layoutOptions.margins.left" placeholder="Left">
    </div>
  </div>
  
  <!-- Section Manager -->
  <div class="sections-manager">
    <h3>Report Sections</h3>
    
    <div 
      *ngFor="let section of sectionConfig.sections; trackBy: trackByFn" 
      class="section-item"
      [class.enabled]="section.enabled">
      
      <div class="section-header">
        <input type="checkbox" [(ngModel)]="section.enabled">
        <span class="section-name">{{ section.name }}</span>
        <button class="configure-btn" (click)="configureSection(section)">
          Configure
        </button>
      </div>
      
      <!-- Field Configuration -->
      <div class="field-config" *ngIf="section.enabled">
        <div 
          *ngFor="let field of section.fields" 
          class="field-item"
          cdkDrag>
          
          <span class="field-label">{{ field.label }}</span>
          <div class="field-controls">
            <input type="checkbox" [(ngModel)]="field.visible" title="Visible">
            <input type="number" [(ngModel)]="field.fontSize" placeholder="Font Size">
            <select [(ngModel)]="field.alignment">
              <option value="left">Left</option>
              <option value="center">Center</option>
              <option value="right">Right</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Preview Panel -->
  <div class="preview-panel">
    <h3>PDF Preview</h3>
    <button (click)="generatePreview()" class="preview-btn">Generate Preview</button>
    
    <div class="pdf-preview" *ngIf="previewUrl">
      <iframe [src]="previewUrl" width="100%" height="600px"></iframe>
    </div>
  </div>
  
  <!-- Action Buttons -->
  <div class="template-actions">
    <button (click)="saveTemplate()" class="save-btn">Save Template</button>
    <button (click)="resetTemplate()" class="reset-btn">Reset to Default</button>
    <button (click)="exportTemplate()" class="export-btn">Export Template</button>
  </div>
  
</div>
```

### **Phase 3: Template System Architecture**

#### **3.1 Database Schema for PDF Templates**

```javascript
// MongoDB Collection: valuation_admin.pdf_templates
{
  "_id": ObjectId("..."),
  "bankCode": "SBI",
  "propertyType": "LAND_PROPERTY", 
  "templateName": "SBI Land Property Valuation Report",
  "version": "1.0",
  "layout": {
    "pageSize": "A4",
    "orientation": "portrait", 
    "margins": { "top": 20, "right": 20, "bottom": 20, "left": 20 },
    "headerHeight": 80,
    "footerHeight": 40
  },
  "branding": {
    "logo": "data:image/png;base64,...",
    "primaryColor": "#1e40af",
    "secondaryColor": "#64748b", 
    "fontFamily": "Arial, sans-serif"
  },
  "sections": [
    {
      "id": "header",
      "name": "Report Header",
      "enabled": true,
      "position": { "x": 0, "y": 0, "width": "100%", "height": "80px" },
      "content": {
        "template": "<div class='header'>...</div>",
        "fields": [
          {
            "fieldId": "report_reference_number",
            "label": "Report Reference", 
            "position": { "x": "10mm", "y": "10mm" },
            "style": { "fontSize": "12pt", "fontWeight": "bold" }
          }
        ]
      }
    },
    {
      "id": "property_details", 
      "name": "Property Details",
      "enabled": true,
      "fields": [
        {
          "fieldId": "property_address",
          "label": "Property Address",
          "visible": true,
          "formatting": {
            "fontSize": 12,
            "alignment": "left",
            "fontWeight": "normal"
          }
        },
        {
          "fieldId": "total_extent_plot", 
          "label": "Plot Area",
          "visible": true,
          "formatting": {
            "fontSize": 12,
            "alignment": "right",
            "suffix": " sq.ft"
          }
        }
      ]
    },
    {
      "id": "valuation_summary",
      "name": "Valuation Summary", 
      "enabled": true,
      "fields": [
        {
          "fieldId": "estimated_land_value",
          "label": "Estimated Land Value",
          "visible": true,
          "formatting": {
            "fontSize": 14,
            "fontWeight": "bold",
            "alignment": "right",
            "type": "currency"
          }
        }
      ]
    }
  ],
  "createdAt": ISODate("2025-12-31T19:00:00Z"),
  "updatedAt": ISODate("2025-12-31T19:00:00Z"),
  "createdBy": "admin",
  "isActive": true
}
```

#### **3.2 HTML Template Structure**

```html
<!-- templates/pdf/sbi_land_property.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ bank_info.name }} - Property Valuation Report</title>
    <style>
        @page {
            size: {{ config.layout.pageSize }};
            margin: {{ config.layout.margins.top }}mm {{ config.layout.margins.right }}mm 
                   {{ config.layout.margins.bottom }}mm {{ config.layout.margins.left }}mm;
            @top-center {
                content: "{{ bank_info.name }} - Property Valuation Report";
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: {{ config.branding.fontFamily }};
            line-height: 1.6;
            color: #333;
        }
        
        .header {
            background-color: {{ config.branding.primaryColor }};
            color: white;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .field-section {
            margin-bottom: 15px;
        }
        
        .field-label {
            font-weight: bold;
            color: {{ config.branding.secondaryColor }};
        }
        
        .field-value {
            margin-left: 10px;
        }
        
        .currency {
            text-align: right;
            font-weight: bold;
        }
        
        /* Bank-specific styling */
        .sbi-branding {
            border-left: 4px solid #1e40af;
            padding-left: 15px;
        }
    </style>
</head>
<body>
    
    <!-- Dynamic Header Section -->
    {% if config.sections.header.enabled %}
    <div class="header sbi-branding">
        <h1>{{ bank_info.fullName }}</h1>
        <h2>Property Valuation Report</h2>
        <div class="report-ref">
            <strong>Report Reference:</strong> {{ report_data.reference_number }}
        </div>
    </div>
    {% endif %}
    
    <!-- Property Details Section -->
    {% if config.sections.property_details.enabled %}
    <div class="section property-details">
        <h3>Property Details</h3>
        
        {% for field in config.sections.property_details.fields %}
            {% if field.visible and report_data[field.fieldId] %}
            <div class="field-section">
                <span class="field-label">{{ field.label }}:</span>
                <span class="field-value">
                    {{ report_data[field.fieldId] }}
                    {{ field.formatting.suffix if field.formatting.suffix }}
                </span>
            </div>
            {% endif %}
        {% endfor %}
    </div>
    {% endif %}
    
    <!-- Valuation Summary Section -->
    {% if config.sections.valuation_summary.enabled %}
    <div class="section valuation-summary">
        <h3>Valuation Summary</h3>
        
        <table class="summary-table">
            {% for field in config.sections.valuation_summary.fields %}
                {% if field.visible and report_data[field.fieldId] %}
                <tr>
                    <td class="field-label">{{ field.label }}</td>
                    <td class="field-value {% if field.formatting.type == 'currency' %}currency{% endif %}">
                        {% if field.formatting.type == 'currency' %}
                            ₹{{ "{:,.2f}".format(report_data[field.fieldId]) }}
                        {% else %}
                            {{ report_data[field.fieldId] }}
                        {% endif %}
                    </td>
                </tr>
                {% endif %}
            {% endfor %}
        </table>
    </div>
    {% endif %}
    
    <!-- Footer -->
    <div class="footer">
        <p>Generated on: {{ report_data.generated_at }}</p>
        <p>Valuation conducted in accordance with {{ bank_info.name }} guidelines</p>
    </div>
    
</body>
</html>
```

### **Phase 4: Integration with Existing System**

#### **4.1 Add PDF Generation to Report Form**

```typescript
// Add to report-form.component.ts

async generatePDF() {
  this.isGeneratingPdf = true;
  
  try {
    const reportId = this.reportId;
    
    // Generate PDF
    const pdfBlob = await this.pdfService.generateReportPdf(reportId);
    
    // Download PDF
    const url = window.URL.createObjectURL(pdfBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report_${reportId}_${new Date().toISOString().split('T')[0]}.pdf`;
    link.click();
    
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('PDF generation failed:', error);
    // Show error message
  } finally {
    this.isGeneratingPdf = false;
  }
}
```

#### **4.2 PDF Service**

```typescript
// valuation-frontend/src/app/services/pdf.service.ts

@Injectable({
  providedIn: 'root'
})
export class PdfService {
  
  constructor(private http: HttpClient) {}
  
  async generateReportPdf(reportId: string, customTemplate?: any): Promise<Blob> {
    const url = `${this.API_BASE_URL}/reports/${reportId}/generate-pdf`;
    
    return this.http.post(url, { template_config: customTemplate }, {
      responseType: 'blob'
    }).toPromise();
  }
  
  async getTemplateConfig(bankCode: string, propertyType: string) {
    const url = `${this.API_BASE_URL}/pdf-templates/${bankCode}/${propertyType}`;
    return this.http.get(url).toPromise();
  }
  
  async saveTemplateConfig(bankCode: string, propertyType: string, config: any) {
    const url = `${this.API_BASE_URL}/pdf-templates/${bankCode}/${propertyType}`;
    return this.http.put(url, config).toPromise();
  }
}
```

## 📋 **Implementation Roadmap**

### **Phase 1 (Week 1-2): Core PDF Generation**
- ✅ Install WeasyPrint: `pip install weasyprint`
- ✅ Create PDFGenerator service
- ✅ Add API endpoints for PDF generation
- ✅ Create basic HTML templates for SBI Land Property

### **Phase 2 (Week 3-4): Template System**
- ✅ Design MongoDB schema for PDF templates
- ✅ Create template configuration API
- ✅ Build basic template manager UI
- ✅ Add PDF preview functionality

### **Phase 3 (Week 5-6): Advanced Customization**
- ✅ Drag-and-drop field positioning
- ✅ Visual styling controls
- ✅ Multiple template versions
- ✅ Template import/export

### **Phase 4 (Week 7-8): Bank-Specific Templates**
- ✅ Create templates for all supported banks
- ✅ Bank branding integration (logos, colors)
- ✅ Compliance-specific formatting
- ✅ Multi-language support

## 🎨 **Customization Features Available**

### **Template Builder UI Features**:
1. **Visual Layout Designer**: Drag-and-drop field positioning
2. **Styling Controls**: Fonts, colors, spacing, alignment
3. **Section Management**: Enable/disable report sections
4. **Field Configuration**: Show/hide, formatting, calculations
5. **Preview System**: Real-time PDF preview
6. **Template Versioning**: Save multiple versions per bank
7. **Export/Import**: Template sharing between environments

### **Bank-Specific Customizations**:
1. **Branding**: Bank logos, color schemes, fonts
2. **Layout**: Page orientation, margins, section ordering
3. **Content**: Required fields, calculations, disclaimers
4. **Compliance**: Regulatory requirements per bank
5. **Signatures**: Digital signature placement
6. **Watermarks**: Draft/Final status indicators

This comprehensive solution provides maximum flexibility while maintaining ease of use for non-technical users to customize PDF templates through the UI.