// Test frontend processing logic
const http = require('http');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/api/templates/SBI/land-property/aggregated-fields',
  method: 'GET'
};

const req = http.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    try {
      const response = JSON.parse(data);
      
      console.log('🔍 TESTING FRONTEND PROCESSING');
      console.log('='.repeat(50));
      
      // Simulate the groupFieldsByGroup logic
      const commonFields = response.commonFields || [];
      console.log('Input commonFields:', commonFields.length);
      
      // Group fields by their fieldGroup property 
      const groupMap = new Map();
      
      commonFields.forEach(field => {
        const groupName = field.fieldGroup || 'default';
        console.log('Field:', field.id, '-> Group:', groupName);
        if (!groupMap.has(groupName)) {
          groupMap.set(groupName, []);
        }
        groupMap.get(groupName).push(field);
      });
      
      // Convert to array
      const fieldGroups = [];
      groupMap.forEach((groupFields, groupName) => {
        fieldGroups.push({
          groupName,
          fields: groupFields.sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
        });
      });
      
      console.log('\n✅ RESULT:');
      console.log('Field groups created:', fieldGroups.length);
      fieldGroups.forEach(group => {
        console.log('- Group "' + group.groupName + '": ' + group.fields.length + ' fields');
      });
      
      console.log('\nhasCommonFields() would return:', fieldGroups.length > 0);
      
    } catch (error) {
      console.error('❌ Error parsing response:', error.message);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request failed:', error.message);
});

req.end();