"""
Metadata Extractor Module
========================

Specialized module for extracting metadata from HTML content
"""

import logging
from typing import Dict, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class MetadataExtractor:
    """
    Professional metadata extractor for news articles
    """

    def __init__(self):
        """Initialize the metadata extractor"""
        self.logger = logging.getLogger(__name__)

    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract comprehensive metadata from HTML content

        Args:
            soup (BeautifulSoup): Parsed HTML content
            url (str): Original URL

        Returns:
            Dict: Extracted metadata
        """
        metadata = {}

        # Extract source
        parsed_url = urlparse(url)
        metadata["source"] = parsed_url.netloc

        # Extract author
        metadata["author"] = self._extract_author(soup)

        # Extract published date
        metadata["published_date"] = self._extract_published_date(soup)

        # Extract summary/description
        metadata["summary"] = self._extract_summary(soup)

        # Extract top image
        metadata["top_image"] = self._extract_top_image(soup, url)

        # Extract additional OpenGraph metadata
        metadata.update(self._extract_opengraph_metadata(soup))

        # Extract Twitter Card metadata
        metadata.update(self._extract_twitter_metadata(soup))

        # Extract JSON-LD structured data
        metadata.update(self._extract_jsonld_metadata(soup))

        # New metadata extraction
        metadata["category"] = self._extract_category(soup)
        metadata["publication_name"] = self._extract_publication_name(
            soup, metadata.get("source")
        )
        metadata["meta_description"] = self._extract_meta_description(soup)
        metadata["meta_keywords"] = self._extract_meta_keywords(soup)
        metadata["tags"] = self._extract_tags(soup, metadata)  # Add tags extraction
        metadata["canonical_link"] = self._extract_canonical_link(soup)
        metadata["image_urls"] = self._extract_image_urls(soup)
        metadata["video_urls"] = self._extract_video_urls(soup)
        metadata["links"] = self._extract_links(soup, url)
        metadata["is_paywalled"] = self._extract_is_paywalled(soup)

        return metadata

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """
        Extract author information using multiple selectors

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            str: Author name or empty string
        """
        author_selectors = [
            '[rel="author"]',
            '[property="article:author"]',
            '[name="author"]',
            ".author",
            ".byline",
            ".writer-name",
            ".article-author",
            ".post-author",
        ]

        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get("content") or element.get_text(strip=True)
                if author and len(author) > 0:
                    return author

        return ""

    def _extract_published_date(self, soup: BeautifulSoup) -> str:
        """
        Extract published date using multiple selectors

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            str: Published date or empty string
        """
        date_selectors = [
            '[property="article:published_time"]',
            '[property="og:published_time"]',
            '[name="article:published_time"]',
            "time[datetime]",
            ".publish-date",
            ".date",
            ".published-date",
            ".article-date",
        ]

        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = (
                    element.get("datetime")
                    or element.get("content")
                    or element.get_text(strip=True)
                )
                if date_text:
                    return date_text

        return ""

    def _extract_summary(self, soup: BeautifulSoup) -> str:
        """
        Extract article summary/description

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            str: Summary or empty string
        """
        summary_selectors = [
            '[property="og:description"]',
            '[name="description"]',
            '[name="twitter:description"]',
            ".article-summary",
            ".excerpt",
            ".article-excerpt",
            ".post-excerpt",
        ]

        for selector in summary_selectors:
            element = soup.select_one(selector)
            if element:
                summary = element.get("content") or element.get_text(strip=True)
                if summary and len(summary) > 20:  # Reasonable summary length
                    return summary

        return ""

    def _extract_top_image(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract the top image from the article with enhanced detection

        Args:
            soup (BeautifulSoup): Parsed HTML content
            url (str): Original URL

        Returns:
            str: URL of the top image or empty string
        """
        from urllib.parse import urljoin

        # Priority 1: OpenGraph image
        og_image = soup.select_one('[property="og:image"]')
        if og_image and og_image.get("content"):
            return self._normalize_image_url(og_image["content"], url)

        # Priority 2: Twitter Card image
        twitter_image = soup.select_one('[name="twitter:image"]')
        if twitter_image and twitter_image.get("content"):
            return self._normalize_image_url(twitter_image["content"], url)

        # Priority 3: JSON-LD structured data image
        jsonld_image = self._extract_jsonld_image(soup)
        if jsonld_image:
            return self._normalize_image_url(jsonld_image, url)

        # Priority 4: Featured image selectors (CMS-specific)
        featured_selectors = [
            ".featured-image img",
            ".post-thumbnail img",
            ".article-image img",
            ".hero-image img",
            ".wp-post-image",
            ".entry-featured-image img",
            ".article-featured-image img",
        ]

        for selector in featured_selectors:
            element = soup.select_one(selector)
            if element and element.get("src"):
                return self._normalize_image_url(element["src"], url)

        # Priority 5: First large image in content
        content_images = soup.select(
            "article img, .content img, .post-content img, .entry-content img"
        )
        for img in content_images:
            if img.get("src") and self._is_valid_image(img):
                return self._normalize_image_url(img["src"], url)

        # Priority 6: Any reasonable image
        all_images = soup.find_all("img", src=True)
        for img in all_images:
            if self._is_valid_image(img):
                return self._normalize_image_url(img["src"], url)

        return ""

    def _extract_jsonld_image(self, soup: BeautifulSoup) -> str:
        """Extract image from JSON-LD structured data"""
        try:
            import json

            jsonld_scripts = soup.find_all("script", type="application/ld+json")

            for script in jsonld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Check for image in Article or NewsArticle
                        if (
                            data.get("@type") in ["Article", "NewsArticle"]
                            and "image" in data
                        ):
                            image = data["image"]
                            if isinstance(image, str):
                                return image
                            elif isinstance(image, dict) and "url" in image:
                                return image["url"]
                            elif isinstance(image, list) and len(image) > 0:
                                first_image = image[0]
                                if isinstance(first_image, str):
                                    return first_image
                                elif (
                                    isinstance(first_image, dict)
                                    and "url" in first_image
                                ):
                                    return first_image["url"]
                except json.JSONDecodeError:
                    continue
        except ImportError:
            pass

        return ""

    def _normalize_image_url(self, image_url: str, base_url: str) -> str:
        """Normalize image URL to absolute URL"""
        from urllib.parse import urljoin, urlparse

        if not image_url:
            return ""

        # If already absolute URL, return as is
        if urlparse(image_url).netloc:
            return image_url

        # Convert relative URL to absolute
        return urljoin(base_url, image_url)

    def _is_valid_image(self, img_element) -> bool:
        """Check if image element represents a valid article image"""
        src = img_element.get("src", "")
        alt = img_element.get("alt", "")

        # Skip if no src
        if not src:
            return False

        # Skip common non-content images
        skip_patterns = [
            "logo",
            "icon",
            "avatar",
            "profile",
            "social",
            "share",
            "advertisement",
            "ad-",
            "banner",
            "placeholder",
            "spacer",
            "tracking",
            "pixel",
            "1x1",
            "transparent",
        ]

        src_lower = src.lower()
        alt_lower = alt.lower()

        for pattern in skip_patterns:
            if pattern in src_lower or pattern in alt_lower:
                return False

        # Check image dimensions if available
        width = img_element.get("width")
        height = img_element.get("height")

        if width and height:
            try:
                w, h = int(width), int(height)
                # Skip very small images (likely icons/spacers)
                if w < 100 or h < 100:
                    return False
                # Skip very wide or very tall images (likely banners)
                ratio = max(w, h) / min(w, h)
                if ratio > 5:
                    return False
            except (ValueError, ZeroDivisionError):
                pass

        return True

    def _extract_opengraph_metadata(self, soup: BeautifulSoup) -> Dict:
        """
        Extract OpenGraph metadata

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            Dict: OpenGraph metadata
        """
        og_metadata = {}

        # Common OpenGraph properties
        og_properties = [
            "og:title",
            "og:description",
            "og:image",
            "og:url",
            "og:type",
            "og:site_name",
            "article:author",
            "article:published_time",
            "article:modified_time",
            "article:section",
            "article:tag",
        ]

        for prop in og_properties:
            element = soup.select_one(f'[property="{prop}"]')
            if element:
                content = element.get("content")
                if content:
                    # Convert property name to snake_case
                    key = prop.replace(":", "_").replace("-", "_")
                    og_metadata[key] = content

        return og_metadata

    def _extract_twitter_metadata(self, soup: BeautifulSoup) -> Dict:
        """
        Extract Twitter Card metadata

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            Dict: Twitter Card metadata
        """
        twitter_metadata = {}

        # Common Twitter Card properties
        twitter_properties = [
            "twitter:card",
            "twitter:title",
            "twitter:description",
            "twitter:image",
            "twitter:site",
            "twitter:creator",
        ]

        for prop in twitter_properties:
            element = soup.select_one(f'[name="{prop}"]')
            if element:
                content = element.get("content")
                if content:
                    # Convert property name to snake_case
                    key = prop.replace(":", "_").replace("-", "_")
                    twitter_metadata[key] = content

        return twitter_metadata

    def _extract_jsonld_metadata(self, soup: BeautifulSoup) -> Dict:
        """
        Extract JSON-LD structured data (basic implementation)

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            Dict: JSON-LD metadata
        """
        jsonld_metadata = {}

        try:
            import json

            # Find JSON-LD script tags
            jsonld_scripts = soup.find_all("script", type="application/ld+json")

            for script in jsonld_scripts:
                try:
                    data = json.loads(script.string)

                    # Extract relevant fields for news articles
                    if isinstance(data, dict):
                        if data.get("@type") in ["Article", "NewsArticle"]:
                            if "headline" in data:
                                jsonld_metadata["jsonld_headline"] = data["headline"]
                            if "author" in data:
                                if isinstance(data["author"], dict):
                                    jsonld_metadata["jsonld_author"] = data[
                                        "author"
                                    ].get("name", "")
                                elif isinstance(data["author"], str):
                                    jsonld_metadata["jsonld_author"] = data["author"]
                            if "datePublished" in data:
                                jsonld_metadata["jsonld_date_published"] = data[
                                    "datePublished"
                                ]
                            if "description" in data:
                                jsonld_metadata["jsonld_description"] = data[
                                    "description"
                                ]

                except json.JSONDecodeError:
                    continue

        except ImportError:
            self.logger.debug("JSON module not available for JSON-LD parsing")
        except Exception as e:
            self.logger.debug(f"Failed to parse JSON-LD: {e}")

        return {}

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract article category."""
        # Try OpenGraph property first
        og_category = soup.find("meta", property="article:section")
        if og_category and og_category.get("content"):
            return og_category["content"]

        # Look for breadcrumbs
        breadcrumb = soup.select_one(
            ".breadcrumb a, .breadcrumbs a, .b-breadcrumbs__item a"
        )
        if breadcrumb:
            return breadcrumb.get_text(strip=True)

        return ""

    def _extract_publication_name(self, soup: BeautifulSoup, source: str) -> str:
        """Extract publication name."""
        og_site_name = soup.find("meta", property="og:site_name")
        if og_site_name and og_site_name.get("content"):
            return og_site_name["content"]

        twitter_site = soup.find("meta", attrs={"name": "twitter:site"})
        if twitter_site and twitter_site.get("content"):
            return twitter_site["content"].lstrip("@")

        if source:
            # Capitalize the first part of the domain
            return source.split(".")[0].capitalize()

        return ""

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
        return ""

    def _extract_meta_keywords(self, soup: BeautifulSoup) -> list[str]:
        """Extract meta keywords."""
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords and meta_keywords.get("content"):
            return [k.strip() for k in meta_keywords["content"].split(",")]
        return []

    def _extract_tags(self, soup: BeautifulSoup, metadata: Dict) -> List[str]:
        """
        Extract tags from various sources including OpenGraph, HTML elements, and meta keywords

        Args:
            soup (BeautifulSoup): Parsed HTML content
            metadata (Dict): Already extracted metadata that might contain tags

        Returns:
            List[str]: List of extracted tags
        """
        tags = []

        # 1. Extract from OpenGraph article:tag (multiple tags possible)
        article_tags = soup.find_all("meta", property="article:tag")
        for tag_element in article_tags:
            content = tag_element.get("content")
            if content:
                tags.append(content.strip())

        # 2. Extract from already extracted OpenGraph metadata
        if "article_tag" in metadata:
            if isinstance(metadata["article_tag"], list):
                tags.extend(metadata["article_tag"])
            elif isinstance(metadata["article_tag"], str):
                tags.append(metadata["article_tag"])

        # 3. Extract from common HTML tag selectors
        tag_selectors = [
            ".tags a",
            ".post-tags a",
            ".article-tags a",
            ".tag-links a",
            ".entry-tags a",
            ".category-tags a",
            ".tags span",
            ".post-tags span",
            ".article-tags span",
            ".wp-tag-cloud a",
            ".tag-list a",
            ".hashtags a",
        ]

        for selector in tag_selectors:
            elements = soup.select(selector)
            for element in elements:
                tag_text = element.get_text(strip=True)
                if tag_text and len(tag_text) > 1:  # Avoid single characters
                    tags.append(tag_text)

        # 4. Extract from meta keywords if no other tags found
        if not tags and metadata.get("meta_keywords"):
            tags.extend(metadata["meta_keywords"])

        # 5. Extract from breadcrumbs as fallback categories
        if not tags:
            breadcrumbs = soup.select(
                ".breadcrumb a, .breadcrumbs a, .nav-breadcrumb a"
            )
            for breadcrumb in breadcrumbs[1:]:  # Skip first (usually "Home")
                breadcrumb_text = breadcrumb.get_text(strip=True)
                if breadcrumb_text and breadcrumb_text.lower() not in [
                    "home",
                    "news",
                    "articles",
                ]:
                    tags.append(breadcrumb_text)

        # Clean and deduplicate tags
        cleaned_tags = []
        for tag in tags:
            tag = tag.strip()
            if tag and len(tag) > 1 and tag not in cleaned_tags:
                cleaned_tags.append(tag)

        return cleaned_tags[:10]  # Limit to 10 tags to avoid spam

    def _extract_canonical_link(self, soup: BeautifulSoup) -> str:
        """Extract canonical link."""
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            return canonical["href"]
        return ""

    def _extract_image_urls(self, soup: BeautifulSoup) -> list[str]:
        """Extract all image URLs from the article body."""
        images = []
        article_body = (
            soup.find("article")
            or soup.find("div", class_="post-content")
            or soup.find("div", class_="entry-content")
        )
        if article_body:
            for img in article_body.find_all("img"):
                if img.get("src"):
                    images.append(img["src"])
        return list(set(images))

    def _extract_video_urls(self, soup: BeautifulSoup) -> list[str]:
        """Extract all video URLs from the article body."""
        videos = []
        # Look for iframes from common video hosts
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src", "")
            if "youtube.com" in src or "vimeo.com" in src:
                videos.append(src)
        return list(set(videos))

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """Extract all outbound links from the article body."""
        from urllib.parse import urljoin, urlparse

        links = []
        article_body = (
            soup.find("article")
            or soup.find("div", class_="post-content")
            or soup.find("div", class_="entry-content")
        )
        if article_body:
            for a in article_body.find_all("a", href=True):
                href = a["href"]
                # Ensure it's an absolute URL and not an internal link
                if (
                    href.startswith("http")
                    and urlparse(href).netloc != urlparse(base_url).netloc
                ):
                    links.append(urljoin(base_url, href))
        return list(set(links))  # Return unique links

    def _extract_is_paywalled(self, soup: BeautifulSoup) -> bool:
        """Detect if the article is behind a paywall."""
        # This is a simple heuristic and might need to be more sophisticated
        paywall_selectors = [
            "#paywall",
            ".paywall",
            ".premium-content",
            "div[class*='paywall']",
        ]
        for selector in paywall_selectors:
            if soup.select_one(selector):
                return True
        return False
