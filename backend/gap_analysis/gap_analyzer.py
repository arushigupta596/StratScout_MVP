"""
Gap Analyzer - Identifies market opportunities and competitive gaps
"""
from typing import Dict, Any, List
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.utils import generate_id, calculate_confidence_score
from common.errors import GapAnalysisError
from gap_analysis.messaging_gaps import MessagingGapAnalyzer
from gap_analysis.creative_gaps import CreativeGapAnalyzer
from gap_analysis.timing_gaps import TimingGapAnalyzer
from gap_analysis.positioning_gaps import PositioningGapAnalyzer
from gap_analysis.opportunity_scorer import OpportunityScorer

logger = get_logger(__name__)


class GapAnalyzer:
    """Analyzes competitive gaps and identifies opportunities."""
    
    def __init__(self):
        """Initialize gap analyzer."""
        self.messaging_analyzer = MessagingGapAnalyzer()
        self.creative_analyzer = CreativeGapAnalyzer()
        self.timing_analyzer = TimingGapAnalyzer()
        self.positioning_analyzer = PositioningGapAnalyzer()
        self.opportunity_scorer = OpportunityScorer()
    
    def analyze_gaps(
        self,
        competitors: List[Dict[str, Any]],
        analyses: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Analyze gaps across all dimensions.
        
        Args:
            competitors: List of competitor data
            analyses: Dict mapping competitor_id to their analyses
        
        Returns:
            Comprehensive gap analysis results
        """
        logger.info(f"Analyzing gaps for {len(competitors)} competitors")
        
        try:
            # Analyze each dimension
            messaging_gaps = self.messaging_analyzer.analyze(competitors, analyses)
            creative_gaps = self.creative_analyzer.analyze(competitors, analyses)
            timing_gaps = self.timing_analyzer.analyze(competitors, analyses)
            positioning_gaps = self.positioning_analyzer.analyze(competitors, analyses)
            
            # Score opportunities
            opportunities = self.opportunity_scorer.score_opportunities(
                messaging_gaps=messaging_gaps,
                creative_gaps=creative_gaps,
                timing_gaps=timing_gaps,
                positioning_gaps=positioning_gaps
            )
            
            # Calculate overall confidence
            confidence = calculate_confidence_score([
                messaging_gaps.get('confidence', 0),
                creative_gaps.get('confidence', 0),
                timing_gaps.get('confidence', 0),
                positioning_gaps.get('confidence', 0)
            ])
            
            # Build result
            result = {
                'gap_analysis_id': generate_id('gap'),
                'timestamp': datetime.utcnow().isoformat(),
                'competitors_analyzed': [c['competitorId'] for c in competitors],
                'messaging_gaps': messaging_gaps,
                'creative_gaps': creative_gaps,
                'timing_gaps': timing_gaps,
                'positioning_gaps': positioning_gaps,
                'opportunities': opportunities,
                'confidence': confidence,
                'summary': self._generate_summary(opportunities)
            }
            
            logger.info(
                f"Gap analysis completed",
                extra={
                    'opportunities_found': len(opportunities),
                    'confidence': confidence
                }
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Gap analysis failed: {str(e)}", exc_info=True)
            raise GapAnalysisError(f"Failed to analyze gaps: {str(e)}")
    
    def _generate_summary(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate executive summary of gaps."""
        if not opportunities:
            return {
                'total_opportunities': 0,
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0,
                'top_recommendation': None
            }
        
        # Count by priority
        high = sum(1 for o in opportunities if o.get('priority') == 'high')
        medium = sum(1 for o in opportunities if o.get('priority') == 'medium')
        low = sum(1 for o in opportunities if o.get('priority') == 'low')
        
        # Get top opportunity
        top = max(opportunities, key=lambda o: o.get('score', 0))
        
        return {
            'total_opportunities': len(opportunities),
            'high_priority': high,
            'medium_priority': medium,
            'low_priority': low,
            'top_recommendation': {
                'type': top.get('type'),
                'description': top.get('description'),
                'score': top.get('score'),
                'priority': top.get('priority')
            }
        }
