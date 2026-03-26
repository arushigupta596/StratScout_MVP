"""
Intent Classifier - Classifies user query intent
"""
from typing import Dict, Any, List
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from ai_analysis.bedrock_client import BedrockClient

logger = get_logger(__name__)


class IntentClassifier:
    """Classifies user query intent."""
    
    # Intent patterns
    INTENT_PATTERNS = {
        'competitor_overview': [
            r'tell me about',
            r'who is',
            r'what does .* do',
            r'overview of',
            r'summary of'
        ],
        'campaign_analysis': [
            r'campaign',
            r'ads',
            r'advertising',
            r'creative',
            r'what are .* running'
        ],
        'gap_analysis': [
            r'gap',
            r'opportunity',
            r'missing',
            r'what should',
            r'recommend'
        ],
        'performance_comparison': [
            r'compare',
            r'versus',
            r'vs',
            r'better than',
            r'performance'
        ],
        'trend_analysis': [
            r'trend',
            r'pattern',
            r'over time',
            r'historical',
            r'evolution'
        ],
        'market_intelligence': [
            r'market',
            r'industry',
            r'landscape',
            r'competitive'
        ]
    }
    
    def __init__(self):
        """Initialize intent classifier."""
        self.bedrock_client = BedrockClient()
    
    def classify(
        self,
        query: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Classify user query intent.
        
        Args:
            query: User query
            conversation_history: Previous conversation messages
        
        Returns:
            Intent classification result
        """
        logger.info(f"Classifying intent for query: {query[:100]}")
        
        # Try pattern matching first (fast)
        pattern_intent = self._pattern_match(query)
        
        if pattern_intent:
            logger.info(f"Pattern matched intent: {pattern_intent}")
            return {
                'intent': pattern_intent,
                'entities': self._extract_entities(query),
                'confidence': 0.85
            }
        
        # Fall back to AI classification (slower but more accurate)
        try:
            ai_result = self._ai_classify(query, conversation_history)
            return ai_result
        except Exception as e:
            logger.warning(f"AI classification failed: {str(e)}")
            return {
                'intent': 'general_question',
                'entities': {},
                'confidence': 0.5
            }
    
    def _pattern_match(self, query: str) -> str:
        """Match query against intent patterns."""
        query_lower = query.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return None
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query."""
        entities = {}
        
        # Extract competitor names (Indian skincare brands)
        brands = [
            'mamaearth', 'plum', 'minimalist', 'derma co', 'dot & key',
            'bella vita', 'wow', 'mcaffeine', 'pilgrim', 'earth rhythm'
        ]
        
        query_lower = query.lower()
        for brand in brands:
            if brand in query_lower:
                entities['competitor'] = brand
                break
        
        # Extract time periods
        time_patterns = {
            'last_week': r'last week|past week',
            'last_month': r'last month|past month',
            'last_quarter': r'last quarter|past quarter',
            'this_year': r'this year|current year'
        }
        
        for period, pattern in time_patterns.items():
            if re.search(pattern, query_lower):
                entities['time_period'] = period
                break
        
        return entities
    
    def _ai_classify(
        self,
        query: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI to classify intent."""
        # Build context from conversation history
        context = ""
        if conversation_history:
            recent = conversation_history[-3:]  # Last 3 messages
            context = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in recent
            ])
        
        prompt = f"""Classify the user's intent for this competitive intelligence query.

Available intents:
- competitor_overview: User wants general information about a competitor
- campaign_analysis: User wants to analyze advertising campaigns
- gap_analysis: User wants to identify market opportunities
- performance_comparison: User wants to compare competitors
- trend_analysis: User wants to see trends over time
- market_intelligence: User wants market/industry insights
- general_question: General question or unclear intent

Conversation context:
{context}

User query: {query}

Respond with JSON:
{{
  "intent": "<intent_name>",
  "entities": {{"competitor": "<name>", "time_period": "<period>"}},
  "confidence": <0.0-1.0>
}}"""
        
        response = self.bedrock_client.invoke_model(
            prompt=prompt,
            max_tokens=200,
            temperature=0.3
        )
        
        # Parse response
        import json
        try:
            result = json.loads(response)
            return result
        except:
            # Fallback if JSON parsing fails
            return {
                'intent': 'general_question',
                'entities': {},
                'confidence': 0.5
            }
