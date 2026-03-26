#!/usr/bin/env python3
"""
Test Lambda handlers locally
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set environment variables
os.environ['PREDICTION_TABLE'] = 'StratScout-Predictions'
os.environ['GAP_ANALYSIS_TABLE'] = 'StratScout-GapAnalysis'
os.environ['CONVERSATION_TABLE'] = 'StratScout-Conversations'
os.environ['COMPETITOR_TABLE'] = 'StratScout-Competitors'
os.environ['AD_DATA_TABLE'] = 'StratScout-Ads'
os.environ['ANALYSIS_TABLE'] = 'StratScout-Analysis'

print("Testing Predictions Handler...")
try:
    from predictions.handler import main as predictions_main
    event = {'httpMethod': 'GET', 'queryStringParameters': None}
    result = predictions_main(event, None)
    print(f"Status: {result['statusCode']}")
    print(f"Body preview: {result['body'][:200]}...")
    print("✓ Predictions handler works!")
except Exception as e:
    print(f"✗ Predictions handler error: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting Gap Analysis Handler...")
try:
    from gap_analysis.handler import main as gap_main
    event = {'httpMethod': 'GET', 'queryStringParameters': None}
    result = gap_main(event, None)
    print(f"Status: {result['statusCode']}")
    print(f"Body preview: {result['body'][:200]}...")
    print("✓ Gap analysis handler works!")
except Exception as e:
    print(f"✗ Gap analysis handler error: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting Scout Handler...")
try:
    from scout_chatbot.handler import main as scout_main
    event = {
        'httpMethod': 'POST',
        'body': '{"message": "Hello"}',
        'requestContext': {'authorizer': {'claims': {'sub': 'test-user'}}}
    }
    result = scout_main(event, None)
    print(f"Status: {result['statusCode']}")
    print(f"Body preview: {result['body'][:200]}...")
    print("✓ Scout handler works!")
except Exception as e:
    print(f"✗ Scout handler error: {e}")
    import traceback
    traceback.print_exc()
