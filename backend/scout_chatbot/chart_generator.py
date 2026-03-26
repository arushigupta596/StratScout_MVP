"""
Chart Generator - Generates chart configurations for data visualization
"""
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logger import get_logger

logger = get_logger(__name__)


class ChartGenerator:
    """Generates chart configurations for frontend visualization."""
    
    def generate(
        self,
        intent: str,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate chart configurations.
        
        Args:
            intent: Query intent
            data: Retrieved data
        
        Returns:
            List of chart configurations
        """
        logger.info(f"Generating charts for intent: {intent}")
        
        charts = []
        
        try:
            if intent == 'performance_comparison':
                charts.extend(self._generate_comparison_charts(data))
            
            elif intent == 'trend_analysis':
                charts.extend(self._generate_trend_charts(data))
            
            elif intent == 'gap_analysis':
                charts.extend(self._generate_gap_charts(data))
            
            elif intent == 'market_intelligence':
                charts.extend(self._generate_market_charts(data))
        
        except Exception as e:
            logger.error(f"Chart generation failed: {str(e)}", exc_info=True)
        
        return charts
    
    def _generate_comparison_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comparison charts."""
        charts = []
        
        competitors = data.get('competitors', [])
        predictions = data.get('predictions', [])
        
        if competitors and predictions:
            # Reach comparison bar chart
            reach_data = []
            for pred in predictions:
                comp_id = pred.get('competitor_id')
                comp = next((c for c in competitors if c.get('competitorId') == comp_id), None)
                if comp:
                    reach_data.append({
                        'name': comp.get('name', 'Unknown'),
                        'reach': pred.get('reach_prediction', {}).get('avg_reach', 0)
                    })
            
            if reach_data:
                charts.append({
                    'type': 'bar',
                    'title': 'Predicted Reach Comparison',
                    'data': reach_data,
                    'xAxis': 'name',
                    'yAxis': 'reach'
                })
        
        return charts
    
    def _generate_trend_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trend charts."""
        charts = []
        
        ads = data.get('ads', [])
        
        if ads:
            # Ad volume over time
            from collections import defaultdict
            from datetime import datetime
            
            monthly_counts = defaultdict(int)
            
            for ad in ads:
                timestamp = ad.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        month_key = dt.strftime('%Y-%m')
                        monthly_counts[month_key] += 1
                    except:
                        pass
            
            if monthly_counts:
                trend_data = [
                    {'month': month, 'count': count}
                    for month, count in sorted(monthly_counts.items())
                ]
                
                charts.append({
                    'type': 'line',
                    'title': 'Ad Volume Over Time',
                    'data': trend_data,
                    'xAxis': 'month',
                    'yAxis': 'count'
                })
        
        return charts
    
    def _generate_gap_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate gap analysis charts."""
        charts = []
        
        gap_analysis = data.get('gap_analysis')
        
        if gap_analysis:
            opportunities = gap_analysis.get('opportunities', [])
            
            if opportunities:
                # Opportunity scores
                opp_data = [
                    {
                        'name': opp.get('type', 'Unknown')[:20],
                        'score': opp.get('score', 0)
                    }
                    for opp in opportunities[:10]
                ]
                
                charts.append({
                    'type': 'bar',
                    'title': 'Top Opportunities',
                    'data': opp_data,
                    'xAxis': 'name',
                    'yAxis': 'score'
                })
        
        return charts
    
    def _generate_market_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate market intelligence charts."""
        charts = []
        
        competitors = data.get('competitors', [])
        
        if competitors:
            # Market share (placeholder - would need actual data)
            market_data = [
                {'name': comp.get('name', 'Unknown'), 'share': 100 / len(competitors)}
                for comp in competitors[:5]
            ]
            
            charts.append({
                'type': 'pie',
                'title': 'Market Presence',
                'data': market_data,
                'nameKey': 'name',
                'valueKey': 'share'
            })
        
        return charts
