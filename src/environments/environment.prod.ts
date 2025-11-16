export const environment = {
  production: true,
  apiUrl: 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod',
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