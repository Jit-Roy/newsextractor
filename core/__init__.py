"""
Core News Extraction Module
==========================

Core functionality for news extraction, translation, and search.
"""

from .news_extractor import NewsExtractor
from .translator import Translator, TranslationProvider
from .trending import NewsSearcher, NewsSearchResult

# Backward compatibility
TrendingTopics = NewsSearcher

__all__ = [
    'NewsExtractor',
    'Translator', 
    'TranslationProvider',
    'NewsSearcher',
    'NewsSearchResult',
    'TrendingTopics'  # For backward compatibility
]