#!/usr/bin/env python3
"""
Test Scout AI API locally
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

from scout_chatbot.handler import main

event = {
    'httpMethod': 'POST',
    'body': json.dumps({'message': 'Hello'}),
    'requestContext': {
        'authorizer': {
            'claims': {
                'sub': 'test-user-123'
            }
        }
    }
}

print("Testing Scout AI Handler...")
try:
    result = main(event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print(f"\nHeaders: {json.dumps(result['headers'], indent=2)}")
    print(f"\nBody:")
    body = result['body']
    parsed = json.loads(body)
    print(json.dumps(parsed, indent=2))
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
