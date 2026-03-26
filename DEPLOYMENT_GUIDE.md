# StratScout MVP - Cost-Effective Deployment Guide

## Overview

This guide provides a cost-optimized deployment strategy for the StratScout MVP, targeting **$200-300/month** instead of the original $625/month estimate.

## Cost Optimization Strategy

### Original Estimate: ~$625/month
- Lambda: $50
- DynamoDB: $100
- Aurora Serverless: $200
- Bedrock: $150
- S3/CloudFront: $25
- Other: $100

### Optimized Estimate: ~$250/month
- Lambda: $20 (reduced invocations)
- DynamoDB: $50 (on-demand with caching)
- **RDS Proxy + Aurora Serverless v2**: $80 (0.5 ACU min, paused when idle)
- Bedrock: $80 (batch processing, caching)
- S3/CloudFront: $15 (optimized caching)
- ElastiCache: $0 (use DynamoDB DAX instead)
- Other: $5

## Pre-Deployment Checklist

### 1. Verify Collected Data ✅

```bash
# Check ad counts
for file in data/scraped_ads_*.json; do
  brand=$(basename "$file" .json | sed 's/scraped_ads_//')
  count=$(cat "$file" | grep -o '"ad_id"' | wc -l)
  echo "$brand: $count ads"
done
```

Expected: 1,000-1,500 total ads across 5 brands

### 2. Install Dependencies

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Infrastructure
cd ../infrastructure
npm install
```

### 3. Configure Environment Variables

```bash
# Backend .env
cat > backend/.env << EOF
AWS_REGION=us-east-1
META_ACCESS_TOKEN=your_token_here
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
LOG_LEVEL=INFO
EOF

# Frontend .env
cat > frontend/.env << EOF
VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
VITE_ENV=production
EOF
```

## Cost-Effective Infrastructure Changes

### 1. Optimize Lambda Configuration

Edit `infrastructure/lib/compute-layer-stack.ts`:

```typescript
// Reduce memory and timeout for cost savings
const lambdaDefaults = {
  runtime: lambda.Runtime.PYTHON_3_12,
  memorySize: 512,  // Reduced from 1024
  timeout: Duration.seconds(30),  // Reduced from 60
  environment: {
    LOG_LEVEL: 'WARN',  // Reduce log volume
  },
}

// Use reserved concurrency to control costs
dataIngestionFn.addReservedConcurrentExecutions(5)
aiAnalysisFn.addReservedConcurrentExecutions(3)
```

### 2. Optimize DynamoDB

Edit `infrastructure/lib/data-layer-stack.ts`:

```typescript
// Use on-demand billing with lower limits
const tableDefaults = {
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  pointInTimeRecovery: false,  // Disable for cost savings
  deletionProtection: false,
  stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
}

// Add TTL for automatic cleanup
adsTable.addTimeToLive({
  attributeName: 'ttl',
  enabled: true,
})
```

### 3. Replace ElastiCache with DynamoDB DAX

```typescript
// Remove ElastiCache cluster
// Add DynamoDB DAX instead (more cost-effective)
const daxCluster = new dax.CfnCluster(this, 'DaxCluster', {
  clusterName: 'stratscout-dax',
  nodeType: 'dax.t3.small',  // Smallest instance
  replicationFactor: 1,  // Single node for MVP
  iamRoleArn: daxRole.roleArn,
  subnetGroupName: daxSubnetGroup.ref,
})
```

### 4. Optimize Aurora Serverless v2

```typescript
// Configure Aurora to pause when idle
const cluster = new rds.DatabaseCluster(this, 'Database', {
  engine: rds.DatabaseClusterEngine.auroraPostgres({
    version: rds.AuroraPostgresEngineVersion.VER_15_3,
  }),
  serverlessV2MinCapacity: 0.5,  // Minimum
  serverlessV2MaxCapacity: 1,    // Low maximum
  enableDataApi: true,  // Use Data API to avoid connection pooling costs
  deletionProtection: false,
  backup: {
    retention: Duration.days(1),  // Minimal backup retention
  },
})
```

### 5. Optimize EventBridge Schedule

```typescript
// Reduce data collection frequency
const dataIngestionRule = new events.Rule(this, 'DataIngestionSchedule', {
  schedule: events.Schedule.rate(Duration.hours(6)),  // Changed from 15 min to 6 hours
})
```

### 6. Optimize S3 and CloudFront

```typescript
// Add lifecycle policies
bucket.addLifecycleRule({
  id: 'DeleteOldCreatives',
  expiration: Duration.days(90),  // Delete after 90 days
  transitions: [
    {
      storageClass: s3.StorageClass.INFREQUENT_ACCESS,
      transitionAfter: Duration.days(30),
    },
  ],
})

