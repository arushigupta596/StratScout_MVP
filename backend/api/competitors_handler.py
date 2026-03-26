"""
Competitors API Handler
"""
import json
import boto3
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.json_encoder import dumps_decimal

logger = get_logger(__name__)


class CompetitorsHandler:
    """Handler for competitor API operations."""
    
    def __init__(self):
        """Initialize handler."""
        self.dynamodb = boto3.resource('dynamodb')
        self.competitor_table = self.dynamodb.Table(Config.COMPETITOR_TABLE)
        self.ad_table = self.dynamodb.Table(Config.AD_DATA_TABLE)
    
    def get_competitors(self) -> List[Dict[str, Any]]:
        """Get all competitors."""
        try:
            response = self.competitor_table.scan()
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get competitors: {str(e)}")
            return []
    
    def get_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """Get a specific competitor."""
        try:
            response = self.competitor_table.get_item(
                Key={'competitorId': competitor_id}
            )
            competitor = response.get('Item', {})
            
            if competitor:
                # Get ad count
                ad_response = self.ad_table.query(
                    IndexName='CompetitorIndex',
                    KeyConditionExpression='competitor_id = :cid',
                    ExpressionAttributeValues={':cid': competitor_id},
                    Select='COUNT'
                )
                competitor['ad_count'] = ad_response.get('Count', 0)
            
            return competitor
        except Exception as e:
            logger.error(f"Failed to get competitor: {str(e)}")
            return {}


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for competitors API.
    
    Args:
        event: Lambda event
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    logger.info('Competitors API handler started', extra={'event': event})
    
    try:
        handler = CompetitorsHandler()
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        path_parameters = event.get('pathParameters') or {}
        competitor_id = path_parameters.get('competitorId')
        
        # Handle GET single competitor
        if http_method == 'GET' and competitor_id:
            competitor = handler.get_competitor(competitor_id)
            
            if not competitor:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Competitor not found'
                    })
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal(competitor)
            }
        
        # Handle GET all competitors
        elif http_method == 'GET':
            competitors = handler.get_competitors()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal(competitors)
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Method not allowed'
                })
            }
    
    except Exception as e:
        logger.error(f"Competitors API handler failed: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
