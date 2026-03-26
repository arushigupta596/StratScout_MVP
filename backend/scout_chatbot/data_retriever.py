"""
Data Retriever - Retrieves relevant data based on intent
"""
from typing import Dict, Any
import boto3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config

logger = get_logger(__name__)


class DataRetriever:
    """Retrieves data from DynamoDB based on intent."""
    
    def __init__(self):
        """Initialize data retriever."""
        self.dynamodb = boto3.resource('dynamodb')
        self.competitor_table = self.dynamodb.Table(Config.COMPETITOR_TABLE)
        self.ads_table = self.dynamodb.Table(Config.ADS_TABLE)
        self.analysis_table = self.dynamodb.Table(Config.ANALYSIS_TABLE)
        self.predictions_table = self.dynamodb.Table(Config.PREDICTIONS_TABLE)
        self.gap_analysis_table = self.dynamodb.Table(Config.GAP_ANALYSIS_TABLE)
    
    def retrieve(
        self,
        intent: str,
        entities: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve relevant data based on intent.
        
        Args:
            intent: Classified intent
            entities: Extracted entities
            user_id: User identifier
        
        Returns:
            Retrieved data
        """
        logger.info(f"Retrieving data for intent: {intent}")
        
        try:
            if intent == 'competitor_overview':
                return self._get_competitor_overview(entities)
            
            elif intent == 'campaign_analysis':
                return self._get_campaign_data(entities)
            
            elif intent == 'gap_analysis':
                return self._get_gap_analysis(entities)
            
            elif intent == 'performance_comparison':
                return self._get_comparison_data(entities)
            
            elif intent == 'trend_analysis':
                return self._get_trend_data(entities)
            
            elif intent == 'market_intelligence':
                return self._get_market_data(entities)
            
            else:
                return {}
        
        except Exception as e:
            logger.error(f"Data retrieval failed: {str(e)}", exc_info=True)
            return {}
    
    def _get_competitor_overview(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get competitor overview data."""
        competitor = entities.get('competitor')
        
        if competitor:
            # Get specific competitor
            response = self.competitor_table.scan(
                FilterExpression='contains(#name, :name)',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':name': competitor}
            )
            competitors = response.get('Items', [])
        else:
            # Get all competitors
            response = self.competitor_table.scan(Limit=10)
            competitors = response.get('Items', [])
        
        return {'competitors': competitors}
    
    def _get_campaign_data(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaign/ad data."""
        competitor = entities.get('competitor')
        
        if competitor:
            # Get ads for specific competitor
            response = self.ads_table.scan(
                FilterExpression='contains(advertiser_name, :name)',
                ExpressionAttributeValues={':name': competitor},
                Limit=20
            )
        else:
            # Get recent ads
            response = self.ads_table.scan(Limit=20)
        
        ads = response.get('Items', [])
        
        # Get analyses for these ads
        analyses = []
        for ad in ads[:5]:  # Limit to avoid too many queries
            ad_id = ad.get('ad_id')
            if ad_id:
                analysis_response = self.analysis_table.query(
                    KeyConditionExpression='ad_id = :aid',
                    ExpressionAttributeValues={':aid': ad_id},
                    Limit=1
                )
                if analysis_response.get('Items'):
                    analyses.append(analysis_response['Items'][0])
        
        return {
            'ads': ads,
            'analyses': analyses
        }
    
    def _get_gap_analysis(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get gap analysis data."""
        # Get most recent gap analysis
        response = self.gap_analysis_table.scan(
            Limit=1,
            ScanIndexForward=False
        )
        
        gap_analyses = response.get('Items', [])
        
        return {
            'gap_analysis': gap_analyses[0] if gap_analyses else None
        }
    
    def _get_comparison_data(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get comparison data."""
        # Get all competitors for comparison
        response = self.competitor_table.scan(Limit=10)
        competitors = response.get('Items', [])
        
        # Get predictions for each
        predictions = []
        for comp in competitors[:5]:
            comp_id = comp.get('competitorId')
            if comp_id:
                pred_response = self.predictions_table.query(
                    IndexName='CompetitorPredictionIndex',
                    KeyConditionExpression='competitor_id = :cid',
                    ExpressionAttributeValues={':cid': comp_id},
                    Limit=1,
                    ScanIndexForward=False
                )
                if pred_response.get('Items'):
                    predictions.append(pred_response['Items'][0])
        
        return {
            'competitors': competitors,
            'predictions': predictions
        }
    
    def _get_trend_data(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get trend data."""
        time_period = entities.get('time_period', 'last_month')
        
        # Get ads over time
        response = self.ads_table.scan(Limit=50)
        ads = response.get('Items', [])
        
        # Sort by timestamp
        ads.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'ads': ads,
            'time_period': time_period
        }
    
    def _get_market_data(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get market intelligence data."""
        # Get all competitors
        comp_response = self.competitor_table.scan()
        competitors = comp_response.get('Items', [])
        
        # Get recent gap analysis
        gap_response = self.gap_analysis_table.scan(Limit=1, ScanIndexForward=False)
        gap_analysis = gap_response.get('Items', [])
        
        return {
            'competitors': competitors,
            'gap_analysis': gap_analysis[0] if gap_analysis else None,
            'market_size': len(competitors)
        }
