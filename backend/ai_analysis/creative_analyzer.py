"""
Ad Creative Analysis using Amazon Bedrock
"""
import os
import sys
from typing import Dict, Any, List
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from common.utils import generate_id, get_current_timestamp, calculate_confidence_score
from common.errors import AIAnalysisError
from ai_analysis.bedrock_client import BedrockClient

logger = get_logger(__name__)


class CreativeAnalyzer:
    """Analyzes ad creatives using AI."""
    
    def __init__(self):
        """Initialize creative analyzer."""
        self.bedrock = BedrockClient()
        self.prompt_template = self._load_prompt_template('creative_analysis.txt')
    
    def _load_prompt_template(self, filename: str) -> str:
        """Load prompt template from file."""
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            'prompts',
            filename
        )
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found: {filename}")
            raise AIAnalysisError(f"Prompt template not found: {filename}")
    
    def analyze_creative(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single ad creative.
        
        Args:
            ad_data: Ad data dictionary from DynamoDB
        
        Returns:
            Analysis results dictionary
        """
        logger.info(f"Analyzing creative: {ad_data.get('ad_id')}")
        
        try:
            # Format prompt with ad data
            prompt = self.prompt_template.format(
                competitor_name=ad_data.get('competitor_name', 'Unknown'),
                ad_text=ad_data.get('ad_text', ''),
                platform=ad_data.get('platform', 'unknown'),
                start_date=self._format_date(ad_data.get('start_date', 0))
            )
            
            # Get structured analysis from Bedrock
            expected_fields = [
                'visual_themes',
                'messaging',
                'hooks_ctas',
                'positioning',
                'indian_context',
                'effectiveness',
                'confidence_score'
            ]
            
            analysis = self.bedrock.analyze_with_structured_output(
                prompt=prompt,
                expected_fields=expected_fields,
                system_prompt="You are an expert marketing analyst. Provide detailed, actionable insights."
            )
            
            # Validate and enrich analysis
            if 'error' in analysis:
                logger.warning(f"Failed to parse structured output for {ad_data.get('ad_id')}")
                return self._create_fallback_analysis(ad_data, analysis.get('raw_text', ''))
            
            # Add metadata
            analysis['analysis_id'] = generate_id('analysis', ad_data.get('ad_id', ''))
            analysis['ad_id'] = ad_data.get('ad_id')
            analysis['competitor_id'] = ad_data.get('competitor_id')
            analysis['created_at'] = get_current_timestamp()
            analysis['analysis_type'] = 'creative'
            
            # Calculate overall confidence
            if 'confidence_score' not in analysis or not isinstance(analysis['confidence_score'], (int, float)):
                analysis['confidence_score'] = self._calculate_analysis_confidence(analysis)
            
            logger.info(
                f"Creative analysis completed",
                extra={
                    'ad_id': ad_data.get('ad_id'),
                    'confidence': analysis['confidence_score']
                }
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Creative analysis failed: {str(e)}", exc_info=True)
            raise AIAnalysisError(f"Failed to analyze creative: {str(e)}")
    
    def batch_analyze_creatives(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple ad creatives.
        
        Args:
            ads: List of ad data dictionaries
        
        Returns:
            List of analysis results
        """
        logger.info(f"Batch analyzing {len(ads)} creatives")
        
        results = []
        for ad in ads:
            try:
                analysis = self.analyze_creative(ad)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze ad {ad.get('ad_id')}: {str(e)}")
                # Continue with other ads
        
        logger.info(f"Batch analysis completed: {len(results)}/{len(ads)} successful")
        return results
    
    def _format_date(self, timestamp: int) -> str:
        """Format timestamp to readable date."""
        if not timestamp:
            return 'Unknown'
        try:
            dt = datetime.fromtimestamp(timestamp / 1000)
            return dt.strftime('%Y-%m-%d')
        except:
            return 'Unknown'
    
    def _calculate_analysis_confidence(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score for analysis.
        
        Args:
            analysis: Analysis results
        
        Returns:
            Confidence score (0-1)
        """
        factors = {}
        
        # Check completeness of each section
        if 'visual_themes' in analysis and analysis['visual_themes']:
            factors['visual_themes'] = 1.0
        
        if 'messaging' in analysis and analysis['messaging']:
            factors['messaging'] = 1.0
        
        if 'hooks_ctas' in analysis and analysis['hooks_ctas']:
            factors['hooks_ctas'] = 1.0
        
        if 'positioning' in analysis and analysis['positioning']:
            factors['positioning'] = 1.0
        
        if 'effectiveness' in analysis and analysis['effectiveness']:
            factors['effectiveness'] = 1.0
        
        # Use effectiveness score if available
        if 'effectiveness' in analysis and 'score' in analysis['effectiveness']:
            try:
                effectiveness_score = float(analysis['effectiveness']['score']) / 10.0
                factors['effectiveness_score'] = effectiveness_score
            except:
                pass
        
        return calculate_confidence_score(factors)
    
    def _create_fallback_analysis(self, ad_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """
        Create fallback analysis when structured parsing fails.
        
        Args:
            ad_data: Original ad data
            raw_text: Raw AI response text
        
        Returns:
            Fallback analysis dictionary
        """
        return {
            'analysis_id': generate_id('analysis', ad_data.get('ad_id', '')),
            'ad_id': ad_data.get('ad_id'),
            'competitor_id': ad_data.get('competitor_id'),
            'created_at': get_current_timestamp(),
            'analysis_type': 'creative',
            'raw_analysis': raw_text,
            'confidence_score': 0.5,
            'error': 'Failed to parse structured output',
            'visual_themes': {},
            'messaging': {},
            'hooks_ctas': {},
            'positioning': {},
            'effectiveness': {'score': 5}
        }
