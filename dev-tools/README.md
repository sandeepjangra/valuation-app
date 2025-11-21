# Development Tools

This directory contains development and testing utilities.

## Directory Structure

### `/test-scripts`
Python test scripts for development and debugging:
- Database connection tests
- API endpoint tests
- Data validation tests
- Collection structure checks

**Usage:** Run these scripts during development to verify functionality.

### `/test-pages`
HTML/JS test pages for frontend testing:
- API integration tests
- UI component tests
- Frontend logging tests

**Usage:** Open these files in a browser while servers are running to test features.

### `/debug`
One-time debug and fix scripts:
- Database migration scripts
- Data cleanup scripts
- Template upload scripts
- Collection recreation scripts

**Note:** These are historical scripts kept for reference. Most are one-time use only.

### `/data-samples`
Sample data files and templates:
- JSON sample data
- Bank templates
- Test data sets

**Usage:** Use these as reference or for testing data imports.

## Important Notes

- Test scripts require backend server to be running
- Always use a development database, never production
- Check script comments before running
- Some scripts may modify database - use with caution
