"""
Positioning Gap Analyzer - Identifies gaps in market positioning
"""
from typing import Dict, Any, List
from collections import Counter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger

logger = get_logger(__name__)


class PositioningGapAnalyzer:
    """Analyzes positioning gaps across competitors."""
    
    def analyze(
        self,
        competitors: List[Dict[str, Any]],
        analyses: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Analyze positioning gaps.
        
        Args:
            competitors: List of competitor data
            analyses: Dict mapping competitor_id to their analyses
        
        Returns:
            Positioning gap analysis
        """
        logger.info("Analyzing positioning gaps")
        
        # Extract positioning data
        all_positions = []
        price_points = []
        target_segments = []
        
        for comp_id, comp_analyses in analyses.items():
            for analysis in comp_analyses:
                positioning = analysis.get('positioning', {})
                all_positions.append(positioning.get('position', 'unknown'))
                
                if 'price_point' in positioning:
                    price_points.append(positioning['price_point'])
                
                target_segments.extend(positioning.get('target_segments', []))
        
        # Analyze patterns
        position_counts = Counter(all_positions)
        segment_counts = Counter(target_segments)
        
        # Identify gaps
        crowded_positions = [p for p, c in position_counts.most_common(3)]
        open_positions = self._identify_open_positions(position_counts)
        underserved_segments = [s for s, c in segment_counts.items() if c <= 2]
        
        # Calculate confidence
        data_points = len(all_positions) + len(target_segments)
        confidence = min(0.90, 0.4 + (data_points / 100))
        
        return {
            'crowded_positions': crowded_positions,
            'open_positions': open_positions,
            'underserved_segments': underserved_segments[:5],
            'price_point_distribution': Counter(price_points).most_common(),
            'gaps': self._identify_positioning_gaps(
                crowded_positions,
                open_positions,
                underserved_segments
            ),
            'confidence': confidence
        }
    
    def _identify_open_positions(
        self,
        position_counts: Counter
    ) -> List[str]:
        """Identify open market positions."""
        # Common positioning strategies in Indian skincare
        common_positions = [
            'natural/ayurvedic',
            'scientific/dermatologist',
            'luxury/premium',
            'affordable/value',
            'clean/sustainable',
            'men-focused',
            'teen-focused'
        ]
        
        occupied = set(position_counts.keys())
        open_positions = [p for p in common_positions if p not in occupied]
        
        return open_positions[:5]
    
    def _identify_positioning_gaps(
        self,
        crowded_positions: List[str],
        open_positions: List[str],
        underserved_segments: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify specific positioning gaps."""
        gaps = []
        
        # Gap: Open positions
        for position in open_positions[:3]:
            gaps.append({
                'type': 'open_position',
                'position': position,
                'description': f"No competitor strongly positioned in '{position}'",
                'opportunity': 'high'
            })
        
        # Gap: Underserved segments
        for segment in underserved_segments[:3]:
            gaps.append({
                'type': 'underserved_segment',
                'segment': segment,
                'description': f"Segment '{segment}' is underserved",
                'opportunity': 'medium'
            })
        
        # Gap: Crowded positions
        for position in crowded_positions:
            gaps.append({
                'type': 'crowded_position',
                'position': position,
                'description': f"Position '{position}' is highly competitive",
                'opportunity': 'low'
            })
        
        return gaps
