# Real Data Integration - Meta Ads Library API

## Overview

StratScout now uses the **real Meta Ads Library API** to collect actual competitor ad data from Indian skincare brands. No more demo data!

## What Changed

### Before (Demo Data)
- Generated fake ads with placeholder text
- No real competitor insights
- Limited testing capability

### After (Real Data)
- ✅ Fetches actual ads from Meta Ads Library
- ✅ Tracks real Indian skincare brands
- ✅ Gets real ad copy, creatives, and metadata
- ✅ Monitors active and historical campaigns
- ✅ Includes impression and spend data (when available)

## How It Works

### 1. API Integration

The `MetaAdsClient` now calls the real Meta Ads Library API:

```python
API_BASE_URL = "https://graph.facebook.com/v18.0/ads_archive"
```

### 2. Search Parameters

For each competitor, we search with:
- **Search terms**: Brand name variations
- **Country**: India (`ad_reached_countries=IN`)
- **Status**: All ads (active and inactive)
- **Limit**: 100 ads per request

### 3. Data Collected

For each ad, we collect:
- Ad ID and Meta Ad ID
- Ad text (body, title, description)
- Creative snapshot URL
- Page name and ID
- Platforms (Facebook, Instagram, etc.)
- Start and stop dates
- Active status
- Impressions and spend ranges (if available)

### 4. Default Brands Tracked

Out of the box, we track these Indian skincare brands:

1. **Mamaearth** - Natural baby and beauty products
2. **Plum** - Vegan beauty and personal care
3. **The Derma Co** - Dermatologist-formulated skincare
4. **Minimalist** - Science-backed skincare
5. **Dot & Key** - Korean beauty-inspired

You can easily add more brands by editing the competitor list.

## Setup Instructions

### Quick Setup (5 minutes)

1. **Get Meta Access Token**
   ```bash
   # Go to https://developers.facebook.com/tools/explorer/
   # Select your app, generate token, copy it
   export META_ACCESS_TOKEN='your_token_here'
   ```

2. **Test Locally**
   ```bash
   python3 scripts/test_meta_ads.py
   ```

3. **Deploy to AWS**
   ```bash
   cd infrastructure
   cdk deploy
   ```

See [META_ADS_SETUP.md](./META_ADS_SETUP.md) for detailed instructions.

## Customizing Competitors

Edit `backend/data_ingestion/meta_ads/client.py`:

```python
self.default_competitors = [
    {
        'id': 'comp-your-brand',
        'name': 'Your Brand Name',
        'search_terms': ['Brand Name', 'Brand Alternate Name'],
        'page_id': None,  # Auto-discovered
    },
    # Add more...
]
```

### Tips for Search Terms

- Use the exact Facebook page name
- Include common variations
- Try both full and short names
- Example: `['Plum Goodness', 'Plum']`

## API Limits

### Rate Limits
- **200 calls per hour** per access token
- **5 calls per second** burst limit

### Our Implementation
- ✅ Automatic retry with exponential backoff
- ✅ 1-second delay between competitor searches
- ✅ Deduplication to avoid storing duplicates
- ✅ Error handling for rate limits

### Staying Within Limits

With 5 competitors and 15-minute collection intervals:
- **4 collections per hour** × **5 competitors** = **20 API calls/hour**
- Well within the 200 calls/hour limit ✅

## Data Quality

### What You Get

**High Quality:**
- ✅ Ad copy and creative text
- ✅ Active/inactive status
- ✅ Start and stop dates
- ✅ Platform distribution
- ✅ Page information

**Limited Availability:**
- ⚠️ Impression ranges (only for some ads)
- ⚠️ Spend ranges (only for some ads)
- ⚠️ Detailed targeting (limited by API)

### Why Some Data is Limited

Meta Ads Library API provides:
- Full data for **political/social issue ads** (7-year archive)
- Limited data for **commercial ads** (active + recent)

For commercial ads (like skincare brands):
- You get creative content and basic metadata
- Impression/spend data is optional and may not always be available
- This is still valuable for competitive intelligence!

## Testing

### Test Single Brand

```bash
export META_ACCESS_TOKEN='your_token'
python3 scripts/test_meta_ads.py
```

Expected output:
```
✓ Successfully fetched 15 ads
Sample ad data:
Ad ID: ad-1234567890-abcdef12
Page Name: Mamaearth
Platform: facebook
Is Active: True
Ad Text: Get glowing skin with our Vitamin C Face Wash...
```

### Test Multiple Brands

```bash
python3 scripts/test_meta_ads.py --multiple
```

### Test in AWS

```bash
# Trigger Lambda manually
aws lambda invoke \
  --function-name StratScoutStack-ComputeLayerDataIngestionFunction* \
  --payload '{}' \
  response.json

# Check results
cat response.json
```

## Troubleshooting

### "Invalid OAuth access token"
**Solution**: Token expired. Generate a new one from Graph API Explorer.

### "No ads found"
**Possible reasons**:
1. Brand not running ads in India currently
2. Search term doesn't match Facebook page name
3. Try different search terms

**Fix**: Test with curl first:
```bash
curl "https://graph.facebook.com/v18.0/ads_archive?access_token=YOUR_TOKEN&search_terms=Mamaearth&ad_reached_countries=IN&limit=5"
```

### "Rate limit exceeded"
**Solution**: Wait 1 hour for limit to reset, or reduce collection frequency.

### DynamoDB errors
**Check**:
1. Lambda has DynamoDB write permissions
2. Table names are correct in environment variables
3. CloudWatch logs for detailed errors

## Monitoring

### CloudWatch Metrics

Monitor these metrics:
- Lambda invocations
- Lambda errors
- Lambda duration
- DynamoDB write capacity

### CloudWatch Logs

Check logs for:
- Number of ads collected per brand
- API errors or rate limits
- Deduplication statistics

### DynamoDB

Query tables to see:
```bash
# Count total ads
aws dynamodb scan \
  --table-name StratScoutStack-DataLayerAdDataTable* \
  --select COUNT

# Get recent ads
aws dynamodb query \
  --table-name StratScoutStack-DataLayerAdDataTable* \
  --index-name CompetitorIndex \
  --key-condition-expression "competitor_id = :cid" \
  --expression-attribute-values '{":cid":{"S":"comp-mamaearth"}}' \
  --limit 10
```

## Benefits of Real Data

### For AI Analysis
- ✅ Accurate creative analysis
- ✅ Real messaging patterns
- ✅ Actual competitive positioning
- ✅ True market trends

### For Predictions
- ✅ Historical campaign data
- ✅ Real ad volume patterns
- ✅ Actual creative diversity
- ✅ Platform distribution insights

### For Gap Analysis
- ✅ Identify real market gaps
- ✅ Spot actual opportunities
- ✅ Benchmark against real competitors
- ✅ Data-driven recommendations

## Next Steps

1. ✅ **Set up Meta API access** (5 min)
2. ✅ **Test locally** with test script
3. ✅ **Customize competitor list** for your needs
4. ✅ **Deploy to AWS** and start collecting
5. ⏳ **Wait 15 minutes** for first collection
6. ⏳ **Check DynamoDB** for collected ads
7. ⏳ **Run AI analysis** on real data
8. ⏳ **Generate predictions** from real patterns

## Support

- [Meta Ads Setup Guide](./META_ADS_SETUP.md)
- [Quick Start Guide](./QUICK_START.md)
- [Meta Ads Library API Docs](https://developers.facebook.com/docs/marketing-api/ads-library-api)

---

**Ready to track real competitors?** Follow the [Quick Start Guide](./QUICK_START.md)!
