"""
Meta Ads Library API Client
"""
import boto3
import requests
from typing import List, Dict, Any, Optional
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logger import get_logger
from common.config import Config
from common.utils import generate_id, get_current_timestamp, generate_hash, retry_with_backoff
from common.errors import MetaAdsAPIError

logger = get_logger(__name__)


class MetaAdsClient:
    """Client for Meta Ads Library API."""
    
    # Meta Ads Library API endpoint
    API_BASE_URL = "https://graph.facebook.com/v21.0/ads_archive"
    
    def __init__(self):
        """Initialize Meta Ads client."""
        self.dynamodb = boto3.resource('dynamodb')
        self.s3 = boto3.client('s3')
        self.ad_table = self.dynamodb.Table(Config.AD_DATA_TABLE)
        self.competitor_table = self.dynamodb.Table(Config.COMPETITOR_TABLE)
        
        # Get access token from config
        self.access_token = Config.META_ACCESS_TOKEN
        
        if not self.access_token:
            logger.warning("META_ACCESS_TOKEN not configured - API calls will fail")
        
        # Default competitors to track (Indian skincare brands)
        # These are Facebook Page names - you can customize this list
        self.default_competitors = [
            {
                'id': 'comp-mamaearth',
                'name': 'Mamaearth',
                'search_terms': ['Mamaearth', 'Mama Earth'],
                'page_id': None,  # Will be discovered via search
            },
            {
                'id': 'comp-plum',
                'name': 'Plum',
                'search_terms': ['Plum Goodness', 'Plum'],
                'page_id': None,
            },
            {
                'id': 'comp-dermaco',
                'name': 'The Derma Co',
                'search_terms': ['The Derma Co', 'Derma Co'],
                'page_id': None,
            },
            {
                'id': 'comp-minimalist',
                'name': 'Minimalist',
                'search_terms': ['Minimalist', 'Be Minimalist'],
                'page_id': None,
            },
            {
                'id': 'comp-dotandkey',
                'name': 'Dot & Key',
                'search_terms': ['Dot & Key', 'Dot and Key'],
                'page_id': None,
            },
        ]
    
    @retry_with_backoff(max_attempts=3, base_delay=2.0)
    def collect_competitor_ads(self, competitor_list: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Collect ads for all tracked competitors using Meta Ads Library API.
        
        Args:
            competitor_list: Optional custom list of competitors to track
        
        Returns:
            List of ad data dictionaries
        """
        logger.info('Starting Meta Ads collection')
        
        if not self.access_token:
            raise MetaAdsAPIError("META_ACCESS_TOKEN not configured. Please set it in environment variables.")
        
        competitors = competitor_list or self.default_competitors
        all_ads = []
        
        for competitor in competitors:
            try:
                ads = self._fetch_competitor_ads(competitor)
                all_ads.extend(ads)
                logger.info(f"Collected {len(ads)} ads for {competitor['name']}")
                
                # Rate limiting - be respectful to Meta's API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to collect ads for {competitor['name']}: {str(e)}")
                # Continue with other competitors
        
        return all_ads
    
    def _fetch_competitor_ads(self, competitor: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch ads for a specific competitor using Meta Ads Library API.
        
        Args:
            competitor: Competitor information with search_terms
        
        Returns:
            List of ad data
        """
        all_ads = []
        
        # Search for ads using each search term
        for search_term in competitor.get('search_terms', [competitor['name']]):
            try:
                ads = self._search_ads(search_term, competitor)
                all_ads.extend(ads)
            except Exception as e:
                logger.error(f"Failed to search ads for '{search_term}': {str(e)}")
        
        # Deduplicate ads by ad_id
        unique_ads = {}
        for ad in all_ads:
            ad_id = ad.get('ad_id')
            if ad_id and ad_id not in unique_ads:
                unique_ads[ad_id] = ad
        
        ads_list = list(unique_ads.values())
        
        # Store ads in DynamoDB
        for ad in ads_list:
            self._store_ad(ad)
        
        return ads_list
    
    def _search_ads(self, search_term: str, competitor: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for ads using Meta Ads Library API.
        
        Args:
            search_term: Search query
            competitor: Competitor information
        
        Returns:
            List of ad data
        """
        logger.info(f"Searching Meta Ads Library for: {search_term}")
        
        params = {
            'access_token': self.access_token,
            'search_terms': search_term,
            'ad_reached_countries': 'IN',  # India
            'ad_active_status': 'ALL',  # Active and inactive ads
            'limit': 100,  # Max results per request
            'fields': ','.join([
                'id',
                'ad_creative_bodies',
                'ad_creative_link_captions',
                'ad_creative_link_descriptions',
                'ad_creative_link_titles',
                'ad_delivery_start_time',
                'ad_delivery_stop_time',
                'ad_snapshot_url',
                'page_name',
                'page_id',
                'publisher_platforms',
                'impressions',
                'spend',
            ])
        }
        
        try:
            response = requests.get(self.API_BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            ads_data = data.get('data', [])
            
            logger.info(f"Found {len(ads_data)} ads for '{search_term}'")
            
            # Transform API response to our format
            transformed_ads = []
            for ad_raw in ads_data:
                try:
                    transformed = self._transform_ad_data(ad_raw, competitor)
                    transformed_ads.append(transformed)
                except Exception as e:
                    logger.error(f"Failed to transform ad {ad_raw.get('id')}: {str(e)}")
            
            return transformed_ads
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Meta Ads API request failed: {str(e)}")
            raise MetaAdsAPIError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in ad search: {str(e)}")
            raise MetaAdsAPIError(f"Ad search failed: {str(e)}")
    
    def _transform_ad_data(self, ad_raw: Dict[str, Any], competitor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Meta Ads API response to our internal format.
        
        Args:
            ad_raw: Raw ad data from Meta API
            competitor: Competitor information
        
        Returns:
            Transformed ad data
        """
        timestamp = get_current_timestamp()
        ad_id = generate_id('ad', competitor['id'], ad_raw.get('id', ''))
        
        # Extract ad text from various fields
        ad_text_parts = []
        if ad_raw.get('ad_creative_bodies'):
            ad_text_parts.extend(ad_raw['ad_creative_bodies'])
        if ad_raw.get('ad_creative_link_titles'):
            ad_text_parts.extend(ad_raw['ad_creative_link_titles'])
        if ad_raw.get('ad_creative_link_descriptions'):
            ad_text_parts.extend(ad_raw['ad_creative_link_descriptions'])
        
        ad_text = ' | '.join(filter(None, ad_text_parts))
        
        # Parse dates
        start_date = ad_raw.get('ad_delivery_start_time')
        stop_date = ad_raw.get('ad_delivery_stop_time')
        
        # Determine if ad is active
        is_active = stop_date is None
        
        # Get platforms
        platforms = ad_raw.get('publisher_platforms', [])
        primary_platform = platforms[0] if platforms else 'facebook'
        
        # Create ad data structure
        ad_data = {
            'ad_id': ad_id,
            'meta_ad_id': ad_raw.get('id'),
            'competitor_id': competitor['id'],
            'competitor_name': competitor['name'],
            'page_name': ad_raw.get('page_name', competitor['name']),
            'page_id': ad_raw.get('page_id'),
            'scraped_at': timestamp,
            'ad_text': ad_text,
            'creative_url': ad_raw.get('ad_snapshot_url', ''),
            'platform': primary_platform,
            'platforms': platforms,
            'is_active': is_active,
            'start_date': self._parse_date(start_date),
            'stop_date': self._parse_date(stop_date) if stop_date else None,
            'impressions': ad_raw.get('impressions', {}),
            'spend': ad_raw.get('spend', {}),
            'targeting_info': {
                'countries': ['India'],
            },
            'hash': generate_hash(f"{competitor['id']}-{ad_raw.get('id')}-{ad_text}"),
            'ttl': int(time.time()) + (90 * 24 * 60 * 60),  # 90 days TTL
        }
        
        return ad_data
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[int]:
        """
        Parse ISO date string to timestamp.
        
        Args:
            date_str: ISO format date string
        
        Returns:
            Unix timestamp in milliseconds or None
        """
        if not date_str:
            return None
        
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except Exception as e:
            logger.error(f"Failed to parse date '{date_str}': {str(e)}")
            return None
    

    def _store_ad(self, ad: Dict[str, Any]) -> None:
        """
        Store ad data in DynamoDB.
        
        Args:
            ad: Ad data dictionary
        """
        try:
            # Check for duplicates using hash
            existing = self.ad_table.query(
                IndexName='CompetitorIndex',
                KeyConditionExpression='competitor_id = :cid',
                FilterExpression='#h = :hash',
                ExpressionAttributeNames={'#h': 'hash'},
                ExpressionAttributeValues={
                    ':cid': ad['competitor_id'],
                    ':hash': ad['hash'],
                },
                Limit=1
            )
            
            if existing.get('Items'):
                logger.debug(f"Ad {ad['ad_id']} already exists, skipping")
                return
            
            # Store new ad
            self.ad_table.put_item(Item=ad)
            logger.debug(f"Stored ad {ad['ad_id']}")
            
        except Exception as e:
            logger.error(f"Failed to store ad {ad['ad_id']}: {str(e)}")
            raise MetaAdsAPIError(f"Failed to store ad: {str(e)}")
