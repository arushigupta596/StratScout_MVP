"""
Campaign Duration Prediction Model
"""
import sys
import os
from typing import Dict, Any, List
import statistics

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.utils import calculate_confidence_score, get_current_timestamp

logger = get_logger(__name__)


class DurationPredictor:
    """Predicts campaign duration based on historical patterns."""
    
    def __init__(self):
        """Initialize duration predictor."""
        # Base duration estimates (in days)
        self.base_duration = 30  # 30 days baseline
    
    def predict(
        self,
        historical_ads: List[Dict[str, Any]],
        campaign_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Predict campaign duration.
        
        Args:
            historical_ads: Historical ad data
            campaign_data: Optional specific campaign data
        
        Returns:
            Duration prediction dictionary
        """
        logger.info("Predicting campaign duration")
        
        campaign_data = campaign_data or {}
        
        # Calculate historical campaign durations
        historical_durations = self._calculate_historical_durations(historical_ads)
        
        # Predict duration
        if historical_durations and len(historical_durations) >= 3:
            # Use historical average
            avg_duration = statistics.mean(historical_durations)
            median_duration = statistics.median(historical_durations)
            
            # Weight average more heavily
            predicted_days = int((avg_duration * 0.7) + (median_duration * 0.3))
        else:
            # Use base duration
            predicted_days = self.base_duration
        
        # Adjust for campaign-specific factors
        if campaign_data:
            predicted_days = int(predicted_days * self._adjust_for_campaign_factors(campaign_data))
        
        # Calculate range
        predicted_min = max(int(predicted_days * 0.7), 7)  # At least 7 days
        predicted_max = int(predicted_days * 1.5)
        
        # Calculate confidence
        confidence_factors = {
            'historical_data': min(len(historical_durations) / 10, 1.0),
            'duration_consistency': self._assess_duration_consistency(historical_durations),
            'data_recency': self._assess_data_recency(historical_ads)
        }
        
        confidence = calculate_confidence_score(confidence_factors)
        
        # Compile factors
        factors = {
            'historical_campaigns': len(historical_durations),
            'avg_historical_duration': round(statistics.mean(historical_durations), 1) if historical_durations else None,
            'campaign_type': campaign_data.get('campaign_type', 'standard')
        }
        
        return {
            'days': predicted_days,
            'range': {
                'min': predicted_min,
                'max': predicted_max
            },
            'confidence': confidence,
            'factors': factors
        }
    
    def _calculate_historical_durations(self, historical_ads: List[Dict[str, Any]]) -> List[float]:
        """
        Calculate durations from historical ads.
        
        Args:
            historical_ads: Historical ad data
        
        Returns:
            List of durations in days
        """
        durations = []
        current_time = get_current_timestamp()
        
        for ad in historical_ads:
            start_date = ad.get('start_date', 0)
            is_active = ad.get('is_active', False)
            
            if not start_date:
                continue
            
            if is_active:
                # For active ads, calculate duration so far
                duration_ms = current_time - start_date
            else:
                # For inactive ads, try to get end date or estimate
                # For MVP, we'll estimate based on typical patterns
                # In production, track actual end dates
                duration_ms = 30 * 24 * 60 * 60 * 1000  # Assume 30 days
            
            duration_days = duration_ms / (1000 * 60 * 60 * 24)
            
            # Filter out unrealistic durations
            if 1 <= duration_days <= 365:
                durations.append(duration_days)
        
        return durations
    
    def _assess_duration_consistency(self, historical_durations: List[float]) -> float:
        """
        Assess consistency of historical durations.
        
        Args:
            historical_durations: List of durations
        
        Returns:
            Consistency score (0-1)
        """
        if len(historical_durations) < 2:
            return 0.5
        
        mean_duration = statistics.mean(historical_durations)
        if mean_duration == 0:
            return 0.5
        
        std_dev = statistics.stdev(historical_durations)
        cv = std_dev / mean_duration
        
        # Lower CV = higher consistency
        consistency = max(1.0 - (cv * 1.5), 0.3)
        
        return consistency
    
    def _assess_data_recency(self, historical_ads: List[Dict[str, Any]]) -> float:
        """
        Assess recency of historical data.
        
        Args:
            historical_ads: Historical ad data
        
        Returns:
            Recency score (0-1)
        """
        if not historical_ads:
            return 0.5
        
        current_time = get_current_timestamp()
        most_recent = max(ad.get('scraped_at', 0) for ad in historical_ads)
        
        days_old = (current_time - most_recent) / (1000 * 60 * 60 * 24)
        
        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        else:
            return 0.4
    
    def _adjust_for_campaign_factors(self, campaign_data: Dict[str, Any]) -> float:
        """
        Adjust duration for campaign-specific factors.
        
        Args:
            campaign_data: Campaign data
        
        Returns:
            Adjustment multiplier
        """
        adjustment = 1.0
        
        # Campaign type
        campaign_type = campaign_data.get('campaign_type', 'standard')
        if campaign_type == 'flash_sale':
            adjustment *= 0.3  # Much shorter
        elif campaign_type == 'seasonal':
            adjustment *= 1.5  # Longer
        elif campaign_type == 'brand_awareness':
            adjustment *= 2.0  # Much longer
        
        # Budget level
        budget_level = campaign_data.get('budget_level', 'medium')
        if budget_level == 'high':
            adjustment *= 1.3
        elif budget_level == 'low':
            adjustment *= 0.7
        
        # Seasonal indicator
        is_seasonal = campaign_data.get('is_seasonal', False)
        if is_seasonal:
            adjustment *= 1.2
        
        return adjustment
