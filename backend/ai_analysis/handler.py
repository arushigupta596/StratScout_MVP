"""
AI Analysis Lambda Handler
"""
import json
import boto3
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.errors import AIAnalysisError
from ai_analysis.creative_analyzer import CreativeAnalyzer
from ai_analysis.messaging_decoder import MessagingDecoder

logger = get_logger(__name__)


class AIAnalysisHandler:
    """Handler for AI analysis operations."""
    
    def __init__(self):
        """Initialize handler."""
        self.dynamodb = boto3.resource('dynamodb')
        self.ad_table = self.dynamodb.Table(Config.AD_DATA_TABLE)
        self.analysis_table = self.dynamodb.Table(Config.ANALYSIS_TABLE)
        self.competitor_table = self.dynamodb.Table(Config.COMPETITOR_TABLE)
        
        self.creative_analyzer = CreativeAnalyzer()
        self.messaging_decoder = MessagingDecoder()
    
    def analyze_recent_ads(self, competitor_id: str = None) -> Dict[str, Any]:
        """
        Analyze recent ads for competitor(s).
        
        Args:
            competitor_id: Optional specific competitor ID
        
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing recent ads for competitor: {competitor_id or 'all'}")
        
        try:
            # Get competitors to analyze
            if competitor_id:
                competitors = [self._get_competitor(competitor_id)]
            else:
                competitors = self._get_all_competitors()
            
            results = {
                'creative_analyses': [],
                'messaging_analyses': [],
                'competitors_analyzed': len(competitors)
            }
            
            for competitor in competitors:
                comp_id = competitor['competitorId']
                comp_name = competitor.get('name', 'Unknown')
                
                # Get recent ads for this competitor
                ads = self._get_recent_ads(comp_id, limit=20)
                
                if not ads:
                    logger.info(f"No ads found for {comp_name}")
                    continue
                
                # Analyze individual creatives
                creative_results = self.creative_analyzer.batch_analyze_creatives(ads)
                
                # Store creative analyses
                for analysis in creative_results:
                    self._store_analysis(analysis)
                    results['creative_analyses'].append(analysis['analysis_id'])
                
                # Analyze messaging strategy
                if len(ads) >= 3:  # Need at least 3 ads for messaging analysis
                    messaging_analysis = self.messaging_decoder.analyze_messaging_strategy(
                        comp_id,
                        comp_name,
                        ads
                    )
                    self._store_analysis(messaging_analysis)
                    results['messaging_analyses'].append(messaging_analysis['analysis_id'])
                
                logger.info(
                    f"Completed analysis for {comp_name}",
                    extra={
                        'creative_analyses': len(creative_results),
                        'ads_analyzed': len(ads)
                    }
                )
            
            return results
        
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise AIAnalysisError(f"Failed to analyze ads: {str(e)}")
    
    def _get_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """Get competitor data."""
        response = self.competitor_table.get_item(
            Key={'competitorId': competitor_id}
        )
        return response.get('Item', {})
    
    def _get_all_competitors(self) -> List[Dict[str, Any]]:
        """Get all tracked competitors."""
        response = self.competitor_table.scan()
        return response.get('Items', [])
    
    def _get_recent_ads(self, competitor_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent ads for a competitor.
        
        Args:
            competitor_id: Competitor ID
            limit: Maximum number of ads
        
        Returns:
            List of ad data
        """
        response = self.ad_table.query(
            IndexName='CompetitorIndex',
            KeyConditionExpression='competitor_id = :cid',
            ExpressionAttributeValues={':cid': competitor_id},
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        
        return response.get('Items', [])
    
    def _store_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Store analysis results in DynamoDB.
        
        Args:
            analysis: Analysis results
        """
        try:
            self.analysis_table.put_item(Item=analysis)
            logger.debug(f"Stored analysis: {analysis.get('analysis_id')}")
        except Exception as e:
            logger.error(f"Failed to store analysis: {str(e)}")
            raise


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for AI analysis.
    
    Args:
        event: Lambda event
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    logger.info('AI analysis started', extra={'event': event})
    
    try:
        handler = AIAnalysisHandler()
        
        # Get competitor_id from event if provided
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        competitor_id = body.get('competitor_id')
        
        # Run analysis
        results = handler.analyze_recent_ads(competitor_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'AI analysis completed',
                'results': results
            })
        }
    
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}", exc_info=True)
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
