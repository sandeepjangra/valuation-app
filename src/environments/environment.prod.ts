export const environment = {
  production: true,
  apiUrl: 'https://your-backend-domain.com',  // Your deployed backend URL
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
  }
};