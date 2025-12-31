#!/usr/bin/env python3
"""
PDF Generation Service for Valuation Reports
Fallback implementation using ReportLab when WeasyPrint is not available
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import json
from datetime import datetime
from typing import Dict, Any, Optional
import io

# PDF Generation Libraries with fallback
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint loaded successfully")
except ImportError as e:
    print(f"⚠️ WeasyPrint not available: {e}")
    WEASYPRINT_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
    print("✅ ReportLab available as fallback")
except ImportError:
    print("⚠️ ReportLab also not available")
    REPORTLAB_AVAILABLE = False

router = APIRouter()

class PDFGenerator:
    def __init__(self):
        self.templates = {
            'SBI': {
                'LAND_PROPERTY': 'sbi_land_template'
            }
        }

    def generate_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF from report data using available PDF library
        """
        bank_code = report_data.get('bankCode', '').upper()
        property_type = report_data.get('propertyType', '').upper()
        
        if WEASYPRINT_AVAILABLE:
            return self._generate_with_weasyprint(report_data)
        elif REPORTLAB_AVAILABLE:
            return self._generate_with_reportlab(report_data)
        else:
            raise HTTPException(status_code=500, detail="No PDF generation library available")

    def _generate_with_reportlab(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF using ReportLab (fallback method)
        """
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Bank and report information
        bank_code = report_data.get('bankCode', 'Unknown Bank')
        property_type = report_data.get('propertyType', 'Property')
        report_ref = report_data.get('reportReferenceNumber', 'N/A')
        org_name = report_data.get('organizationShortName', 'Valuation Organization')
        
        # Title
        title_text = f"{bank_code} - {property_type.title()} Property Valuation Report"
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 20))
        
        # Report Information
        report_info = [
            ['Report Reference:', report_ref],
            ['Bank:', bank_code],
            ['Property Type:', property_type.title()],
            ['Organization:', org_name],
            ['Generated Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        info_table = Table(report_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Process template data and form values
        template_data = report_data.get('templateData', {})
        form_values = report_data.get('formValues', {})
        
        # Extract fields from template data
        if template_data and 'documents' in template_data:
            for document in template_data.get('documents', []):
                for section in document.get('sections', []):
                    section_title = section.get('title', 'Section')
                    story.append(Paragraph(section_title, heading_style))
                    story.append(Spacer(1, 10))
                    
                    # Create table for section fields
                    section_data = []
                    
                    for field in section.get('fields', []):
                        field_id = field.get('fieldId', '')
                        field_label = field.get('label', field_id)
                        
                        # Get value from form data or field default
                        field_value = (
                            form_values.get(field_id, '') or 
                            field.get('value', '') or 
                            field.get('defaultValue', 'N/A')
                        )
                        
                        section_data.append([field_label, str(field_value)])
                    
                    if section_data:
                        section_table = Table(section_data, colWidths=[3*inch, 3*inch])
                        section_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        story.append(section_table)
                        story.append(Spacer(1, 20))
        
        # Add any additional form values not in template
        other_fields = []
        template_field_ids = set()
        
        # Collect all template field IDs
        if template_data and 'documents' in template_data:
            for document in template_data.get('documents', []):
                for section in document.get('sections', []):
                    for field in section.get('fields', []):
                        template_field_ids.add(field.get('fieldId', ''))
        
        # Find form values not in template
        for field_id, value in form_values.items():
            if field_id not in template_field_ids and value:
                other_fields.append([field_id.replace('_', ' ').title(), str(value)])
        
        if other_fields:
            story.append(Paragraph("Additional Information", heading_style))
            story.append(Spacer(1, 10))
            
            other_table = Table(other_fields, colWidths=[3*inch, 3*inch])
            other_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(other_table)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated by {org_name} Valuation System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, normal_style))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def _generate_with_weasyprint(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF using WeasyPrint (preferred method)
        """
        # This would use the original WeasyPrint implementation
        # For now, falling back to ReportLab
        return self._generate_with_reportlab(report_data)

    def get_available_templates(self) -> Dict[str, Any]:
        """
        Get list of available PDF templates
        """
        return {
            "templates": [
                {
                    "bank": "SBI",
                    "propertyType": "land",
                    "templateName": "SBI Land Property Valuation",
                    "available": True,
                    "generatorUsed": "WeasyPrint" if WEASYPRINT_AVAILABLE else "ReportLab"
                }
            ],
            "capabilities": {
                "weasyprint": WEASYPRINT_AVAILABLE,
                "reportlab": REPORTLAB_AVAILABLE,
                "currentGenerator": "WeasyPrint" if WEASYPRINT_AVAILABLE else "ReportLab"
            }
        }

# Create global instance
pdf_generator = PDFGenerator()