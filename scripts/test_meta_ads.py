#!/usr/bin/env python3
"""
Test script for Meta Ads Library API integration.
Run this locally to verify your API access before deploying to AWS.
"""
import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from data_ingestion.meta_ads.client import MetaAdsClient
from common.logger import get_logger

logger = get_logger(__name__)


def test_meta_ads_api():
    """Test Meta Ads API integration."""
    
    print("=" * 60)
    print("StratScout - Meta Ads Library API Test")
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
    
    # Initialize client
    print("Initializing Meta Ads client...")
    client = MetaAdsClient()
    print("✓ Client initialized")
    print()
    
    # Test with a single brand
    test_competitor = {
        'id': 'comp-test',
        'name': 'Mamaearth',
        'search_terms': ['Mamaearth'],
        'page_id': None,
    }
    
    print(f"Testing API with brand: {test_competitor['name']}")
    print(f"Search terms: {test_competitor['search_terms']}")
    print()
    
    try:
        # Collect ads
        print("Fetching ads from Meta Ads Library...")
        ads = client._fetch_competitor_ads(test_competitor)
        
        print(f"✓ Successfully fetched {len(ads)} ads")
        print()
        
        if ads:
            print("Sample ad data:")
            print("-" * 60)
            sample_ad = ads[0]
            print(f"Ad ID: {sample_ad.get('ad_id')}")
            print(f"Meta Ad ID: {sample_ad.get('meta_ad_id')}")
            print(f"Page Name: {sample_ad.get('page_name')}")
            print(f"Platform: {sample_ad.get('platform')}")
            print(f"Is Active: {sample_ad.get('is_active')}")
            print(f"Ad Text: {sample_ad.get('ad_text', '')[:100]}...")
            print(f"Creative URL: {sample_ad.get('creative_url', 'N/A')}")
            print("-" * 60)
            print()
            
            # Show all ads summary
            print("All ads summary:")
            for i, ad in enumerate(ads[:10], 1):  # Show first 10
                status = "🟢 Active" if ad.get('is_active') else "🔴 Inactive"
                print(f"{i}. {status} - {ad.get('page_name')} - {ad.get('ad_text', '')[:50]}...")
            
            if len(ads) > 10:
                print(f"... and {len(ads) - 10} more ads")
            
            print()
            print("✅ Meta Ads API integration is working!")
            print()
            print("Next steps:")
            print("1. Review the competitor list in backend/data_ingestion/meta_ads/client.py")
            print("2. Add your desired Indian skincare brands")
            print("3. Deploy to AWS with: cd infrastructure && cdk deploy")
            
            return True
        else:
            print("⚠️  No ads found for this brand")
            print()
            print("This could mean:")
            print("- The brand is not currently running ads in India")
            print("- The search term doesn't match their Facebook page name")
            print("- Try different search terms or brands")
            
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Common issues:")
        print("- Invalid or expired access token")
        print("- Rate limit exceeded (wait an hour)")
        print("- Network connectivity issues")
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
    
    client = MetaAdsClient()
    
    brands_to_test = [
        {'id': 'comp-mamaearth', 'name': 'Mamaearth', 'search_terms': ['Mamaearth']},
        {'id': 'comp-plum', 'name': 'Plum', 'search_terms': ['Plum Goodness']},
        {'id': 'comp-minimalist', 'name': 'Minimalist', 'search_terms': ['Minimalist']},
    ]
    
    results = {}
    
    for brand in brands_to_test:
        print(f"Fetching ads for {brand['name']}...")
        try:
            ads = client._fetch_competitor_ads(brand)
            results[brand['name']] = len(ads)
            print(f"  ✓ Found {len(ads)} ads")
        except Exception as e:
            results[brand['name']] = f"Error: {str(e)}"
            print(f"  ❌ Error: {str(e)}")
    
    print()
    print("Summary:")
    print("-" * 60)
    for brand, count in results.items():
        print(f"{brand}: {count}")
    print("-" * 60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Meta Ads Library API integration')
    parser.add_argument('--multiple', action='store_true', help='Test multiple brands')
    args = parser.parse_args()
    
    success = test_meta_ads_api()
    
    if success and args.multiple:
        test_multiple_brands()
    
    sys.exit(0 if success else 1)
