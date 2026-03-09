# StratScout - AI-Powered Competitive Intelligence Platform

StratScout is a serverless competitive intelligence platform for D2C brands, built on AWS with Amazon Bedrock AI.

## Features

- Real-time competitor ad monitoring (Meta Ads Library)
- AI-powered analysis with Amazon Bedrock (Claude 3 Sonnet)
- Scout chatbot for conversational insights
- Campaign performance predictions
- Gap analysis with opportunity identification
- Interactive dashboards and visualizations

## Architecture

- **Backend**: Python 3.12 Lambda functions
- **Infrastructure**: AWS CDK (TypeScript)
- **AI**: Amazon Bedrock (Claude 3 Sonnet)
- **Data**: DynamoDB, Aurora Serverless v2 PostgreSQL, S3
- **Frontend**: React 18 + TypeScript
- **APIs**: Meta Ads Library, Google Trends (Pytrends)

## Project Structure

```
stratscout/
├── infrastructure/         # AWS CDK infrastructure code
├── backend/               # Lambda functions and services
│   ├── data_ingestion/    # Meta Ads, Google Trends integration
│   ├── ai_analysis/       # Bedrock AI analysis engine
│   ├── predictions/       # Campaign prediction models
│   ├── gap_analysis/      # Gap analysis engine
│   ├── scout_chatbot/     # Conversational AI interface
│   └── api/               # API Gateway handlers
├── frontend/              # React TypeScript app
└── docs/                  # Documentation

```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- AWS CLI configured
- AWS CDK CLI (`npm install -g aws-cdk`)
- Meta Developer account (for Ads Library API)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   # Infrastructure
   cd infrastructure
   npm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. Deploy infrastructure:
   ```bash
   cd infrastructure
   cdk bootstrap
   cdk deploy
   ```

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get running in 30 minutes
- [Meta Ads Setup](docs/META_ADS_SETUP.md) - How to get Meta API access
- [Real Data Integration](docs/REAL_DATA_INTEGRATION.md) - How real data collection works
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - What's built and how to use it
- [Build Status](BUILD_STATUS.md) - Detailed progress tracking
- [MVP Plan](MVP_PLAN.md) - Full implementation roadmap
- [Architecture Design](design.md) - Technical architecture
- [Requirements](requirements.md) - Functional requirements

## 🎯 Tracked Brands (Default)

Out of the box, we track these Indian skincare brands:
- Mamaearth
- Plum
- The Derma Co
- Minimalist
- Dot & Key

Easy to customize - just edit the competitor list in `backend/data_ingestion/meta_ads/client.py`

## 💰 Costs

Expected monthly costs for MVP usage:
- Lambda: ~$75
- Bedrock: ~$300
- DynamoDB: ~$35
- Aurora: ~$120
- Other: ~$95
- **Total: ~$625/month**

## 🧪 Testing

```bash
# Test Meta Ads API integration
python3 scripts/test_meta_ads.py

# Test with multiple brands
python3 scripts/test_meta_ads.py --multiple

# Test in AWS
aws lambda invoke \
  --function-name StratScoutStack-ComputeLayerDataIngestionFunction* \
  --payload '{}' \
  response.json
```

## 🗺️ Roadmap

- [x] Infrastructure setup (AWS CDK)
- [x] Data ingestion (Meta Ads Library API)
- [x] AI analysis engine (Bedrock)
- [x] Campaign predictions
- [ ] Gap analysis
- [ ] Scout chatbot
- [ ] Frontend dashboard
- [ ] Testing & CI/CD

## 🤝 Contributing

This is a proprietary project. For questions or support, please contact the development team.

## License

Proprietary - All rights reserved

## Contact

For questions or support, please contact the development team.
