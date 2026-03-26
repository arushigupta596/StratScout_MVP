"""
Timing Gap Analyzer - Identifies gaps in campaign timing
"""
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger

logger = get_logger(__name__)


class TimingGapAnalyzer:
    """Analyzes timing gaps across competitors."""
    
    def analyze(
        self,
        competitors: List[Dict[str, Any]],
        analyses: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Analyze timing gaps.
        
        Args:
            competitors: List of competitor data
            analyses: Dict mapping competitor_id to their analyses
        
        Returns:
            Timing gap analysis
        """
        logger.info("Analyzing timing gaps")
        
        # Extract timing data
        campaign_timings = defaultdict(list)
        seasonal_patterns = defaultdict(int)
        
        for comp_id, comp_analyses in analyses.items():
            for analysis in comp_analyses:
                timestamp = analysis.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        month = dt.strftime('%B')
                        seasonal_patterns[month] += 1
                        campaign_timings[comp_id].append(dt)
                    except:
                        pass
        
        # Identify timing patterns
        busy_months = sorted(
            seasonal_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        quiet_months = sorted(
            seasonal_patterns.items(),
            key=lambda x: x[1]
        )[:3]
        
        # Calculate confidence
        data_points = sum(seasonal_patterns.values())
        confidence = min(0.90, 0.4 + (data_points / 100))
        
        return {
            'busy_periods': [{'month': m, 'activity': c} for m, c in busy_months],
            'quiet_periods': [{'month': m, 'activity': c} for m, c in quiet_months],
            'seasonal_patterns': dict(seasonal_patterns),
            'gaps': self._identify_timing_gaps(busy_months, quiet_months),
            'confidence': confidence
        }
    
    def _identify_timing_gaps(
        self,
        busy_months: List[tuple],
        quiet_months: List[tuple]
    ) -> List[Dict[str, Any]]:
        """Identify specific timing gaps."""
        gaps = []
        
        # Gap: Quiet periods
        for month, activity in quiet_months:
            if activity < 5:
                gaps.append({
                    'type': 'quiet_period',
                    'month': month,
                    'description': f"{month} has low competitive activity",
                    'opportunity': 'high'
                })
        
        # Gap: Overcrowded periods
        for month, activity in busy_months:
            if activity > 20:
                gaps.append({
                    'type': 'overcrowded_period',
                    'month': month,
                    'description': f"{month} is highly competitive",
                    'opportunity': 'low'
                })
        
        return gaps
