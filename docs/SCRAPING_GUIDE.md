# Ad Scraping Guide

## Overview

The automated scraper collects 200-300 ads per brand from Facebook Ads Library using Playwright browser automation.

## Features

- **High Volume Collection**: Targets 250 ads per brand
- **Smart Scrolling**: Automatically scrolls and loads more ads
- **Deduplication**: Prevents duplicate ads using content hashing
- **Proper URL Encoding**: Correctly handles "Dot & Key" and other special characters
- **Official Page Filtering**: Filters for official brand pages only
- **Progress Tracking**: Shows real-time progress during scraping

## Brands Tracked

1. **Mamaearth** (Official Page: Mamaearth)
2. **Plum Goodness** (Official Page: Plum)
3. **Minimalist** (Official Page: Minimalist)
4. **The Derma Co** (Official Page: The Derma Co)
5. **Dot & Key** (Official Page: Dot & Key) ✅ Fixed URL encoding

## How to Run

### 1. Activate Virtual Environment

```bash
cd backend
source venv/bin/activate
```

### 2. Install Playwright (First Time Only)

```bash
pip install playwright
playwright install chromium
```

### 3. Run the Scraper

```bash
cd ..
python3 scripts/scrape_ads_automated.py
```

### 4. Monitor Progress

The scraper will:
- Launch a headless browser
- Visit Facebook Ads Library for each brand
- Scroll up to 50 times to load more ads
- Extract and deduplicate ads
- Save results to JSON files

Expected output:
```
🔍 Scraping Meta Ads Library for: Mamaearth
   Country: IN
   Target ads: 250

🌐 Launching browser...
📄 Loading page: https://www.facebook.com/ads/library/...
⏳ Waiting for ads to load...
📜 Scrolling to load 250 ads...
   Scroll 1/50: 15 total ads (+15 new)
   Scroll 2/50: 28 total ads (+13 new)
   Scroll 3/50: 42 total ads (+14 new)
   ...
   Scroll 35/50: 247 total ads (+7 new)
   ✓ Target reached: 247 ads

✅ Successfully extracted 247 ads
💾 Saved to: data/scraped_ads_mamaearth.json
```

## Output Files

Data is saved to `data/` folder:

- `scraped_ads_mamaearth.json`
- `scraped_ads_plum_goodness.json`
- `scraped_ads_minimalist.json`
- `scraped_ads_the_derma_co.json`
- `scraped_ads_dot_&_key.json`

Each file contains:
```json
{
  "brand": "Mamaearth",
  "collection_date": "2026-03-08T...",
  "source": "automated_scraping",
  "country": "IN",
  "ads": [
    {
      "ad_id": "scraped-123456789",
      "page_name": "Mamaearth",
      "ad_text": "Discover natural skincare...",
      "start_date": "Mar 1, 2026",
      "stop_date": null,
      "platforms": ["Facebook", "Instagram"],
      "is_active": true,
      "creative_type": "image",
      "scraped_at": "2026-03-08T..."
    }
  ]
}
```

## Configuration

### Adjust Target Ads

Edit `scripts/scrape_ads_automated.py`:

```python
# Line 235: Change max_ads_per_brand
results = await scrape_multiple_brands(brands, country='IN', max_ads_per_brand=300)
```

### Change Scroll Behavior

Edit the scraping function:

```python
# Line 35: Adjust max scrolls
max_scrolls = 50  # Increase for more ads

# Line 42: Adjust wait time between scrolls
await page.wait_for_timeout(3000)  # 3 seconds
```

### Enable Visual Mode

To see the browser while scraping:

```python
# Line 27: Change headless setting
browser = await p.chromium.launch(headless=False)
```

## Troubleshooting

### Issue: Not enough ads collected

**Solution**: Increase scroll count and wait time
```python
max_scrolls = 100  # More scrolls
await page.wait_for_timeout(5000)  # Longer wait
```

### Issue: "Dot & Key" returns wrong results

**Solution**: Already fixed! The scraper now properly URL-encodes brand names:
```python
from urllib.parse import quote
encoded_brand = quote(brand_name)  # "Dot & Key" → "Dot%20%26%20Key"
```

### Issue: Too many duplicate ads

**Solution**: The scraper uses content hashing for deduplication. If you still see duplicates, they might be legitimate variations.

### Issue: Scraper stops early

**Solution**: The scraper stops if no new ads are found after 3 consecutive scrolls. This is normal if Facebook has fewer ads available.

### Issue: Browser crashes or timeouts

**Solution**: 
1. Check your internet connection
2. Increase timeout values
3. Reduce concurrent scrolling speed

## Performance

- **Time per brand**: 5-10 minutes (depending on ad volume)
- **Total time for 5 brands**: 25-50 minutes
- **Expected ads per brand**: 200-300 (varies by brand activity)
- **Memory usage**: ~500MB (Chromium browser)

## Best Practices

1. **Run during off-peak hours**: Less likely to hit rate limits
2. **Don't run too frequently**: Wait at least 24 hours between runs
3. **Verify data quality**: Check JSON files before importing
4. **Backup existing data**: Keep previous scrapes for comparison

## Next Steps

After scraping:

1. **Review the data**:
   ```bash
   cat data/scraped_ads_mamaearth.json | jq '.ads | length'
   ```

2. **Import to database** (when ready):
   ```bash
   python3 scripts/import_manual_ads.py
   ```

3. **Run AI analysis** (after deployment):
   - Deploy infrastructure with CDK
   - Lambda functions will automatically analyze new ads

## Notes

- The scraper respects Facebook's Ads Library terms of use
- Data is publicly available information
- No authentication required (public ads only)
- Filters for official brand pages to avoid influencer posts
- Headless mode is faster but visual mode helps debugging

---

**Last Updated**: March 8, 2026  
**Script**: `scripts/scrape_ads_automated.py`
