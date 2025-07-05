"""
NewsExtractor - Professional News Article Extraction Library
============================================================

A comprehensive library for extracting and processing news articles from any website.

Features:
- Smart article extraction from any news website
- Advanced NLP processing (keywords, sentiment, summarization, entities)
- Multi-language support with translation
- RSS feed processing
- High-performance with caching support

Quick Start:
    from newsextractor import NewsExtractor

    extractor = NewsExtractor(enable_nlp=True)
    article = extractor.extract_from_url("https://news-site.com/article")

    print(f"Title: {article.title}")
    print(f"Content: {article.content}")
    print(f"Entities: {article.entities}")
    print(f"Sentiment: {article.sentiment}")
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import core components
try:
    from .core.news_extractor import NewsExtractor
    from .models.article import Article
    from .utils.validators import URLValidator
    from .utils.helpers import TextProcessor
    
    # Try to import optional components
    try:
        from .core.trending import NewsSearcher
    except ImportError:
        NewsSearcher = None
        
    try:
        from .core.translator import Translator
    except ImportError:
        Translator = None

    __all__ = [
        "NewsExtractor",
        "Article", 
        "URLValidator",
        "TextProcessor",
    ]
    
    if NewsSearcher:
        __all__.append("NewsSearcher")
    if Translator:
        __all__.append("Translator")
        
except ImportError as e:
    # Fallback for development/testing
    import warnings

    warnings.warn(f"Could not import all modules: {e}")

    __all__ = []
TrendingTopics = NewsSearcher

__version__ = "1.0.0"
__author__ = "NewsExtractor Team"
__email__ = "team@newsextractor.com"
__description__ = "Professional news article extraction with advanced NLP"

__all__ = [
    # Main classes
    "NewsExtractor",
    "Article",
    # Support classes
    "Translator",
    "NewsSearcher",
    "TrendingTopics",  # Backward compatibility
    "URLValidator",
    "TextProcessor",
    # Convenience functions
    "extract_article",
    "extract_keywords",
    # Package info
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]


# Quick access functions for convenience
def extract_article(url: str, enable_nlp: bool = True) -> Article:
    """
    Quick article extraction function for simple use cases

    Args:
        url (str): Article URL to extract
        enable_nlp (bool): Whether to enable NLP processing

    Returns:
        Article: Extracted article with metadata and content

    Example:
        >>> article = extract_article("https://example.com/news/article")
        >>> print(article.title)
    """
    extractor = NewsExtractor(enable_nlp=enable_nlp)
    return extractor.extract_from_url(url)


def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """
    Quick keyword extraction from text

    Args:
        text (str): Text to extract keywords from
        max_keywords (int): Maximum number of keywords

    Returns:
        list: List of extracted keywords

    Example:
        >>> keywords = extract_keywords("Your text content here")
        >>> print(keywords)
    """
    return TextProcessor.extract_keywords(text, max_keywords=max_keywords)
