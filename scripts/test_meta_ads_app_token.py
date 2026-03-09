#!/usr/bin/env python3
"""
Test Meta Ads Library API with App Access Token (recommended approach)
"""
import os
import sys
import json
import requests

def get_app_access_token(app_id, app_secret):
    """Get App Access Token from Meta."""
    print("Getting App Access Token...")
    
    token_resp = requests.get(
        "https://graph.facebook.com/oauth/access_token",
        params={
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "client_credentials"
        }
    )
    
    if token_resp.status_code != 200:
        print(f"❌ Failed to get token: {token_resp.text}")
        return None
    
    data = token_resp.json()
    token = data.get("access_token")
    print(f"✓ Got App Access Token: {token[:50]}...")
    return token


def test_ads_library(access_token, brand="Mamaearth"):
    """Test Ads Library API."""
    print(f"\nSearching for ads from: {brand}")
    
    resp = requests.get(
        "https://graph.facebook.com/v21.0/ads_archive",
        params={
            "access_token": access_token,
            "search_terms": brand,
            "ad_reached_countries": '["IN"]',  # JSON array format
            "ad_active_status": "ALL",
            "limit": 10,
            "fields": "id,ad_creative_bodies,page_name,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,publisher_platforms"
        }
    )
    
    data = resp.json()
    
    if "error" in data:
        print(f"❌ Error: {data['error']['message']}")
        print(f"   Code: {data['error'].get('code')}")
        print(f"   Subcode: {data['error'].get('error_subcode')}")
        return False
    
    ads = data.get("data", [])
    print(f"✅ Success! Found {len(ads)} ads")
    print()
    
    if ads:
        print("Sample ads:")
        print("-" * 70)
        for i, ad in enumerate(ads[:5], 1):
            page_name = ad.get('page_name', 'Unknown')
            ad_id = ad.get('id', 'N/A')
            platforms = ', '.join(ad.get('publisher_platforms', []))
            is_active = ad.get('ad_delivery_stop_time') is None
            status = "🟢 Active" if is_active else "🔴 Inactive"
            
            # Get ad text
            bodies = ad.get('ad_creative_bodies', [])
            ad_text = bodies[0][:60] if bodies else "No text"
            
            print(f"{i}. {status} | {page_name}")
            print(f"   ID: {ad_id}")
            print(f"   Platforms: {platforms}")
            print(f"   Text: {ad_text}...")
            print()
        
        print("-" * 70)
        print()
        print("✅ Meta Ads Library API is working!")
        print()
        print("Next steps:")
        print("1. Save your APP_ID and APP_SECRET in .env file")
        print("2. Update backend/common/config.py to use app token")
        print("3. Deploy to AWS: cd infrastructure && cdk deploy")
        
        return True
    else:
        print("⚠️  No ads found for this brand")
        print("Try a different brand or check if they're running ads in India")
        return False


def main():
    print("=" * 70)
    print("StratScout - Meta Ads Library API Test (App Access Token)")
    print("=" * 70)
    print()
    
    # Get credentials from environment or .env file
    app_id = os.environ.get('META_APP_ID')
    app_secret = os.environ.get('META_APP_SECRET')
    
    # Alternative: use direct app token format (APP_ID|APP_SECRET)
    direct_token = os.environ.get('META_ACCESS_TOKEN')
    
    if direct_token and '|' in direct_token:
        print("Using direct App Access Token format (APP_ID|APP_SECRET)")
        access_token = direct_token
    elif app_id and app_secret:
        print(f"Using APP_ID: {app_id}")
        access_token = get_app_access_token(app_id, app_secret)
        if not access_token:
            return False
    else:
        print("❌ ERROR: Missing credentials")
        print()
        print("Please set one of:")
        print("  Option 1: export META_APP_ID='your_app_id'")
        print("            export META_APP_SECRET='your_app_secret'")
        print()
        print("  Option 2: export META_ACCESS_TOKEN='app_id|app_secret'")
        print()
        print("Find these in your Meta App Dashboard:")
        print("  https://developers.facebook.com/apps/")
        print("  → Your App → Settings → Basic")
        return False
    
    # Test with multiple brands
    brands = ["Mamaearth", "Plum Goodness", "Minimalist"]
    
    success = False
    for brand in brands:
        if test_ads_library(access_token, brand):
            success = True
            break
        print()
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
