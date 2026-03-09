#!/usr/bin/env python3
"""
Import manually collected ad data from JSON files into the system.
This allows you to manually browse Facebook Ads Library and save the data.
"""
import json
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def import_manual_ads(json_file):
    """
    Import ads from a manually created JSON file.
    
    Args:
        json_file: Path to JSON file with ad data
    """
    print(f"Importing ads from: {json_file}")
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        brand = data.get('brand', 'Unknown')
        ads = data.get('ads', [])
        
        print(f"Brand: {brand}")
        print(f"Ads found: {len(ads)}")
        print()
        
        imported_ads = []
        
        for i, ad in enumerate(ads, 1):
            print(f"{i}. {ad.get('page_name', 'Unknown')}")
            print(f"   Text: {ad.get('ad_text', 'N/A')[:60]}...")
            print(f"   Platforms: {', '.join(ad.get('platforms', []))}")
            print(f"   Active: {'Yes' if ad.get('is_active') else 'No'}")
            
            # Transform to internal format
            ad_data = {
                'ad_id': f"manual-{brand.lower().replace(' ', '-')}-{i}",
                'competitor_id': f"comp-{brand.lower().replace(' ', '-')}",
                'competitor_name': brand,
                'page_name': ad.get('page_name', brand),
                'scraped_at': int(datetime.now().timestamp() * 1000),
                'ad_text': ad.get('ad_text', ''),
                'creative_url': ad.get('creative_url', ''),
                'platform': ad.get('platforms', ['facebook'])[0] if ad.get('platforms') else 'facebook',
                'platforms': ad.get('platforms', ['facebook']),
                'is_active': ad.get('is_active', True),
                'start_date': self._parse_date_string(ad.get('start_date')),
                'stop_date': self._parse_date_string(ad.get('stop_date')) if ad.get('stop_date') else None,
                'creative_type': ad.get('creative_type', 'unknown'),
                'source': 'manual_import',
                'notes': ad.get('notes', '')
            }
            
            imported_ads.append(ad_data)
            print()
        
        # Save to output file
        output_file = json_file.replace('.json', '_imported.json')
        with open(output_file, 'w') as f:
            json.dump(imported_ads, f, indent=2)
        
        print(f"✅ Imported {len(imported_ads)} ads")
        print(f"✓ Saved to: {output_file}")
        print()
        print("Next steps:")
        print("1. Review the imported data in the output file")
        print("2. Deploy to AWS and upload this data to DynamoDB")
        print("3. Run AI analysis on the imported ads")
        
        return imported_ads
    
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
        print()
        print("Create the file first by running:")
        print("  python3 scripts/scrape_ads_library.py")
        return []
    
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return []
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def _parse_date_string(date_str):
    """Parse date string to timestamp."""
    if not date_str:
        return None
    
    try:
        # Try ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return int(dt.timestamp() * 1000)
    except:
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return int(dt.timestamp() * 1000)
                except:
                    continue
        except:
            pass
    
    return None


def main():
    print("=" * 70)
    print("Manual Ads Data Importer")
    print("=" * 70)
    print()
    
    # Look for JSON files in data directory
    data_dir = 'data'
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        print()
        print("Run this first to create templates:")
        print("  python3 scripts/scrape_ads_library.py")
        return
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and not f.endswith('_imported.json')]
    
    if not json_files:
        print(f"❌ No JSON files found in {data_dir}/")
        print()
        print("Run this first to create templates:")
        print("  python3 scripts/scrape_ads_library.py")
        return
    
    print(f"Found {len(json_files)} data file(s):")
    for f in json_files:
        print(f"  - {f}")
    print()
    
    # Import each file
    for json_file in json_files:
        file_path = os.path.join(data_dir, json_file)
        import_manual_ads(file_path)
        print()


if __name__ == '__main__':
    main()
