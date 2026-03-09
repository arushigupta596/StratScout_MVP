"""
Configuration management for StratScout backend services.
"""
import os
from typing import Optional


class Config:
    """Central configuration class for all backend services."""
    
    # DynamoDB Tables
    COMPETITOR_TABLE = os.environ.get('COMPETITOR_TABLE', '')
    AD_DATA_TABLE = os.environ.get('AD_DATA_TABLE', '')
    ANALYSIS_TABLE = os.environ.get('ANALYSIS_TABLE', '')
    PREDICTION_TABLE = os.environ.get('PREDICTION_TABLE', '')
    GAP_ANALYSIS_TABLE = os.environ.get('GAP_ANALYSIS_TABLE', '')
    CONVERSATION_TABLE = os.environ.get('CONVERSATION_TABLE', '')
    REPORT_TABLE = os.environ.get('REPORT_TABLE', '')
    
    # S3 Buckets
    AD_CREATIVES_BUCKET = os.environ.get('AD_CREATIVES_BUCKET', '')
    
    # Database
    DB_ENDPOINT = os.environ.get('DB_ENDPOINT', '')
    DB_NAME = os.environ.get('DB_NAME', 'stratscout')
    DB_PORT = int(os.environ.get('DB_PORT', '5432'))
    
    # Redis
    REDIS_ENDPOINT = os.environ.get('REDIS_ENDPOINT', '')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
    
    # Amazon Bedrock
    BEDROCK_MODEL_ID = os.environ.get(
        'BEDROCK_MODEL_ID',
        'anthropic.claude-3-sonnet-20240229-v1:0'
    )
    BEDROCK_REGION = os.environ.get('BEDROCK_REGION', 'us-east-1')
    
    # Meta Ads Library API
    META_ACCESS_TOKEN = os.environ.get('META_ACCESS_TOKEN', '')
    META_APP_ID = os.environ.get('META_APP_ID', '')
    META_APP_SECRET = os.environ.get('META_APP_SECRET', '')
    
    # Processing
    PROCESSING_QUEUE_URL = os.environ.get('PROCESSING_QUEUE_URL', '')
    
    # Analysis settings
    AI_CONFIDENCE_THRESHOLD = float(os.environ.get('AI_CONFIDENCE_THRESHOLD', '0.7'))
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', '4096'))
    TEMPERATURE = float(os.environ.get('TEMPERATURE', '0.7'))
    
    # Prediction settings
    PREDICTION_LOOKBACK_DAYS = int(os.environ.get('PREDICTION_LOOKBACK_DAYS', '90'))
    PREDICTION_CONFIDENCE_MIN = float(os.environ.get('PREDICTION_CONFIDENCE_MIN', '0.6'))
    
    # Gap analysis settings
    GAP_ANALYSIS_MIN_COMPETITORS = int(os.environ.get('GAP_ANALYSIS_MIN_COMPETITORS', '2'))
    OPPORTUNITY_SCORE_THRESHOLD = float(os.environ.get('OPPORTUNITY_SCORE_THRESHOLD', '0.5'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required = [
            cls.COMPETITOR_TABLE,
            cls.AD_DATA_TABLE,
            cls.ANALYSIS_TABLE,
            cls.AD_CREATIVES_BUCKET,
        ]
        return all(required)
    
    @classmethod
    def get_db_connection_string(cls, secret_value: dict) -> str:
        """Generate PostgreSQL connection string."""
        username = secret_value.get('username', 'stratscout_admin')
        password = secret_value.get('password', '')
        return (
            f"postgresql://{username}:{password}@"
            f"{cls.DB_ENDPOINT}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
