# StratScout Quick Start Guide

Get StratScout up and running with real competitor data in 30 minutes.

## Prerequisites

- AWS Account with CLI configured
- Node.js 18+ and npm
- Python 3.12+
- Meta Developer account (free - see below)

## Step 1: Get Meta Ads API Access (10 minutes)

1. **Create Meta Developer Account**
   - Go to https://developers.facebook.com/
   - Click "Get Started" and log in with Facebook

2. **Create an App**
   - Go to https://developers.facebook.com/apps
   - Click "Create App" → Select "Business"
   - Name it "StratScout" and create

3. **Get Access Token**
   - In your app, go to Tools → Graph API Explorer
   - Select your app from dropdown
   - Click "Generate Access Token"
   - Copy the token

4. **Test Your Token**
   ```bash
   curl "https://graph.facebook.com/v18.0/ads_archive?access_token=YOUR_TOKEN&search_terms=Mamaearth&ad_reached_countries=IN&limit=5&fields=id,page_name"
   ```

See [META_ADS_SETUP.md](./META_ADS_SETUP.md) for detailed instructions.

## Step 2: Clone and Setup (5 minutes)

```bash
# Set your Meta access token
export META_ACCESS_TOKEN='your_token_here'

# Install infrastructure dependencies
cd infrastructure
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt

# Test Meta Ads API integration
cd ..
python3 scripts/test_meta_ads.py
```

You should see ads being fetched from Meta Ads Library!

## Step 3: Customize Competitors (2 minutes)

Edit `backend/data_ingestion/meta_ads/client.py`:

```python
self.default_competitors = [
    {
        'id': 'comp-brand1',
        'name': 'Your Brand Name',
        'search_terms': ['Brand Name', 'Brand Alternate'],
        'page_id': None,
    },
    # Add more brands...
]
```

Popular Indian skincare brands to track:
- Mamaearth
- Plum (search: "Plum Goodness")
- The Derma Co
- Minimalist (search: "Be Minimalist")
- Dot & Key
- mCaffeine
- Wow Skin Science

## Step 4: Deploy to AWS (10 minutes)

```bash
cd infrastructure

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy all stacks
cdk deploy --all

# Note the outputs - you'll need these
```

The deployment will create:
- DynamoDB tables for data storage
- Lambda functions for data collection and AI analysis
- API Gateway for frontend access
- S3 buckets for ad creatives
- Aurora Serverless for analytics
- CloudFront distribution for frontend

## Step 5: Configure AWS Environment

After deployment, add your Meta token to AWS:

```bash
# Store Meta access token in Parameter Store
aws ssm put-parameter \
  --name "/stratscout/meta/access-token" \
  --value "YOUR_TOKEN" \
  --type "SecureString"

# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name StratScoutStack-ComputeLayerDataIngestionFunction* \
  --environment "Variables={META_ACCESS_TOKEN=$(aws ssm get-parameter --name /stratscout/meta/access-token --with-decryption --query Parameter.Value --output text)}"
```

Or use the AWS Console:
1. Go to Lambda → Functions
2. Find "DataIngestionFunction"
3. Configuration → Environment variables
4. Add `META_ACCESS_TOKEN` with your token

## Step 6: Verify Data Collection

Wait 15 minutes for the first scheduled run, or trigger manually:

```bash
# Trigger data ingestion manually
aws lambda invoke \
  --function-name StratScoutStack-ComputeLayerDataIngestionFunction* \
  --payload '{}' \
  response.json

cat response.json
```

Check DynamoDB:
```bash
# List collected ads
aws dynamodb scan \
  --table-name StratScoutStack-DataLayerAdDataTable* \
  --limit 5
```

## Step 7: Test AI Analysis

Trigger AI analysis:

```bash
aws lambda invoke \
  --function-name StratScoutStack-ComputeLayerAIAnalysisFunction* \
  --payload '{}' \
  response.json

cat response.json
```

Check analysis results:
```bash
aws dynamodb scan \
  --table-name StratScoutStack-DataLayerAnalysisTable* \
  --limit 5
```

## Step 8: Test Predictions

Generate campaign predictions:

```bash
aws lambda invoke \
  --function-name StratScoutStack-ComputeLayerPredictionsFunction* \
  --payload '{"body":"{\"competitor_id\":\"comp-mamaearth\"}"}' \
  response.json

cat response.json
```

## What's Happening Now

Your StratScout platform is now:

1. **Collecting ads every 15 minutes** from Meta Ads Library
2. **Analyzing creatives** with Amazon Bedrock AI
3. **Generating predictions** for campaign performance
4. **Storing everything** in DynamoDB for quick access

## View Your Data

### Using AWS Console

1. **DynamoDB** → Tables → View collected ads and analyses
2. **CloudWatch** → Logs → View Lambda execution logs
3. **Lambda** → Functions → Monitor execution metrics

### Using AWS CLI

```bash
# Count total ads collected
aws dynamodb scan \
  --table-name StratScoutStack-DataLayerAdDataTable* \
  --select COUNT

# Get latest analysis
aws dynamodb query \
  --table-name StratScoutStack-DataLayerAnalysisTable* \
  --limit 1 \
  --scan-index-forward false
```

## Next Steps

1. **Build Frontend** - React dashboard to visualize data
2. **Add Gap Analysis** - Identify market opportunities
3. **Create Scout Chatbot** - Conversational AI interface
4. **Set up Monitoring** - CloudWatch alarms and dashboards

## Costs

Expected monthly costs for MVP usage:
- Lambda: ~$75
- Bedrock: ~$300
- DynamoDB: ~$35
- Aurora: ~$120
- Other: ~$95
- **Total: ~$625/month**

## Troubleshooting

### No ads being collected
- Check Lambda logs in CloudWatch
- Verify META_ACCESS_TOKEN is set
- Test token with curl command above
- Check EventBridge rule is enabled

### AI analysis failing
- Verify Bedrock is enabled in your region
- Check Lambda has Bedrock permissions
- Review CloudWatch logs for errors

### High costs
- Reduce number of competitors
- Increase EventBridge schedule interval
- Lower Lambda memory allocation

## Support

- [Meta Ads Setup Guide](./META_ADS_SETUP.md)
- [Architecture Documentation](../design.md)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

## Clean Up

To avoid charges, destroy all resources:

```bash
cd infrastructure
cdk destroy --all
```

This will delete all AWS resources created by StratScout.
