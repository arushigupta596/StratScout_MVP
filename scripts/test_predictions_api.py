#!/usr/bin/env python3
"""
Test predictions API locally
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set environment variables
os.environ['PREDICTION_TABLE'] = 'StratScout-Predictions'
os.environ['AD_DATA_TABLE'] = 'StratScout-Ads'
os.environ['ANALYSIS_TABLE'] = 'StratScout-Analysis'
os.environ['COMPETITOR_TABLE'] = 'StratScout-Competitors'
os.environ['GAP_ANALYSIS_TABLE'] = 'StratScout-GapAnalysis'
os.environ['CONVERSATION_TABLE'] = 'StratScout-Conversations'

from predictions.handler import main

event = {
    'httpMethod': 'GET',
    'queryStringParameters': None,
    'headers': {},
    'body': None
}

print("Testing Predictions Handler...")
result = main(event, None)
print(f"\nStatus Code: {result['statusCode']}")
print(f"\nHeaders: {json.dumps(result['headers'], indent=2)}")
print(f"\nBody (first 500 chars):")
body = result['body']
print(body[:500])

# Try to parse the body
try:
    parsed = json.loads(body)
    print(f"\n✓ Body is valid JSON")
    print(f"Type: {type(parsed)}")
    if isinstance(parsed, list):
        print(f"Array length: {len(parsed)}")
        if len(parsed) > 0:
            print(f"\nFirst item keys: {list(parsed[0].keys())}")
            print(f"\nFirst item:")
            print(json.dumps(parsed[0], indent=2))
    else:
        print(f"Keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'Not a dict'}")
except Exception as e:
    print(f"\n✗ Failed to parse body: {e}")
