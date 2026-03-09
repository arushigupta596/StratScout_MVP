"""
Custom JSON encoder for DynamoDB Decimal types
"""
import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that converts Decimal to int or float"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert to int if it's a whole number, otherwise float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        return super(DecimalEncoder, self).default(obj)


def dumps_decimal(obj):
    """Helper function to dump JSON with Decimal handling"""
    return json.dumps(obj, cls=DecimalEncoder)
