#!/usr/bin/env python3
"""
Scrape Meta Ads Library web interface directly (no API needed!)
This extracts data from the public web page.
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

def scrape_ads_library(brand_name, country='IN', limit=20):
    """
    Scrape ads from Meta Ads Library web interface.
    
    Args:
        brand_name: Brand to search for
        country: Country code (default: IN for India)
        limit: Max ads to collect
    
    Returns:
        List of ad data dictionaries
    """
    print(f"Scraping Meta Ads Library for: {brand_name}")
    print(f"URL: https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={brand_name}")
    print()
    
    # The Ads Library page loads data via JavaScript, so we need to extract it from the page source
    url = f"https://www.facebook.com/ads/library/"
    
    params = {
        'active_status': 'all',
        'ad_type': 'all',
        'country': country,
        'q': brand_name,
        'media_type': 'all'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        print("Fetching page...")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✓ Page loaded (status: {response.status_code})")
        print()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # The Ads Library embeds data in script tags
        # Look for JSON data in the page
        ads_data = []
        
        # Method 1: Extract from script tags containing ad data
        scripts = soup.find_all('script', type='application/json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Look for ad data in the JSON structure
                if isinstance(data, dict):
                    # Navigate through the data structure to find ads
                    # This structure may vary, so we'll try multiple paths
                    ads_data.extend(extract_ads_from_json(data))
            except:
                continue
        
        # Method 2: Look for visible ad cards on the page
        ad_cards = soup.find_all('div', {'data-testid': re.compile('ad-card|search-result')})
        
        print(f"Found {len(ad_cards)} ad cards on page")
        
        for card in ad_cards[:limit]:
            ad_info = extract_ad_from_card(card)
            if ad_info:
                ads_data.append(ad_info)
        
        # Method 3: Manual extraction guide
        if not ads_data:
            print("⚠️  Automated extraction didn't find ads.")
            print()
            print("The Facebook Ads Library uses heavy JavaScript rendering.")
            print("Here's how to manually collect the data:")
            print()
            print("1. Open this URL in your browser:")
            print(f"   https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={brand_name}")
            print()
            print("2. Scroll through the ads you want to track")
            print()
            print("3. For each ad, note:")
            print("   - Page name (advertiser)")
            print("   - Ad text/copy")
            print("   - Start date")
            print("   - Platforms (Facebook, Instagram, etc.)")
            print("   - Creative type (image, video, carousel)")
            print()
            print("4. Create a JSON file with this structure:")
            print("""
{
  "brand": "Mamaearth",
  "ads": [
    {
      "page_name": "Mamaearth",
      "ad_text": "Get glowing skin with our Vitamin C Face Wash...",
      "start_date": "2024-01-15",
      "platforms": ["Facebook", "Instagram"],
      "is_active": true,
      "creative_type": "image"
    }
  ]
}
            """)
            print()
            print("5. Save as: data/manual_ads_{brand_name}.json")
            print()
            print("We'll create a script to import this manual data into the system.")
        
        return ads_data
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []


def extract_ads_from_json(data, ads=None):
    """Recursively extract ad data from JSON structure."""
    if ads is None:
        ads = []
    
    if isinstance(data, dict):
        # Look for ad-like structures
        if 'snapshot' in data or 'adArchiveID' in data or 'pageID' in data:
            ad_info = {
                'ad_id': data.get('adArchiveID') or data.get('id'),
                'page_name': data.get('pageName'),
                'ad_text': data.get('snapshot', {}).get('body_text') if isinstance(data.get('snapshot'), dict) else None,
                'start_date': data.get('startDate'),
                'platforms': data.get('publisherPlatforms', []),
            }
            if ad_info['ad_id']:
                ads.append(ad_info)
        
        # Recurse into nested structures
        for value in data.values():
            extract_ads_from_json(value, ads)
    
    elif isinstance(data, list):
        for item in data:
            extract_ads_from_json(item, ads)
    
    return ads


def extract_ad_from_card(card):
    """Extract ad information from an HTML card element."""
    try:
        ad_info = {
            'page_name': None,
            'ad_text': None,
            'start_date': None,
            'platforms': [],
            'is_active': True
        }
        
        # Try to extract page name
        page_elem = card.find('div', string=re.compile('Page name', re.I))
        if page_elem:
            ad_info['page_name'] = page_elem.get_text(strip=True)
        
        # Try to extract ad text
        text_elem = card.find('div', {'class': re.compile('ad.*body|ad.*text', re.I)})
        if text_elem:
            ad_info['ad_text'] = text_elem.get_text(strip=True)
        
        # Try to extract date
        date_elem = card.find('div', string=re.compile('Started running', re.I))
        if date_elem:
            ad_info['start_date'] = date_elem.get_text(strip=True)
        
        return ad_info if ad_info['page_name'] else None
    
    except:
        return None


def create_manual_import_template(brand_name):
    """Create a template JSON file for manual data entry."""
    template = {
        "brand": brand_name,
        "collection_date": datetime.now().isoformat(),
        "source": "manual_facebook_ads_library",
        "ads": [
            {
                "page_name": "Example Brand",
                "ad_text": "Example ad copy text here...",
                "start_date": "2024-01-15",
                "stop_date": None,
                "platforms": ["Facebook", "Instagram"],
                "is_active": True,
                "creative_type": "image",
                "creative_url": "https://www.facebook.com/ads/library/?id=123456",
                "notes": "Any additional notes about this ad"
            }
        ]
    }
    
    filename = f"data/manual_ads_{brand_name.lower().replace(' ', '_')}.json"
    
    import os
    os.makedirs('data', exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✓ Created template file: {filename}")
    print("  Edit this file to add your manually collected ad data")
    
    return filename


def main():
    print("=" * 70)
    print("Meta Ads Library Web Scraper")
    print("=" * 70)
    print()
    
    brands = ["Mamaearth", "Plum Goodness", "Minimalist", "The Derma Co"]
    
    for brand in brands:
        print(f"\n{'='*70}")
        ads = scrape_ads_library(brand, country='IN', limit=10)
        
        if ads:
            print(f"✅ Extracted {len(ads)} ads for {brand}")
            for i, ad in enumerate(ads[:3], 1):
                print(f"\n{i}. {ad.get('page_name', 'Unknown')}")
                print(f"   Text: {ad.get('ad_text', 'N/A')[:60]}...")
        else:
            print(f"⚠️  No ads extracted automatically for {brand}")
            print("   Creating manual import template...")
            create_manual_import_template(brand)
        
        time.sleep(2)  # Be respectful with requests
    
    print()
    print("=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print()
    print("Since Facebook Ads Library uses heavy JavaScript rendering,")
    print("automated scraping is challenging. Here are your options:")
    print()
    print("Option 1: Manual Collection (Recommended for MVP)")
    print("  - Browse the Ads Library manually")
    print("  - Fill in the JSON templates created in data/ folder")
    print("  - Run: python3 scripts/import_manual_ads.py")
    print()
    print("Option 2: Use Selenium/Playwright (More Complex)")
    print("  - Install browser automation tools")
    print("  - Wait for JavaScript to render")
    print("  - Extract data from rendered page")
    print()
    print("Option 3: Fix Meta API Access (Best Long-term)")
    print("  - Add Marketing API product to your app")
    print("  - Use App Access Token")
    print("  - Automated collection every 15 minutes")


if __name__ == '__main__':
    main()
