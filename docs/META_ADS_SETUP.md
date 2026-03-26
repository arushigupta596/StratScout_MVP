# Meta Ads Library API Setup Guide

This guide will help you set up access to the Meta Ads Library API to track real competitor ads for Indian skincare brands.

## Overview

The Meta Ads Library API is a public API that provides access to ads running on Facebook, Instagram, and other Meta platforms. It's free to use and doesn't require app review for basic ad search functionality.

## Prerequisites

- Facebook account
- Meta Developer account (free)
- 10-15 minutes for setup

## Step 1: Create Meta Developer Account

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click "Get Started" in the top right
3. Log in with your Facebook account
4. Complete the registration process

## Step 2: Create a Meta App

1. Go to [Meta Apps Dashboard](https://developers.facebook.com/apps)
2. Click "Create App"
3. Select "Business" as the app type
4. Fill in app details:
   - **App Name**: StratScout (or your preferred name)
   - **App Contact Email**: Your email
   - **Business Account**: Optional (can skip for now)
5. Click "Create App"

## Step 3: Get Access Token

### Option A: Short-term Access Token (Quick Testing)

1. In your app dashboard, go to **Tools** > **Graph API Explorer**
2. Select your app from the dropdown
3. Click "Generate Access Token"
4. Copy the access token (valid for ~1-2 hours)

### Option B: Long-lived Access Token (Recommended)

1. Get a short-term token from Graph API Explorer (as above)
2. Use this curl command to exchange it for a long-lived token:

```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

Replace:
- `YOUR_APP_ID`: Found in App Dashboard > Settings > Basic
- `YOUR_APP_SECRET`: Found in App Dashboard > Settings > Basic (click "Show")
- `YOUR_SHORT_LIVED_TOKEN`: The token from Graph API Explorer

3. The response will contain a long-lived token (valid for ~60 days)

### Option C: System User Token (Production)

For production use, create a System User token that doesn't expire:

1. Go to **Business Settings** (create a Business Account if needed)
2. Navigate to **Users** > **System Users**
3. Click "Add" to create a new system user
4. Assign your app to the system user
5. Generate a token with no expiration

## Step 4: Configure StratScout

### For Local Development

Create a `.env` file in the backend directory:

```bash
META_ACCESS_TOKEN=your_access_token_here
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
```

### For AWS Deployment

Store credentials in AWS Systems Manager Parameter Store:

```bash
# Using AWS CLI
aws ssm put-parameter \
  --name "/stratscout/meta/access-token" \
  --value "your_access_token_here" \
  --type "SecureString"

aws ssm put-parameter \
  --name "/stratscout/meta/app-id" \
  --value "your_app_id" \
  --type "String"

aws ssm put-parameter \
  --name "/stratscout/meta/app-secret" \
  --value "your_app_secret" \
  --type "SecureString"
```

Then update the Lambda environment variables to read from Parameter Store.

## Step 5: Test the API

Test your access token with this curl command:

```bash
curl -X GET "https://graph.facebook.com/v18.0/ads_archive?access_token=YOUR_ACCESS_TOKEN&search_terms=Mamaearth&ad_reached_countries=IN&limit=5&fields=id,ad_creative_bodies,page_name"
```

You should see a JSON response with ads from Mamaearth (or whichever brand you searched).

## Step 6: Customize Competitor List

Edit `backend/data_ingestion/meta_ads/client.py` to track your desired brands:

```python
self.default_competitors = [
    {
        'id': 'comp-brand1',
        'name': 'Brand Name',
        'search_terms': ['Brand Name', 'Brand Alternate Name'],
        'page_id': None,
    },
    # Add more competitors...
]
```

## API Limits and Best Practices

### Rate Limits
- **200 calls per hour** per access token
- **5 calls per second** burst limit
- Our implementation includes automatic retry with exponential backoff

### Best Practices
1. **Use specific search terms**: Brand names work best
2. **Limit to India**: Use `ad_reached_countries=IN` parameter
3. **Respect rate limits**: We add 1-second delays between requests
4. **Monitor usage**: Check your app dashboard for API usage

### Available Fields

The API provides these fields (we use most of them):
- `id`: Unique ad ID
- `ad_creative_bodies`: Ad text/copy
- `ad_creative_link_titles`: Link titles
- `ad_creative_link_descriptions`: Link descriptions
- `ad_delivery_start_time`: When ad started running
- `ad_delivery_stop_time`: When ad stopped (null if active)
- `ad_snapshot_url`: URL to view the ad
- `page_name`: Facebook page name
- `publisher_platforms`: Where ad runs (Facebook, Instagram, etc.)
- `impressions`: Impression ranges (if available)
- `spend`: Spend ranges (if available)

## Troubleshooting

### Error: "Invalid OAuth access token"
- Your token has expired - generate a new one
- For production, use a long-lived or system user token

### Error: "Application does not have permission"
- Make sure you're using the correct app ID
- Verify the token is associated with your app

### Error: "Rate limit exceeded"
- Wait an hour for the limit to reset
- Reduce the number of competitors you're tracking
- Increase the delay between requests

### No ads returned
- Try different search terms (brand variations)
- Check if the brand actually runs ads in India
- Verify the brand's Facebook page name

## Indian Skincare Brands to Track

Here are some popular Indian skincare brands you can track:

1. **Mamaearth** - Natural baby and beauty products
2. **Plum** - Vegan beauty and personal care
3. **The Derma Co** - Dermatologist-formulated skincare
4. **Minimalist** - Science-backed skincare
5. **Dot & Key** - Korean beauty-inspired
6. **mCaffeine** - Caffeine-based personal care
7. **Wow Skin Science** - Natural beauty products
8. **Forest Essentials** - Ayurvedic luxury
9. **Kama Ayurveda** - Ayurvedic skincare
10. **Nykaa Naturals** - Natural beauty products

## Next Steps

Once configured:
1. Deploy your Lambda functions to AWS
2. The EventBridge schedule will trigger data collection every 15 minutes
3. Check DynamoDB tables to see collected ads
4. View AI analysis results in the analysis table

## Support

For Meta API issues:
- [Meta Ads Library API Documentation](https://developers.facebook.com/docs/marketing-api/ads-library-api)
- [Meta Developer Community](https://developers.facebook.com/community/)

For StratScout issues:
- Check CloudWatch logs for Lambda errors
- Verify DynamoDB table permissions
- Ensure Bedrock access is enabled in your AWS region
