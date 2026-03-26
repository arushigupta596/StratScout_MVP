"""
Data Ingestion Lambda Handler - Meta Ads Library & Google Trends
"""
import json
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.errors import DataIngestionError
from meta_ads.client import MetaAdsClient
from google_trends.pytrends_client import GoogleTrendsClient

logger = get_logger(__name__)


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main handler for data ingestion.
    
    Triggered by EventBridge schedule (every 15 minutes).
    Collects data from Meta Ads Library and Google Trends.
    
    Args:
        event: Lambda event
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    logger.info('Data ingestion started', extra={'event': event})
    
    try:
        # Validate configuration
        if not Config.validate():
            raise DataIngestionError('Invalid configuration')
        
        results = {
            'meta_ads': None,
            'google_trends': None,
        }
        
        # Collect Meta Ads data
        try:
            meta_client = MetaAdsClient()
            meta_results = meta_client.collect_competitor_ads()
            results['meta_ads'] = {
                'success': True,
                'ads_collected': len(meta_results),
                'competitors': list(set(ad['competitor_id'] for ad in meta_results))
            }
            logger.info(f"Collected {len(meta_results)} ads from Meta Ads Library")
        except Exception as e:
            logger.error(f"Meta Ads collection failed: {str(e)}")
            results['meta_ads'] = {
                'success': False,
                'error': str(e)
            }
        
        # Collect Google Trends data
        try:
            trends_client = GoogleTrendsClient()
            trends_results = trends_client.collect_trends()
            results['google_trends'] = {
                'success': True,
                'keywords_tracked': len(trends_results)
            }
            logger.info(f"Collected trends for {len(trends_results)} keywords")
        except Exception as e:
            logger.error(f"Google Trends collection failed: {str(e)}")
            results['google_trends'] = {
                'success': False,
                'error': str(e)
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data ingestion completed',
                'results': results
            })
        }
    
    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
