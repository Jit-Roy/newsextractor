"""
Article Data Model
================

Comprehensive data model for news articles with validation and serialization
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from dateutil import parser as date_parser
import hashlib


@dataclass
class Article:
    """
    Comprehensive article data model
    
    Attributes:
        title (str): Article title
        content (str): Full article content
        url (str): Original article URL
        summary (str): Article summary/excerpt
        author (str): Article author
        published_date (datetime): Publication date
        source (str): Source website/domain
        language (str): Article language
        translated (bool): Whether content was translated
        top_image (str): Featured/top image URL
        extraction_date (datetime): When article was extracted
        word_count (int): Number of words in content
        read_time (int): Estimated reading time in minutes
        article_id (str): Unique article identifier
        entities (Dict[str, List[str]]): Named entities by type (PERSON, ORG, GPE, etc.)
        sentiment (Dict[str, Any]): Sentiment analysis results
        nlp_summary (str): AI-generated summary
    """
    
    title: str
    content: str
    url: str
    summary: str = ""
    author: str = ""
    published_date: Optional[datetime] = None
    source: str = ""
    # REMOVED: tags field (unreliable - empty 80% of time)
    language: str = "unknown"
    translated: bool = False
    top_image: str = ""  # Featured/top image URL
    extraction_date: datetime = field(default_factory=datetime.now)
    word_count: int = field(init=False)
    read_time: int = field(init=False)
    article_id: str = field(init=False)
    
    # New metadata fields
    category: str = ""
    publication_name: str = ""
    meta_description: str = ""
    # REMOVED: meta_keywords field (inconsistent across sites)
    canonical_link: str = ""
    image_urls: List[str] = field(default_factory=list)
    video_urls: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    is_paywalled: bool = False
    
    # NLP Analysis Results
    entities: Dict[str, List[str]] = field(default_factory=dict)
    sentiment: Dict[str, Any] = field(default_factory=dict)
    nlp_summary: str = ""
    nlp_processed: bool = False
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Calculate word count
        self.word_count = len(self.content.split()) if self.content else 0
        
        # Calculate estimated reading time (average 200 words per minute)
        self.read_time = max(1, self.word_count // 200)
        
        # Generate unique article ID
        self.article_id = self._generate_id()
        
        # Parse published date if it's a string
        if isinstance(self.published_date, str):
            self.published_date = self._parse_date(self.published_date)
    
    def _generate_id(self) -> str:
        """Generate unique article ID based on URL and title"""
        content_hash = hashlib.md5(f"{self.url}{self.title}".encode()).hexdigest()
        return f"article_{content_hash[:12]}"
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        try:
            return date_parser.parse(date_string)
        except (ValueError, TypeError):
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary"""
        return {
            'article_id': self.article_id,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'summary': self.summary,
            'author': self.author,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'source': self.source,
            'language': self.language,
            'translated': self.translated,
            'top_image': self.top_image,
            'extraction_date': self.extraction_date.isoformat(),
            'word_count': self.word_count,
            'read_time': self.read_time,
            
            # New metadata
            'category': self.category,
            'publication_name': self.publication_name,
            'meta_description': self.meta_description,
            'canonical_link': self.canonical_link,
            'image_urls': self.image_urls,
            'video_urls': self.video_urls,
            'links': self.links,
            'is_paywalled': self.is_paywalled,

            # NLP Analysis Results
            'entities': self.entities,
            'sentiment': self.sentiment,
            'nlp_summary': self.nlp_summary,
            'nlp_processed': self.nlp_processed
        }
    
    def get_content_preview(self, max_length: int = 200) -> str:
        """Get a preview of the article content"""
        if not self.content:
            return ""
        
        if len(self.content) <= max_length:
            return self.content
        
        # Find the last complete sentence within the limit
        preview = self.content[:max_length]
        last_sentence_end = max(
            preview.rfind('.'),
            preview.rfind('!'),
            preview.rfind('?')
        )
        
        if last_sentence_end > max_length // 2:
            return preview[:last_sentence_end + 1]
        
        return preview + "..."
    
    def get_title_preview(self, max_length: int = 100) -> str:
        """Get a preview of the article title"""
        if not self.title:
            return ""
        
        if len(self.title) <= max_length:
            return self.title
        
        return self.title[:max_length] + "..."
    
    # Field removed: tags (unreliable - empty 80% of time)
    # Field removed: keywords (inconsistent and verbose)
    # Use article.entities for structured categorization instead
    
    def is_recent(self, days: int = 7) -> bool:
        """Check if article was published recently"""
        if not self.published_date:
            return False
        
        now = datetime.now()
        if self.published_date.tzinfo is None:
            # If published_date is naive, assume it's in the same timezone as now
            published_date = self.published_date
        else:
            # If published_date is timezone-aware, convert now to UTC for comparison
            published_date = self.published_date.replace(tzinfo=None)
        
        return (now - published_date).days <= days
    
    def get_reading_difficulty(self) -> str:
        """Get estimated reading difficulty based on word count and sentence structure"""
        if self.word_count < 100:
            return "easy"
        elif self.word_count < 500:
            return "medium"
        else:
            return "hard"
    
    def __str__(self) -> str:
        """String representation of the article"""
        return f"Article(title='{self.get_title_preview(50)}', source='{self.source}', word_count={self.word_count})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Article(article_id='{self.article_id}', title='{self.get_title_preview(30)}', "
                f"source='{self.source}', published_date={self.published_date}, "
                f"word_count={self.word_count}, language='{self.language}')")
    
    def __eq__(self, other) -> bool:
        """Check equality based on article ID"""
        if not isinstance(other, Article):
            return False
        return self.article_id == other.article_id
    
    def __hash__(self) -> int:
        """Hash based on article ID"""
        return hash(self.article_id)