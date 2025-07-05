"""
Content Parser Module
====================

Handles HTML parsing and content extraction from web pages
Supports multiple extraction methods including advanced text cleaning tools
"""

import logging
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from utils.selectors import ContentSelectors

# Try to import lxml for better parsing performance
try:
    import lxml
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

# Try to import advanced text extraction tools
try:
    from boilerpy3 import extractors
    BOILERPY3_AVAILABLE = True
except ImportError:
    BOILERPY3_AVAILABLE = False

try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False


class ContentParser:
    """
    Professional HTML content parser with advanced text cleaning capabilities
    Supports multiple extraction methods: custom, boilerpy3, readability, trafilatura
    """
    
    def __init__(self, 
                 use_lxml: bool = True,
                 extraction_method: str = 'auto',
                 fallback_methods: bool = True):
        """
        Initialize the content parser
        
        Args:
            use_lxml (bool): Whether to use lxml parser if available
            extraction_method (str): Preferred extraction method 
                                   ('auto', 'custom', 'boilerpy3', 'readability', 'trafilatura')
            fallback_methods (bool): Whether to try fallback methods if primary fails
        """
        self.content_selectors = ContentSelectors()
        self.logger = logging.getLogger(__name__)
        self.extraction_method = extraction_method
        self.fallback_methods = fallback_methods
        
        # Determine which parser to use
        if use_lxml and LXML_AVAILABLE:
            self.parser = 'lxml'
            self.logger.debug("Using lxml parser for better performance")
        else:
            self.parser = 'html.parser'
            self.logger.debug("Using html.parser (lxml not available or disabled)")
        
        # Log available extraction methods
        self._log_available_methods()
    
    def _log_available_methods(self):
        """Log which advanced extraction methods are available"""
        methods = []
        if BOILERPY3_AVAILABLE:
            methods.append("boilerpy3")
        if READABILITY_AVAILABLE:
            methods.append("readability")
        if TRAFILATURA_AVAILABLE:
            methods.append("trafilatura")
        
        if methods:
            self.logger.debug(f"Advanced extraction methods available: {', '.join(methods)}")
        else:
            self.logger.debug("No advanced extraction methods available, using custom parser")
    
    def parse_article_data(self, html_content: str, url: str) -> Dict:
        """
        Parse HTML content and extract article data with advanced text cleaning
        
        Args:
            html_content (str): Raw HTML content
            url (str): Original URL for context
            
        Returns:
            Dict: Extracted article data containing title, content, and metadata
        """
        try:
            soup = BeautifulSoup(html_content, self.parser)
        except Exception as e:
            # Fallback to html.parser if lxml fails
            self.logger.warning(f"Parser {self.parser} failed, falling back to html.parser: {e}")
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract content using the specified method
        content = self._extract_content_advanced(html_content, url, soup)
        
        return {
            'title': self._extract_title(soup),
            'content': content,
            'metadata': self._extract_basic_metadata(soup, url)
        }
    
    def _extract_content_advanced(self, html_content: str, url: str, soup: BeautifulSoup) -> str:
        """
        Extract content using advanced methods with fallbacks
        
        Args:
            html_content (str): Raw HTML content
            url (str): Original URL
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            str: Extracted and cleaned content
        """
        extraction_methods = self._get_extraction_methods()
        
        for method_name, method_func in extraction_methods:
            try:
                self.logger.debug(f"Trying extraction method: {method_name}")
                content = method_func(html_content, url, soup)
                
                if content and len(content.strip()) > 100:  # Minimum content threshold
                    self.logger.debug(f"Successfully extracted content using {method_name}")
                    return self._clean_extracted_content(content)
                else:
                    self.logger.debug(f"{method_name} returned insufficient content")
                    
            except Exception as e:
                self.logger.debug(f"{method_name} extraction failed: {e}")
                continue
        
        # If all methods fail, return empty string
        self.logger.warning("All extraction methods failed")
        return ""
    
    def _get_extraction_methods(self) -> List[tuple]:
        """Get list of extraction methods to try based on preferences"""
        methods = []
        
        if self.extraction_method == 'auto':
            # Auto mode: try advanced methods first, then custom
            if TRAFILATURA_AVAILABLE:
                methods.append(('trafilatura', self._extract_with_trafilatura))
            if READABILITY_AVAILABLE:
                methods.append(('readability', self._extract_with_readability))
            if BOILERPY3_AVAILABLE:
                methods.append(('boilerpy3', self._extract_with_boilerpy3))
            methods.append(('custom', self._extract_with_custom))
            
        elif self.extraction_method == 'trafilatura' and TRAFILATURA_AVAILABLE:
            methods.append(('trafilatura', self._extract_with_trafilatura))
            if self.fallback_methods:
                methods.append(('custom', self._extract_with_custom))
                
        elif self.extraction_method == 'readability' and READABILITY_AVAILABLE:
            methods.append(('readability', self._extract_with_readability))
            if self.fallback_methods:
                methods.append(('custom', self._extract_with_custom))
                
        elif self.extraction_method == 'boilerpy3' and BOILERPY3_AVAILABLE:
            methods.append(('boilerpy3', self._extract_with_boilerpy3))
            if self.fallback_methods:
                methods.append(('custom', self._extract_with_custom))
        else:
            # Default to custom method
            methods.append(('custom', self._extract_with_custom))
        
        return methods
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract article title using multiple selectors
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: Extracted title
        """
        title_selectors = [
            'h1',
            'title',
            '[property="og:title"]',
            '[name="twitter:title"]',
            '.article-title',
            '.post-title',
            '.entry-title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 10:  # Reasonable title length
                    return title
        
        return "Unknown Title"
    
    def _extract_content(self, soup: BeautifulSoup, url: str = None) -> str:
        """
        Extract main content from HTML
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            url (str, optional): Original URL for domain-specific selectors
            
        Returns:
            str: Extracted and cleaned content
        """
        # Get domain for site-specific selectors
        domain = None
        if url:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
        
        # Get appropriate selectors for this domain
        selectors = self.content_selectors.get_selectors(domain)
        
        # Try each selector group until we find content
        for selector_group in selectors:
            elements = soup.select(selector_group)
            if elements:
                self.logger.debug(f"Found content using selector: {selector_group}")
                return self._process_content_elements(elements)
        
        return ""
    
    def _process_content_elements(self, elements: List) -> str:
        """
        Process content elements into clean text
        
        Args:
            elements (List): List of BeautifulSoup elements
            
        Returns:
            str: Processed and cleaned content
        """
        content_parts = []
        
        for element in elements:
            # Skip if element is likely not main content
            if self._should_skip_element(element):
                continue
            
            text = element.get_text(strip=True)
            
            # Use enhanced exclusion logic from selectors
            if self.content_selectors.should_exclude_content(text):
                continue
                
            if text and len(text) > 20:  # Minimum content length
                # Add header formatting for headings
                if self.content_selectors.is_likely_header(element.name):
                    text = f"[{element.name.upper()}] {text}"
                
                content_parts.append(text)
        
        return '\n\n'.join(content_parts)
    
    def _extract_basic_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract basic metadata that doesn't require specialized handling
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            url (str): Original URL
            
        Returns:
            Dict: Basic metadata
        """
        metadata = {}
        
        # Extract source from URL
        parsed_url = urlparse(url)
        metadata['source'] = parsed_url.netloc
        
        # Extract summary/description
        summary_selectors = [
            '[property="og:description"]',
            '[name="description"]',
            '.article-summary',
            '.excerpt'
        ]
        
        for selector in summary_selectors:
            element = soup.select_one(selector)
            if element:
                summary = element.get('content') or element.get_text(strip=True)
                if summary:
                    metadata['summary'] = summary
                    break
        
        return metadata
    
    def _should_skip_element(self, element) -> bool:
        """
        Check if element should be skipped based on HTML attributes and content
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            bool: True if element should be skipped
        """
        # Skip elements with certain classes or IDs
        skip_patterns = [
            'advertisement', 'ad-', 'sidebar', 'footer', 'header',
            'navigation', 'menu', 'social', 'share', 'comment',
            'related', 'recommended', 'trending', 'popular',
            'newsletter', 'subscribe', 'privacy', 'cookie'
        ]
        
        element_classes = ' '.join(element.get('class', []))
        element_id = element.get('id', '')
        
        for pattern in skip_patterns:
            if pattern in element_classes.lower() or pattern in element_id.lower():
                return True
        
        # Skip if element text content suggests it's not main content
        text = element.get_text(strip=True)
        if self.content_selectors.should_exclude_content(text):
            return True
        
        return False
    
    def _extract_with_trafilatura(self, html_content: str, url: str, soup: BeautifulSoup) -> str:
        """Extract content using trafilatura"""
        if not TRAFILATURA_AVAILABLE:
            raise ImportError("trafilatura not available")
        
        # Use trafilatura for content extraction
        content = trafilatura.extract(html_content, 
                                    include_comments=False,
                                    include_tables=True,
                                    include_formatting=False,
                                    url=url)
        return content or ""
    
    def _extract_with_readability(self, html_content: str, url: str, soup: BeautifulSoup) -> str:
        """Extract content using readability-lxml"""
        if not READABILITY_AVAILABLE:
            raise ImportError("readability not available")
        
        # Use readability algorithm
        doc = Document(html_content)
        content_html = doc.summary()
        
        # Parse the cleaned HTML to extract text
        content_soup = BeautifulSoup(content_html, self.parser)
        return content_soup.get_text(separator='\n\n', strip=True)
    
    def _extract_with_boilerpy3(self, html_content: str, url: str, soup: BeautifulSoup) -> str:
        """Extract content using boilerpy3"""
        if not BOILERPY3_AVAILABLE:
            raise ImportError("boilerpy3 not available")
        
        # Try different boilerpy3 extractors
        extractors_to_try = [
            extractors.ArticleExtractor(),
            extractors.DefaultExtractor(),
            extractors.LargestContentExtractor(),
            extractors.CanolaExtractor()
        ]
        
        for extractor in extractors_to_try:
            try:
                content = extractor.get_content(html_content)
                if content and len(content.strip()) > 100:
                    return content
            except Exception as e:
                self.logger.debug(f"Boilerpy3 extractor {extractor.__class__.__name__} failed: {e}")
                continue
        
        return ""
    
    def _extract_with_custom(self, html_content: str, url: str, soup: BeautifulSoup) -> str:
        """Extract content using custom method (original implementation)"""
        return self._extract_content(soup, url)
    
    def _clean_extracted_content(self, content: str) -> str:
        """
        Apply additional cleaning to extracted content
        
        Args:
            content (str): Raw extracted content
            
        Returns:
            str: Cleaned content
        """
        if not content:
            return ""
        
        # Split into lines for processing
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip very short lines (likely not meaningful content)
            if len(line) < 10:
                continue
            
            # Skip lines that look like navigation or boilerplate
            skip_patterns = [
                'click here', 'read more', 'share this', 'subscribe',
                'newsletter', 'follow us', 'contact us', 'privacy policy',
                'terms of service', 'cookies', 'advertisement'
            ]
            
            line_lower = line.lower()
            if any(pattern in line_lower for pattern in skip_patterns):
                continue
            
            # Skip lines that are mostly punctuation or numbers
            alpha_chars = sum(1 for c in line if c.isalpha())
            if alpha_chars < len(line) * 0.5:  # Less than 50% alphabetic characters
                continue
            
            cleaned_lines.append(line)
        
        # Join cleaned lines
        cleaned_content = '\n\n'.join(cleaned_lines)
        
        # Remove excessive whitespace
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
        cleaned_content = re.sub(r' {2,}', ' ', cleaned_content)
        
        return cleaned_content.strip()
