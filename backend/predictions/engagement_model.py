"""
Engagement Prediction Model
"""
import sys
import os
from typing import Dict, Any, List
import statistics

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.utils import calculate_confidence_score

logger = get_logger(__name__)


class EngagementPredictor:
    """Predicts campaign engagement based on creative quality and messaging."""
    
    def __init__(self):
        """Initialize engagement predictor."""
        # Base engagement rates for Indian D2C beauty brands (demo values)
        self.base_engagement_rate = 0.03  # 3% baseline
    
    def predict(
        self,
        historical_metrics: Dict[str, Any],
        historical_analyses: List[Dict[str, Any]],
        campaign_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Predict campaign engagement.
        
        Args:
            historical_metrics: Historical performance metrics
            historical_analyses: Historical analysis results
            campaign_data: Optional specific campaign data
        
        Returns:
            Engagement prediction dictionary
        """
        logger.info("Predicting campaign engagement")
        
        campaign_data = campaign_data or {}
        
        # Calculate engagement multiplier from creative quality
        multiplier = self._calculate_engagement_multiplier(
            historical_metrics,
            historical_analyses
        )
        
        # Adjust for campaign-specific factors
        if campaign_data:
            multiplier *= self._adjust_for_campaign_factors(campaign_data)
        
        # Calculate engagement predictions
        predicted_rate = self.base_engagement_rate * multiplier
        predicted_rate = min(max(predicted_rate, 0.005), 0.15)  # Clamp between 0.5% and 15%
        
        # Convert to engagement score (0-10)
        predicted_score = (predicted_rate / 0.15) * 10
        
        # Calculate confidence
        confidence_factors = {
            'analysis_coverage': min(len(historical_analyses) / 10, 1.0),
            'effectiveness_consistency': self._assess_effectiveness_consistency(historical_analyses),
            'data_quality': min(historical_metrics.get('total_ads', 0) / 15, 1.0)
        }
        
        confidence = calculate_confidence_score(confidence_factors)
        
        # Compile factors
        factors = {
            'avg_effectiveness': historical_metrics.get('avg_effectiveness', 5.0),
            'creative_diversity': historical_metrics.get('creative_diversity', 0.5),
            'num_analyses': len(historical_analyses),
            'multiplier_applied': round(multiplier, 2)
        }
        
        return {
            'rate': round(predicted_rate, 4),
            'score': round(predicted_score, 2),
            'confidence': confidence,
            'factors': factors
        }
    
    def _calculate_engagement_multiplier(
        self,
        historical_metrics: Dict[str, Any],
        historical_analyses: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate engagement multiplier from creative quality.
        
        Args:
            historical_metrics: Historical metrics
            historical_analyses: Analysis results
        
        Returns:
            Multiplier value
        """
        multiplier = 1.0
        
        # Effectiveness score factor
        avg_effectiveness = historical_metrics.get('avg_effectiveness', 5.0)
        # Map 0-10 score to 0.5-1.5 multiplier
        effectiveness_multiplier = 0.5 + (avg_effectiveness / 10) * 1.0
        multiplier *= effectiveness_multiplier
        
        # Creative diversity factor
        diversity = historical_metrics.get('creative_diversity', 0.5)
        multiplier *= (0.9 + (diversity * 0.2))  # 0.9 to 1.1 range
        
        # Messaging strength factor
        messaging_strength = self._assess_messaging_strength(historical_analyses)
        multiplier *= (0.8 + (messaging_strength * 0.4))  # 0.8 to 1.2 range
        
        return multiplier
    
    def _assess_messaging_strength(self, historical_analyses: List[Dict[str, Any]]) -> float:
        """
        Assess messaging strength from analyses.
        
        Args:
            historical_analyses: Analysis results
        
        Returns:
            Strength score (0-1)
        """
        if not historical_analyses:
            return 0.5
        
        scores = []
        
        for analysis in historical_analyses:
            # Look for messaging effectiveness scores
            if 'effectiveness_scores' in analysis:
                eff_scores = analysis['effectiveness_scores']
                if isinstance(eff_scores, dict):
                    # Average the effectiveness sub-scores
                    sub_scores = []
                    for key in ['clarity_consistency', 'emotional_resonance', 'differentiation']:
                        if key in eff_scores:
                            try:
                                sub_scores.append(float(eff_scores[key]) / 10)
                            except:
                                pass
                    
                    if sub_scores:
                        scores.append(statistics.mean(sub_scores))
        
        if scores:
            return statistics.mean(scores)
        
        return 0.5
    
    def _assess_effectiveness_consistency(self, historical_analyses: List[Dict[str, Any]]) -> float:
        """
        Assess consistency of effectiveness scores.
        
        Args:
            historical_analyses: Analysis results
        
        Returns:
            Consistency score (0-1)
        """
        if not historical_analyses:
            return 0.5
        
        scores = []
        for analysis in historical_analyses:
            if 'effectiveness' in analysis and 'score' in analysis['effectiveness']:
                try:
                    scores.append(float(analysis['effectiveness']['score']))
                except:
                    pass
        
        if len(scores) < 2:
            return 0.5
        
        # Calculate coefficient of variation (lower = more consistent)
        mean_score = statistics.mean(scores)
        if mean_score == 0:
            return 0.5
        
        std_dev = statistics.stdev(scores)
        cv = std_dev / mean_score
        
        # Map CV to consistency score (lower CV = higher consistency)
        # CV of 0 = 1.0, CV of 0.5+ = 0.5
        consistency = max(1.0 - (cv * 2), 0.5)
        
        return consistency
    
    def _adjust_for_campaign_factors(self, campaign_data: Dict[str, Any]) -> float:
        """
        Adjust multiplier for campaign-specific factors.
        
        Args:
            campaign_data: Campaign data
        
        Returns:
            Adjustment multiplier
        """
        adjustment = 1.0
        
        # Creative quality indicator
        creative_quality = campaign_data.get('creative_quality', 'medium')
        if creative_quality == 'high':
            adjustment *= 1.3
        elif creative_quality == 'low':
            adjustment *= 0.7
        
        # Offer strength
        has_strong_offer = campaign_data.get('has_strong_offer', False)
        if has_strong_offer:
            adjustment *= 1.2
        
        # Urgency factor
        has_urgency = campaign_data.get('has_urgency', False)
        if has_urgency:
            adjustment *= 1.15
        
        return adjustment
