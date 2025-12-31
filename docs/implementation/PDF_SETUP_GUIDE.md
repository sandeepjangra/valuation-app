# PDF Generation System - Quick Setup and Test Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install WeasyPrint (if not already installed)
pip install weasyprint==61.2

# Or install all requirements
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
cd backend
python main.py
```

The server should start on http://localhost:8000

### 3. Test PDF Generation

```bash
# Run the test script
python test_pdf_generation.py
```

This will:
- Check backend health
- List available PDF templates
- Generate a test PDF file
- Save it as `test_sbi_land_valuation_[timestamp].pdf`

### 4. Frontend Integration

1. Open the Angular frontend
2. Navigate to any existing report
3. Click the **📄 Generate PDF** button in the header
4. The PDF will automatically download

## 📋 Available Endpoints

- `GET /api/pdf-templates` - List all available PDF templates
- `GET /api/pdf-templates/{bank}/{propertyType}` - Get specific template info
- `POST /api/reports/{reportId}/generate-pdf` - Generate PDF for a report
- `GET /api/health` - Backend health check

## 🎨 PDF Templates

### Current Templates:
- **SBI Land Property Valuation** - Professional template with SBI branding
- Extensible architecture for additional bank templates

### Template Features:
- Bank-specific branding and logos
- Professional styling with proper spacing
- Dynamic field population from form data
- Calculated fields display
- Responsive layout

## 🛠️ Customization

### Adding New Bank Templates:
1. Edit `backend/pdf_generator.py`
2. Add new template in `get_template_html()` method
3. Follow the existing SBI template structure
4. Update the bank mapping in frontend

### Styling Customization:
- Modify CSS within the HTML templates
- Change colors, fonts, spacing as needed
- Add bank logos and branding elements

## 🔧 Troubleshooting

### Common Issues:

1. **WeasyPrint Installation Error**
   ```bash
   # On macOS
   brew install python-tk pango gdk-pixbuf libffi
   
   # On Ubuntu/Debian
   sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0
   ```

2. **PDF Generation Timeout**
   - Check backend logs
   - Verify template data is properly formatted
   - Ensure MongoDB connection is working

3. **Frontend Button Not Working**
   - Verify `reportId` is available
   - Check browser console for errors
   - Ensure backend server is running

### Debug Mode:
Set `DEBUG=True` in backend environment to get detailed error logs.

## 📊 Architecture

```
Frontend (Angular)
    ↓ PDF Request
Backend (FastAPI)
    ↓ Template Processing
PDF Generator (WeasyPrint)
    ↓ HTML to PDF
Download Response
```

## 🔄 Next Steps

1. **Test with Real Data**: Use actual report data instead of sample data
2. **Add More Templates**: Create templates for other banks (HDFC, ICICI, etc.)
3. **Enhanced Styling**: Add more sophisticated layouts and charts
4. **Template Builder**: Create UI for custom template creation
5. **Batch Processing**: Support multiple report PDF generation

## 📞 Support

If you encounter issues:
1. Check the test script output
2. Review backend logs
3. Verify all dependencies are installed
4. Ensure proper network connectivity between frontend and backend

---

**Generated PDF Features:**
- ✅ Bank branding and logos
- ✅ Professional styling
- ✅ Dynamic field population
- ✅ Calculated values
- ✅ Proper formatting
- ✅ Downloadable file naming