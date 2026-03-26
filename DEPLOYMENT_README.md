# StratScout MVP - Deployment Guide

## 🚀 Live Application
**URL**: https://dh9mb4macowil.cloudfront.net

## 📋 Project Overview
StratScout is a competitive intelligence platform for Indian D2C skincare brands, providing:
- Campaign predictions
- Gap analysis
- AI-powered chatbot (Scout AI)
- Comprehensive campaign reports

## 🏗️ Architecture
- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Backend**: Python Lambda functions
- **Infrastructure**: AWS CDK (TypeScript)
- **Database**: DynamoDB
- **AI**: Amazon Bedrock (Claude 3 Sonnet)
- **Auth**: AWS Cognito
- **Hosting**: S3 + CloudFront

## 📁 Project Structure
```
stratscout-competitive-intelligence/
├── backend/                 # Python Lambda functions
│   ├── ai_analysis/        # Bedrock AI integration
│   ├── api/                # API handlers
│   ├── common/             # Shared utilities
│   ├── data_ingestion/     # Data collection
│   ├── gap_analysis/       # Market gap analysis
│   ├── predictions/        # Campaign predictions
│   ├── reports/            # Report generation
│   └── scout_chatbot/      # AI chatbot
├── frontend/               # React application
│   └── src/
│       ├── components/     # React components
│       ├── contexts/       # Auth context
│       ├── lib/            # API client & auth
│       ├── pages/          # Page components
│       ├── store/          # State management
│       └── types/          # TypeScript types
├── infrastructure/         # AWS CDK stacks
│   └── lib/
│       ├── api-layer-stack.ts
│       ├── compute-layer-stack.ts
│       ├── data-layer-stack.ts
│       └── stratscout-stack.ts
├── data/                   # Scraped ad data
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## 🔧 Prerequisites
- Node.js 18+
- Python 3.12+
- AWS CLI configured
- AWS CDK installed (`npm install -g aws-cdk`)
- AWS Account with Bedrock access (optional)

## 🚀 Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/arushigupta596/StratScout_MVP.git
cd StratScout_MVP
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Infrastructure Setup
```bash
cd infrastructure
npm install
```

### 5. Configure Environment
Create `frontend/.env`:
```env
VITE_API_URL=https://your-api-gateway-url.amazonaws.com/prod
VITE_USER_POOL_ID=your-user-pool-id
VITE_USER_POOL_CLIENT_ID=your-client-id
VITE_AWS_REGION=us-east-1
```

### 6. Deploy Infrastructure
```bash
cd infrastructure
npx cdk bootstrap  # First time only
npx cdk deploy --require-approval never
```

This will output:
- API Gateway URL
- CloudFront URL
- Cognito User Pool ID
- Cognito Client ID

### 7. Update Frontend Environment
Update `frontend/.env` with the outputs from step 6.

### 8. Build and Deploy Frontend
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-frontend-bucket --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### 9. Import Sample Data
```bash
cd scripts
python import_to_dynamodb.py
```

## 🔑 AWS Resources Created
- **DynamoDB Tables**: 7 tables (Competitors, Ads, Analysis, Predictions, GapAnalysis, Conversations, Reports)
- **Lambda Functions**: 7 functions (DataIngestion, AIAnalysis, Predictions, GapAnalysis, ScoutChatbot, CompetitorsApi, Report)
- **API Gateway**: REST API with Cognito authorizer
- **S3 Buckets**: 2 buckets (Frontend, Ad Creatives)
- **CloudFront**: Distribution for frontend
- **Cognito**: User Pool and Client

## 💰 Cost Estimate
- **DynamoDB**: ~$5-10/month (pay-per-request)
- **Lambda**: ~$5-10/month (free tier eligible)
- **S3**: ~$1-2/month
- **CloudFront**: ~$1-2/month
- **API Gateway**: ~$3-5/month
- **Cognito**: Free (up to 50,000 MAUs)
- **Bedrock**: ~$0 (if not used) or ~$10-20/month

**Total**: ~$15-50/month depending on usage

## 🔒 Security Notes
- `.env` files are gitignored
- AWS credentials never committed
- Cognito handles authentication
- API Gateway has CORS configured
- All Lambda functions have minimal IAM permissions

## 📊 Features
1. **Dashboard (Report)**: Comprehensive campaign plan
2. **Predictions**: AI-powered campaign performance predictions
3. **Gap Analysis**: Market opportunity identification
4. **Scout AI**: Intelligent chatbot with chart generation
5. **Authentication**: Sign up/Sign in with Cognito

## 🐛 Troubleshooting

### Bedrock Access
If you see "Model access not granted":
1. Go to AWS Console → Bedrock
2. Request model access for Claude 3 Sonnet
3. Wait for approval (usually instant)

### Lambda Package Size
If deployment fails with package size error:
- Ensure `venv/` is excluded in CDK code
- Check `exclude` patterns in `compute-layer-stack.ts`

### Frontend Not Loading
1. Check CloudFront distribution status
2. Verify S3 bucket policy allows public read
3. Invalidate CloudFront cache
4. Check browser console for errors

### API Errors
1. Check Lambda logs in CloudWatch
2. Verify DynamoDB tables exist
3. Check IAM permissions
4. Verify API Gateway configuration

## 📝 Environment Variables

### Backend (Lambda)
Set automatically by CDK:
- `COMPETITOR_TABLE`
- `AD_DATA_TABLE`
- `ANALYSIS_TABLE`
- `PREDICTION_TABLE`
- `GAP_ANALYSIS_TABLE`
- `CONVERSATION_TABLE`
- `REPORT_TABLE`
- `AD_CREATIVES_BUCKET`
- `BEDROCK_MODEL_ID`
- `BEDROCK_REGION`

### Frontend
Required in `frontend/.env`:
- `VITE_API_URL`
- `VITE_USER_POOL_ID`
- `VITE_USER_POOL_CLIENT_ID`
- `VITE_AWS_REGION`

## 🔄 Update Deployment

### Backend Changes
```bash
cd infrastructure
npx cdk deploy --require-approval never
```

### Frontend Changes
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket --delete
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

## 🧪 Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📚 Documentation
- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
- `TESTING_GUIDE.md` - Testing procedures
- `docs/AWS_CREDENTIALS_SETUP.md` - AWS setup
- `docs/META_ADS_SETUP.md` - Meta Ads API setup
- `BEDROCK_ACCESS_SETUP.md` - Bedrock access instructions

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License
MIT License

## 👥 Team
Developed for AI for Bharat

## 🆘 Support
For issues or questions:
1. Check documentation in `/docs`
2. Review troubleshooting section
3. Check AWS CloudWatch logs
4. Open an issue on GitHub

## ✅ Deployment Checklist
- [ ] AWS CLI configured
- [ ] Node.js and Python installed
- [ ] Dependencies installed
- [ ] Infrastructure deployed
- [ ] Frontend environment configured
- [ ] Frontend built and deployed
- [ ] Sample data imported
- [ ] Application tested
- [ ] Bedrock access requested (optional)
- [ ] CloudFront cache invalidated

## 🎉 Success!
Your StratScout MVP is now deployed and ready to use!
