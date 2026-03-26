"""
Query Processor for Scout Chatbot - LLM-powered with full data context
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
    """Process user queries using LLM with full data context."""
    
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
        """Process a user query: gather all data, send to LLM, return response."""
        logger.info(f"Processing query: {query[:80]}...")
        
        # Always gather ALL data so LLM has full context
        context_data = self._gather_all_data(query)
        
        # Detect intent for chart generation
        intent = self._detect_intent(query)
        
        # Try LLM first
        try:
            response = self._generate_llm_response(query, intent, context_data, conversation_history)
            return response
        except Exception as e:
            logger.error(f"LLM response failed: {str(e)}")
            return self._fallback_response(query, intent, context_data)

    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query."""
        q = query.lower()
        
        if any(w in q for w in ['chart', 'graph', 'visualize', 'plot', 'visual']):
            return 'visualization'
        elif any(w in q for w in ['gap', 'opportunity', 'missing', 'underutilized', 'untapped']):
            return 'gap_analysis'
        elif any(w in q for w in ['predict', 'forecast', 'future', 'will', 'expect', 'reach']):
            return 'predictions'
        elif any(w in q for w in ['compare', 'versus', 'vs', 'difference', 'better', 'worse']):
            return 'comparison'
        elif any(w in q for w in ['campaign', 'ad ', 'ads', 'creative', 'running', 'launch']):
            return 'competitor_info'
        elif any(w in q for w in ['trend', 'pattern', 'over time', 'growth']):
            return 'trend'
        elif any(w in q for w in ['strategy', 'recommend', 'suggest', 'should', 'advice', 'plan']):
            return 'strategy'
        elif any(w in q for w in ['mamaearth', 'derma', 'plum', 'dot', 'key', 'minimalist']):
            return 'competitor_info'
        else:
            return 'general'
    
    def _gather_all_data(self, query: str) -> Dict[str, Any]:
        """Gather ALL available data so LLM has full context."""
        context = {
            'competitors': [],
            'ads': [],
            'predictions': [],
            'gaps': {}
        }
        
        query_lower = query.lower()
        
        # Always get competitors
        try:
            context['competitors'] = self.competitor_table.scan().get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get competitors: {e}")
        
        # Detect specific competitor
        specific_competitor = None
        for comp in context['competitors']:
            if comp.get('name', '').lower() in query_lower:
                specific_competitor = comp
                break
        
        # Get ads - specific competitor or all
        try:
            if specific_competitor:
                try:
                    ad_response = self.ad_table.query(
                        IndexName='CompetitorIndex',
                        KeyConditionExpression='competitor_id = :cid',
                        ExpressionAttributeValues={':cid': specific_competitor['competitorId']},
                        Limit=30,
                        ScanIndexForward=False
                    )
                    context['ads'] = ad_response.get('Items', [])
                except Exception:
                    ad_response = self.ad_table.scan(Limit=30)
                    context['ads'] = [
                        a for a in ad_response.get('Items', [])
                        if a.get('competitor_id') == specific_competitor.get('competitorId')
                    ]
            else:
                ad_response = self.ad_table.scan(Limit=50)
                context['ads'] = ad_response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get ads: {e}")
        
        # Always get predictions
        try:
            pred_response = self.prediction_table.scan(Limit=10)
            context['predictions'] = pred_response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get predictions: {e}")
        
        # Always get gap analysis
        try:
            gap_response = self.gap_table.scan(Limit=1)
            if gap_response.get('Items'):
                context['gaps'] = gap_response['Items'][0]
        except Exception as e:
            logger.error(f"Failed to get gaps: {e}")
        
        return context

    def _generate_llm_response(
        self,
        query: str,
        intent: str,
        context_data: Dict[str, Any],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response using Bedrock LLM with full data context."""
        
        # Build rich context summary
        context_summary = self._build_context_summary(context_data)
        
        # Build conversation context
        conv_context = ""
        if conversation_history and len(conversation_history) > 0:
            recent_messages = conversation_history[-4:]
            for msg in recent_messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conv_context += f"{role.capitalize()}: {content}\n"
        
        system_prompt = """You are Scout, an AI competitive intelligence assistant for the Indian D2C skincare market.
You have access to real data about these brands: Mamaearth, Plum Goodness, Minimalist, The Derma Co, and Dot & Key.

Your job is to answer ANY question using the provided data. Be specific, cite numbers, and give actionable insights.

Rules:
- Always use the actual data provided to answer questions
- If asked about campaigns, list specific campaign details (text, platforms, status)
- If asked about predictions, share specific reach/engagement numbers
- If asked about gaps/opportunities, describe each opportunity with priority
- If asked to compare, create structured comparisons with data points
- If asked for strategy/recommendations, base them on the actual data
- Use bullet points and clear formatting
- Keep responses concise but data-rich (under 300 words)
- If the data doesn't fully answer the question, say what you can from the data and note what's missing"""
        
        user_prompt = f"""Answer this question using the competitive intelligence data below:

Question: {query}

=== COMPETITIVE INTELLIGENCE DATA ===
{context_summary}
=== END DATA ===

{f"Previous conversation:\n{conv_context}" if conv_context else ""}

Provide a helpful, data-driven answer."""
        
        # Call Bedrock
        response = self.bedrock_client.invoke_model(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response['text'].strip()
        
        # Generate charts based on intent and data
        charts = self._generate_charts(query, intent, context_data)
        
        return {
            'answer': answer,
            'intent': intent,
            'data': context_data,
            'charts': charts,
            'confidence': 0.9
        }

    def _build_context_summary(self, context_data: Dict[str, Any]) -> str:
        """Build a rich summary of all data for the LLM."""
        summary = []
        
        # Competitors
        competitors = context_data.get('competitors', [])
        if competitors:
            summary.append(f"COMPETITORS ({len(competitors)}):")
            for comp in competitors:
                name = comp.get('name', 'Unknown')
                cid = comp.get('competitorId', '')
                website = comp.get('website', '')
                summary.append(f"  - {name} (ID: {cid}) {website}")
        
        # Ads / Campaigns
        ads = context_data.get('ads', [])
        if ads:
            summary.append(f"\nCAMPAIGNS ({len(ads)} total):")
            # Group by competitor
            by_competitor = {}
            for ad in ads:
                comp_id = ad.get('competitor_id', 'unknown')
                comp_name = ad.get('page_name', comp_id)
                if comp_id not in by_competitor:
                    by_competitor[comp_id] = {'name': comp_name, 'ads': []}
                by_competitor[comp_id]['ads'].append(ad)
            
            for comp_id, info in by_competitor.items():
                comp_name = info['name']
                comp_ads = info['ads']
                active = sum(1 for a in comp_ads if a.get('is_active'))
                inactive = len(comp_ads) - active
                summary.append(f"\n  {comp_name} ({len(comp_ads)} campaigns, {active} active, {inactive} inactive):")
                
                for i, ad in enumerate(comp_ads[:8], 1):
                    text = ad.get('ad_text', '')
                    if text:
                        text = text[:200].replace('\n', ' ')
                    platforms = ', '.join(ad.get('platforms', []))
                    status = 'Active' if ad.get('is_active') else 'Inactive'
                    start = ad.get('start_date', ad.get('ad_delivery_start_time', 'N/A'))
                    summary.append(f"    {i}. [{status}] Platforms: {platforms}")
                    if start and start != 'N/A':
                        summary.append(f"       Started: {start}")
                    if text:
                        summary.append(f"       Ad text: {text}")
        
        # Predictions
        predictions = context_data.get('predictions', [])
        if predictions:
            summary.append(f"\nPREDICTIONS ({len(predictions)}):")
            for pred in predictions:
                comp_id = pred.get('competitor_id', 'Unknown')
                comp_name = next(
                    (c['name'] for c in competitors if c.get('competitorId') == comp_id),
                    comp_id
                )
                reach = pred.get('reach_prediction', {})
                engagement = pred.get('engagement_prediction', {})
                confidence = pred.get('confidence', 0)
                
                summary.append(f"  {comp_name}:")
                if reach:
                    summary.append(f"    Reach: avg={reach.get('avg_reach', 0):,.0f}, "
                                   f"min={reach.get('min_reach', 0):,.0f}, "
                                   f"max={reach.get('max_reach', 0):,.0f}")
                if engagement:
                    summary.append(f"    Engagement: avg={engagement.get('avg_engagement', 0):,.0f}")
                summary.append(f"    Confidence: {confidence:.0%}")
        
        # Gap Analysis
        gaps = context_data.get('gaps', {})
        if gaps and gaps.get('opportunities'):
            opportunities = gaps['opportunities']
            summary.append(f"\nMARKET OPPORTUNITIES ({len(opportunities)}):")
            for opp in opportunities:
                opp_type = opp.get('type', 'unknown').replace('_', ' ').title()
                desc = opp.get('description', 'N/A')
                priority = opp.get('priority', 'unknown')
                score = opp.get('score', 0)
                summary.append(f"  - [{priority.upper()}] {opp_type}: {desc} (score: {score})")
        
        return '\n'.join(summary) if summary else "No data available"

    def _generate_charts(self, query: str, intent: str, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts based on query intent and data."""
        charts = []
        q = query.lower()
        wants_chart = any(w in q for w in ['chart', 'graph', 'visualize', 'plot', 'show me', 'compare', 'visual'])
        
        competitors = context_data.get('competitors', [])
        ads = context_data.get('ads', [])
        predictions = context_data.get('predictions', [])
        gaps = context_data.get('gaps', {})
        
        # Campaign activity chart
        if intent in ['competitor_info', 'comparison', 'visualization', 'general'] and ads and (wants_chart or intent == 'visualization'):
            by_comp = {}
            for ad in ads:
                comp_id = ad.get('competitor_id', 'unknown')
                comp_name = next(
                    (c['name'] for c in competitors if c.get('competitorId') == comp_id),
                    ad.get('page_name', comp_id)
                )
                by_comp[comp_name] = by_comp.get(comp_name, 0) + 1
            
            if by_comp:
                charts.append({
                    'type': 'bar',
                    'title': 'Campaign Activity by Competitor',
                    'data': sorted(
                        [{'name': k, 'value': v} for k, v in by_comp.items()],
                        key=lambda x: x['value'], reverse=True
                    )
                })
        
        # Reach prediction chart
        if intent in ['predictions', 'comparison', 'visualization'] and predictions:
            chart_data = []
            for pred in predictions:
                comp_id = pred.get('competitor_id', 'Unknown')
                comp_name = next(
                    (c['name'] for c in competitors if c.get('competitorId') == comp_id),
                    comp_id
                )
                reach = pred.get('reach_prediction', {}).get('avg_reach', 0)
                chart_data.append({'name': comp_name, 'value': int(reach)})
            
            if chart_data:
                charts.append({
                    'type': 'bar',
                    'title': 'Predicted Reach Comparison',
                    'data': sorted(chart_data, key=lambda x: x['value'], reverse=True)
                })
        
        # Gap analysis chart
        if intent in ['gap_analysis', 'visualization'] and gaps.get('opportunities'):
            opportunities = gaps['opportunities']
            priority_counts = {'high': 0, 'medium': 0, 'low': 0}
            for opp in opportunities:
                p = opp.get('priority', 'low')
                priority_counts[p] = priority_counts.get(p, 0) + 1
            
            charts.append({
                'type': 'pie',
                'title': 'Market Opportunities by Priority',
                'data': [
                    {'name': 'High Priority', 'value': priority_counts.get('high', 0)},
                    {'name': 'Medium Priority', 'value': priority_counts.get('medium', 0)},
                    {'name': 'Low Priority', 'value': priority_counts.get('low', 0)}
                ]
            })
        
        # Active vs inactive chart
        if wants_chart and ads and 'active' in q:
            active = sum(1 for a in ads if a.get('is_active'))
            inactive = len(ads) - active
            charts.append({
                'type': 'pie',
                'title': 'Campaign Status Distribution',
                'data': [
                    {'name': 'Active', 'value': active},
                    {'name': 'Inactive', 'value': inactive}
                ]
            })
        
        # Platform distribution chart
        if wants_chart and ads and 'platform' in q:
            platform_counts = {}
            for ad in ads:
                for p in ad.get('platforms', []):
                    platform_counts[p] = platform_counts.get(p, 0) + 1
            if platform_counts:
                charts.append({
                    'type': 'bar',
                    'title': 'Platform Distribution',
                    'data': [{'name': k, 'value': v} for k, v in platform_counts.items()]
                })
        
        return charts

    def _fallback_response(self, query: str, intent: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Smart fallback when LLM is unavailable - uses data to answer."""
        competitors = context_data.get('competitors', [])
        ads = context_data.get('ads', [])
        predictions = context_data.get('predictions', [])
        gaps = context_data.get('gaps', {})
        
        q = query.lower()
        charts = self._generate_charts(query, intent, context_data)
        
        # --- Competitor-specific queries ---
        for comp in competitors:
            if comp.get('name', '').lower() in q:
                comp_ads = [a for a in ads if a.get('competitor_id') == comp.get('competitorId')]
                active = sum(1 for a in comp_ads if a.get('is_active'))
                
                answer = f"📊 {comp['name']} - Campaign Analysis\n\n"
                answer += f"Total campaigns: {len(comp_ads)} ({active} active, {len(comp_ads) - active} inactive)\n\n"
                
                if comp_ads:
                    answer += "Recent campaigns:\n"
                    for i, ad in enumerate(comp_ads[:6], 1):
                        text = ad.get('ad_text', '')
                        if text:
                            text = text[:120].replace('\n', ' ')
                            if len(ad.get('ad_text', '')) > 120:
                                text += '...'
                        platforms = ', '.join(ad.get('platforms', ['Unknown']))
                        status = '🟢 Active' if ad.get('is_active') else '🔴 Inactive'
                        answer += f"\n{i}. {status} | Platforms: {platforms}\n"
                        if text:
                            answer += f"   {text}\n"
                    
                    if len(comp_ads) > 6:
                        answer += f"\n...and {len(comp_ads) - 6} more campaigns"
                
                # Add prediction if available
                comp_pred = next(
                    (p for p in predictions if p.get('competitor_id') == comp.get('competitorId')),
                    None
                )
                if comp_pred:
                    reach = comp_pred.get('reach_prediction', {}).get('avg_reach', 0)
                    conf = comp_pred.get('confidence', 0)
                    answer += f"\n\n📈 Predicted reach: {int(reach):,} (confidence: {int(conf * 100)}%)"
                
                return {
                    'answer': answer,
                    'intent': intent,
                    'data': context_data,
                    'charts': charts,
                    'confidence': 0.85
                }
        
        # --- Comparison queries ---
        if intent == 'comparison' and competitors:
            answer = "📊 Competitor Comparison\n\n"
            for comp in competitors:
                comp_ads = [a for a in ads if a.get('competitor_id') == comp.get('competitorId')]
                active = sum(1 for a in comp_ads if a.get('is_active'))
                comp_pred = next(
                    (p for p in predictions if p.get('competitor_id') == comp.get('competitorId')),
                    None
                )
                
                answer += f"• {comp['name']}: {len(comp_ads)} campaigns ({active} active)"
                if comp_pred:
                    reach = comp_pred.get('reach_prediction', {}).get('avg_reach', 0)
                    answer += f", predicted reach: {int(reach):,}"
                answer += "\n"
            
            return {
                'answer': answer,
                'intent': intent,
                'data': context_data,
                'charts': charts,
                'confidence': 0.85
            }
        
        # --- Gap analysis queries ---
        if intent == 'gap_analysis' and gaps.get('opportunities'):
            opportunities = gaps['opportunities']
            answer = f"🎯 Market Opportunities ({len(opportunities)} identified)\n\n"
            for opp in opportunities:
                priority = opp.get('priority', 'unknown')
                emoji = '🔴' if priority == 'high' else '🟡' if priority == 'medium' else '🟢'
                opp_type = opp.get('type', 'unknown').replace('_', ' ').title()
                answer += f"{emoji} {opp_type} [{priority.upper()}]\n"
                answer += f"   {opp.get('description', 'N/A')}\n\n"
            
            return {
                'answer': answer,
                'intent': intent,
                'data': context_data,
                'charts': charts,
                'confidence': 0.85
            }
        
        # --- Prediction queries ---
        if intent == 'predictions' and predictions:
            answer = "📈 Campaign Performance Predictions\n\n"
            for pred in predictions:
                comp_id = pred.get('competitor_id', 'Unknown')
                comp_name = next(
                    (c['name'] for c in competitors if c.get('competitorId') == comp_id),
                    comp_id
                )
                reach = pred.get('reach_prediction', {}).get('avg_reach', 0)
                engagement = pred.get('engagement_prediction', {}).get('avg_engagement', 0)
                confidence = pred.get('confidence', 0)
                
                answer += f"• {comp_name}\n"
                answer += f"  Predicted reach: {int(reach):,}\n"
                if engagement:
                    answer += f"  Predicted engagement: {int(engagement):,}\n"
                answer += f"  Confidence: {int(confidence * 100)}%\n\n"
            
            return {
                'answer': answer,
                'intent': intent,
                'data': context_data,
                'charts': charts,
                'confidence': 0.85
            }
        
        # --- Strategy / recommendation queries ---
        if intent == 'strategy':
            answer = "💡 Strategic Recommendations\n\n"
            answer += "Based on the competitive data:\n\n"
            
            if gaps.get('opportunities'):
                high_priority = [o for o in gaps['opportunities'] if o.get('priority') == 'high']
                if high_priority:
                    answer += "High-priority opportunities:\n"
                    for opp in high_priority:
                        answer += f"• {opp.get('description', 'N/A')}\n"
                    answer += "\n"
            
            if predictions:
                top_pred = max(predictions, key=lambda p: p.get('reach_prediction', {}).get('avg_reach', 0))
                comp_id = top_pred.get('competitor_id')
                comp_name = next(
                    (c['name'] for c in competitors if c.get('competitorId') == comp_id),
                    comp_id
                )
                answer += f"Top predicted performer: {comp_name}\n"
                answer += f"Study their campaign strategies for best practices.\n\n"
            
            if ads:
                active_ads = [a for a in ads if a.get('is_active')]
                answer += f"Market activity: {len(active_ads)} active campaigns across {len(competitors)} competitors\n"
            
            return {
                'answer': answer,
                'intent': intent,
                'data': context_data,
                'charts': charts,
                'confidence': 0.8
            }
        
        # --- General / catch-all: provide a data summary ---
        answer = "📊 Competitive Intelligence Overview\n\n"
        
        if competitors:
            answer += f"Tracking {len(competitors)} competitors: {', '.join(c['name'] for c in competitors)}\n\n"
        
        if ads:
            active = sum(1 for a in ads if a.get('is_active'))
            answer += f"Campaigns: {len(ads)} total ({active} active)\n"
            # Top by campaign count
            by_comp = {}
            for ad in ads:
                cid = ad.get('competitor_id', 'unknown')
                cname = next((c['name'] for c in competitors if c.get('competitorId') == cid), cid)
                by_comp[cname] = by_comp.get(cname, 0) + 1
            top = sorted(by_comp.items(), key=lambda x: x[1], reverse=True)
            answer += "Campaign breakdown: " + ", ".join(f"{n}: {c}" for n, c in top) + "\n\n"
        
        if predictions:
            answer += "Predictions available for: " + ", ".join(
                next((c['name'] for c in competitors if c.get('competitorId') == p.get('competitor_id')), p.get('competitor_id', ''))
                for p in predictions
            ) + "\n\n"
        
        if gaps.get('opportunities'):
            answer += f"Market opportunities: {len(gaps['opportunities'])} identified\n"
            high = sum(1 for o in gaps['opportunities'] if o.get('priority') == 'high')
            if high:
                answer += f"  {high} high-priority opportunities\n"
        
        answer += "\nAsk me anything specific about the data - campaigns, predictions, gaps, strategy, or comparisons."
        
        return {
            'answer': answer,
            'intent': intent,
            'data': context_data,
            'charts': charts,
            'confidence': 0.75
        }
