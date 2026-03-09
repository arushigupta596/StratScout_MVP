"""
Opportunity Scorer - Scores and prioritizes market opportunities
"""
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger

logger = get_logger(__name__)


class OpportunityScorer:
    """Scores and prioritizes market opportunities."""
    
    def score_opportunities(
        self,
        messaging_gaps: Dict[str, Any],
        creative_gaps: Dict[str, Any],
        timing_gaps: Dict[str, Any],
        positioning_gaps: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Score and prioritize all identified opportunities.
        
        Args:
            messaging_gaps: Messaging gap analysis
            creative_gaps: Creative gap analysis
            timing_gaps: Timing gap analysis
            positioning_gaps: Positioning gap analysis
        
        Returns:
            Sorted list of scored opportunities
        """
        logger.info("Scoring opportunities")
        
        opportunities = []
        
        # Score messaging opportunities
        for gap in messaging_gaps.get('gaps', []):
            score = self._score_messaging_gap(gap)
            opportunities.append({
                **gap,
                'category': 'messaging',
                'score': score,
                'priority': self._get_priority(score)
            })
        
        # Score creative opportunities
        for gap in creative_gaps.get('gaps', []):
            score = self._score_creative_gap(gap)
            opportunities.append({
                **gap,
                'category': 'creative',
                'score': score,
                'priority': self._get_priority(score)
            })
        
        # Score timing opportunities
        for gap in timing_gaps.get('gaps', []):
            score = self._score_timing_gap(gap)
            opportunities.append({
                **gap,
                'category': 'timing',
                'score': score,
                'priority': self._get_priority(score)
            })
        
        # Score positioning opportunities
        for gap in positioning_gaps.get('gaps', []):
            score = self._score_positioning_gap(gap)
            opportunities.append({
                **gap,
                'category': 'positioning',
                'score': score,
                'priority': self._get_priority(score)
            })
        
        # Sort by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities
    
    def _score_messaging_gap(self, gap: Dict[str, Any]) -> float:
        """Score a messaging gap."""
        base_score = 0.5
        
        gap_type = gap.get('type', '')
        opportunity = gap.get('opportunity', 'medium')
        
        # Type-based scoring
        if gap_type == 'underutilized_theme':
            base_score = 0.7
        elif gap_type == 'counter_narrative':
            base_score = 0.8
        
        # Opportunity multiplier
        multipliers = {'high': 1.2, 'medium': 1.0, 'low': 0.8}
        score = base_score * multipliers.get(opportunity, 1.0)
        
        return min(1.0, score)
    
    def _score_creative_gap(self, gap: Dict[str, Any]) -> float:
        """Score a creative gap."""
        base_score = 0.5
        
        gap_type = gap.get('type', '')
        opportunity = gap.get('opportunity', 'medium')
        
        # Type-based scoring
        if gap_type == 'format_gap':
            base_score = 0.8
        elif gap_type == 'underutilized_visual':
            base_score = 0.6
        elif gap_type == 'creative_saturation':
            base_score = 0.3
        
        # Opportunity multiplier
        multipliers = {'high': 1.2, 'medium': 1.0, 'low': 0.8}
        score = base_score * multipliers.get(opportunity, 1.0)
        
        return min(1.0, score)
    
    def _score_timing_gap(self, gap: Dict[str, Any]) -> float:
        """Score a timing gap."""
        base_score = 0.5
        
        gap_type = gap.get('type', '')
        opportunity = gap.get('opportunity', 'medium')
        
        # Type-based scoring
        if gap_type == 'quiet_period':
            base_score = 0.75
        elif gap_type == 'overcrowded_period':
            base_score = 0.3
        
        # Opportunity multiplier
        multipliers = {'high': 1.2, 'medium': 1.0, 'low': 0.8}
        score = base_score * multipliers.get(opportunity, 1.0)
        
        return min(1.0, score)
    
    def _score_positioning_gap(self, gap: Dict[str, Any]) -> float:
        """Score a positioning gap."""
        base_score = 0.5
        
        gap_type = gap.get('type', '')
        opportunity = gap.get('opportunity', 'medium')
        
        # Type-based scoring
        if gap_type == 'open_position':
            base_score = 0.9
        elif gap_type == 'underserved_segment':
            base_score = 0.7
        elif gap_type == 'crowded_position':
            base_score = 0.2
        
        # Opportunity multiplier
        multipliers = {'high': 1.2, 'medium': 1.0, 'low': 0.8}
        score = base_score * multipliers.get(opportunity, 1.0)
        
        return min(1.0, score)
    
    def _get_priority(self, score: float) -> str:
        """Convert score to priority level."""
        if score >= 0.7:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
