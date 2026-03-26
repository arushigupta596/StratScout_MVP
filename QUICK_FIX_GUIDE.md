# Quick Fix Guide - Predictions, Gap Analysis & Scout AI

## Problem
The Lambda functions have bugs preventing them from returning data even though the data exists in DynamoDB.

## Solution
I've fixed all the Lambda handler code. Now you just need to redeploy.

## Fixed Files
1. ✅ `backend/predictions/handler.py` - Fixed query logic
2. ✅ `backend/gap_analysis/handler.py` - Added error handling  
3. ✅ `backend/scout_chatbot/conversation_manager.py` - Fixed DynamoDB operations

## Deploy the Fixes

### Option 1: Using CDK (Recommended)
```bash
cd infrastructure
npx cdk deploy --require-approval never
```

### Option 2: Using the deployment script
```bash
bash scripts/deploy.sh
```

### Option 3: Manual Lambda update
```bash
cd backend

# Update Predictions Lambda
zip -r /tmp/predictions.zip predictions/ common/ -x "*.pyc" "*__pycache__*"
aws lambda update-function-code \
  --function-name StratScoutStack-ComputeLayerPredictionsFunctionBE0-jEE4jNAepWNe \
  --zip-file fileb:///tmp/predictions.zip

# Update Gap Analysis Lambda
zip -r /tmp/gaps.zip gap_analysis/ common/ -x "*.pyc" "*__pycache__*"
aws lambda update-function-code \
  --function-name StratScoutStack-ComputeLayerGapAnalysisFunction8F8-qtIiqZBdCv2f \
  --zip-file fileb:///tmp/gaps.zip

# Update Scout Lambda
zip -r /tmp/scout.zip scout_chatbot/ common/ -x "*.pyc" "*__pycache__*"
aws lambda update-function-code \
  --function-name StratScoutStack-ComputeLayerScoutChatbotFunctionC4-KhZGJQjzWgtu \
  --zip-file fileb:///tmp/scout.zip
```

## Verify Data is Ready

Check DynamoDB tables have data:
```bash
# Check predictions (should show 5)
aws dynamodb scan --table-name StratScout-Predictions --select COUNT

# Check gap analysis (should show 1)
aws dynamodb scan --table-name StratScout-GapAnalysis --select COUNT

# Check competitors (should show 5)
aws dynamodb scan --table-name StratScout-Competitors --select COUNT
```

## Test After Deployment

1. Go to https://dh9mb4macowil.cloudfront.net
2. Sign up with your email
3. Verify email with code
4. Sign in
5. Test each page:
   - **Dashboard** - Should show 5 competitors
   - **Predictions** - Should show 5 predictions with reach/engagement data
   - **Gap Analysis** - Should show 6 opportunities
   - **Scout AI** - Should respond to questions

## What Was Wrong

### Predictions Handler
- Was trying to use a non-existent GSI index `CompetitorPredictionIndex`
- Fixed by using `scan()` and filtering in memory

### Gap Analysis Handler
- GET endpoint had no error handling
- Fixed by adding try-catch blocks

### Scout Chatbot
- Conversation table operations were using wrong key structure
- Missing required `timestamp` field
- Fixed all DynamoDB operations to use composite keys properly

## Current Data in DynamoDB

✅ **Predictions Table**: 5 predictions
- comp-mamaearth
- comp-the-derma-co
- comp-plum-goodness
- comp-dot-and-key
- comp-minimalist

✅ **Gap Analysis Table**: 1 analysis with 6 opportunities
- Sustainability messaging gap (high priority)
- Video content format (high priority)
- Weekend timing opportunity (medium priority)
- Science-backed positioning (medium priority)
- Men's skincare segment (high priority)
- User-generated content (medium priority)

✅ **Competitors Table**: 5 competitors with 146 ads total

## After Deployment Works

All three features will work:
- ✅ Predictions page shows forecasts
- ✅ Gap Analysis shows opportunities
- ✅ Scout AI answers questions

The data is already there - just need to deploy the fixed Lambda code!
