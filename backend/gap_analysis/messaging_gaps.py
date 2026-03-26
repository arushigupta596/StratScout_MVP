"""
Messaging Gap Analyzer - Identifies gaps in messaging strategies
"""
from typing import Dict, Any, List
from collections import Counter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.utils import calculate_confidence_score

logger = get_logger(__name__)


class MessagingGapAnalyzer:
    """Analyzes messaging gaps across competitors."""
    
    def analyze(
        self,
        competitors: List[Dict[str, Any]],
        analyses: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Analyze messaging gaps.
        
        Args:
            competitors: List of competitor data
            analyses: Dict mapping competitor_id to their analyses
        
        Returns:
            Messaging gap analysis
        """
        logger.info("Analyzing messaging gaps")
        
        # Extract all messaging themes
        all_themes = []
        all_keywords = []
        all_hooks = []
        all_ctas = []
        
        for comp_id, comp_analyses in analyses.items():
            for analysis in comp_analyses:
                messaging = analysis.get('messaging_analysis', {})
                all_themes.extend(messaging.get('themes', []))
                all_keywords.extend(messaging.get('keywords', []))
                all_hooks.extend(messaging.get('hooks', []))
                all_ctas.extend(messaging.get('ctas', []))
        
        # Find common and unique themes
        theme_counts = Counter(all_themes)
        keyword_counts = Counter(all_keywords)
        
        # Identify gaps (underutilized themes)
        common_themes = [t for t, c in theme_counts.most_common(10)]
        underutilized_themes = [t for t, c in theme_counts.items() if c <= 2]
        
        # Identify unique messaging angles
        unique_angles = self._find_unique_angles(analyses)
        
        # Calculate confidence
        data_points = len(all_themes) + len(all_keywords)
        confidence = min(0.95, 0.5 + (data_points / 200))
        
        return {
            'common_themes': common_themes[:5],
            'underutilized_themes': underutilized_themes[:5],
            'unique_angles': unique_angles,
            'keyword_saturation': self._calculate_saturation(keyword_counts),
            'hook_diversity': len(set(all_hooks)),
            'cta_patterns': Counter(all_ctas).most_common(5),
            'gaps': self._identify_messaging_gaps(
                common_themes,
                underutilized_themes,
                unique_angles
            ),
            'confidence': confidence
        }
    
    def _find_unique_angles(
        self,
        analyses: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Find unique messaging angles used by specific competitors."""
        unique = []
        
        for comp_id, comp_analyses in analyses.items():
            themes = []
            for analysis in comp_analyses:
                messaging = analysis.get('messaging_analysis', {})
                themes.extend(messaging.get('themes', []))
            
            # Find themes unique to this competitor
            theme_counts = Counter(themes)
            for theme, count in theme_counts.items():
                if count >= 3:  # Used consistently
                    unique.append({
                        'competitor_id': comp_id,
                        'angle': theme,
                        'frequency': count
                    })
        
        return unique[:10]
    
    def _calculate_saturation(self, keyword_counts: Counter) -> Dict[str, Any]:
        """Calculate keyword saturation levels."""
        if not keyword_counts:
            return {'level': 'low', 'oversaturated': [], 'opportunities': []}
        
        total = sum(keyword_counts.values())
        avg = total / len(keyword_counts)
        
        oversaturated = [k for k, c in keyword_counts.items() if c > avg * 2]
        underused = [k for k, c in keyword_counts.items() if c < avg * 0.5]
        
        return {
            'level': 'high' if len(oversaturated) > 5 else 'medium',
            'oversaturated': oversaturated[:5],
            'opportunities': underused[:5]
        }
    
    def _identify_messaging_gaps(
        self,
        common_themes: List[str],
        underutilized_themes: List[str],
        unique_angles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify specific messaging gaps."""
        gaps = []
        
        # Gap: Underutilized themes
        for theme in underutilized_themes[:3]:
            gaps.append({
                'type': 'underutilized_theme',
                'theme': theme,
                'description': f"Theme '{theme}' is rarely used by competitors",
                'opportunity': 'high'
            })
        
        # Gap: Missing counter-narratives
        if len(common_themes) > 3:
            gaps.append({
                'type': 'counter_narrative',
                'description': f"All competitors focus on {', '.join(common_themes[:3])}",
                'opportunity': 'medium'
            })
        
        return gaps
