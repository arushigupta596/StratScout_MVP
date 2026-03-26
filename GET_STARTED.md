# Get Started with StratScout MVP 🚀

## You're Almost There!

Everything is built and ready. You just need AWS credentials to deploy.

## Step 1: Get AWS Credentials (5 minutes) ⚡

### Quick Guide
Follow: **`docs/QUICK_AWS_SETUP.md`** (5-minute visual guide)

### Detailed Guide
Follow: **`docs/AWS_CREDENTIALS_SETUP.md`** (comprehensive instructions)

### Summary
1. Go to https://console.aws.amazon.com/iam/
2. Create user: `stratscout-deployer`
3. Add permission: `AdministratorAccess`
4. Create access key for CLI
5. Save credentials (Access Key ID + Secret Access Key)
6. Run: `aws configure` and paste credentials

**Region**: Use `us-east-1` (required for Bedrock)

---

## Step 2: Deploy to AWS (30-45 minutes)

Once you have AWS credentials:

```bash
# Make deploy script executable
chmod +x scripts/deploy.sh

# Run deployment (automated)
./scripts/deploy.sh
```

The script will:
- ✅ Check AWS credentials
- ✅ Install dependencies
- ✅ Build frontend
- ✅ Deploy infrastructure
- ✅ Configure everything
- ✅ Give you access URLs

---

## Step 3: Monitor Costs

```bash
# Make cost checker executable
chmod +x scripts/check_costs.sh

# Check costs daily
./scripts/check_costs.sh
```

**Target**: $200-300/month (optimized from $625)

---

## What You'll Get

After deployment:

### Frontend Dashboard
- URL: `https://xxxxx.cloudfront.net`
- Features:
  - Overview dashboard with metrics
  - Competitor deep dive
  - Gap analysis with opportunities
  - Campaign predictions
  - Scout AI chatbot

### Backend API
- URL: `https://xxxxx.execute-api.us-east-1.amazonaws.com/prod`
- Services:
  - Data ingestion (every 6 hours)
  - AI analysis (Bedrock)
  - Predictions
  - Gap analysis
  - Scout chatbot

### Data
- 5 brands tracked
- 1,000+ ads collected
- AI-powered insights
- Market opportunities

---

## Documentation

### Quick Start
- **GET_STARTED.md** ← You are here
- **docs/QUICK_AWS_SETUP.md** - 5-minute AWS setup
- **READY_TO_DEPLOY.md** - Deployment overview

### Detailed Guides
- **docs/AWS_CREDENTIALS_SETUP.md** - Complete AWS setup
- **DEPLOYMENT_GUIDE.md** - Detailed deployment with cost optimizations
- **BACKEND_COMPLETE.md** - Backend documentation
- **FRONTEND_COMPLETE.md** - Frontend documentation

### Reference
- **BUILD_STATUS.md** - Implementation status
- **MVP_READY.md** - Complete feature list
- **docs/SCRAPING_GUIDE.md** - How to collect more ads

---

## Troubleshooting

### "I don't have AWS credentials"
→ Follow: `docs/QUICK_AWS_SETUP.md`

### "aws configure asks for Access Key"
→ You need to create IAM user first (see above guide)

### "I don't have an AWS account"
→ Create one at: https://aws.amazon.com/ (requires credit card)

### "Deploy script fails"
→ Check AWS credentials: `aws sts get-caller-identity`

### "Costs are too high"
→ Run: `./scripts/check_costs.sh` and review DEPLOYMENT_GUIDE.md

---

## Cost Breakdown

### Optimized Monthly Costs: ~$250

| Service | Cost |
|---------|------|
| Lambda | $20 |
| DynamoDB | $50 |
| Aurora Serverless v2 | $80 |
| Bedrock (AI) | $80 |
| S3 + CloudFront | $15 |
| Other | $5 |

**Savings**: 60% reduction from original $625 estimate!

### Cost Optimizations Applied
- ✅ Reduced Lambda memory and timeout
- ✅ Data collection every 6 hours (not 15 min)
- ✅ Aurora auto-pause when idle
- ✅ Bedrock batch processing
- ✅ CloudFront caching
- ✅ S3 lifecycle policies
- ✅ DynamoDB on-demand with TTL

---

## Timeline

### Today (1-2 hours)
1. Get AWS credentials (5 min)
2. Run deployment (30-45 min)
3. Test application (15 min)

### This Week
- Monitor costs daily
- Test all features
- Collect more ads if needed

### This Month
- Optimize based on usage
- Add more competitors
- Enhance AI prompts

---

## Support

### Need Help?
1. Check documentation in `docs/` folder
2. Review troubleshooting sections
3. Check CloudWatch logs in AWS Console
4. Review error messages carefully

### Common Issues
- **AWS Permissions**: User needs `AdministratorAccess`
- **Region**: Must use `us-east-1` for Bedrock
- **Credentials**: Never commit to Git!
- **Costs**: Monitor daily with check_costs.sh

---

## Quick Commands

```bash
# Get AWS credentials
# → Follow: docs/QUICK_AWS_SETUP.md

# Configure AWS CLI
aws configure

# Verify credentials
aws sts get-caller-identity

# Deploy everything
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# Check costs
chmod +x scripts/check_costs.sh
./scripts/check_costs.sh

# Collect more ads
cd backend
source venv/bin/activate
cd ..
python3 scripts/scrape_ads_automated.py
```

---

## What's Included

### ✅ Complete Backend (Python)
- Data ingestion service
- AI analysis with Bedrock
- Campaign predictions
- Gap analysis
- Scout AI chatbot
- Google Trends integration
- Common utilities

### ✅ Complete Frontend (React + TypeScript)
- Dashboard with metrics
- Competitor deep dive
- Gap analysis view
- Predictions with charts
- Scout AI chat interface
- Responsive design

### ✅ Complete Infrastructure (AWS CDK)
- Lambda functions
- DynamoDB tables
- Aurora Serverless v2
- S3 + CloudFront
- API Gateway
- EventBridge scheduling
- Cost-optimized configuration

### ✅ Data Collection
- 5 Indian skincare brands
- 1,000+ ads collected
- Automated scraper
- Official page filtering

---

## Success Checklist

Before going live:
- [ ] AWS credentials configured
- [ ] Deployment completed successfully
- [ ] Frontend accessible
- [ ] API responding
- [ ] Billing alerts set up
- [ ] Costs monitored
- [ ] All features tested

---

## Ready to Start?

### 1. Get AWS Credentials
📖 **Read**: `docs/QUICK_AWS_SETUP.md`

### 2. Deploy
```bash
./scripts/deploy.sh
```

### 3. Enjoy!
Your competitive intelligence platform is live! 🎉

---

**Questions?** Check the documentation in `docs/` folder.

**Ready to deploy?** Follow `docs/QUICK_AWS_SETUP.md` first!

🚀 **Let's build something amazing!**
