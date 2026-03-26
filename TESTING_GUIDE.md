# Testing Guide - Quick Start

## Option 1: Simple Test (No AWS Dependencies)

This is the fastest way to test if your Meta API token works:

### Step 1: Install minimal dependencies
```bash
pip install requests
```

### Step 2: Set your token
```bash
export META_ACCESS_TOKEN='your_token_here'
```

### Step 3: Run simple test
```bash
python3 scripts/test_meta_ads_simple.py
```

This will test the Meta Ads API without requiring boto3 or other AWS dependencies.

### Test multiple brands
```bash
python3 scripts/test_meta_ads_simple.py --multiple
```

---

## Option 2: Full Test (With AWS Dependencies)

If you want to test the full integration including DynamoDB storage:

### Step 1: Fix dependency conflicts
```bash
cd backend
pip install -r requirements.txt
```

If you get urllib3 conflicts, try:
```bash
pip install --upgrade pip
pip install boto3 requests pandas numpy scikit-learn
```

### Step 2: Run full test
```bash
cd ..
python3 scripts/test_meta_ads.py
```

---

## Troubleshooting

### urllib3 Conflict Error

If you see:
```
ERROR: Cannot install -r requirements.txt (line 3) and urllib3==2.1.0 
because these package versions have conflicting dependencies.
```

**Solution 1**: Use the simple test (Option 1 above) - no AWS dependencies needed

**Solution 2**: Install packages individually:
```bash
pip install boto3 requests pandas numpy scikit-learn scipy redis psycopg2-binary python-dateutil pytz facebook-business pytrends
```

**Solution 3**: Use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### ModuleNotFoundError: No module named 'boto3'

This means dependencies aren't installed. Use Option 1 (simple test) which doesn't need boto3.

### Invalid OAuth access token

Your token expired. Generate a new one from Graph API Explorer:
https://developers.facebook.com/tools/explorer/

---

## What Each Test Does

### Simple Test (`test_meta_ads_simple.py`)
- ✅ Tests Meta Ads API directly
- ✅ No AWS dependencies
- ✅ Shows real ad data
- ✅ Fast and easy
- ❌ Doesn't test DynamoDB storage

### Full Test (`test_meta_ads.py`)
- ✅ Tests complete integration
- ✅ Tests DynamoDB storage
- ✅ Tests deduplication
- ✅ Full error handling
- ❌ Requires all AWS dependencies

---

## Expected Output

### Successful Test:
```
============================================================
StratScout - Meta Ads Library API Test (Simple)
============================================================

✓ Access token found (length: 200)

Testing API with brand: Mamaearth

Fetching ads from Meta Ads Library...
✓ Successfully fetched 15 ads

Sample ad data:
------------------------------------------------------------
Ad ID: 123456789
Page Name: Mamaearth
Platforms: facebook, instagram
Ad Text: Get glowing skin with our Vitamin C Face Wash...
------------------------------------------------------------

✅ Meta Ads API integration is working!
```

### Failed Test:
```
❌ ERROR: Invalid OAuth access token

Common issues:
- Invalid or expired access token
- Token doesn't have access to Ads Library API
```

---

## Next Steps After Successful Test

1. ✅ Your Meta API token works!
2. Customize competitor list in `backend/data_ingestion/meta_ads/client.py`
3. Deploy to AWS: `cd infrastructure && cdk deploy`
4. Configure AWS Lambda with your token
5. Start collecting real competitor data!

---

## Quick Reference

### Get Meta Access Token
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Click "Generate Access Token"
4. Copy token (no permissions needed!)

### Test Commands
```bash
# Simple test (recommended)
pip install requests
export META_ACCESS_TOKEN='your_token'
python3 scripts/test_meta_ads_simple.py

# Full test (if dependencies work)
pip install -r backend/requirements.txt
python3 scripts/test_meta_ads.py

# Test multiple brands
python3 scripts/test_meta_ads_simple.py --multiple
```

### Brands to Test
- Mamaearth
- Plum Goodness
- Minimalist
- The Derma Co
- Dot & Key
- mCaffeine
- Wow Skin Science
