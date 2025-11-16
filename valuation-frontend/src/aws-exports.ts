const awsmobile = {
  "aws_project_region": "us-east-1",
  "aws_cognito_identity_pool_id": "us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "aws_cognito_region": "us-east-1",
  "aws_user_pools_id": "us-east-1_XXXXXXXXX",
  "aws_user_pools_web_client_id": "XXXXXXXXXXXXXXXXXXXXXXXXXX",
  "oauth": {},
  "aws_cognito_username_attributes": ["EMAIL"],
  "aws_cognito_social_providers": [],
  "aws_cognito_signup_attributes": ["EMAIL"],
  "aws_cognito_mfa_configuration": "OFF",
  "aws_cognito_mfa_types": ["SMS"],
  "aws_cognito_password_protection_settings": {
    "passwordPolicyMinLength": 8,
    "passwordPolicyCharacters": []
  },
  "aws_cognito_verification_mechanisms": ["EMAIL"],
  "aws_appsync_graphqlEndpoint": "https://XXXXXXXXXXXXXXXXXXXXXXXXXX.appsync-api.us-east-1.amazonaws.com/graphql",
  "aws_appsync_region": "us-east-1",
  "aws_appsync_authenticationType": "AMAZON_COGNITO_USER_POOLS",
  "aws_user_files_s3_bucket": "valuationapp-storage-XXXXXXXXX",
  "aws_user_files_s3_bucket_region": "us-east-1"
};

export default awsmobile;