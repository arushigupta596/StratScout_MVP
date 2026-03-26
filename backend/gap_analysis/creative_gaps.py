"""
Creative Gap Analyzer - Identifies gaps in creative strategies
"""
from typing import Dict, Any, List
from collections import Counter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger

logger = get_logger(__name__)


class CreativeGapAnalyzer:
    """Analyzes creative gaps across competitors."""
    
    def analyze(
        self,
        competitors: List[Dict[str, Any]],
        analyses: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Analyze creative gaps.
        
        Args:
            competitors: List of competitor data
            analyses: Dict mapping competitor_id to their analyses
        
        Returns:
            Creative gap analysis
        """
        logger.info("Analyzing creative gaps")
        
        # Extract creative elements
        all_themes = []
        all_colors = []
        all_formats = []
        
        for comp_id, comp_analyses in analyses.items():
            for analysis in comp_analyses:
                creative = analysis.get('creative_analysis', {})
                all_themes.extend(creative.get('visual_themes', []))
                all_colors.extend(creative.get('color_palette', []))
                all_formats.append(creative.get('format', 'unknown'))
        
        # Analyze patterns
        theme_counts = Counter(all_themes)
        color_counts = Counter(all_colors)
        format_counts = Counter(all_formats)
        
        # Identify gaps
        overused_themes = [t for t, c in theme_counts.most_common(3)]
        underused_themes = [t for t, c in theme_counts.items() if c <= 2]
        
        # Calculate diversity scores
        theme_diversity = len(set(all_themes)) / max(len(all_themes), 1)
        color_diversity = len(set(all_colors)) / max(len(all_colors), 1)
        
        # Calculate confidence
        data_points = len(all_themes) + len(all_colors)
        confidence = min(0.95, 0.5 + (data_points / 150))
        
        return {
            'overused_themes': overused_themes,
            'underused_themes': underused_themes[:5],
            'color_trends': color_counts.most_common(5),
            'format_distribution': dict(format_counts),
            'theme_diversity_score': round(theme_diversity, 2),
            'color_diversity_score': round(color_diversity, 2),
            'gaps': self._identify_creative_gaps(
                overused_themes,
                underused_themes,
                format_counts
            ),
            'confidence': confidence
        }
    
    def _identify_creative_gaps(
        self,
        overused_themes: List[str],
        underused_themes: List[str],
        format_counts: Counter
    ) -> List[Dict[str, Any]]:
        """Identify specific creative gaps."""
        gaps = []
        
        # Gap: Underutilized visual themes
        for theme in underused_themes[:3]:
            gaps.append({
                'type': 'underutilized_visual',
                'theme': theme,
                'description': f"Visual theme '{theme}' is rarely used",
                'opportunity': 'medium'
            })
        
        # Gap: Format opportunities
        if 'video' not in format_counts or format_counts['video'] < 5:
            gaps.append({
                'type': 'format_gap',
                'format': 'video',
                'description': "Video format is underutilized",
                'opportunity': 'high'
            })
        
        # Gap: Creative saturation
        if overused_themes:
            gaps.append({
                'type': 'creative_saturation',
                'themes': overused_themes,
                'description': f"Market saturated with {', '.join(overused_themes)}",
                'opportunity': 'low'
            })
        
        return gaps
