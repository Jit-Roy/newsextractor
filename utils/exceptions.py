class NewsExtractorError(Exception):
    """Base exception for the news extractor library"""
    pass

class ExtractionError(NewsExtractorError):
    """Exception raised when article extraction fails"""
    pass

class ValidationError(NewsExtractorError):
    """Exception raised for validation errors"""
    pass

class TranslationError(NewsExtractorError):
    """Exception raised when translation fails"""
    pass

class TrendingError(NewsExtractorError):
    """Exception raised when trending topics fetch fails"""
    pass

class APIError(NewsExtractorError):
    """Exception raised for API-related errors"""
    pass
