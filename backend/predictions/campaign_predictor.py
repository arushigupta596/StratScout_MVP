"""
Campaign Performance Predictor
"""
import sys
import os
from typing import Dict, Any, List
import statistics

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.utils import generate_id, get_current_timestamp, calculate_confidence_score
from common.errors import PredictionError
from predictions.reach_model import ReachPredictor
from predictions.engagement_model import EngagementPredictor
from predictions.duration_model import DurationPredictor

logger = get_logger(__name__)


class CampaignPredictor:
    """Predicts campaign performance metrics."""
    
    def __init__(self):
        """Initialize campaign predictor."""
        self.reach_predictor = ReachPredictor()
        self.engagement_predictor = EngagementPredictor()
        self.duration_predictor = DurationPredictor()
    
    def predict_campaign(
        self,
        competitor_id: str,
        historical_ads: List[Dict[str, Any]],
        historical_analyses: List[Dict[str, Any]],
        campaign_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive campaign predictions.
        
        Args:
            competitor_id: Competitor ID
            historical_ads: Historical ad data
            historical_analyses: Historical analysis results
            campaign_data: Optional specific campaign data
        
        Returns:
            Prediction results dictionary
        """
        logger.info(f"Generating campaign predictions for {competitor_id}")
        
        try:
            # Calculate historical metrics
            historical_metrics = self._calculate_historical_metrics(
                historical_ads,
                historical_analyses
            )
            
            # Predict reach
            reach_prediction = self.reach_predictor.predict(
                historical_metrics,
                campaign_data
            )
            
            # Predict engagement
            engagement_prediction = self.engagement_predictor.predict(
                historical_metrics,
                historical_analyses,
                campaign_data
            )
            
            # Predict duration
            duration_prediction = self.duration_predictor.predict(
                historical_ads,
                campaign_data
            )
            
            # Calculate overall confidence
            confidence_factors = {
                'reach': reach_prediction.get('confidence', 0.7),
                'engagement': engagement_prediction.get('confidence', 0.7),
                'duration': duration_prediction.get('confidence', 0.7),
                'data_quality': self._assess_data_quality(historical_ads, historical_analyses)
            }
            
            overall_confidence = calculate_confidence_score(confidence_factors)
            
            # Compile prediction
            prediction = {
                'prediction_id': generate_id('pred', competitor_id),
                'competitor_id': competitor_id,
                'created_at': get_current_timestamp(),
                'prediction_type': 'campaign_performance',
                
                # Reach prediction
                'reach': {
                    'predicted_min': reach_prediction.get('min', 0),
                    'predicted_max': reach_prediction.get('max', 0),
                    'predicted_avg': reach_prediction.get('avg', 0),
                    'confidence': reach_prediction.get('confidence', 0.7),
                    'factors': reach_prediction.get('factors', {})
                },
                
                # Engagement prediction
                'engagement': {
                    'predicted_rate': engagement_prediction.get('rate', 0),
                    'predicted_score': engagement_prediction.get('score', 0),
                    'confidence': engagement_prediction.get('confidence', 0.7),
                    'factors': engagement_prediction.get('factors', {})
                },
                
                # Duration prediction
                'duration': {
                    'predicted_days': duration_prediction.get('days', 0),
                    'predicted_range': duration_prediction.get('range', {}),
                    'confidence': duration_prediction.get('confidence', 0.7),
                    'factors': duration_prediction.get('factors', {})
                },
                
                # Overall metrics
                'overall_confidence': overall_confidence,
                'historical_data_points': len(historical_ads),
                'historical_analyses': len(historical_analyses),
                
                # Metadata
                'model_version': '1.0',
                'prediction_date': get_current_timestamp()
            }
            
            logger.info(
                f"Campaign predictions generated",
                extra={
                    'competitor_id': competitor_id,
                    'confidence': overall_confidence,
                    'reach_avg': reach_prediction.get('avg', 0),
                    'engagement_rate': engagement_prediction.get('rate', 0)
                }
            )
            
            return prediction
        
        except Exception as e:
            logger.error(f"Campaign prediction failed: {str(e)}", exc_info=True)
            raise PredictionError(f"Failed to predict campaign: {str(e)}")
    
    def _calculate_historical_metrics(
        self,
        historical_ads: List[Dict[str, Any]],
        historical_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate aggregate metrics from historical data.
        
        Args:
            historical_ads: Historical ad data
            historical_analyses: Historical analysis results
        
        Returns:
            Metrics dictionary
        """
        if not historical_ads:
            return {}
        
        # Calculate ad volume metrics
        total_ads = len(historical_ads)
        active_ads = sum(1 for ad in historical_ads if ad.get('is_active', False))
        
        # Calculate platform distribution
        platforms = {}
        for ad in historical_ads:
            platform = ad.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
        
        # Calculate creative diversity (unique ad texts)
        unique_texts = len(set(ad.get('ad_text', '') for ad in historical_ads))
        creative_diversity = unique_texts / total_ads if total_ads > 0 else 0
        
        # Calculate average effectiveness from analyses
        effectiveness_scores = []
        for analysis in historical_analyses:
            if 'effectiveness' in analysis and 'score' in analysis['effectiveness']:
                try:
                    score = float(analysis['effectiveness']['score'])
                    effectiveness_scores.append(score)
                except:
                    pass
        
        avg_effectiveness = statistics.mean(effectiveness_scores) if effectiveness_scores else 5.0
        
        return {
            'total_ads': total_ads,
            'active_ads': active_ads,
            'platforms': platforms,
            'creative_diversity': creative_diversity,
            'avg_effectiveness': avg_effectiveness,
            'num_analyses': len(historical_analyses)
        }
    
    def _assess_data_quality(
        self,
        historical_ads: List[Dict[str, Any]],
        historical_analyses: List[Dict[str, Any]]
    ) -> float:
        """
        Assess quality of historical data for predictions.
        
        Args:
            historical_ads: Historical ad data
            historical_analyses: Historical analysis results
        
        Returns:
            Quality score (0-1)
        """
        factors = {}
        
        # Data volume
        if len(historical_ads) >= 20:
            factors['volume'] = 1.0
        elif len(historical_ads) >= 10:
            factors['volume'] = 0.8
        elif len(historical_ads) >= 5:
            factors['volume'] = 0.6
        else:
            factors['volume'] = 0.4
        
        # Analysis coverage
        analysis_coverage = len(historical_analyses) / len(historical_ads) if historical_ads else 0
        factors['analysis_coverage'] = min(analysis_coverage, 1.0)
        
        # Data recency (check if we have recent data)
        if historical_ads:
            most_recent = max(ad.get('scraped_at', 0) for ad in historical_ads)
            current_time = get_current_timestamp()
            days_old = (current_time - most_recent) / (1000 * 60 * 60 * 24)
            
            if days_old <= 7:
                factors['recency'] = 1.0
            elif days_old <= 30:
                factors['recency'] = 0.8
            elif days_old <= 90:
                factors['recency'] = 0.6
            else:
                factors['recency'] = 0.4
        
        return calculate_confidence_score(factors)
