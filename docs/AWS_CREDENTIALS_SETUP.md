# AWS Credentials Setup Guide

## Overview

To deploy StratScout to AWS, you need AWS Access Keys. This guide shows you how to get them.

## Step-by-Step Instructions

### Option 1: Create IAM User (Recommended for Development)

#### 1. Sign in to AWS Console

Go to: https://console.aws.amazon.com/

- If you don't have an AWS account, click "Create a new AWS account"
- Follow the signup process (requires credit card, but free tier available)

#### 2. Navigate to IAM

1. In the AWS Console search bar, type "IAM"
2. Click on "IAM" (Identity and Access Management)

Or go directly to: https://console.aws.amazon.com/iam/

#### 3. Create a New IAM User

1. In the left sidebar, click **"Users"**
2. Click **"Create user"** button (top right)
3. Enter user details:
   - **User name**: `stratscout-deployer`
   - Click **"Next"**

#### 4. Set Permissions

1. Select **"Attach policies directly"**
2. Search and select these policies:
   - ✅ `AdministratorAccess` (for full deployment access)
   
   **OR** for more restricted access, select:
   - ✅ `AWSLambda_FullAccess`
   - ✅ `AmazonDynamoDBFullAccess`
   - ✅ `AmazonS3FullAccess`
   - ✅ `CloudFrontFullAccess`
   - ✅ `AmazonAPIGatewayAdministrator`
   - ✅ `IAMFullAccess`
   - ✅ `AWSCloudFormationFullAccess`
   - ✅ `AmazonRDSFullAccess`
   - ✅ `AmazonBedrockFullAccess`

3. Click **"Next"**
4. Review and click **"Create user"**

#### 5. Create Access Keys

1. Click on the newly created user (`stratscout-deployer`)
2. Go to the **"Security credentials"** tab
3. Scroll down to **"Access keys"** section
4. Click **"Create access key"**
5. Select use case: **"Command Line Interface (CLI)"**
6. Check the confirmation box
7. Click **"Next"**
8. (Optional) Add description: "StratScout deployment"
9. Click **"Create access key"**

#### 6. Save Your Credentials

**⚠️ IMPORTANT: This is the ONLY time you'll see the Secret Access Key!**

You'll see:
```
Access key ID: AKIAIOSFODNN7EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Save these immediately!**

Options to save:
- Click **"Download .csv file"** (recommended)
- Copy to a password manager
- Write them down securely

**Never share these keys or commit them to Git!**

#### 7. Configure AWS CLI

Now use these credentials:

```bash
aws configure
```

Enter the values:
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

#### 8. Verify Configuration

```bash
# Test credentials
aws sts get-caller-identity

# Should output:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/stratscout-deployer"
# }
```

✅ **You're ready to deploy!**

---

### Option 2: Use AWS IAM Identity Center (SSO) - For Organizations

If your organization uses AWS SSO:

1. Get SSO login URL from your AWS administrator
2. Install AWS CLI v2
3. Configure SSO:
   ```bash
   aws configure sso
   ```
4. Follow the prompts to authenticate

---

### Option 3: Use Root Account (NOT Recommended)

⚠️ **Warning**: Only use for testing, never for production!

1. Sign in to AWS Console as root user
2. Click your account name (top right)
3. Select **"Security credentials"**
4. Scroll to **"Access keys"**
5. Click **"Create access key"**
6. Follow the warnings and create key

**Important**: Create an IAM user instead for better security!

---

## Security Best Practices

### 1. Never Commit Credentials to Git

Add to `.gitignore`:
```
.env
.env.local
.aws/
credentials
```

### 2. Use Environment Variables

Instead of `aws configure`, you can use:

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Rotate Keys Regularly

1. Create new access key
2. Update your configuration
3. Test with new key
4. Delete old key

### 4. Use MFA (Multi-Factor Authentication)

1. In IAM, select your user
2. Go to "Security credentials"
3. Click "Assign MFA device"
4. Follow setup instructions

### 5. Monitor Key Usage

Check CloudTrail logs for unusual activity:
```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=stratscout-deployer
```

---

## Troubleshooting

### Issue: "Access Denied" errors

**Solution**: User needs more permissions
1. Go to IAM → Users → stratscout-deployer
2. Add missing permissions
3. Common needed: `AdministratorAccess` or specific service policies

### Issue: "Invalid security token"

**Solution**: Credentials expired or incorrect
```bash
# Reconfigure
aws configure

# Or check current config
cat ~/.aws/credentials
```

### Issue: "Region not specified"

**Solution**: Set default region
```bash
aws configure set region us-east-1
```

### Issue: Can't find credentials file

**Solution**: Create manually
```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
EOF

cat > ~/.aws/config << EOF
[default]
region = us-east-1
output = json
EOF
```

---

## AWS Free Tier

Good news! AWS offers a free tier:

### Always Free
- Lambda: 1M requests/month
- DynamoDB: 25GB storage
- S3: 5GB storage
- CloudFront: 1TB data transfer

### 12 Months Free (New Accounts)
- Additional Lambda compute
- Additional DynamoDB capacity
- RDS: 750 hours/month

**Note**: StratScout MVP will likely exceed free tier due to:
- Bedrock AI usage (not free)
- Aurora Serverless (not free)
- High Lambda invocations

**Estimated cost**: $200-300/month with optimizations

---

## Cost Management

### Set Up Billing Alerts

1. Go to AWS Console → Billing
2. Click "Billing preferences"
3. Enable "Receive Billing Alerts"
4. Save preferences

Then create alarm:
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name stratscout-cost-alert \
  --alarm-description "Alert when cost exceeds $300" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 300 \
  --comparison-operator GreaterThanThreshold
```

### Monitor Costs Daily

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost
```

Or use the provided script:
```bash
./scripts/check_costs.sh
```

---

## Quick Reference

### AWS CLI Configuration Files

**Credentials**: `~/.aws/credentials`
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

**Config**: `~/.aws/config`
```ini
[default]
region = us-east-1
output = json
```

### Common AWS CLI Commands

```bash
# Verify credentials
aws sts get-caller-identity

# List S3 buckets
aws s3 ls

# List Lambda functions
aws lambda list-functions

# Check region
aws configure get region

# Change region
aws configure set region us-west-2
```

---

## Next Steps

After configuring AWS credentials:

1. ✅ Verify credentials work:
   ```bash
   aws sts get-caller-identity
   ```

2. ✅ Check Bedrock access (required for AI):
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```

3. ✅ Run deployment:
   ```bash
   ./scripts/deploy.sh
   ```

---

## Support

### AWS Documentation
- IAM User Guide: https://docs.aws.amazon.com/IAM/latest/UserGuide/
- AWS CLI Configuration: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html

### Common Issues
- **Permissions**: Add `AdministratorAccess` policy
- **Region**: Use `us-east-1` for Bedrock availability
- **Credentials**: Never commit to Git!

### Getting Help
1. Check AWS Console → IAM → Users
2. Verify policies attached to user
3. Check CloudTrail for access denied errors
4. Review this guide's troubleshooting section

---

**Ready to deploy?** Once you have your credentials configured, run:

```bash
./scripts/deploy.sh
```

🚀 **Let's go!**
