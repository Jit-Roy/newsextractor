"""
RSS Parser Module
================

Handles RSS/Atom feed parsing and entry processing
"""

import re
import logging
import feedparser
from datetime import datetime
from typing import List, Optional, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from models.article import Article
from utils.exceptions import ExtractionError
from core.http_client import HTTPClient


class RSSParser:
    """
    Professional RSS/Atom feed parser with robust entry processing
    """

    def __init__(self, http_client: HTTPClient):
        """
        Initialize the RSS parser

        Args:
            http_client (HTTPClient): HTTP client for making requests
        """
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)

    def is_rss_feed(self, url: str) -> bool:
        """
        Check if URL is an RSS/Atom feed

        Args:
            url (str): URL to check

        Returns:
            bool: True if URL is RSS feed, False otherwise
        """
        try:
            # Check URL patterns first (quick check)
            rss_patterns = [
                r"\.xml$",
                r"\.rss$",
                r"/rss/",
                r"/feed/",
                r"/feeds/",
                r"rss\.xml$",
                r"feed\.xml$",
                r"atom\.xml$",
                r"/rss$",
                r"/feed$",
            ]

            url_lower = url.lower()
            for pattern in rss_patterns:
                if re.search(pattern, url_lower):
                    self.logger.debug(f"RSS pattern detected in URL: {pattern}")
                    return True

            # If no pattern matches, try to fetch and check content type
            try:
                response = self.http_client.fetch_head(url)
                content_type = response.headers.get("content-type", "").lower()

                rss_content_types = [
                    "application/rss+xml",
                    "application/atom+xml",
                    "application/xml",
                    "text/xml",
                ]

                if any(ct in content_type for ct in rss_content_types):
                    self.logger.debug(f"RSS content type detected: {content_type}")
                    return True

            except Exception as e:
                self.logger.debug(f"Failed to check content type for {url}: {e}")

            # Final check: try to parse as RSS (lightweight check)
            try:
                feed = feedparser.parse(url)
                # If feed has entries and no major errors, it's likely RSS
                if feed.entries and not feed.bozo_exception:
                    self.logger.debug("RSS structure detected via feedparser")
                    return True

            except Exception as e:
                self.logger.debug(f"Feedparser check failed for {url}: {e}")

            return False

        except Exception as e:
            self.logger.error(f"Error checking if {url} is RSS feed: {e}")
            return False

    def parse_feed(self, feed_url: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Parse RSS/Atom feed and extract article data

        Args:
            feed_url (str): URL of the RSS feed
            limit (int, optional): Maximum number of articles to extract

        Returns:
            List[Dict]: List of article data dictionaries

        Raises:
            ExtractionError: If feed parsing fails
        """
        try:
            self.logger.info(f"Parsing RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            if feed.bozo and feed.bozo_exception:
                self.logger.warning(
                    f"RSS feed has parsing issues: {feed.bozo_exception}"
                )

            articles_data = []
            entries = feed.entries[:limit] if limit else feed.entries

            for entry in entries:
                try:
                    article_data = self._parse_entry(entry, feed_url)
                    if article_data:
                        articles_data.append(article_data)

                except Exception as e:
                    self.logger.error(f"Failed to parse RSS entry: {e}")
                    continue

            self.logger.info(
                f"Successfully parsed {len(articles_data)} entries from RSS feed"
            )
            return articles_data

        except Exception as e:
            self.logger.error(f"Failed to parse RSS feed {feed_url}: {e}")
            raise ExtractionError(f"Failed to parse RSS feed: {str(e)}")

    def _parse_entry(self, entry, feed_url: str) -> Optional[Dict]:
        """
        Parse a single RSS entry into article data

        Args:
            entry: RSS entry from feedparser
            feed_url (str): Original feed URL

        Returns:
            Optional[Dict]: Article data dictionary or None if parsing fails
        """
        try:
            # Extract basic information
            title = getattr(entry, "title", "Unknown Title")
            link = getattr(entry, "link", "")
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")

            # Extract content (try different fields)
            content = self._extract_entry_content(entry, summary)

            # Extract author
            author = self._extract_entry_author(entry)

            # Extract published date
            published_date = self._extract_entry_date(entry)

            # Extract source from feed URL
            parsed_feed_url = urlparse(feed_url)
            source = parsed_feed_url.netloc

            # Extract tags/categories
            tags = self._extract_entry_tags(entry)

            return {
                "title": title,
                "content": content,
                "url": link,
                "summary": summary,
                "author": author,
                "published_date": published_date,
                "source": source,
                "tags": tags,
                "language": "unknown",  # Will be detected later
                "translated": False,  # Will be set during translation
            }

        except Exception as e:
            self.logger.error(f"Failed to parse RSS entry: {e}")
            return None

    def _extract_entry_content(self, entry, summary: str = "") -> str:
        """
        Extract content from RSS entry, trying multiple fields

        Args:
            entry: RSS entry from feedparser
            summary (str): Entry summary as fallback

        Returns:
            str: Extracted and cleaned content
        """
        content = ""

        # Try different content fields
        if hasattr(entry, "content") and entry.content:
            content = (
                entry.content[0].value
                if isinstance(entry.content, list)
                else entry.content
            )
        elif hasattr(entry, "description"):
            content = entry.description
        elif summary:
            content = summary

        # Clean HTML from content if present
        if content:
            soup = BeautifulSoup(content, "html.parser")
            content = soup.get_text(separator="\n", strip=True)

        return content

    def _extract_entry_author(self, entry) -> str:
        """
        Extract author from RSS entry

        Args:
            entry: RSS entry from feedparser

        Returns:
            str: Author name or empty string
        """
        author = ""

        if hasattr(entry, "author"):
            author = entry.author
        elif hasattr(entry, "author_detail") and entry.author_detail:
            author = entry.author_detail.get("name", "")

        return author

    def _extract_entry_date(self, entry) -> Optional[str]:
        """
        Extract published date from RSS entry

        Args:
            entry: RSS entry from feedparser

        Returns:
            Optional[str]: ISO formatted date string or None
        """
        published_date = None

        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_date = datetime(*entry.published_parsed[:6]).isoformat()
            except:
                pass
        elif hasattr(entry, "published"):
            published_date = entry.published

        return published_date

    def _extract_entry_tags(self, entry) -> List[str]:
        """
        Extract tags/categories from RSS entry

        Args:
            entry: RSS entry from feedparser

        Returns:
            List[str]: List of tags
        """
        tags = []

        if hasattr(entry, "tags"):
            tags = [tag.term for tag in entry.tags if hasattr(tag, "term")]

        return tags
