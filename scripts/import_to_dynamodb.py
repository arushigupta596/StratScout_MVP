#!/usr/bin/env python3
"""
Import scraped ad data from JSON files into DynamoDB tables.
"""
import json
import os
import sys
import boto3
from datetime import datetime
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Table names from CloudFormation outputs
COMPETITOR_TABLE = 'StratScoutStack-DataLayerCompetitorTable'
AD_DATA_TABLE = 'StratScoutStack-DataLayerAdDataTable'

def convert_floats_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB."""
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj

def get_table_name(partial_name):
    """Get full table name from CloudFormation stack."""
    cf = boto3.client('cloudformation', region_name='us-east-1')
    try:
        response = cf.describe_stacks(StackName='StratScoutStack')
        outputs = response['Stacks'][0].get('Outputs', [])
        
        # Try to find table name in outputs or resources
        resources = cf.list_stack_resources(StackName='StratScoutStack')
        for resource in resources['StackResourceSummaries']:
            if partial_name in resource['LogicalResourceId']:
                return resource['PhysicalResourceId']
    except Exception as e:
        print(f"Warning: Could not get table name from CloudFormation: {e}")
    
    return None

def import_competitor(brand_name, brand_data):
    """Import competitor data into CompetitorTable."""
    competitor_table_name = get_table_name('CompetitorTable')
    if not competitor_table_name:
        # Fallback to known table name
        competitor_table_name = 'StratScout-Competitors'
    
    table = dynamodb.Table(competitor_table_name)
    
    competitor_id = f"comp-{brand_name.lower().replace(' ', '-').replace('&', 'and')}"
    
    competitor_item = {
        'competitorId': competitor_id,  # camelCase for DynamoDB
        'name': brand_name,
        'industry': 'D2C Skincare',
        'country': 'India',
        'created_at': int(datetime.now().timestamp() * 1000),
        'updated_at': int(datetime.now().timestamp() * 1000),
        'total_ads': len(brand_data.get('ads', [])),
        'active_ads': sum(1 for ad in brand_data.get('ads', []) if ad.get('is_active', True)),
        'platforms': list(set(
            platform 
            for ad in brand_data.get('ads', []) 
            for platform in ad.get('platforms', ['facebook'])
        )),
        'metadata': {
            'source': 'manual_scrape',
            'import_date': datetime.now().isoformat()
        }
    }
    
    try:
        table.put_item(Item=convert_floats_to_decimal(competitor_item))
        print(f"✅ Imported competitor: {brand_name} ({competitor_id})")
        return competitor_id
    except Exception as e:
        print(f"❌ Error importing competitor {brand_name}: {e}")
        return None

def import_ads(competitor_id, brand_name, ads_data):
    """Import ad data into AdDataTable."""
    ad_table_name = get_table_name('AdDataTable')
    if not ad_table_name:
        # Fallback to known table name
        ad_table_name = 'StratScout-Ads'
    
    table = dynamodb.Table(ad_table_name)
    
    imported_count = 0
    
    for i, ad in enumerate(ads_data, 1):
        ad_id = f"{competitor_id}-ad-{i}"
        
        # Parse dates
        start_date = ad.get('start_date', '')
        if start_date and not isinstance(start_date, int):
            try:
                dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                start_date = int(dt.timestamp() * 1000)
            except:
                start_date = int(datetime.now().timestamp() * 1000)
        elif not start_date:
            start_date = int(datetime.now().timestamp() * 1000)
        
        # Create timestamp for sort key
        timestamp = datetime.now().isoformat()
        
        ad_item = {
            'ad_id': ad_id,
            'timestamp': timestamp,  # Required sort key
            'competitor_id': competitor_id,
            'competitor_name': brand_name,
            'page_name': ad.get('page_name', brand_name),
            'scraped_at': int(datetime.now().timestamp() * 1000),
            'ad_text': ad.get('ad_text', '')[:5000],  # Limit text length
            'creative_url': ad.get('creative_url', ''),
            'platform': ad.get('platforms', ['facebook'])[0] if ad.get('platforms') else 'facebook',
            'platforms': ad.get('platforms', ['facebook']),
            'is_active': ad.get('is_active', True),
            'start_date': start_date,
            'creative_type': ad.get('creative_type', 'image'),
            'source': 'manual_scrape',
            'metadata': {
                'import_date': datetime.now().isoformat(),
                'original_index': i
            }
        }
        
        # Add optional fields if present
        if ad.get('stop_date'):
            try:
                dt = datetime.fromisoformat(ad['stop_date'].replace('Z', '+00:00'))
                ad_item['stop_date'] = int(dt.timestamp() * 1000)
            except:
                pass
        
        if ad.get('notes'):
            ad_item['notes'] = ad['notes']
        
        try:
            table.put_item(Item=convert_floats_to_decimal(ad_item))
            imported_count += 1
            if imported_count % 10 == 0:
                print(f"  Imported {imported_count}/{len(ads_data)} ads...")
        except Exception as e:
            print(f"  ⚠️  Error importing ad {i}: {e}")
    
    return imported_count

def import_json_file(json_file_path):
    """Import data from a single JSON file."""
    print(f"\n{'='*70}")
    print(f"Importing: {os.path.basename(json_file_path)}")
    print('='*70)
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        brand_name = data.get('brand', 'Unknown')
        ads = data.get('ads', [])
        
        print(f"Brand: {brand_name}")
        print(f"Total ads: {len(ads)}")
        
        # Import competitor
        competitor_id = import_competitor(brand_name, data)
        if not competitor_id:
            return False
        
        # Import ads
        print(f"\nImporting ads...")
        imported_count = import_ads(competitor_id, brand_name, ads)
        
        print(f"\n✅ Successfully imported {imported_count}/{len(ads)} ads for {brand_name}")
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("StratScout - Import Scraped Ads to DynamoDB")
    print("="*70)
    
    # Check data directory (handle both root and subdirectory execution)
    data_dir = 'data' if os.path.exists('data') else '../data'
    if not os.path.exists(data_dir):
        print(f"\n❌ Data directory not found: {data_dir}")
        return
    
    # Find JSON files
    json_files = [
        f for f in os.listdir(data_dir) 
        if f.endswith('.json') and not f.endswith('_imported.json')
    ]
    
    if not json_files:
        print(f"\n❌ No JSON files found in {data_dir}/")
        return
    
    print(f"\nFound {len(json_files)} data file(s):")
    for f in json_files:
        file_path = os.path.join(data_dir, f)
        file_size = os.path.getsize(file_path) / 1024  # KB
        print(f"  - {f} ({file_size:.1f} KB)")
    
    # Import each file
    success_count = 0
    for json_file in json_files:
        file_path = os.path.join(data_dir, json_file)
        if import_json_file(file_path):
            success_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"Import Complete!")
    print(f"{'='*70}")
    print(f"Successfully imported: {success_count}/{len(json_files)} files")
    print()
    print("Next steps:")
    print("1. Visit your app: https://dh9mb4macowil.cloudfront.net")
    print("2. Create a Cognito user to log in")
    print("3. Explore the dashboard with real data!")
    print()

if __name__ == '__main__':
    main()
