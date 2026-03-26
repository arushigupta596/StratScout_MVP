"""
Custom exceptions for StratScout backend services.
"""


class StratScoutError(Exception):
    """Base exception for StratScout errors."""
    pass


class DataIngestionError(StratScoutError):
    """Error during data ingestion from external sources."""
    pass


class MetaAdsAPIError(DataIngestionError):
    """Error calling Meta Ads Library API."""
    pass


class GoogleTrendsError(DataIngestionError):
    """Error fetching Google Trends data."""
    pass


class AIAnalysisError(StratScoutError):
    """Error during AI analysis."""
    pass


class BedrockError(AIAnalysisError):
    """Error calling Amazon Bedrock."""
    pass


class PredictionError(StratScoutError):
    """Error during campaign prediction."""
    pass


class GapAnalysisError(StratScoutError):
    """Error during gap analysis."""
    pass


class DataValidationError(StratScoutError):
    """Error validating data."""
    pass


class DatabaseError(StratScoutError):
    """Error interacting with database."""
    pass


class CacheError(StratScoutError):
    """Error interacting with cache."""
    pass


class ConfigurationError(StratScoutError):
    """Error in configuration."""
    pass


class ChatbotError(StratScoutError):
    """Error in Scout chatbot."""
    pass
