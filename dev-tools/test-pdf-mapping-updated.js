/**
 * Test script to verify updated PDF field mapping logic with camelCase conversion
 */

// Simulate extracted PDF fields (as they would come from backend)
const extractedPdfFields = {
  "applicantName": "John Doe", 
  "propertyAddress": "123 Main Street",
  "inspectionDate": "2025-12-05",
  "valuationDate": "2025-12-05",
  "marketValue": "150000"
};

// Simulate form controls (as they would exist in Angular form)
const availableControls = [
  "applicant_name",
  "property_address", 
  "inspection_date",
  "valuation_date",
  "market_value",
  "report_reference_number",
  "other_field"
];

console.log('🧪 Testing Updated PDF Field Mapping Logic');
console.log('==========================================');
console.log('📄 PDF Fields:', extractedPdfFields);
console.log('🎛️ Form Controls:', availableControls);
console.log('');

let appliedCount = 0;

// Test the updated mapping logic (same as in applyExtractedPdfFields method)
Object.keys(extractedPdfFields).forEach(pdfFieldKey => {
  const pdfValue = extractedPdfFields[pdfFieldKey];
  let matchingControl;
  
  // Strategy 1: Direct case-insensitive match
  matchingControl = availableControls.find(controlKey => 
    controlKey.toLowerCase() === pdfFieldKey.toLowerCase()
  );
  
  // Strategy 2: Convert camelCase to snake_case and match
  if (!matchingControl) {
    const snakeCaseKey = pdfFieldKey.replace(/([A-Z])/g, '_$1').toLowerCase();
    matchingControl = availableControls.find(controlKey => 
      controlKey.toLowerCase() === snakeCaseKey
    );
    if (matchingControl) {
      console.log(`🔄 Mapped camelCase to snake_case: ${pdfFieldKey} -> ${snakeCaseKey} -> ${matchingControl}`);
    }
  }
  
  // Strategy 3: Remove underscores and match
  if (!matchingControl) {
    const noUnderscoreKey = pdfFieldKey.replace(/_/g, '');
    matchingControl = availableControls.find(controlKey => 
      controlKey.replace(/_/g, '').toLowerCase() === noUnderscoreKey.toLowerCase()
    );
    if (matchingControl) {
      console.log(`🔄 Mapped by removing underscores: ${pdfFieldKey} -> ${matchingControl}`);
    }
  }
  
  if (matchingControl && pdfValue !== null && pdfValue !== undefined && pdfValue !== '') {
    appliedCount++;
    console.log(`✅ Applied PDF field: ${pdfFieldKey} -> ${matchingControl} = "${pdfValue}"`);
  } else {
    console.log(`❌ No matching form control found for PDF field: ${pdfFieldKey}`);
  }
});

console.log('');
console.log(`📊 Result: Applied ${appliedCount} of ${Object.keys(extractedPdfFields).length} PDF fields`);
console.log(appliedCount === Object.keys(extractedPdfFields).length ? '🎉 SUCCESS: All PDF fields mapped!' : '⚠️  Some fields could not be mapped');