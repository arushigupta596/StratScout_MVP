#!/bin/bash
set -e

echo "======================================"
echo "StratScout MVP - Deployment Script"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"
echo ""

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo ""

# Step 1: Check collected ads
echo "Step 1: Checking collected ad data..."
if [ ! -d "data" ] || [ -z "$(ls -A data/scraped_ads_*.json 2>/dev/null)" ]; then
    echo -e "${YELLOW}Warning: No ad data found in data/ folder${NC}"
    echo "Run: python3 scripts/scrape_ads_automated.py"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    ad_count=$(cat data/scraped_ads_*.json | grep -o '"ad_id"' | wc -l | tr -d ' ')
    echo -e "${GREEN}✓ Found $ad_count ads${NC}"
fi
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing dependencies..."

echo "  - Backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
cd ..
echo -e "${GREEN}  ✓ Backend dependencies installed${NC}"

echo "  - Frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
cd ..
echo -e "${GREEN}  ✓ Frontend dependencies installed${NC}"

echo "  - Infrastructure dependencies..."
cd infrastructure
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
cd ..
echo -e "${GREEN}  ✓ Infrastructure dependencies installed${NC}"
echo ""

# Step 3: Build frontend
echo "Step 3: Building frontend..."
cd frontend
npm run build
cd ..
echo -e "${GREEN}✓ Frontend built${NC}"
echo ""

# Step 4: Bootstrap CDK (if needed)
echo "Step 4: Checking CDK bootstrap..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit &> /dev/null; then
    echo "  Bootstrapping CDK..."
    cd infrastructure
    npx cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION
    cd ..
    echo -e "${GREEN}  ✓ CDK bootstrapped${NC}"
else
    echo -e "${GREEN}  ✓ CDK already bootstrapped${NC}"
fi
echo ""

# Step 5: Deploy infrastructure
echo "Step 5: Deploying infrastructure..."
echo -e "${YELLOW}This may take 10-15 minutes...${NC}"
cd infrastructure
npx cdk deploy --all --require-approval never
cd ..
echo -e "${GREEN}✓ Infrastructure deployed${NC}"
echo ""

# Step 6: Get outputs
echo "Step 6: Getting deployment outputs..."
API_URL=$(aws cloudformation describe-stacks \
  --stack-name StratScoutApiLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text 2>/dev/null || echo "")

CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name StratScoutApiLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
  --output text 2>/dev/null || echo "")

FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name StratScoutApiLayerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
  --output text 2>/dev/null || echo "")

echo -e "${GREEN}✓ Outputs retrieved${NC}"
echo ""

# Step 7: Update frontend with API URL
if [ -n "$API_URL" ]; then
    echo "Step 7: Updating frontend configuration..."
    cat > frontend/.env << EOF
VITE_API_URL=$API_URL
VITE_ENV=production
EOF
    
    # Rebuild frontend with new API URL
    cd frontend
    npm run build
    cd ..
    echo -e "${GREEN}✓ Frontend updated${NC}"
    echo ""
fi

# Step 8: Deploy frontend to S3
if [ -n "$FRONTEND_BUCKET" ]; then
    echo "Step 8: Deploying frontend to S3..."
    aws s3 sync frontend/dist/ s3://$FRONTEND_BUCKET/ --delete --quiet
    echo -e "${GREEN}✓ Frontend deployed${NC}"
    echo ""
    
    # Invalidate CloudFront cache
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
      --stack-name StratScoutApiLayerStack \
      --query 'Stacks[0].Outputs[?OutputKey==`DistributionId`].OutputValue' \
      --output text 2>/dev/null || echo "")
    
    if [ -n "$DISTRIBUTION_ID" ]; then
        echo "  Invalidating CloudFront cache..."
        aws cloudfront create-invalidation \
          --distribution-id $DISTRIBUTION_ID \
          --paths "/*" --output text > /dev/null
        echo -e "${GREEN}  ✓ Cache invalidated${NC}"
    fi
fi
echo ""

# Step 9: Set up billing alerts
echo "Step 9: Setting up cost monitoring..."
SNS_TOPIC_ARN=$(aws sns create-topic --name stratscout-billing-alerts --query TopicArn --output text 2>/dev/null || echo "")

if [ -n "$SNS_TOPIC_ARN" ]; then
    echo "  SNS Topic created: $SNS_TOPIC_ARN"
    echo -e "${YELLOW}  Subscribe to billing alerts:${NC}"
    echo "  aws sns subscribe --topic-arn $SNS_TOPIC_ARN --protocol email --notification-endpoint your-email@example.com"
fi
echo ""

# Summary
echo "======================================"
echo "Deployment Complete! 🚀"
echo "======================================"
echo ""
echo -e "${GREEN}Frontend URL:${NC} $CLOUDFRONT_URL"
echo -e "${GREEN}API URL:${NC} $API_URL"
echo ""
echo "Next steps:"
echo "1. Subscribe to billing alerts (see command above)"
echo "2. Import ad data: python3 scripts/import_to_dynamodb.py"
echo "3. Test the application: open $CLOUDFRONT_URL"
echo "4. Monitor costs: aws ce get-cost-and-usage ..."
echo ""
echo "Documentation:"
echo "- Deployment Guide: DEPLOYMENT_GUIDE.md"
echo "- Cost Monitoring: See DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${GREEN}Happy analyzing! 📊${NC}"
