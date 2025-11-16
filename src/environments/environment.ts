export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',  // Your local Python backend
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