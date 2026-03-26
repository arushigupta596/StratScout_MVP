# Quick AWS Setup - 5 Minutes ⚡

## TL;DR - Get AWS Credentials Fast

### Step 1: Go to AWS IAM Console
🔗 https://console.aws.amazon.com/iam/

### Step 2: Create User
1. Click **"Users"** (left sidebar)
2. Click **"Create user"**
3. Name: `stratscout-deployer`
4. Click **"Next"**

### Step 3: Add Permissions
1. Select **"Attach policies directly"**
2. Search and check: `AdministratorAccess`
3. Click **"Next"** → **"Create user"**

### Step 4: Create Access Key
1. Click on the user you just created
2. Go to **"Security credentials"** tab
3. Scroll to **"Access keys"**
4. Click **"Create access key"**
5. Select: **"Command Line Interface (CLI)"**
6. Check the box → **"Next"**
7. Click **"Create access key"**

### Step 5: Save Credentials
**⚠️ SAVE THESE NOW - You won't see them again!**

```
Access key ID: AKIAIOSFODNN7EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Click **"Download .csv file"** to save them!

### Step 6: Configure AWS CLI

```bash
aws configure
```

Paste your credentials:
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

### Step 7: Verify

```bash
aws sts get-caller-identity
```

Should show your account info ✅

### Step 8: Deploy!

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

---

## Visual Guide

```
AWS Console
    ↓
IAM Dashboard
    ↓
Users → Create user
    ↓
Name: stratscout-deployer
    ↓
Permissions: AdministratorAccess
    ↓
Create user
    ↓
Security credentials → Create access key
    ↓
CLI → Create
    ↓
SAVE CREDENTIALS! ⚠️
    ↓
aws configure (paste credentials)
    ↓
./scripts/deploy.sh
    ↓
Done! 🚀
```

---

## Don't Have AWS Account?

### Create New Account (5 minutes)

1. Go to: https://aws.amazon.com/
2. Click **"Create an AWS Account"**
3. Enter email and account name
4. Verify email
5. Enter payment info (required, but free tier available)
6. Verify phone number
7. Choose **"Basic Support - Free"**
8. Complete!

Then follow the steps above to create IAM user.

---

## Important Notes

### ⚠️ Security
- **Never commit credentials to Git!**
- **Never share your secret key!**
- **Download the CSV file and store it safely!**

### 💰 Costs
- Free tier available for new accounts
- StratScout MVP: ~$250/month (optimized)
- Set up billing alerts (see DEPLOYMENT_GUIDE.md)

### 🌍 Region
- Use **us-east-1** (required for Bedrock)
- Don't change region unless you know what you're doing

---

## Troubleshooting

### "Access Denied"
→ User needs `AdministratorAccess` policy

### "Invalid credentials"
→ Double-check you copied the keys correctly

### "Region not found"
→ Use `us-east-1`

### "Command not found: aws"
→ Install AWS CLI: https://aws.amazon.com/cli/

---

## Next Steps

1. ✅ AWS credentials configured
2. ✅ Run deployment: `./scripts/deploy.sh`
3. ✅ Monitor costs: `./scripts/check_costs.sh`

---

**Need more details?** See: `docs/AWS_CREDENTIALS_SETUP.md`

**Ready to deploy?** Run: `./scripts/deploy.sh`

🚀 **Let's build something awesome!**
