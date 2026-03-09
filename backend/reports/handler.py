"""
Campaign Report Lambda Handler
Saves and retrieves detailed campaign reports
"""
import json
import boto3
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.json_encoder import dumps_decimal
from reports.report_generator import ReportGenerator

logger = get_logger(__name__)


class ReportHandler:
    """Handler for campaign report operations."""
    
    def __init__(self):
        """Initialize handler."""
        self.dynamodb = boto3.resource('dynamodb')
        self.competitor_table = self.dynamodb.Table(Config.COMPETITOR_TABLE)
        self.ad_table = self.dynamodb.Table(Config.AD_DATA_TABLE)
        self.prediction_table = self.dynamodb.Table(Config.PREDICTION_TABLE)
        self.gap_table = self.dynamodb.Table(Config.GAP_ANALYSIS_TABLE)
        self.report_table = self.dynamodb.Table(Config.REPORT_TABLE)
        
        self.report_generator = ReportGenerator()
    
    def get_latest_report(self) -> Dict[str, Any]:
        """
        Get the latest saved report or generate a new one.
        
        Returns:
            Campaign report
        """
        logger.info("Getting latest report")
        
        try:
            # Try to get the latest saved report
            response = self.report_table.scan(Limit=10)
            items = response.get('Items', [])
            
            if items:
                # Sort by timestamp and get latest
                items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                latest_report = items[0]
                logger.info(f"Found saved report: {latest_report.get('report_id')}")
                return latest_report
            
            # No saved report, generate new one
            logger.info("No saved report found, generating new one")
            return self.generate_new_report()
        
        except Exception as e:
            logger.error(f"Failed to get report: {str(e)}", exc_info=True)
            return self.generate_new_report()
    
    def generate_new_report(self) -> Dict[str, Any]:
        """
        Generate and save a new campaign report.
        
        Returns:
            Campaign report
        """
        logger.info("Generating new campaign report")
        
        try:
            # Get all data
            competitors = self._get_competitors()
            ads = self._get_ads()
            predictions = self._get_predictions()
            gap_analysis = self._get_latest_gap_analysis()
            
            # If no gap analysis, create minimal one
            if not gap_analysis:
                logger.warning("No gap analysis found, using minimal data")
                gap_analysis = {
                    'opportunities': [],
                    'confidence': 0.5
                }
            
            # Generate report with LLM
            report = self.report_generator.generate_campaign_plan(
                competitors=competitors,
                ads=ads,
                predictions=predictions,
                gap_analysis=gap_analysis
            )
            
            # Save report to DynamoDB
            self._save_report(report)
            
            logger.info(f"Campaign report generated and saved: {report.get('report_id')}")
            return report
        
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}", exc_info=True)
            # Return minimal report on error
            return {
                'report_id': 'error_report',
                'timestamp': '2024-01-01T00:00:00Z',
                'executive_summary': 'Unable to generate full report. Please try regenerating.',
                'market_insights': {
                    'total_competitors': 0,
                    'total_campaigns_analyzed': 0,
                    'high_priority_opportunities': 0
                },
                'strategic_recommendations': [],
                'campaign_ideas': [],
                'timeline': [],
                'budget_allocation': [],
                'confidence': 0.0
            }
    
    def _save_report(self, report: Dict[str, Any]) -> None:
        """Save report to DynamoDB."""
        try:
            self.report_table.put_item(Item=report)
            logger.info(f"Report saved: {report.get('report_id')}")
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
    
    def _get_competitors(self) -> list:
        """Get all competitors."""
        try:
            response = self.competitor_table.scan()
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get competitors: {str(e)}")
            return []
    
    def _get_ads(self) -> list:
        """Get all ads."""
        try:
            response = self.ad_table.scan(Limit=100)
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get ads: {str(e)}")
            return []
    
    def _get_predictions(self) -> list:
        """Get all predictions."""
        try:
            response = self.prediction_table.scan(Limit=50)
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get predictions: {str(e)}")
            return []
    
    def _get_latest_gap_analysis(self) -> Dict[str, Any]:
        """Get latest gap analysis."""
        try:
            response = self.gap_table.scan(Limit=10)
            items = response.get('Items', [])
            
            if not items:
                return None
            
            # Sort by timestamp and get latest
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return items[0]
        except Exception as e:
            logger.error(f"Failed to get gap analysis: {str(e)}")
            return None


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for campaign reports.
    
    Args:
        event: Lambda event
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    logger.info('Report handler started', extra={'event': event})
    
    try:
        handler = ReportHandler()
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        query_params = event.get('queryStringParameters') or {}
        
        # Handle GET - get latest report
        if http_method == 'GET':
            # Check if regenerate is requested
            if query_params.get('regenerate') == 'true':
                logger.info("Regenerate requested")
                report = handler.generate_new_report()
            else:
                report = handler.get_latest_report()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal(report)
            }
        
        # Handle POST - generate new report
        elif http_method == 'POST':
            report = handler.generate_new_report()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal(report)
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
        logger.error(f"Report handler failed: {str(e)}", exc_info=True)
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
