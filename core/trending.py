"""
News Search Module
==================

Module for searching and extracting trending news articles from various sources
"""

import requests
from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass
from datetime import datetime
import time

from models.article import Article
from utils.exceptions import TrendingError, APIError


@dataclass
class NewsSearchResult:
    """
    Data class for news search results
    
    Attributes:
        title (str): Article title
        url (str): Article URL
        source (str): News source
        published_date (datetime): Publication date
        snippet (str): Article snippet/summary
        category (str): News category
        search_term (str): Original search term used
    """
    title: str
    url: str
    source: str = ""
    published_date: datetime = None
    snippet: str = ""
    category: str = "general"
    search_term: str = ""
    
    def __post_init__(self):
        if self.published_date is None:
            self.published_date = datetime.now()


class NewsSearcher:
    """
    News searcher class for finding and extracting trending news articles
    
    This class focuses on:
    1. Searching for trending news articles (not just topics)
    2. Extracting full content from news URLs
    3. Keyword-based news search
    4. Returning complete Article objects with content
    """
    
    def __init__(self, 
                 serpapi_key: str = None,
                 newsapi_key: str = None,
                 country: str = "IN",
                 language: str = "en",
                 cache_duration: int = 3600):
        """
        Initialize news searcher
        
        Args:
            serpapi_key (str): SerpAPI key for Google News search
            newsapi_key (str): NewsAPI key for news search
            country (str): Country code for news search
            language (str): Language code for translation
            cache_duration (int): Cache duration in seconds
        """
        self.serpapi_key = serpapi_key
        self.newsapi_key = newsapi_key
        self.country = country
        self.language = language
        self.cache_duration = cache_duration
        
        # Initialize components with new simplified API
        # Dynamic import to avoid circular dependency
        from core.news_extractor import NewsExtractor
        self.extractor = NewsExtractor(language=language)
        self.logger = logging.getLogger(__name__)
        
        # Cache for search results
        self._cache = {}
        self._cache_timestamps = {}
    
    def get_trending_news(self, limit: int = 10) -> List[Article]:
        """
        Get trending news articles with full content extraction
        
        Args:
            limit (int): Maximum number of articles to return
            
        Returns:
            List[Article]: List of trending news articles with full content
        """
        cache_key = f"trending_news_{self.country}_{limit}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            # Search for trending news articles
            news_results = self._search_trending_news(limit)
            
            # Extract full content from each article
            articles = []
            for i, news_item in enumerate(news_results):
                try:
                    self.logger.info(f"Extracting article {i+1}/{len(news_results)}: {news_item.title[:50]}...")
                    
                    # Extract full article content
                    article = self.extractor.extract_from_url(news_item.url)
                    
                    # Enrich with search metadata
                    article.category = news_item.category
                    if not article.published_date and news_item.published_date:
                        article.published_date = news_item.published_date
                    
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract article from {news_item.url}: {e}")
                    continue
            
            # Cache results
            self._cache[cache_key] = articles
            self._cache_timestamps[cache_key] = datetime.now()
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to fetch trending news: {str(e)}")
            raise TrendingError(f"Failed to fetch trending news: {str(e)}")
    
    def search_news_by_keyword(self, keyword: str, limit: int = 10) -> List[Article]:
        """
        Search for news articles by keyword and extract full content
        
        Args:
            keyword (str): Search keyword or phrase
            limit (int): Maximum number of articles to return
            
        Returns:
            List[Article]: List of news articles with full content
        """
        cache_key = f"search_{keyword}_{limit}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            # Search for news by keyword
            news_results = self._search_news_by_keyword(keyword, limit)
            
            # Extract full content from each article
            articles = []
            for i, news_item in enumerate(news_results):
                try:
                    self.logger.info(f"Extracting article {i+1}/{len(news_results)}: {news_item.title[:50]}...")
                    
                    # Extract full article content
                    article = self.extractor.extract_from_url(news_item.url)
                    
                    # Enrich with search metadata
                    article.category = news_item.category
                    if not article.published_date and news_item.published_date:
                        article.published_date = news_item.published_date
                    
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract article from {news_item.url}: {e}")
                    continue
            
            # Cache results
            self._cache[cache_key] = articles
            self._cache_timestamps[cache_key] = datetime.now()
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to search news for '{keyword}': {str(e)}")
            raise TrendingError(f"Failed to search news for '{keyword}': {str(e)}")
    
    def _search_trending_news(self, limit: int) -> List[NewsSearchResult]:
        """
        Search for trending news articles using SerpAPI
        
        Args:
            limit (int): Maximum number of results
            
        Returns:
            List[NewsSearchResult]: List of news search results
        """
        if not self.serpapi_key:
            raise TrendingError("SerpAPI key is required for trending news search")
        
        try:
            # Search for trending news using Google News
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_news",
                "q": "trending",
                "gl": self.country.lower(),
                "hl": self.language,
                "api_key": self.serpapi_key,
                "num": limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                raise APIError(f"SerpAPI error: {data['error']}")
            
            news_results = []
            for item in data.get("news_results", [])[:limit]:
                try:
                    # Parse the news item
                    result = NewsSearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        source=item.get("source", {}).get("name", ""),
                        snippet=item.get("snippet", ""),
                        category="trending",
                        search_term="trending"
                    )
                    
                    # Parse date if available
                    if "date" in item:
                        try:
                            # Parse different date formats
                            date_str = item["date"]
                            # Add parsing logic for different date formats
                            result.published_date = datetime.now()  # Fallback for now
                        except:
                            result.published_date = datetime.now()
                    
                    news_results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse news item: {e}")
                    continue
            
            return news_results
            
        except requests.RequestException as e:
            raise APIError(f"Failed to fetch trending news from SerpAPI: {str(e)}")
        except Exception as e:
            raise TrendingError(f"Unexpected error in trending news search: {str(e)}")
    
    def _search_news_by_keyword(self, keyword: str, limit: int) -> List[NewsSearchResult]:
        """
        Search for news articles by keyword using SerpAPI
        
        Args:
            keyword (str): Search keyword
            limit (int): Maximum number of results
            
        Returns:
            List[NewsSearchResult]: List of news search results
        """
        if not self.serpapi_key:
            raise TrendingError("SerpAPI key is required for news search")
        
        try:
            # Search for news by keyword using Google News
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_news",
                "q": keyword,
                "gl": self.country.lower(),
                "hl": self.language,
                "api_key": self.serpapi_key,
                "num": limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                raise APIError(f"SerpAPI error: {data['error']}")
            
            news_results = []
            for item in data.get("news_results", [])[:limit]:
                try:
                    # Parse the news item
                    result = NewsSearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        source=item.get("source", {}).get("name", ""),
                        snippet=item.get("snippet", ""),
                        category="search",
                        search_term=keyword
                    )
                    
                    # Parse date if available
                    if "date" in item:
                        try:
                            # Parse different date formats
                            date_str = item["date"]
                            # Add parsing logic for different date formats
                            result.published_date = datetime.now()  # Fallback for now
                        except:
                            result.published_date = datetime.now()
                    
                    news_results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse news item: {e}")
                    continue
            
            return news_results
            
        except requests.RequestException as e:
            raise APIError(f"Failed to search news from SerpAPI: {str(e)}")
        except Exception as e:
            raise TrendingError(f"Unexpected error in news search: {str(e)}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cache entry is still valid
        
        Args:
            cache_key (str): Cache key to check
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if cache_key not in self._cache or cache_key not in self._cache_timestamps:
            return False
        
        cache_time = self._cache_timestamps[cache_key]
        elapsed = (datetime.now() - cache_time).total_seconds()
        
        return elapsed < self.cache_duration
    
    def clear_cache(self):
        """Clear all cached results"""
        self._cache.clear()
        self._cache_timestamps.clear()
        self.logger.info("Cache cleared")