// Optimize CloudFront caching
const distribution = new cloudfront.Distribution(this, 'Distribution', {
  defaultBehavior: {
    cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
    compress: true,
  },
  priceClass: cloudfront.PriceClass.PRICE_CLASS_100,  // Use only US/Europe edge locations
})
```

## Deployment Steps

### Step 1: Build Frontend

```bash
cd frontend
npm run build
```

### Step 2: Bootstrap CDK (First Time Only)

```bash
cd ../infrastructure
npx cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

### Step 3: Deploy Infrastructure

```bash
# Deploy with cost optimizations
npx cdk deploy --all --require-approval never

# Or deploy stacks individually
npx cdk deploy StratScoutDataLayerStack
npx cdk deploy StratScoutComputeLayerStack
npx cdk deploy StratScoutApiLayerStack
```

### Step 4: Upload Ad Data to S3

```bash
# Get bucket name from CDK output
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name StratScoutDataLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`CreativesBucketName`].OutputValue' \
  --output text)

# Upload collected ads
aws s3 sync data/ s3://$BUCKET_NAME/ads/ --exclude "*" --include "*.json"
```

### Step 5: Import Data to DynamoDB

Create a data import script:

```bash
cat > scripts/import_to_dynamodb.py << 'EOF'
import json
import boto3
from pathlib import Path

dynamodb = boto3.resource('dynamodb')
ads_table = dynamodb.Table('StratScout-Ads')
competitors_table = dynamodb.Table('StratScout-Competitors')

# Import competitors
competitors = [
    {'competitorId': 'mama', 'name': 'Mamaearth', 'category': 'Natural Skincare'},
    {'competitorId': 'plum', 'name': 'Plum Goodness', 'category': 'Vegan Beauty'},
    {'competitorId': 'mini', 'name': 'Minimalist', 'category': 'Science-backed'},
    {'competitorId': 'derma', 'name': 'The Derma Co', 'category': 'Dermatology'},
    {'competitorId': 'dotkey', 'name': 'Dot & Key', 'category': 'K-beauty'},
]

for comp in competitors:
    competitors_table.put_item(Item=comp)
    print(f"Imported competitor: {comp['name']}")

# Import ads
for json_file in Path('data').glob('scraped_ads_*.json'):
    with open(json_file) as f:
        data = json.load(f)
        brand = data['brand']
        ads = data['ads']
        
        for ad in ads[:100]:  # Limit to 100 ads per brand for MVP
            ads_table.put_item(Item=ad)
        
        print(f"Imported {len(ads[:100])} ads for {brand}")

print("Data import complete!")
EOF

python3 scripts/import_to_dynamodb.py
```

### Step 6: Update Frontend API URL

```bash
# Get API Gateway URL from CDK output
API_URL=$(aws cloudformation describe-stacks \
  --stack-name StratScoutApiLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Update frontend .env
echo "VITE_API_URL=$API_URL" > frontend/.env
echo "VITE_ENV=production" >> frontend/.env

# Rebuild frontend
cd frontend
npm run build
```

### Step 7: Deploy Frontend to S3

```bash
# Get frontend bucket name
FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name StratScoutApiLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
  --output text)

# Upload frontend
aws s3 sync dist/ s3://$FRONTEND_BUCKET/ --delete

# Invalidate CloudFront cache
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name StratScoutApiLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`DistributionId`].OutputValue' \
  --output text)

aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

### Step 8: Test Deployment

```bash
# Get CloudFront URL
CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name StratScoutApiLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
  --output text)

