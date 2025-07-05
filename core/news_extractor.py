"""
News Extractor - Main Module
===========================

Professional news extraction engine with modular architecture
"""

import logging
import time
from typing import List, Dict, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.article import Article
from utils.exceptions import ExtractionError, ValidationError
from utils.validators import URLValidator

from core.http_client import HTTPClient
from core.content_parser import ContentParser
from core.rss_parser import RSSParser
from core.metadata_extractor import MetadataExtractor
from core.language_processor import LanguageProcessor
from core.nlp_processor import NLPProcessor


class NewsExtractor:
    """
    Professional news extraction engine with support for multiple formats
    """

    def __init__(
        self,
        language: Optional[str] = None,
        request_timeout: int = 30,
        max_retries: int = 3,
        delay_between_requests: float = 1.0,
        custom_headers: Optional[Dict] = None,
        enable_nlp: bool = True,
        enable_transformers: bool = False,
        summarization_method: str = "auto",
    ):
        """
        Initialize the NewsExtractor

        Args:
            language (Optional[str]): Target language for translation.
                                    If None, no translation is performed.
                                    Examples: 'en', 'es', 'fr', 'de', etc.
            request_timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retry attempts
            delay_between_requests (float): Delay between requests
            custom_headers (dict): Custom HTTP headers
            enable_nlp (bool): Whether to enable NLP processing
            enable_transformers (bool): Whether to enable transformer models for NLP
            summarization_method (str): Preferred summarization method ('auto', 'sumy', 'transformers', 'simple')
        """
        self.language = language
        self.delay_between_requests = delay_between_requests
        self.enable_nlp = enable_nlp

        # Initialize components
        self.http_client = HTTPClient(request_timeout, max_retries, custom_headers)
        self.content_parser = ContentParser()
        self.rss_parser = RSSParser(self.http_client)
        self.metadata_extractor = MetadataExtractor()
        self.language_processor = LanguageProcessor(language)
        self.nlp_processor = (
            NLPProcessor(
                enable_transformers=enable_transformers,
                summarization_method=summarization_method,
            )
            if enable_nlp
            else None
        )
        self.url_validator = URLValidator()

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def extract_from_url(self, url: str) -> Union[Article, List[Article]]:
        """
        Extract article(s) from a single URL - auto-detects RSS feeds vs regular articles

        Args:
            url (str): URL of the news article or RSS feed

        Returns:
            Union[Article, List[Article]]: Single article for regular URLs, list for RSS feeds

        Raises:
            ExtractionError: If extraction fails
            ValidationError: If URL is invalid
        """
        # Validate URL
        if not self.url_validator.is_valid(url):
            raise ValidationError(f"Invalid URL: {url}")

        try:
            # Check if URL is an RSS feed
            if self.rss_parser.is_rss_feed(url):
                self.logger.info(f"Detected RSS feed: {url}")
                return self.extract_from_rss_feed(url)
            else:
                self.logger.info(f"Extracting regular article: {url}")
                return self._extract_single_article(url)

        except Exception as e:
            self.logger.error(f"Failed to extract from {url}: {str(e)}")
            raise ExtractionError(f"Failed to extract: {str(e)}")

    def extract_from_urls(self, urls: List[str], max_workers: int = 5) -> List[Article]:
        """
        Extract articles from multiple URLs concurrently

        Args:
            urls (List[str]): List of URLs to extract
            max_workers (int): Maximum number of concurrent workers

        Returns:
            List[Article]: List of extracted articles
        """
        articles = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.extract_from_url, url): url for url in urls
            }

            # Collect results
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    # Handle both single articles and lists from RSS feeds
                    if isinstance(result, list):
                        articles.extend(result)
                    else:
                        articles.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to extract from {url}: {str(e)}")
                    continue

                # Add delay between requests
                time.sleep(self.delay_between_requests)

        return articles

    def extract_from_rss_feed(
        self, feed_url: str, limit: Optional[int] = None
    ) -> List[Article]:
        """
        Extract articles from RSS/Atom feed

        Args:
            feed_url (str): URL of the RSS feed
            limit (int, optional): Maximum number of articles to extract

        Returns:
            List[Article]: List of extracted articles
        """
        try:
            # Parse RSS feed to get article data
            articles_data = self.rss_parser.parse_feed(feed_url, limit)

            # Convert to Article objects
            articles = []
            for article_data in articles_data:
                article = self._create_article_from_data(article_data)
                if article:
                    articles.append(article)

            self.logger.info(
                f"Successfully extracted {len(articles)} articles from RSS feed"
            )
            return articles

        except Exception as e:
            self.logger.error(f"Failed to extract from RSS feed {feed_url}: {e}")
            raise ExtractionError(f"Failed to extract from RSS feed: {str(e)}")

    def _extract_single_article(self, url: str) -> Article:
        """
        Extract article from a single URL (non-RSS)

        Args:
            url (str): URL of the news article

        Returns:
            Article: Extracted article object
        """
        try:
            # Fetch content
            response = self.http_client.fetch_url(url)

            # Parse content
            article_data = self.content_parser.parse_article_data(response.text, url)

            # Extract comprehensive metadata
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")
            metadata = self.metadata_extractor.extract_metadata(soup, url)

            # Merge metadata
            article_data.update(metadata)
            article_data["url"] = url

            # Create Article object
            article = self._create_article_from_data(article_data)

            if not article:
                raise ExtractionError("Failed to create article from extracted data")

            # Process language and NLP if enabled
            self._process_language_and_nlp(article)

            return article

        except Exception as e:
            self.logger.error(f"Failed to extract single article from {url}: {e}")
            raise ExtractionError(f"Failed to extract article: {str(e)}")

    def _create_article_from_data(self, data: Dict) -> Optional[Article]:
        """
        Create an Article object from extracted data dictionary

        Args:
            data (Dict): Dictionary of article data

        Returns:
            Optional[Article]: Article object or None if validation fails
        """
        try:
            # Basic validation
            if not data.get("title") or not data.get("content"):
                self.logger.warning(
                    f"Skipping article due to missing title or content: {data.get('url')}"
                )
                return None

            # Process language detection using the language processor
            processed_data = self.language_processor.process_content(data)

            article = Article(
                title=processed_data.get("title", ""),
                content=processed_data.get("content", ""),
                url=processed_data.get("url", ""),
                summary=processed_data.get("summary", ""),
                author=processed_data.get("author", ""),
                published_date=processed_data.get("published_date"),
                source=processed_data.get("source", ""),
                # REMOVED: tags field (unreliable)
                top_image=processed_data.get("top_image", ""),
                language=processed_data.get(
                    "language", "unknown"
                ),  # Set detected language
            )

            # Assign new metadata fields if they exist in the data
            article.category = processed_data.get("category", "")
            article.publication_name = processed_data.get("publication_name", "")
            article.meta_description = processed_data.get("meta_description", "")
            # REMOVED: meta_keywords field (inconsistent)
            article.canonical_link = processed_data.get("canonical_link", "")
            article.image_urls = processed_data.get("image_urls", [])
            article.video_urls = processed_data.get("video_urls", [])
            article.links = processed_data.get("links", [])
            article.is_paywalled = processed_data.get("is_paywalled", False)
            article.translated = processed_data.get("translated", False)

            return article

        except Exception as e:
            self.logger.error(f"Error creating article object: {e}")
            return None

    def _process_language_and_nlp(self, article: Article):
        """
        Process language translation and NLP analysis for the article

        Args:
            article (Article): Article object to process
        """
        try:
            # Language translation
            if self.language and not article.translated:
                from core.translator import Translator, TranslationProvider

                translator = Translator(provider=TranslationProvider.GOOGLE_FREE)

                # Translate title and content
                try:
                    if article.content:
                        translated_content = translator.translate(
                            article.content, target_lang=self.language
                        )
                        article.content = translated_content
                    if article.title:
                        translated_title = translator.translate(
                            article.title, target_lang=self.language
                        )
                        article.title = translated_title
                    article.translated = True
                    self.logger.info(f"Article translated to {self.language}")
                except Exception as e:
                    self.logger.warning(
                        f"Translation failed: {e}. Continuing without translation."
                    )

            # NLP processing
            if self.enable_nlp and self.nlp_processor:
                nlp_results = self.nlp_processor.process_article(
                    article.title, article.content
                )

                # Update article with NLP results
                article.entities = nlp_results.entities
                article.sentiment = nlp_results.sentiment
                article.nlp_summary = nlp_results.summary
                article.nlp_processed = True

                self.logger.debug(
                    f"NLP processing completed for article: {sum(len(v) for v in nlp_results.entities.values())} entities"
                )

        except Exception as e:
            self.logger.error(f"Error in language or NLP processing: {e}")
            article.nlp_processed = False
