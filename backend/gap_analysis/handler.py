"""
Gap Analysis Lambda Handler
"""
import json
import boto3
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.errors import GapAnalysisError
from common.json_encoder import dumps_decimal
from gap_analysis.gap_analyzer import GapAnalyzer
from ai_analysis.bedrock_client import BedrockClient

logger = get_logger(__name__)


class GapAnalysisHandler:
    """Handler for gap analysis operations."""
    
    def __init__(self):
        """Initialize handler."""
        self.dynamodb = boto3.resource('dynamodb')
        self.analysis_table = self.dynamodb.Table(Config.ANALYSIS_TABLE)
        self.competitor_table = self.dynamodb.Table(Config.COMPETITOR_TABLE)
        self.gap_analysis_table = self.dynamodb.Table(Config.GAP_ANALYSIS_TABLE)
        
        self.gap_analyzer = GapAnalyzer()
        self.bedrock_client = BedrockClient()
    
    def analyze_market_gaps(self, competitor_ids: List[str] = None) -> Dict[str, Any]:
        """
        Analyze market gaps across competitors.
        
        Args:
            competitor_ids: Optional list of specific competitor IDs
        
        Returns:
            Gap analysis results
        """
        logger.info(f"Analyzing market gaps for competitors: {competitor_ids or 'all'}")
        
        try:
            # Get competitors
            if competitor_ids:
                competitors = [self._get_competitor(cid) for cid in competitor_ids]
            else:
                competitors = self._get_all_competitors()
            
            if len(competitors) < Config.GAP_ANALYSIS_MIN_COMPETITORS:
                raise GapAnalysisError(
                    f"Need at least {Config.GAP_ANALYSIS_MIN_COMPETITORS} competitors for gap analysis"
                )
            
            # Get analyses for all competitors
            all_analyses = {}
            for competitor in competitors:
                comp_id = competitor['competitorId']
                analyses = self._get_competitor_analyses(comp_id)
                all_analyses[comp_id] = analyses
            
            # Perform gap analysis
            gap_results = self.gap_analyzer.analyze_gaps(
                competitors=competitors,
                analyses=all_analyses
            )
            
            # Store results
            self._store_gap_analysis(gap_results)
            
            logger.info(
                f"Gap analysis completed",
                extra={
                    'competitors_analyzed': len(competitors),
                    'gaps_identified': len(gap_results.get('opportunities', []))
                }
            )
            
            return gap_results
        
        except Exception as e:
            logger.error(f"Gap analysis failed: {str(e)}", exc_info=True)
            raise GapAnalysisError(f"Failed to analyze gaps: {str(e)}")
    
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
    
    def _get_competitor_analyses(self, competitor_id: str) -> List[Dict[str, Any]]:
        """Get analyses for a competitor."""
        response = self.analysis_table.query(
            IndexName='CompetitorAnalysisIndex',
            KeyConditionExpression='competitor_id = :cid',
            ExpressionAttributeValues={':cid': competitor_id},
            ScanIndexForward=False,
            Limit=50
        )
        return response.get('Items', [])
    
    def _store_gap_analysis(self, gap_results: Dict[str, Any]) -> None:
        """Store gap analysis results."""
        try:
            self.gap_analysis_table.put_item(Item=gap_results)
            logger.debug(f"Stored gap analysis: {gap_results.get('gap_analysis_id')}")
        except Exception as e:
            logger.error(f"Failed to store gap analysis: {str(e)}")
            raise
    
    def _generate_gap_explanation(self, gap_analysis: Dict[str, Any]) -> str:
        """Generate LLM explanation for gap analysis."""
        try:
            opportunities = gap_analysis.get('opportunities', [])
            high_priority = [o for o in opportunities if o.get('priority') == 'high']
            confidence = gap_analysis.get('confidence', 0)
            
            # Build opportunity summary
            opp_summary = []
            for opp in opportunities[:5]:
                opp_summary.append(f"- {opp.get('type', 'Unknown')}: {opp.get('description', '')} (Priority: {opp.get('priority', 'unknown')})")
            
            prompt = f"""Analyze this market gap analysis and provide a concise, strategic explanation:

Total Opportunities: {len(opportunities)}
High Priority Opportunities: {len(high_priority)}
Confidence: {confidence * 100:.0f}%

Top Opportunities:
{chr(10).join(opp_summary)}

Provide a 2-3 sentence strategic summary covering:
1. The most significant market gaps identified
2. Key recommendations for competitive advantage
3. Priority areas to focus on

Be concise and actionable."""

            response = self.bedrock_client.invoke_model(
                prompt=prompt,
                system_prompt="You are a competitive strategy expert providing insights on market gaps and opportunities.",
                max_tokens=200,
                temperature=0.7
            )
            
            return response['text'].strip()
        
        except Exception as e:
            logger.error(f"Failed to generate gap explanation: {str(e)}")
            # Fallback explanation
            opportunities = gap_analysis.get('opportunities', [])
            high_priority = [o for o in opportunities if o.get('priority') == 'high']
            
            return f"Analysis identified {len(opportunities)} market opportunities, with {len(high_priority)} high-priority gaps. Focus on addressing the high-priority opportunities first to gain competitive advantage in underserved market segments."


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for gap analysis.
    
    Args:
        event: Lambda event
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    logger.info('Gap analysis handler started', extra={'event': event})
    
    try:
        handler = GapAnalysisHandler()
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body) if body else {}
        
        # Handle GET - retrieve gap analyses
        if http_method == 'GET':
            query_params = event.get('queryStringParameters') or {}
            
            # Get latest gap analyses
            try:
                response = handler.gap_analysis_table.scan(Limit=10)
                gap_analyses = response.get('Items', [])
                
                # Sort by timestamp descending
                gap_analyses.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Add LLM explanations if not present
                for gap in gap_analyses:
                    if 'llm_explanation' not in gap:
                        gap['llm_explanation'] = handler._generate_gap_explanation(gap)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': dumps_decimal(gap_analyses)
                }
            except Exception as e:
                logger.error(f"Failed to retrieve gap analyses: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': str(e)})
                }
        
        # Handle POST - generate new gap analysis
        elif http_method == 'POST':
            competitor_ids = body.get('competitor_ids')
            
            gap_results = handler.analyze_market_gaps(competitor_ids)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': dumps_decimal({
                    'message': 'Gap analysis completed',
                    'results': gap_results
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
        logger.error(f"Gap analysis handler failed: {str(e)}", exc_info=True)
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
