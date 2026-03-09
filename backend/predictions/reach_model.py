"""
Reach Prediction Model
"""
import sys
import os
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.utils import calculate_confidence_score

logger = get_logger(__name__)


class ReachPredictor:
    """Predicts campaign reach based on historical patterns."""
    
    def __init__(self):
        """Initialize reach predictor."""
        # Base reach estimates for Indian D2C beauty brands (demo values)
        self.base_reach = {
            'low': 10000,
            'medium': 50000,
            'high': 200000
        }
    
    def predict(
        self,
        historical_metrics: Dict[str, Any],
        campaign_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Predict campaign reach.
        
        Args:
            historical_metrics: Historical performance metrics
            campaign_data: Optional specific campaign data
        
        Returns:
            Reach prediction dictionary
        """
        logger.info("Predicting campaign reach")
        
        campaign_data = campaign_data or {}
        
        # Calculate base reach multiplier from historical data
        multiplier = self._calculate_reach_multiplier(historical_metrics)
        
        # Adjust for campaign-specific factors
        if campaign_data:
            multiplier *= self._adjust_for_campaign_factors(campaign_data)
        
        # Calculate reach estimates
        base = self.base_reach['medium']
        predicted_avg = int(base * multiplier)
        predicted_min = int(predicted_avg * 0.7)  # -30%
        predicted_max = int(predicted_avg * 1.5)  # +50%
        
        # Calculate confidence
        confidence_factors = {
            'data_volume': min(historical_metrics.get('total_ads', 0) / 20, 1.0),
            'creative_diversity': historical_metrics.get('creative_diversity', 0.5),
            'platform_coverage': self._assess_platform_coverage(historical_metrics)
        }
        
        confidence = calculate_confidence_score(confidence_factors)
        
        # Compile factors that influenced prediction
        factors = {
            'ad_volume': historical_metrics.get('total_ads', 0),
            'creative_diversity': historical_metrics.get('creative_diversity', 0),
            'platform_distribution': historical_metrics.get('platforms', {}),
            'multiplier_applied': round(multiplier, 2)
        }
        
        return {
            'min': predicted_min,
            'max': predicted_max,
            'avg': predicted_avg,
            'confidence': confidence,
            'factors': factors
        }
    
    def _calculate_reach_multiplier(self, historical_metrics: Dict[str, Any]) -> float:
        """
        Calculate reach multiplier based on historical performance.
        
        Args:
            historical_metrics: Historical metrics
        
        Returns:
            Multiplier value
        """
        multiplier = 1.0
        
        # Ad volume factor (more ads = more reach)
        total_ads = historical_metrics.get('total_ads', 0)
        if total_ads >= 20:
            multiplier *= 1.3
        elif total_ads >= 10:
            multiplier *= 1.15
        elif total_ads >= 5:
            multiplier *= 1.0
        else:
            multiplier *= 0.8
        
        # Creative diversity factor (more variety = better reach)
        diversity = historical_metrics.get('creative_diversity', 0.5)
        multiplier *= (0.8 + (diversity * 0.4))  # 0.8 to 1.2 range
        
        # Platform coverage factor
        platforms = historical_metrics.get('platforms', {})
        num_platforms = len(platforms)
        if num_platforms >= 2:
            multiplier *= 1.2
        
        return multiplier
    
    def _adjust_for_campaign_factors(self, campaign_data: Dict[str, Any]) -> float:
        """
        Adjust multiplier for specific campaign factors.
        
        Args:
            campaign_data: Campaign-specific data
        
        Returns:
            Adjustment multiplier
        """
        adjustment = 1.0
        
        # Budget indicator (if provided)
        budget_level = campaign_data.get('budget_level', 'medium')
        if budget_level == 'high':
            adjustment *= 1.3
        elif budget_level == 'low':
            adjustment *= 0.7
        
        # Seasonal factor
        is_seasonal = campaign_data.get('is_seasonal', False)
        if is_seasonal:
            adjustment *= 1.2
        
        # Target audience size
        audience_size = campaign_data.get('audience_size', 'medium')
        if audience_size == 'large':
            adjustment *= 1.25
        elif audience_size == 'small':
            adjustment *= 0.8
        
        return adjustment
    
    def _assess_platform_coverage(self, historical_metrics: Dict[str, Any]) -> float:
        """
        Assess platform coverage quality.
        
        Args:
            historical_metrics: Historical metrics
        
        Returns:
            Coverage score (0-1)
        """
        platforms = historical_metrics.get('platforms', {})
        
        if not platforms:
            return 0.5
        
        # Score based on number of platforms
        num_platforms = len(platforms)
        if num_platforms >= 3:
            return 1.0
        elif num_platforms == 2:
            return 0.8
        else:
            return 0.6
