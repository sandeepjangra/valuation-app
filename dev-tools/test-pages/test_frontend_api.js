// Test script to simulate frontend API calls
const https = require('http');
const URL = require('url');

console.log('🔍 Testing Frontend API Call Simulation');
console.log('=====================================');

const apiUrl = 'http://localhost:8000/api/common-fields';
const startTime = Date.now();

const urlObj = new URL.URL(apiUrl);

const options = {
  hostname: urlObj.hostname,
  port: urlObj.port,
  path: urlObj.pathname + urlObj.search,
  method: 'GET',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Frontend-Test-Script'
  }
};

console.log('📡 Making API request to:', apiUrl);
console.log('⏱️  Start time:', startTime);

const req = https.request(options, (res) => {
  const responseTime = Date.now();
  console.log('📊 Status Code:', res.statusCode);
  console.log('⏱️  First response in:', (responseTime - startTime), 'ms');
  
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
    const chunkTime = Date.now();
    console.log('📦 Received chunk of', chunk.length, 'bytes at', (chunkTime - startTime), 'ms');
  });
  
  res.on('end', () => {
    const endTime = Date.now();
    console.log('⏱️  Total request time:', (endTime - startTime), 'ms');
    console.log('📏 Total data size:', data.length, 'bytes');
    
    try {
      const fields = JSON.parse(data);
      console.log('✅ Successfully parsed JSON with', fields.length, 'fields');
      console.log('🏗️  Field types:', fields.map(f => f.fieldType).join(', '));
    } catch (error) {
      console.error('❌ JSON parsing error:', error.message);
    }
  });
});

req.on('error', (error) => {
  const errorTime = Date.now();
  console.error('❌ Request error at', (errorTime - startTime), 'ms:', error.message);
});

req.setTimeout(10000, () => {
  console.error('⏰ Request timeout after 10 seconds');
  req.destroy();
});

req.end();