"""
Messaging Strategy Decoder using Amazon Bedrock
"""
import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.utils import generate_id, get_current_timestamp
from common.errors import AIAnalysisError
from ai_analysis.bedrock_client import BedrockClient

logger = get_logger(__name__)


class MessagingDecoder:
    """Decodes messaging strategy patterns across multiple ads."""
    
    def __init__(self):
        """Initialize messaging decoder."""
        self.bedrock = BedrockClient()
        self.prompt_template = self._load_prompt_template('messaging_analysis.txt')
    
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
    
    def analyze_messaging_strategy(
        self,
        competitor_id: str,
        competitor_name: str,
        ads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze messaging strategy across multiple ads.
        
        Args:
            competitor_id: Competitor ID
            competitor_name: Competitor name
            ads: List of ad data dictionaries
        
        Returns:
            Messaging analysis results
        """
        logger.info(f"Analyzing messaging strategy for {competitor_name} ({len(ads)} ads)")
        
        if not ads:
            raise AIAnalysisError("No ads provided for messaging analysis")
        
        try:
            # Format ads data for prompt
            ads_data = self._format_ads_data(ads)
            
            # Format prompt
            prompt = self.prompt_template.format(
                competitor_name=competitor_name,
                num_ads=len(ads),
                ads_data=ads_data
            )
            
            # Get structured analysis from Bedrock
            expected_fields = [
                'messaging_themes',
                'messaging_evolution',
                'keywords',
                'value_proposition',
                'audience_targeting',
                'effectiveness_scores',
                'confidence_score'
            ]
            
            analysis = self.bedrock.analyze_with_structured_output(
                prompt=prompt,
                expected_fields=expected_fields,
                system_prompt="You are an expert marketing strategist. Analyze messaging patterns and provide actionable insights."
            )
            
            # Add metadata
            analysis['analysis_id'] = generate_id('messaging', competitor_id)
            analysis['competitor_id'] = competitor_id
            analysis['competitor_name'] = competitor_name
            analysis['created_at'] = get_current_timestamp()
            analysis['analysis_type'] = 'messaging_strategy'
            analysis['num_ads_analyzed'] = len(ads)
            
            # Ensure confidence score
            if 'confidence_score' not in analysis or not isinstance(analysis['confidence_score'], (int, float)):
                analysis['confidence_score'] = 0.8  # Default for messaging analysis
            
            logger.info(
                f"Messaging analysis completed",
                extra={
                    'competitor_id': competitor_id,
                    'num_ads': len(ads),
                    'confidence': analysis.get('confidence_score', 0)
                }
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Messaging analysis failed: {str(e)}", exc_info=True)
            raise AIAnalysisError(f"Failed to analyze messaging strategy: {str(e)}")
    
    def _format_ads_data(self, ads: List[Dict[str, Any]]) -> str:
        """
        Format ads data for prompt.
        
        Args:
            ads: List of ad data
        
        Returns:
            Formatted string
        """
        formatted = []
        
        for i, ad in enumerate(ads[:20], 1):  # Limit to 20 ads to avoid token limits
            ad_text = ad.get('ad_text', 'No text available')
            platform = ad.get('platform', 'unknown')
            
            formatted.append(f"Ad {i} ({platform}):\n{ad_text}\n")
        
        if len(ads) > 20:
            formatted.append(f"\n... and {len(ads) - 20} more ads")
        
        return '\n'.join(formatted)
    
    def extract_messaging_categories(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Extract messaging categories from analysis.
        
        Args:
            analysis: Messaging analysis results
        
        Returns:
            List of category names
        """
        categories = []
        
        if 'messaging_themes' in analysis and 'themes' in analysis['messaging_themes']:
            themes = analysis['messaging_themes']['themes']
            if isinstance(themes, list):
                categories = [theme.get('name', '') for theme in themes if isinstance(theme, dict)]
        
        return categories
    
    def get_top_keywords(self, analysis: Dict[str, Any], limit: int = 10) -> List[str]:
        """
        Get top keywords from analysis.
        
        Args:
            analysis: Messaging analysis results
            limit: Maximum number of keywords
        
        Returns:
            List of top keywords
        """
        keywords = []
        
        if 'keywords' in analysis:
            top_keywords = analysis['keywords'].get('top_keywords', [])
            if isinstance(top_keywords, list):
                keywords = top_keywords[:limit]
        
        return keywords
