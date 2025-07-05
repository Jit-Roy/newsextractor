"""
Test suite for NewsExtractor
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.news_extractor import NewsExtractor
from models.article import Article
from utils.validators import URLValidator


class TestNewsExtractor:
    """Test cases for NewsExtractor class"""

    def test_extractor_initialization(self):
        """Test that NewsExtractor can be initialized with default parameters"""
        extractor = NewsExtractor()
        assert extractor is not None
        assert hasattr(extractor, "extract_from_url")

    def test_extractor_with_nlp(self):
        """Test that NewsExtractor can be initialized with NLP enabled"""
        extractor = NewsExtractor(enable_nlp=True)
        assert extractor is not None

    def test_extractor_with_custom_language(self):
        """Test that NewsExtractor can be initialized with custom language"""
        extractor = NewsExtractor(language="es")
        assert extractor is not None


class TestArticleModel:
    """Test cases for Article data model"""

    def test_article_creation(self):
        """Test basic article creation"""
        article = Article(
            title="Test Article",
            content="This is test content for the article.",
            url="https://example.com/test-article",
        )

        assert article.title == "Test Article"
        assert article.content == "This is test content for the article."
        assert article.url == "https://example.com/test-article"
        assert article.word_count > 0
        assert article.read_time > 0
        assert article.article_id.startswith("article_")

    def test_article_word_count(self):
        """Test word count calculation"""
        article = Article(
            title="Test", content="One two three four five", url="https://example.com"
        )
        assert article.word_count == 5

    def test_article_read_time(self):
        """Test reading time calculation"""
        # Create content with exactly 200 words
        content = " ".join(["word"] * 200)
        article = Article(title="Test", content=content, url="https://example.com")
        assert article.read_time == 1


class TestURLValidator:
    """Test cases for URL validation"""

    def test_valid_urls(self):
        """Test validation of valid URLs"""
        valid_urls = [
            "https://example.com",
            "http://test.org/article",
            "https://news.bbc.co.uk/article/123",
        ]

        for url in valid_urls:
            assert URLValidator.is_valid(url)

    def test_invalid_urls(self):
        """Test validation of invalid URLs"""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "",
            None,
            "javascript:alert('xss')",
        ]

        for url in invalid_urls:
            assert not URLValidator.is_valid(url)


if __name__ == "__main__":
    pytest.main([__file__])
