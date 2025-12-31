// Test script to run in browser console to test frontend authentication
// Open http://localhost:4200 and run this in the browser console

console.log('🧪 Testing Frontend Authentication');

// Test 1: Check if AuthService is available
if (typeof angular !== 'undefined') {
    console.log('✅ Angular is loaded');
} else {
    console.log('❌ Angular not found - this is likely an Angular standalone app');
}

// Test 2: Test dev login API call directly
async function testDevLogin() {
    console.log('🔐 Testing dev login API call...');
    
    try {
        const response = await fetch('http://localhost:8000/api/auth/dev-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: 'manager@test.com',
                organizationId: 'sk-tindwal',
                role: 'manager'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('✅ Dev login successful:', data);
            
            // Store token in localStorage
            localStorage.setItem('access_token', data.data.access_token);
            localStorage.setItem('current_user', JSON.stringify(data.data.user));
            
            console.log('💾 Token stored in localStorage');
            
            // Test template creation
            return testTemplateCreation(data.data.access_token);
        } else {
            console.error('❌ Dev login failed:', data);
            return false;
        }
    } catch (error) {
        console.error('❌ Dev login error:', error);
        return false;
    }
}

// Test 3: Test template creation with token
async function testTemplateCreation(token) {
    console.log('📝 Testing template creation...');
    
    const templateData = {
        templateName: `Browser Test Template ${new Date().getTime()}`,
        description: 'Test template created from browser console',
        bankCode: 'SBI',
        propertyType: 'land',
        fieldValues: {
            property_area: '1500 sq ft',
            property_value: '7000000',
            location: 'Browser Test Location'
        }
    };
    
    try {
        const response = await fetch('http://localhost:8000/api/custom-templates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(templateData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('✅ Template created successfully:', data);
            return true;
        } else {
            console.error('❌ Template creation failed:', response.status, data);
            return false;
        }
    } catch (error) {
        console.error('❌ Template creation error:', error);
        return false;
    }
}

// Test 4: Check current localStorage state
function checkAuthState() {
    console.log('🔍 Checking current auth state...');
    
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('current_user');
    
    console.log('Token:', token ? `${token.substring(0, 50)}...` : 'None');
    console.log('User:', user ? JSON.parse(user) : 'None');
    
    return { token, user };
}

// Run tests
console.log('🚀 Starting frontend authentication tests...');
console.log('Run these functions manually:');
console.log('1. checkAuthState() - Check current auth state');
console.log('2. testDevLogin() - Test dev login and template creation');

// Auto-run basic checks
checkAuthState();