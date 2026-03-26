#!/usr/bin/env python3
"""
Automated scraper for Meta Ads Library using Playwright.
This renders the JavaScript and extracts real ad data.
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from urllib.parse import quote
from playwright.async_api import async_playwright
import re

async def scrape_ads_library_automated(brand_name, country='IN', max_ads=250):
    """
    Scrape ads from Meta Ads Library using browser automation.
    
    Args:
        brand_name: Brand to search for
        country: Country code (default: IN for India)
        max_ads: Maximum number of ads to collect
    
    Returns:
        List of ad data dictionaries
    """
    print(f"🔍 Scraping Meta Ads Library for: {brand_name}")
    print(f"   Country: {country}")
    print(f"   Target ads: {max_ads}")
    print()
    
    # URL encode the brand name properly
    from urllib.parse import quote
    encoded_brand = quote(brand_name)
    url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={encoded_brand}&media_type=all"
    
    ads_data = []
    seen_ad_ids = set()
    
    async with async_playwright() as p:
        # Launch browser (headless=True for production)
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        try:
            print(f"📄 Loading page: {url}")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait for ads to load
            print("⏳ Waiting for ads to load...")
            await page.wait_for_timeout(5000)  # Wait 5 seconds for initial load
            
            # Scroll to load more ads - increased scrolling
            print(f"📜 Scrolling to load {max_ads} ads...")
            scroll_count = 0
            max_scrolls = 50  # Increased from 3 to 50
            no_new_ads_count = 0
            
            while len(ads_data) < max_ads and scroll_count < max_scrolls:
                previous_count = len(ads_data)
                
                # Scroll down
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)  # Wait 3 seconds for new ads to load
                scroll_count += 1
                
                # Extract ads after each scroll
                current_ads = await extract_ads_from_page(page, seen_ad_ids)
                ads_data.extend(current_ads)
                
                new_ads = len(ads_data) - previous_count
                print(f"   Scroll {scroll_count}/{max_scrolls}: {len(ads_data)} total ads (+{new_ads} new)")
                
                # Stop if no new ads found for 3 consecutive scrolls
                if new_ads == 0:
                    no_new_ads_count += 1
                    if no_new_ads_count >= 3:
                        print(f"   ⚠️  No new ads found after 3 scrolls. Stopping.")
                        break
                else:
                    no_new_ads_count = 0
                
                # Stop if we've reached the target
                if len(ads_data) >= max_ads:
                    print(f"   ✓ Target reached: {len(ads_data)} ads")
                    break
            
            print()
            print(f"✅ Successfully extracted {len(ads_data)} ads")
            
        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
        
        finally:
            await browser.close()
    
    return ads_data[:max_ads]  # Return up to max_ads


async def extract_ads_from_page(page, seen_ad_ids):
    """Extract ads from the current page state."""
    new_ads = []
    
    # Try multiple selectors for ad cards
    selectors = [
        '[data-testid*="search-result"]',
        '[data-testid*="ad-card"]',
        'div[role="article"]',
        'div._7jyr',  # Facebook's class for ad cards
    ]
    
    ad_elements = []
    for selector in selectors:
        elements = await page.query_selector_all(selector)
        if elements:
            ad_elements = elements
            break
    
    # Extract data from each ad card
    for idx, element in enumerate(ad_elements):
        try:
            # Get all text content from the ad card
            text_content = await element.inner_text()
            
            # Create a simple hash for deduplication
            content_hash = hash(text_content[:200])  # Use first 200 chars
            
            if content_hash in seen_ad_ids:
                continue
            
            seen_ad_ids.add(content_hash)
            
            # Extract structured data
            ad_data = await extract_ad_data(element, text_content, content_hash)
            
            if ad_data:
                new_ads.append(ad_data)
        
        except Exception as e:
            continue
    
    return new_ads


async def extract_ad_data(element, text_content, content_hash):
    """Extract structured data from an ad element."""
    
    ad_data = {
        'ad_id': f'scraped-{content_hash}',
        'page_name': None,
        'ad_text': None,
        'start_date': None,
        'stop_date': None,
        'platforms': [],
        'is_active': True,
        'creative_type': 'unknown',
        'scraped_at': datetime.now().isoformat(),
    }
    
    # Extract page name (usually at the top of the ad card)
    page_name_match = re.search(r'Page name[:\s]+([^\n]+)', text_content, re.IGNORECASE)
    if page_name_match:
        ad_data['page_name'] = page_name_match.group(1).strip()
    else:
        # Try to find it in the first few lines
        lines = text_content.split('\n')
        if lines:
            ad_data['page_name'] = lines[0].strip()
    
    # Extract start date
    date_match = re.search(r'Started running on ([^\n]+)', text_content, re.IGNORECASE)
    if date_match:
        ad_data['start_date'] = date_match.group(1).strip()
    
    # Check if still active
    if 'Stopped running' in text_content or 'Ended' in text_content:
        ad_data['is_active'] = False
        stop_match = re.search(r'Stopped running on ([^\n]+)', text_content, re.IGNORECASE)
        if stop_match:
            ad_data['stop_date'] = stop_match.group(1).strip()
    
    # Extract platforms
    if 'Facebook' in text_content:
        ad_data['platforms'].append('Facebook')
    if 'Instagram' in text_content:
        ad_data['platforms'].append('Instagram')
    if 'Messenger' in text_content:
        ad_data['platforms'].append('Messenger')
    
    # Extract ad text (usually the main body of text)
    # Remove metadata lines and keep the actual ad copy
    lines = text_content.split('\n')
    ad_text_lines = []
    skip_keywords = ['Page name', 'Started running', 'Stopped running', 'See ad details', 'Platforms']
    
    for line in lines:
        line = line.strip()
        if line and not any(keyword in line for keyword in skip_keywords):
            if len(line) > 20:  # Likely ad copy if longer than 20 chars
                ad_text_lines.append(line)
    
    if ad_text_lines:
        ad_data['ad_text'] = ' '.join(ad_text_lines[:3])  # Take first 3 lines
    
    # Determine creative type
    if 'video' in text_content.lower():
        ad_data['creative_type'] = 'video'
    elif 'carousel' in text_content.lower():
        ad_data['creative_type'] = 'carousel'
    elif 'image' in text_content.lower() or ad_data['ad_text']:
        ad_data['creative_type'] = 'image'
    
    return ad_data if ad_data['page_name'] else None


async def scrape_multiple_brands(brands, country='IN', max_ads_per_brand=20):
    """Scrape ads for multiple brands."""
    all_results = {}
    
    for brand_info in brands:
        # Support both string and dict format
        if isinstance(brand_info, dict):
            brand = brand_info['name']
            official_page = brand_info.get('official_page')
        else:
            brand = brand_info
            official_page = None
        
        print(f"\n{'='*70}")
        print(f"Brand: {brand}")
        if official_page:
            print(f"Official Page: {official_page}")
        print('='*70)
        
        ads = await scrape_ads_library_automated(brand, country, max_ads_per_brand)
        
        # Filter for official page if specified
        if official_page:
            original_count = len(ads)
            ads = [ad for ad in ads if official_page.lower() in ad.get('page_name', '').lower()]
            print(f"   Filtered: {original_count} → {len(ads)} ads (official page only)")
        
        all_results[brand] = ads
        
        # Save individual brand data
        filename = f"data/scraped_ads_{brand.lower().replace(' ', '_')}.json"
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump({
                'brand': brand,
                'collection_date': datetime.now().isoformat(),
                'source': 'automated_scraping',
                'country': country,
                'ads': ads
            }, f, indent=2)
        
        print(f"💾 Saved to: {filename}")
        
        # Wait between brands to be respectful
        if brand != brands[-1]:
            print("\n⏳ Waiting 5 seconds before next brand...")
            await asyncio.sleep(5)
    
    return all_results


async def main():
    print("=" * 70)
    print("Meta Ads Library - Automated Scraper (Playwright)")
    print("=" * 70)
    print()
    
    # Brands to scrape with official page names for filtering
    brands = [
        {"name": "Mamaearth", "official_page": "Mamaearth"},
        {"name": "Plum Goodness", "official_page": "Plum"},
        {"name": "Minimalist", "official_page": "Minimalist"},
        {"name": "The Derma Co", "official_page": "The Derma Co"},
        {"name": "Dot & Key", "official_page": "Dot & Key"}  # Official page name
    ]
    
    print("Brands to scrape:")
    for i, brand_info in enumerate(brands, 1):
        if isinstance(brand_info, dict):
            print(f"  {i}. {brand_info['name']} (Page: {brand_info.get('official_page', 'Any')})")
        else:
            print(f"  {i}. {brand_info}")
    print()
    
    # Scrape all brands
    results = await scrape_multiple_brands(brands, country='IN', max_ads_per_brand=250)
    
    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    for brand_info, ads in results.items():
        brand_name = brand_info if isinstance(brand_info, str) else brand_info
        print(f"{brand_name}: {len(ads)} ads collected")
    
    total_ads = sum(len(ads) for ads in results.values())
    print(f"\nTotal: {total_ads} ads collected")
    print()
    print("✅ Scraping complete!")
    print()
    print("Data saved in data/ folder:")
    print("  - scraped_ads_mamaearth.json")
    print("  - scraped_ads_plum_goodness.json")
    print("  - scraped_ads_minimalist.json")
    print("  - scraped_ads_the_derma_co.json")
    print("  - scraped_ads_dot_&_key.json")
    print()
    print("Next steps:")
    print("1. Review the JSON files to verify data quality")
    print("2. Run: python3 scripts/import_manual_ads.py")
    print("3. Deploy to AWS and start AI analysis")


if __name__ == '__main__':
    asyncio.run(main())