echo "Frontend URL: $CLOUDFRONT_URL"
echo "API URL: $API_URL"

# Test API
curl $API_URL/competitors

# Open frontend in browser
open $CLOUDFRONT_URL
```

## Cost Monitoring

### Set Up Billing Alerts

```bash
# Create SNS topic for alerts
aws sns create-topic --name stratscout-billing-alerts

# Subscribe your email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT-ID:stratscout-billing-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Create billing alarm
aws cloudwatch put-metric-alarm \
  --alarm-name stratscout-monthly-cost \
  --alarm-description "Alert when monthly cost exceeds $300" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 300 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT-ID:stratscout-billing-alerts
```

### Monitor Costs Daily

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

## Additional Cost Optimizations

### 1. Use Bedrock Batch Processing

```python
# backend/ai_analysis/bedrock_client.py
# Add batch processing to reduce API calls

def analyze_batch(self, ads: List[Dict]) -> List[Dict]:
    """Analyze multiple ads in one API call"""
    # Combine multiple ads into one prompt
    combined_prompt = self._build_batch_prompt(ads)
    response = self.invoke_model(combined_prompt)
    return self._parse_batch_response(response)
```

### 2. Cache Bedrock Responses

```python
# Use DynamoDB for caching
def get_cached_analysis(self, ad_id: str) -> Optional[Dict]:
    """Check cache before calling Bedrock"""
    response = self.cache_table.get_item(Key={'ad_id': ad_id})
    return response.get('Item')
```

### 3. Reduce Data Collection Frequency

- Change from 15 minutes to 6 hours
- Run analysis in batches overnight
- Use EventBridge scheduler for off-peak hours

### 4. Use Spot Instances for Batch Jobs

For large batch processing, use AWS Batch with Spot instances:

```typescript
const batchJob = new batch.JobDefinition(this, 'BatchAnalysis', {
  container: {
    image: ecs.ContainerImage.fromAsset('./backend'),
    vcpus: 2,
    memoryLimitMiB: 4096,
  },
  retryAttempts: 3,
  timeout: Duration.hours(2),
})
```

## Estimated Monthly Costs (Optimized)

| Service | Original | Optimized | Savings |
|---------|----------|-----------|---------|
| Lambda | $50 | $20 | $30 |
| DynamoDB | $100 | $50 | $50 |
| Aurora Serverless | $200 | $80 | $120 |
| Bedrock | $150 | $80 | $70 |
| S3/CloudFront | $25 | $15 | $10 |
| ElastiCache | $100 | $0 | $100 |
| Other | $0 | $5 | -$5 |
| **Total** | **$625** | **$250** | **$375** |

## Monitoring and Maintenance

### Daily Tasks
- Check CloudWatch logs for errors
- Monitor cost dashboard
- Review API Gateway metrics

### Weekly Tasks
- Review DynamoDB capacity
- Check Lambda cold starts
- Analyze Bedrock token usage

### Monthly Tasks
- Review and optimize costs
- Update dependencies
- Backup critical data
- Review security settings

## Rollback Plan

If deployment fails:

```bash
# Rollback infrastructure
npx cdk destroy --all

# Or rollback specific stack
npx cdk destroy StratScoutComputeLayerStack
```

## Troubleshooting

### Issue: Lambda timeout
**Solution**: Increase timeout or optimize code

### Issue: DynamoDB throttling
**Solution**: Enable auto-scaling or increase capacity

### Issue: High Bedrock costs
**Solution**: Implement caching and batch processing

### Issue: CloudFront cache not working
**Solution**: Check cache policy and TTL settings

## Next Steps After Deployment

1. **Monitor for 1 week**: Watch costs and performance
2. **Optimize based on usage**: Adjust resources as needed
3. **Enable auto-scaling**: For production traffic
4. **Set up CI/CD**: Automate future deployments
5. **Add monitoring**: CloudWatch dashboards and alarms

## Support

For deployment issues:
- Check CloudWatch logs
- Review CDK deployment output
- Check AWS Console for resource status
- Review this guide's troubleshooting section

---

**Target Cost**: $200-300/month  
**Deployment Time**: 30-45 minutes  
**Last Updated**: March 8, 2026
