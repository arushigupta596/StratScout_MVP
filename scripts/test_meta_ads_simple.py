#!/usr/bin/env python3
"""
Simple test script for Meta Ads Library API - No AWS dependencies required.
Run this locally to verify your API access before deploying.
"""
import os
import sys
import json
import requests

def test_meta_ads_api():
    """Test Meta Ads API integration without AWS dependencies."""
    
    print("=" * 60)
    print("StratScout - Meta Ads Library API Test (Simple)")
    print("=" * 60)
    print()
    
    # Check for access token
    access_token = os.environ.get('META_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ ERROR: META_ACCESS_TOKEN not found in environment variables")
        print()
        print("Please set your Meta access token:")
        print("  export META_ACCESS_TOKEN='your_token_here'")
        print()
        print("See docs/META_ADS_SETUP.md for instructions on getting a token.")
        return False
    
    print(f"✓ Access token found (length: {len(access_token)})")
    print()
    
    # Test API endpoint
    api_url = "https://graph.facebook.com/v21.0/ads_archive"
    
    # Test with Mamaearth
    test_brand = "Mamaearth"
    
    print(f"Testing API with brand: {test_brand}")
    print()
    
    params = {
        'access_token': access_token,
        'search_terms': test_brand,
        'ad_reached_countries': 'IN',
        'ad_active_status': 'ALL',
        'limit': 10,
        'fields': ','.join([
            'id',
            'ad_creative_bodies',
            'ad_creative_link_titles',
            'ad_creative_link_descriptions',
            'ad_delivery_start_time',
            'ad_delivery_stop_time',
            'ad_snapshot_url',
            'page_name',
            'page_id',
            'publisher_platforms',
        ])
    }
    
    try:
        print("Fetching ads from Meta Ads Library...")
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        ads = data.get('data', [])
        
        print(f"✓ Successfully fetched {len(ads)} ads")
        print()
        
        if ads:
            print("Sample ad data:")
            print("-" * 60)
            sample_ad = ads[0]
            
            # Extract ad text
            ad_text_parts = []
            if sample_ad.get('ad_creative_bodies'):
                ad_text_parts.extend(sample_ad['ad_creative_bodies'])
            if sample_ad.get('ad_creative_link_titles'):
                ad_text_parts.extend(sample_ad['ad_creative_link_titles'])
            
            ad_text = ' | '.join(filter(None, ad_text_parts))
            
            print(f"Ad ID: {sample_ad.get('id')}")
            print(f"Page Name: {sample_ad.get('page_name')}")
            print(f"Page ID: {sample_ad.get('page_id')}")
            print(f"Platforms: {', '.join(sample_ad.get('publisher_platforms', []))}")
            print(f"Start Date: {sample_ad.get('ad_delivery_start_time', 'N/A')}")
            print(f"Stop Date: {sample_ad.get('ad_delivery_stop_time', 'Active')}")
            print(f"Ad Text: {ad_text[:100]}...")
            print(f"Snapshot URL: {sample_ad.get('ad_snapshot_url', 'N/A')}")
            print("-" * 60)
            print()
            
            # Show all ads summary
            print("All ads summary:")
            for i, ad in enumerate(ads, 1):
                is_active = ad.get('ad_delivery_stop_time') is None
                status = "🟢 Active" if is_active else "🔴 Inactive"
                
                # Get ad text
                text_parts = []
                if ad.get('ad_creative_bodies'):
                    text_parts.extend(ad['ad_creative_bodies'])
                text = ' '.join(filter(None, text_parts))[:50]
                
                print(f"{i}. {status} - {ad.get('page_name')} - {text}...")
            
            print()
            print("✅ Meta Ads API integration is working!")
            print()
            print("Next steps:")
            print("1. Install full dependencies: pip install -r backend/requirements.txt")
            print("2. Review the competitor list in backend/data_ingestion/meta_ads/client.py")
            print("3. Add your desired Indian skincare brands")
            print("4. Deploy to AWS with: cd infrastructure && cdk deploy")
            
            return True
        else:
            print("⚠️  No ads found for this brand")
            print()
            print("This could mean:")
            print("- The brand is not currently running ads in India")
            print("- The search term doesn't match their Facebook page name")
            print("- Try different search terms or brands")
            
            return False
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP ERROR: {e}")
        print()
        if e.response.status_code == 400:
            error_data = e.response.json()
            print(f"Error message: {error_data.get('error', {}).get('message', 'Unknown error')}")
            print()
            print("Common issues:")
            print("- Invalid or expired access token")
            print("- Token doesn't have access to Ads Library API")
        elif e.response.status_code == 429:
            print("Rate limit exceeded - wait an hour and try again")
        else:
            print(f"Status code: {e.response.status_code}")
        
        return False
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Common issues:")
        print("- Invalid or expired access token")
        print("- Network connectivity issues")
        print("- Rate limit exceeded (wait an hour)")
        print()
        print("Check the error details above and see docs/META_ADS_SETUP.md")
        
        return False


def test_multiple_brands():
    """Test with multiple brands."""
    
    print()
    print("=" * 60)
    print("Testing Multiple Brands")
    print("=" * 60)
    print()
    
    access_token = os.environ.get('META_ACCESS_TOKEN')
    api_url = "https://graph.facebook.com/v18.0/ads_archive"
    
    brands_to_test = [
        'Mamaearth',
        'Plum Goodness',
        'Minimalist',
        'The Derma Co',
    ]
    
    results = {}
    
    for brand in brands_to_test:
        print(f"Fetching ads for {brand}...")
        
        params = {
            'access_token': access_token,
            'search_terms': brand,
            'ad_reached_countries': 'IN',
            'limit': 10,
            'fields': 'id,page_name'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            ads = data.get('data', [])
            results[brand] = len(ads)
            print(f"  ✓ Found {len(ads)} ads")
        except Exception as e:
            results[brand] = f"Error: {str(e)}"
            print(f"  ❌ Error: {str(e)}")
    
    print()
    print("Summary:")
    print("-" * 60)
    for brand, count in results.items():
        print(f"{brand}: {count}")
    print("-" * 60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Meta Ads Library API integration (simple version)')
    parser.add_argument('--multiple', action='store_true', help='Test multiple brands')
    args = parser.parse_args()
    
    success = test_meta_ads_api()
    
    if success and args.multiple:
        test_multiple_brands()
    
    sys.exit(0 if success else 1)
