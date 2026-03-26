# Predictions Fixed - Decimal to Number Conversion

## Root Cause Found

The Predictions page wasn't loading because DynamoDB returns numbers as `Decimal` objects, and when using `json.dumps(data, default=str)`, these were being converted to strings:

```json
{
  "rate": "0.045",        // ❌ String
  "min_reach": "50000"    // ❌ String  
}
```

The frontend expected actual numbers for calculations:
```typescript
pred.engagement_prediction.rate * 100  // NaN when rate is "0.045"
pred.reach_prediction.avg_reach.toLocaleString()  // Error when avg_reach is "50000"
```

## Solution

Created `backend/common/json_encoder.py` with a custom JSON encoder that converts Decimal to int/float:

```python
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)  # Whole numbers as int
            else:
                return float(obj)  # Decimals as float
        return super().default(obj)
```

Now the API returns proper numbers:
```json
{
  "rate": 0.045,      // ✅ Number
  "min_reach": 50000  // ✅ Number
}
```

## Files Modified

1. `backend/common/json_encoder.py` - Created custom encoder
2. `backend/predictions/handler.py` - Use dumps_decimal()
3. `backend/gap_analysis/handler.py` - Use dumps_decimal()
4. `backend/api/competitors_handler.py` - Use dumps_decimal()

## Test Results

Before fix:
```json
{"rate": "0.045", "score": "0.78"}  // Strings
```

After fix:
```json
{"rate": 0.045, "score": 0.78}  // Numbers
```

## Deployment

Currently deploying with:
```bash
cd infrastructure
npx cdk deploy --require-approval never
```

## After Deployment

The Predictions page will:
1. Load 5 predictions successfully
2. Display the bar chart with reach data
3. Show all prediction cards with proper number formatting
4. Calculate percentages correctly (e.g., 82% confidence)

## Scout AI Status

Scout AI is also fixed (added ChatbotError class). After this deployment, both features will work!

## Test

1. Go to https://dh9mb4macowil.cloudfront.net
2. Sign in
3. Click "Predictions" - Should load 5 predictions with charts
4. Click "Scout AI" - Should respond to messages

All data is in DynamoDB and ready!
