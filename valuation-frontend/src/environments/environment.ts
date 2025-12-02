export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  templateVersioningApiUrl: 'http://localhost:8000',
  developmentMode: true,
  amplify: {
    Auth: {
      region: 'us-east-1',
      userPoolId: 'us-east-1_XXXXXXXXX',
      userPoolWebClientId: 'XXXXXXXXXXXXXXXXXXXXXXXXXX',
    },
    Storage: {
      AWSS3: {
        bucket: 'valuationapp-storage-XXXXXXXXX',
        region: 'us-east-1',
      }
    }
  },
  // Development tokens for testing
  devTokens: {
    systemAdmin: 'dev_admin_system.com_system_admin_system_admin',
    manager: 'dev_manager_demo.com_demo_org_001_manager',
    employee: 'dev_employee_demo.com_demo_org_001_employee'
  }
};