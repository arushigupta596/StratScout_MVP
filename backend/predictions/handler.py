"""
Campaign Predictions Lambda Handler
"""
import json
import boto3
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.errors import PredictionError
from common.json_encoder import dumps_decimal
from predictions.campaign_predictor import CampaignPredictor
from ai_analysis.bedrock_client import BedrockClient

logger = get_logger(__name__)


class PredictionsHandler:
    """Handler for campaign prediction operations."""
    
    def __init__(self):
        """Initialize handler."""
        self.dynamodb = boto3.resource('dynamodb')
        self.ad_table = self.dynamodb.Table(Config.AD_DATA_TABLE)
        self.analysis_table = self.dynamodb.Table(Config.ANALYSIS_TABLE)
        self.prediction_table = self.dynamodb.Table(Config.PREDICTION_TABLE)
        
        self.predictor = CampaignPredictor()
        self.bedrock_client = BedrockClient()
    
    def predict_campaign_performance(
        self,
        competitor_id: str,
        campaign_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Predict campaign performance for a competitor.
        
        Args:
            competitor_id: Competitor ID
            campaign_data: Optional specific campaign data
        
        Returns:
            Prediction results
        """
        logger.info(f"Predicting campaign performance for: {competitor_id}")
        
        try:
            # Get historical data
            historical_ads = self._get_historical_ads(competitor_id)
            historical_analyses = self._get_historical_analyses(competitor_id)
            
            if not historical_ads:
                raise PredictionError(f"No historical data for competitor: {competitor_id}")
            
            # Generate predictions
            predictions = self.predictor.predict_campaign(
                competitor_id=competitor_id,
                historical_ads=historical_ads,
                historical_analyses=historical_analyses,
                campaign_data=campaign_data
            )
            
            # Store predictions
            self._store_prediction(predictions)
            
            logger.info(
                f"Predictions generated",
                extra={
                    'competitor_id': competitor_id,
                    'prediction_id': predictions.get('prediction_id'),
                    'confidence': predictions.get('overall_confidence', 0)
                }
            )
            
            return predictions
        
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise PredictionError(f"Failed to generate predictions: {str(e)}")
    
    def get_predictions(self, competitor_id: str = None) -> List[Dict[str, Any]]:
        """
        Get existing predictions.
        
        Args:
            competitor_id: Optional competitor ID filter
        
        Returns:
            List of predictions
        """
        try:
            response = self.prediction_table.scan(Limit=50)
            items = response.get('Items', [])
            
            # Filter by competitor_id if provided
            if competitor_id:
                items = [item for item in items if item.get('competitor_id') == competitor_id]
            
            # Sort by timestamp descending
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Add simple fallback explanations (skip LLM for speed)
            for item in items:
                if 'llm_explanation' not in item:
                    reach_avg = item.get('reach_prediction', {}).get('avg_reach', 0)
                    engagement_rate = item.get('engagement_prediction', {}).get('rate', 0) * 100
                    confidence = item.get('confidence', 0) * 100
                    
                    item['llm_explanation'] = f"This campaign is predicted to reach approximately {reach_avg:,} users with a {engagement_rate:.1f}% engagement rate. The {confidence:.0f}% confidence score suggests {'high' if confidence > 80 else 'moderate' if confidence > 60 else 'low'} reliability in these predictions based on historical data."
            
            return items[:10] if competitor_id else items
        
        except Exception as e:
            logger.error(f"Failed to get predictions: {str(e)}")
            return []
    
    def _generate_prediction_explanation(self, prediction: Dict[str, Any]) -> str:
        """Generate LLM explanation for prediction."""
        try:
            reach = prediction.get('reach_prediction', {})
            engagement = prediction.get('engagement_prediction', {})
            duration = prediction.get('duration_prediction', {})
            confidence = prediction.get('confidence', 0)
            
            prompt = f"""Analyze this campaign performance prediction and provide a concise, actionable explanation:

Predicted Reach: {reach.get('min_reach', 0):,} - {reach.get('max_reach', 0):,} (avg: {reach.get('avg_reach', 0):,})
Engagement Rate: {engagement.get('rate', 0) * 100:.2f}%
Campaign Duration: {duration.get('days', 0)} days
Confidence: {confidence * 100:.0f}%

Provide a 2-3 sentence explanation covering:
1. What these numbers mean for campaign performance
2. Key insights or recommendations
3. Any notable strengths or concerns

Be concise and actionable."""

            response = self.bedrock_client.invoke_model(
                prompt=prompt,
                system_prompt="You are a marketing analytics expert providing insights on campaign predictions.",
                max_tokens=200,
                temperature=0.7
            )
            
            return response['text'].strip()
        
        except Exception as e:
            logger.error(f"Failed to generate explanation: {str(e)}")
            # Fallback explanation
            reach_avg = prediction.get('reach_prediction', {}).get('avg_reach', 0)
            engagement_rate = prediction.get('engagement_prediction', {}).get('rate', 0) * 100
            confidence = prediction.get('confidence', 0) * 100
            
            return f"This campaign is predicted to reach approximately {reach_avg:,} users with a {engagement_rate:.1f}% engagement rate. The {confidence:.0f}% confidence score suggests {'high' if confidence > 80 else 'moderate' if confidence > 60 else 'low'} reliability in these predictions based on historical data."
    
    def _get_historical_ads(
        self,
        competitor_id: str,
        days: int = None
    ) -> List[Dict[str, Any]]:
        """Get historical ads for competitor."""
        days = days or Config.PREDICTION_LOOKBACK_DAYS
        
        response = self.ad_table.query(
            IndexName='CompetitorIndex',
            KeyConditionExpression='competitor_id = :cid',
            ExpressionAttributeValues={':cid': competitor_id},
            ScanIndexForward=False,
            Limit=100
        )
        
        return response.get('Items', [])
    
    def _get_historical_analyses(
        self,
        competitor_id: str
    ) -> List[Dict[str, Any]]:
        """Get historical analyses for competitor."""
        response = self.analysis_table.query(
            IndexName='CompetitorAnalysisIndex',
            KeyConditionExpression='competitor_id = :cid',
            ExpressionAttributeValues={':cid': competitor_id},
            ScanIndexForward=False,
            Limit=50
        )
        
        return response.get('Items', [])
    
    def _store_prediction(self, prediction: Dict[str, Any]) -> None:
        """Store prediction in DynamoDB."""
        try:
            self.prediction_table.put_item(Item=prediction)
            logger.debug(f"Stored prediction: {prediction.get('prediction_id')}")
        except Exception as e:
            logger.error(f"Failed to store prediction: {str(e)}")
            raise


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for campaign predictions.
    
    Args:
        event: Lambda event
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    logger.info('Predictions handler started', extra={'event': event})
    
    try:
        handler = PredictionsHandler()
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body) if body else {}
        
        # Handle GET - retrieve predictions
        if http_method == 'GET':
            query_params = event.get('queryStringParameters') or {}
            competitor_id = query_params.get('competitor_id')
            
            predictions = handler.get_predictions(competitor_id)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal(predictions)
            }
        
        # Handle POST - generate new predictions
        elif http_method == 'POST':
            competitor_id = body.get('competitor_id')
            campaign_data = body.get('campaign_data')
            
            if not competitor_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'competitor_id is required'
                    })
                }
            
            predictions = handler.predict_campaign_performance(
                competitor_id,
                campaign_data
            )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal({
                    'message': 'Predictions generated',
                    'predictions': predictions
                })
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
        logger.error(f"Predictions handler failed: {str(e)}", exc_info=True)
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
