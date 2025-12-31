#!/usr/bin/env python3
"""
PDF Generation Service for Valuation Reports
Basic implementation to get started with SBI Land Property reports
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import json
from datetime import datetime
from typing import Dict, Any, Optional
import io

# For now, we'll use a simple HTML-to-PDF approach
# Later can be enhanced with WeasyPrint for better styling
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("⚠️ WeasyPrint not installed. Using basic PDF generation.")

router = APIRouter()

class PDFGenerator:
    def __init__(self):
        self.templates = {
            'SBI': {
                'LAND_PROPERTY': self.get_sbi_land_template()
            }
        }
    
    def get_sbi_land_template(self) -> str:
        """SBI Land Property PDF Template"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>State Bank of India - Land Property Valuation Report</title>
            <style>
                @page {
                    size: A4;
                    margin: 20mm;
                    @top-center {
                        content: "State Bank of India - Property Valuation Report";
                        font-size: 10pt;
                        color: #666;
                    }
                    @bottom-center {
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 8pt;
                        color: #666;
                    }
                }
                
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }
                
                .header {
                    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                    color: white;
                    padding: 25px;
                    margin-bottom: 25px;
                    border-radius: 8px;
                }
                
                .header h1 {
                    margin: 0 0 10px 0;
                    font-size: 24px;
                    font-weight: bold;
                }
                
                .header h2 {
                    margin: 0 0 15px 0;
                    font-size: 18px;
                    font-weight: normal;
                }
                
                .report-info {
                    display: flex;
                    justify-content: space-between;
                    background: rgba(255, 255, 255, 0.2);
                    padding: 15px;
                    border-radius: 5px;
                }
                
                .section {
                    margin-bottom: 25px;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 20px;
                }
                
                .section h3 {
                    margin: 0 0 15px 0;
                    color: #1e40af;
                    font-size: 18px;
                    border-bottom: 2px solid #1e40af;
                    padding-bottom: 8px;
                }
                
                .field-row {
                    display: flex;
                    margin-bottom: 12px;
                    padding: 8px 0;
                    border-bottom: 1px dotted #d1d5db;
                }
                
                .field-label {
                    font-weight: bold;
                    width: 40%;
                    color: #374151;
                }
                
                .field-value {
                    width: 60%;
                    color: #111827;
                }
                
                .currency {
                    font-weight: bold;
                    color: #059669;
                    font-size: 16px;
                }
                
                .highlight {
                    background-color: #fef3c7;
                    padding: 15px;
                    border-left: 4px solid #f59e0b;
                    margin: 15px 0;
                }
                
                .calculation-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }
                
                .calculation-table th,
                .calculation-table td {
                    border: 1px solid #d1d5db;
                    padding: 10px;
                    text-align: left;
                }
                
                .calculation-table th {
                    background-color: #f3f4f6;
                    font-weight: bold;
                }
                
                .calculation-table .currency-cell {
                    text-align: right;
                    font-weight: bold;
                }
                
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #1e40af;
                    font-size: 12px;
                    color: #6b7280;
                }
                
                .signature-section {
                    margin-top: 30px;
                    display: flex;
                    justify-content: space-between;
                }
                
                .signature-box {
                    width: 200px;
                    text-align: center;
                }
                
                .signature-line {
                    border-top: 1px solid #374151;
                    margin-top: 50px;
                    padding-top: 5px;
                }
            </style>
        </head>
        <body>
            
            <!-- Header Section -->
            <div class="header">
                <h1>State Bank of India</h1>
                <h2>Land Property Valuation Report</h2>
                <div class="report-info">
                    <div>
                        <strong>Report Reference:</strong> {report_reference_number}
                    </div>
                    <div>
                        <strong>Date:</strong> {report_date}
                    </div>
                </div>
            </div>
            
            <!-- Property Details Section -->
            <div class="section">
                <h3>Property Details</h3>
                
                <div class="field-row">
                    <div class="field-label">Property Address:</div>
                    <div class="field-value">{property_address}</div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Survey Number:</div>
                    <div class="field-value">{survey_number}</div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Village:</div>
                    <div class="field-value">{village}</div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Taluka:</div>
                    <div class="field-value">{taluka}</div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">District:</div>
                    <div class="field-value">{district}</div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Total Extent of Plot:</div>
                    <div class="field-value">{total_extent_plot} sq.ft</div>
                </div>
            </div>
            
            <!-- Valuation Details Section -->
            <div class="section">
                <h3>Valuation Assessment</h3>
                
                <table class="calculation-table">
                    <tr>
                        <th>Description</th>
                        <th>Area (sq.ft)</th>
                        <th>Rate per sq.ft</th>
                        <th>Value (₹)</th>
                    </tr>
                    <tr>
                        <td>Land Valuation</td>
                        <td>{total_extent_plot}</td>
                        <td class="currency-cell">₹{valuation_rate}</td>
                        <td class="currency-cell">₹{estimated_land_value}</td>
                    </tr>
                </table>
            </div>
            
            <!-- Summary Section -->
            <div class="section">
                <h3>Valuation Summary</h3>
                
                <div class="highlight">
                    <div class="field-row">
                        <div class="field-label">Total Estimated Land Value:</div>
                        <div class="field-value currency">₹{estimated_land_value}</div>
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Valuation Method:</div>
                    <div class="field-value">Market Comparison Approach</div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Valuation Date:</div>
                    <div class="field-value">{report_date}</div>
                </div>
            </div>
            
            <!-- Signature Section -->
            <div class="signature-section">
                <div class="signature-box">
                    <div class="signature-line">
                        <strong>Valuation Officer</strong><br>
                        State Bank of India
                    </div>
                </div>
                
                <div class="signature-box">
                    <div class="signature-line">
                        <strong>Branch Manager</strong><br>
                        State Bank of India
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p><strong>Note:</strong> This valuation report is prepared for the specific purpose of loan processing and is valid for 6 months from the date of issue.</p>
                <p>Generated on: {generated_at} | Report ID: {report_id}</p>
                <p>© 2025 State Bank of India. All rights reserved.</p>
            </div>
            
        </body>
        </html>
        '''
    
    def generate_pdf(self, bank_code: str, property_type: str, form_data: Dict[str, Any]) -> bytes:
        """Generate PDF from form data"""
        
        # Get template
        template_key = f"{bank_code}_{property_type}"
        if bank_code not in self.templates or property_type not in self.templates[bank_code]:
            raise HTTPException(status_code=404, detail=f"Template not found for {template_key}")
        
        html_template = self.templates[bank_code][property_type]
        
        # Prepare data for template
        template_data = self.prepare_template_data(form_data)
        
        # Replace placeholders in template
        rendered_html = self.render_template(html_template, template_data)
        
        # Generate PDF
        if WEASYPRINT_AVAILABLE:
            # Use WeasyPrint for high-quality PDF
            pdf_bytes = weasyprint.HTML(string=rendered_html).write_pdf()
        else:
            # Fallback: create a simple text-based response
            pdf_bytes = self.create_simple_pdf(rendered_html, template_data)
        
        return pdf_bytes
    
    def prepare_template_data(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare and format data for template rendering"""
        
        # Extract and format values
        data = {
            'report_reference_number': form_data.get('reference_number', 'N/A'),
            'report_date': datetime.now().strftime('%d %B %Y'),
            'generated_at': datetime.now().strftime('%d %B %Y at %I:%M %p'),
            'report_id': form_data.get('_id', 'N/A'),
            
            # Property details
            'property_address': form_data.get('property_address', 'N/A'),
            'survey_number': form_data.get('survey_number', 'N/A'),
            'village': form_data.get('village', 'N/A'),
            'taluka': form_data.get('taluka', 'N/A'),
            'district': form_data.get('district', 'N/A'),
            'total_extent_plot': self.format_number(form_data.get('total_extent_plot', 0)),
            
            # Valuation details
            'valuation_rate': self.format_currency(form_data.get('valuation_rate', 0)),
            'estimated_land_value': self.format_currency(form_data.get('estimated_land_value', 0)),
        }
        
        return data
    
    def render_template(self, template: str, data: Dict[str, str]) -> str:
        """Replace placeholders in template with actual data"""
        rendered = template
        for key, value in data.items():
            placeholder = '{' + key + '}'
            rendered = rendered.replace(placeholder, str(value))
        return rendered
    
    def format_currency(self, value: Any) -> str:
        """Format number as Indian currency"""
        try:
            num_value = float(value) if value else 0
            return f"{num_value:,.2f}"
        except (ValueError, TypeError):
            return "0.00"
    
    def format_number(self, value: Any) -> str:
        """Format number with commas"""
        try:
            num_value = float(value) if value else 0
            return f"{num_value:,.0f}"
        except (ValueError, TypeError):
            return "0"
    
    def create_simple_pdf(self, html_content: str, data: Dict[str, str]) -> bytes:
        """Fallback method when WeasyPrint is not available"""
        # Create a simple text-based PDF content
        simple_content = f"""
PDF Generation Available!

State Bank of India - Land Property Valuation Report
==================================================

Report Reference: {data.get('report_reference_number')}
Date: {data.get('report_date')}

Property Details:
- Address: {data.get('property_address')}
- Survey Number: {data.get('survey_number')}
- Village: {data.get('village')}
- Total Area: {data.get('total_extent_plot')} sq.ft

Valuation:
- Rate per sq.ft: ₹{data.get('valuation_rate')}
- Total Land Value: ₹{data.get('estimated_land_value')}

Generated: {data.get('generated_at')}

Note: Install WeasyPrint for full PDF generation with styling.
pip install weasyprint
        """
        
        return simple_content.encode('utf-8')

# Initialize PDF generator
pdf_generator = PDFGenerator()

@router.post("/reports/{report_id}/generate-pdf")
async def generate_report_pdf(report_id: str):
    """Generate PDF for a specific report"""
    
    try:
        # For demo purposes, using sample data
        # In production, you would fetch actual report data from database
        sample_form_data = {
            '_id': report_id,
            'reference_number': f'SBI-LP-{report_id[:8].upper()}',
            'property_address': '123 Sample Street, Sample Area, Sample City',
            'survey_number': '123/4A',
            'village': 'Sample Village',
            'taluka': 'Sample Taluka',  
            'district': 'Sample District',
            'total_extent_plot': 2400,
            'valuation_rate': 5000,
            'estimated_land_value': 12000000
        }
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_pdf('SBI', 'LAND_PROPERTY', sample_form_data)
        
        # Return PDF response
        if WEASYPRINT_AVAILABLE:
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=SBI_Land_Report_{report_id}.pdf"
                }
            )
        else:
            # Return text response when WeasyPrint not available
            return Response(
                content=pdf_bytes,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename=SBI_Land_Report_{report_id}.txt"
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/pdf-templates/{bank_code}/{property_type}")
async def get_pdf_template_info(bank_code: str, property_type: str):
    """Get available PDF template information"""
    
    templates_info = {
        'SBI': {
            'LAND_PROPERTY': {
                'name': 'State Bank of India - Land Property Valuation',
                'description': 'Comprehensive land property valuation report with SBI branding',
                'sections': ['Header', 'Property Details', 'Valuation Assessment', 'Summary', 'Signatures'],
                'customizable': True,
                'available': True
            }
        }
    }
    
    if bank_code in templates_info and property_type in templates_info[bank_code]:
        return templates_info[bank_code][property_type]
    else:
        return {
            'available': False,
            'message': f'Template for {bank_code} {property_type} not yet available'
        }

# Add to main.py
# Include the PDF router in your main FastAPI app:
# app.include_router(router, prefix="/api", tags=["PDF Generation"])