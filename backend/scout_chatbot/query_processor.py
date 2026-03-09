"""
Query Processor for Scout Chatbot
"""
import boto3
import json
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger
from common.config import Config
from ai_analysis.bedrock_client import BedrockClient

logger = get_logger(__name__)


class QueryProcessor:
    """Process user queries and generate responses."""
    
    def __init__(self):
        """Initialize query processor."""
        self.dynamodb = boto3.resource('dynamodb')
        self.competitor_table = self.dynamodb.Table(Config.COMPETITOR_TABLE)
        self.ad_table = self.dynamodb.Table(Config.AD_DATA_TABLE)
        self.prediction_table = self.dynamodb.Table(Config.PREDICTION_TABLE)
        self.gap_table = self.dynamodb.Table(Config.GAP_ANALYSIS_TABLE)
        self.bedrock_client = BedrockClient()
    
    def process_query(
        self,
        query: str,
        user_id: str,
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query and generate response using LLM.
        
        Args:
            query: User query
            user_id: User identifier
            conversation_history: Previous messages
        
        Returns:
            Response with answer and metadata
        """
        logger.info(f"Processing query: {query[:50]}...")
        
        # Detect intent
        intent = self._detect_intent(query)
        
        # Gather relevant data based on intent
        context_data = self._gather_context(query, intent)
        
        # Generate response using LLM
        response = self._generate_llm_response(query, intent, context_data, conversation_history)
        
        return response
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['gap', 'opportunity', 'market', 'missing', 'underutilized']):
            return 'gap_analysis'
        elif any(word in query_lower for word in ['predict', 'forecast', 'future', 'will', 'expect']):
            return 'predictions'
        elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference', 'better', 'worse']):
            return 'comparison'
        elif any(word in query_lower for word in ['campaign', 'ad', 'creative', 'performing', 'top', 'best', 'recent']):
            return 'competitor_info'
        elif any(word in query_lower for word in ['mamaearth', 'derma', 'plum', 'dot', 'key', 'minimalist']):
            return 'competitor_info'
        else:
            return 'general'
    
    def _gather_context(self, query: str, intent: str) -> Dict[str, Any]:
        """Gather relevant data for the query."""
        context = {
            'competitors': [],
            'ads': [],
            'predictions': [],
            'gaps': []
        }
        
        query_lower = query.lower()
        
        # Get competitors
        competitors = self.competitor_table.scan().get('Items', [])
        context['competitors'] = competitors
        
        # Check if asking about specific competitor
        specific_competitor = None
        for comp in competitors:
            if comp['name'].lower() in query_lower:
                specific_competitor = comp
                break
        
        # Get ads (limit to specific competitor if mentioned)
        if specific_competitor:
            try:
                ad_response = self.ad_table.query(
                    IndexName='CompetitorIndex',
                    KeyConditionExpression='competitor_id = :cid',
                    ExpressionAttributeValues={':cid': specific_competitor['competitorId']},
                    Limit=20,
                    ScanIndexForward=False
                )
                context['ads'] = ad_response.get('Items', [])
            except Exception as e:
                logger.error(f"Failed to get ads: {str(e)}")
        else:
            # Get sample ads from all competitors
            try:
                ad_response = self.ad_table.scan(Limit=10)
                context['ads'] = ad_response.get('Items', [])
            except Exception as e:
                logger.error(f"Failed to get ads: {str(e)}")
        
        # Get predictions if relevant
        if intent in ['predictions', 'comparison']:
            try:
                pred_response = self.prediction_table.scan(Limit=10)
                context['predictions'] = pred_response.get('Items', [])
            except Exception as e:
                logger.error(f"Failed to get predictions: {str(e)}")
        
        # Get gap analysis if relevant
        if intent in ['gap_analysis', 'comparison']:
            try:
                gap_response = self.gap_table.scan(Limit=1)
                if gap_response.get('Items'):
                    context['gaps'] = gap_response['Items'][0]
            except Exception as e:
                logger.error(f"Failed to get gaps: {str(e)}")
        
        return context
    
    def _generate_llm_response(
        self,
        query: str,
        intent: str,
        context_data: Dict[str, Any],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response using Bedrock LLM."""
        
        # Build context summary
        context_summary = self._build_context_summary(context_data)
        
        # Build conversation context
        conv_context = ""
        if conversation_history and len(conversation_history) > 0:
            recent_messages = conversation_history[-4:]  # Last 2 exchanges
            for msg in recent_messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conv_context += f"{role.capitalize()}: {content}\n"
        
        # Create system prompt
        system_prompt = """You are Scout, an AI assistant for competitive intelligence in the Indian D2C skincare market. 
You help analyze competitor campaigns, identify market gaps, and provide strategic insights.

Be concise, data-driven, and actionable. Use the provided data to answer questions accurately.
Format your responses clearly with bullet points or numbered lists when appropriate."""
        
        # Create user prompt with context
        user_prompt = f"""Based on the following competitive intelligence data, answer this question:

Question: {query}

Available Data:
{context_summary}

{f"Previous conversation:\n{conv_context}" if conv_context else ""}

Provide a helpful, specific answer using the data above. If the data doesn't contain enough information, say so and suggest what additional data would be helpful."""
        
        try:
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            answer = response['text'].strip()
            
            return {
                'answer': answer,
                'intent': intent,
                'data': context_data,
                'confidence': 0.85
            }
        
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            # Fallback to simple response
            return self._fallback_response(query, intent, context_data)
    
    def _build_context_summary(self, context_data: Dict[str, Any]) -> str:
        """Build a concise summary of context data for LLM."""
        summary = []
        
        # Competitors
        if context_data.get('competitors'):
            summary.append(f"Competitors ({len(context_data['competitors'])}):")
            for comp in context_data['competitors']:
                summary.append(f"  - {comp['name']} (ID: {comp['competitorId']})")
        
        # Ads
        if context_data.get('ads'):
            summary.append(f"\nRecent Campaigns ({len(context_data['ads'])}):")
            for i, ad in enumerate(context_data['ads'][:10], 1):
                summary.append(f"  {i}. {ad.get('page_name', 'Unknown')}")
                if ad.get('ad_text'):
                    text = ad['ad_text'][:150]
                    summary.append(f"     Text: {text}...")
                summary.append(f"     Platforms: {', '.join(ad.get('platforms', []))}")
                summary.append(f"     Status: {'Active' if ad.get('is_active') else 'Inactive'}")
        
        # Predictions
        if context_data.get('predictions'):
            summary.append(f"\nPredictions ({len(context_data['predictions'])}):")
            for pred in context_data['predictions'][:5]:
                comp_id = pred.get('competitor_id', 'Unknown')
                reach = pred.get('reach_prediction', {}).get('avg_reach', 0)
                confidence = pred.get('confidence', 0)
                summary.append(f"  - {comp_id}: Avg reach {reach}, Confidence {confidence}")
        
        # Gap Analysis
        if context_data.get('gaps'):
            gaps = context_data['gaps']
            if gaps.get('opportunities'):
                summary.append(f"\nMarket Opportunities ({len(gaps['opportunities'])}):")
                for opp in gaps['opportunities'][:5]:
                    summary.append(f"  - {opp.get('type')}: {opp.get('description')} (Priority: {opp.get('priority')})")
        
        return '\n'.join(summary)
    
    def _fallback_response(self, query: str, intent: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback response if LLM fails - provide intelligent data-driven answer."""
        competitors = context_data.get('competitors', [])
        ads = context_data.get('ads', [])
        predictions = context_data.get('predictions', [])
        gaps = context_data.get('gaps', {})
        
        query_lower = query.lower()
        charts = []
        
        # Detect if user wants a chart/graph
        wants_chart = any(word in query_lower for word in ['chart', 'graph', 'visualize', 'plot', 'compare', 'show me'])
        
        # Handle competitor-specific queries
        for comp in competitors:
            if comp['name'].lower() in query_lower:
                comp_ads = [ad for ad in ads if ad.get('competitor_id') == comp['competitorId']]
                
                if comp_ads:
                    answer = f"📊 **{comp['name']} Campaign Analysis**\n\n"
                    answer += f"I found {len(comp_ads)} recent campaigns:\n\n"
                    
                    for i, ad in enumerate(comp_ads[:5], 1):
                        answer += f"**{i}. {ad.get('page_name', 'Campaign')}**\n"
                        if ad.get('ad_text'):
                            text = ad['ad_text'][:120] + '...' if len(ad.get('ad_text', '')) > 120 else ad.get('ad_text', '')
                            answer += f"   💬 {text}\n"
                        answer += f"   📱 Platforms: {', '.join(ad.get('platforms', ['Unknown']))}\n"
                        answer += f"   {'🟢 Active' if ad.get('is_active') else '🔴 Inactive'}\n\n"
                    
                    if len(comp_ads) > 5:
                        answer += f"_...and {len(comp_ads) - 5} more campaigns_\n"
                    
                    # Generate chart for platform distribution
                    if wants_chart:
                        charts.append(self._generate_platform_chart(comp_ads, comp['name']))
                    
                    return {
                        'answer': answer,
                        'intent': intent,
                        'data': {'competitor': comp, 'ads': comp_ads},
                        'charts': charts,
                        'confidence': 0.85
                    }
        
        # Handle comparison queries - generate comparison charts
        if intent == 'comparison' or 'compare' in query_lower:
            if predictions:
                charts.append(self._generate_reach_comparison_chart(predictions, competitors))
                answer = f"📊 **Competitor Comparison**\n\n"
                answer += f"Comparing {len(predictions)} competitors by predicted reach.\n"
                answer += f"See the chart below for visual comparison.\n"
            else:
                # Compare by campaign count
                charts.append(self._generate_campaign_count_chart(competitors, ads))
                answer = f"📊 **Competitor Comparison**\n\n"
                answer += f"Comparing {len(competitors)} competitors by campaign activity.\n"
                answer += f"See the chart below for visual comparison.\n"
            
            return {
                'answer': answer,
                'intent': intent,
                'data': {'competitors': competitors, 'predictions': predictions},
                'charts': charts,
                'confidence': 0.85
            }
        
        # Handle gap analysis queries
        if intent == 'gap_analysis' and gaps:
            opportunities = gaps.get('opportunities', [])
            answer = f"🎯 **Market Opportunities**\n\n"
            answer += f"I identified {len(opportunities)} opportunities:\n\n"
            
            for opp in opportunities[:6]:
                priority_emoji = '🔴' if opp.get('priority') == 'high' else '🟡' if opp.get('priority') == 'medium' else '🟢'
                answer += f"{priority_emoji} **{opp.get('type', 'Opportunity').replace('_', ' ').title()}**\n"
                answer += f"   {opp.get('description')}\n"
                answer += f"   Priority: {opp.get('priority', 'unknown').upper()}\n\n"
            
            # Generate chart for opportunities by priority
            if wants_chart:
                charts.append(self._generate_opportunities_chart(opportunities))
            
            return {
                'answer': answer,
                'intent': intent,
                'data': gaps,
                'charts': charts,
                'confidence': 0.85
            }
        
        # Handle prediction queries
        if intent == 'predictions' and predictions:
            answer = f"📈 **Campaign Performance Predictions**\n\n"
            
            for pred in predictions[:5]:
                comp_id = pred.get('competitor_id', 'Unknown')
                comp_name = next((c['name'] for c in competitors if c['competitorId'] == comp_id), comp_id)
                reach = pred.get('reach_prediction', {}).get('avg_reach', 0)
                confidence = pred.get('confidence', 0)
                
                answer += f"**{comp_name}**\n"
                answer += f"   📊 Predicted Reach: {int(reach):,}\n"
                answer += f"   ✅ Confidence: {int(confidence * 100)}%\n\n"
            
            # Generate chart for predictions
            if wants_chart or 'chart' in query_lower or 'graph' in query_lower:
                charts.append(self._generate_reach_comparison_chart(predictions, competitors))
            
            return {
                'answer': answer,
                'intent': intent,
                'data': predictions,
                'charts': charts,
                'confidence': 0.85
            }
        
        # General response with data summary
        answer = f"📊 **Competitive Intelligence Summary**\n\n"
        answer += f"I have data on:\n"
        answer += f"• {len(competitors)} competitors tracked\n"
        answer += f"• {len(ads)} campaigns analyzed\n"
        
        if predictions:
            answer += f"• {len(predictions)} performance predictions\n"
        if gaps:
            answer += f"• {len(gaps.get('opportunities', []))} market opportunities\n"
        
        answer += f"\n💡 Try asking:\n"
        answer += f"• 'What are Mamaearth's campaigns?'\n"
        answer += f"• 'Compare competitor reach predictions'\n"
        answer += f"• 'Show me a chart of market opportunities'\n"
        answer += f"• 'Visualize campaign activity by competitor'\n"
        
        return {
            'answer': answer,
            'intent': intent,
            'data': context_data,
            'charts': charts,
            'confidence': 0.7
        }
    
    def _generate_platform_chart(self, ads: List[Dict], competitor_name: str) -> Dict[str, Any]:
        """Generate chart data for platform distribution."""
        platform_counts = {}
        for ad in ads:
            for platform in ad.get('platforms', []):
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        return {
            'type': 'bar',
            'title': f'{competitor_name} - Platform Distribution',
            'data': [
                {'name': platform, 'value': count}
                for platform, count in platform_counts.items()
            ]
        }
    
    def _generate_reach_comparison_chart(self, predictions: List[Dict], competitors: List[Dict]) -> Dict[str, Any]:
        """Generate chart data for reach comparison."""
        chart_data = []
        for pred in predictions:
            comp_id = pred.get('competitor_id', 'Unknown')
            comp_name = next((c['name'] for c in competitors if c['competitorId'] == comp_id), comp_id)
            reach = pred.get('reach_prediction', {}).get('avg_reach', 0)
            chart_data.append({
                'name': comp_name,
                'value': int(reach)
            })
        
        return {
            'type': 'bar',
            'title': 'Predicted Reach Comparison',
            'data': sorted(chart_data, key=lambda x: x['value'], reverse=True)
        }
    
    def _generate_campaign_count_chart(self, competitors: List[Dict], ads: List[Dict]) -> Dict[str, Any]:
        """Generate chart data for campaign count comparison."""
        chart_data = []
        for comp in competitors:
            comp_ads = [ad for ad in ads if ad.get('competitor_id') == comp['competitorId']]
            chart_data.append({
                'name': comp['name'],
                'value': len(comp_ads)
            })
        
        return {
            'type': 'bar',
            'title': 'Campaign Activity by Competitor',
            'data': sorted(chart_data, key=lambda x: x['value'], reverse=True)
        }
    
    def _generate_opportunities_chart(self, opportunities: List[Dict]) -> Dict[str, Any]:
        """Generate chart data for opportunities by priority."""
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        for opp in opportunities:
            priority = opp.get('priority', 'low')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            'type': 'pie',
            'title': 'Market Opportunities by Priority',
            'data': [
                {'name': 'High Priority', 'value': priority_counts['high']},
                {'name': 'Medium Priority', 'value': priority_counts['medium']},
                {'name': 'Low Priority', 'value': priority_counts['low']}
            ]
        }
