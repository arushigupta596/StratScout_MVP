"""
Response Generator - Generates natural language responses
"""
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from ai_analysis.bedrock_client import BedrockClient

logger = get_logger(__name__)


class ResponseGenerator:
    """Generates natural language responses using AI."""
    
    def __init__(self):
        """Initialize response generator."""
        self.bedrock_client = BedrockClient()
    
    def generate(
        self,
        query: str,
        intent: str,
        data: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Generate natural language response.
        
        Args:
            query: User query
            intent: Classified intent
            data: Retrieved data
            conversation_history: Previous conversation messages
        
        Returns:
            Natural language response
        """
        logger.info(f"Generating response for intent: {intent}")
        
        try:
            # Build context
            context = self._build_context(conversation_history)
            
            # Build data summary
            data_summary = self._summarize_data(data, intent)
            
            # Generate response using Bedrock
            prompt = f"""You are Scout, an AI assistant for competitive intelligence in the Indian D2C beauty market.

User query: {query}

Intent: {intent}

Relevant data:
{data_summary}

Conversation context:
{context}

Generate a helpful, concise response that:
1. Directly answers the user's question
2. Uses specific data points from the retrieved data
3. Provides actionable insights
4. Maintains a professional but friendly tone
5. Keeps response under 200 words

Response:"""
            
            response = self.bedrock_client.invoke_model(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.strip()
        
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}", exc_info=True)
            return "I'm having trouble generating a response. Could you try rephrasing your question?"
    
    def _build_context(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Build conversation context."""
        if not conversation_history:
            return "No previous context"
        
        recent = conversation_history[-3:]  # Last 3 messages
        context_lines = []
        
        for msg in recent:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # Truncate long messages
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def _summarize_data(self, data: Dict[str, Any], intent: str) -> str:
        """Summarize retrieved data."""
        if not data:
            return "No data available"
        
        summary_lines = []
        
        # Competitors
        if 'competitors' in data:
            competitors = data['competitors']
            summary_lines.append(f"Found {len(competitors)} competitors")
            for comp in competitors[:3]:
                name = comp.get('name', 'Unknown')
                summary_lines.append(f"- {name}")
        
        # Ads
        if 'ads' in data:
            ads = data['ads']
            summary_lines.append(f"Found {len(ads)} ads")
        
        # Analyses
        if 'analyses' in data:
            analyses = data['analyses']
            summary_lines.append(f"Found {len(analyses)} analyses")
            for analysis in analyses[:2]:
                themes = analysis.get('messaging_analysis', {}).get('themes', [])
                if themes:
                    summary_lines.append(f"- Themes: {', '.join(themes[:3])}")
        
        # Gap analysis
        if 'gap_analysis' in data and data['gap_analysis']:
            gap = data['gap_analysis']
            opportunities = gap.get('opportunities', [])
            summary_lines.append(f"Found {len(opportunities)} opportunities")
            if opportunities:
                top = opportunities[0]
                summary_lines.append(f"- Top: {top.get('description', 'N/A')}")
        
        # Predictions
        if 'predictions' in data:
            predictions = data['predictions']
            summary_lines.append(f"Found {len(predictions)} predictions")
        
        return "\n".join(summary_lines) if summary_lines else "No specific data"
