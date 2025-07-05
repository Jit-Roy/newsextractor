class ContentSelectors:
    """
    Enhanced content selectors for different news site formats
    Includes both headings and paragraphs for comprehensive content extraction
    """

    def __init__(self):
        # Enhanced selectors that include headings and paragraphs
        self.selectors = [
            # Standard article tags with headings and paragraphs (highest priority)
            "article h1, article h2, article h3, article p",
            "article div.content h1, article div.content h2, article div.content h3, article div.content p",
            "article div.body h1, article div.body h2, article div.body h3, article div.body p",
            # Common content containers with both headings and paragraphs
            ".article-content h1, .article-content h2, .article-content h3, .article-content p",
            ".article-body h1, .article-body h2, .article-body h3, .article-body p",
            ".post-content h1, .post-content h2, .post-content h3, .post-content p",
            ".entry-content h1, .entry-content h2, .entry-content h3, .entry-content p",
            ".story-content h1, .story-content h2, .story-content h3, .story-content p",
            ".news-content h1, .news-content h2, .news-content h3, .news-content p",
            # Flexible class-based selectors
            '[class*="article"] h1, [class*="article"] h2, [class*="article"] h3, [class*="article"] p',
            '[class*="content"] h1, [class*="content"] h2, [class*="content"] h3, [class*="content"] p',
            '[class*="story"] h1, [class*="story"] h2, [class*="story"] h3, [class*="story"] p',
            '[class*="post"] h1, [class*="post"] h2, [class*="post"] h3, [class*="post"] p',
            # Main content areas
            "main h1, main h2, main h3, main p",
            ".main h1, .main h2, .main h3, .main p",
            "#main h1, #main h2, #main h3, #main p",
            # Container-based selectors
            ".container h1, .container h2, .container h3, .container p",
            ".wrapper h1, .wrapper h2, .wrapper h3, .wrapper p",
            # Fallback selectors
            "h1, h2, h3, p",  # Last resort - all headings and paragraphs
        ]

        # Site-specific selectors with enhanced coverage
        self.site_selectors = {
            "timesofindia.indiatimes.com": [
                ".Normal",
                "._3YYSt",
                ".article-content h1, .article-content h2, .article-content h3, .article-content p",
            ],
            "hindustantimes.com": [
                ".story-details h1, .story-details h2, .story-details h3, .story-details p",
                ".detail h1, .detail h2, .detail h3, .detail p",
            ],
            "indianexpress.com": [
                ".story-element-text",
                ".ie-customstory h1, .ie-customstory h2, .ie-customstory h3, .ie-customstory p",
            ],
            "ndtv.com": [
                ".sp-cn",
                ".ins__story-body h1, .ins__story-body h2, .ins__story-body h3, .ins__story-body p",
            ],
            "news18.com": [
                ".story-article-content h1, .story-article-content h2, .story-article-content h3, .story-article-content p",
                ".article-content h1, .article-content h2, .article-content h3, .article-content p",
            ],
            "reuters.com": [
                ".StandardArticleBody_body h1, .StandardArticleBody_body h2, .StandardArticleBody_body h3, .StandardArticleBody_body p",
                ".ArticleBodyWrapper h1, .ArticleBodyWrapper h2, .ArticleBodyWrapper h3, .ArticleBodyWrapper p",
            ],
            "bbc.com": [
                ".story-body__inner h1, .story-body__inner h2, .story-body__inner h3, .story-body__inner p",
                ".gel-body-copy h1, .gel-body-copy h2, .gel-body-copy h3, .gel-body-copy p",
            ],
            "cnn.com": [
                ".zn-body__paragraph",
                ".el__leafmedia--sourced-paragraph",
                ".article__content h1, .article__content h2, .article__content h3, .article__content p",
            ],
            "theguardian.com": [
                ".dcr-1kas69x h1, .dcr-1kas69x h2, .dcr-1kas69x h3, .dcr-1kas69x p",
                ".content__article-body h1, .content__article-body h2, .content__article-body h3, .content__article-body p",
            ],
            "nytimes.com": [
                ".css-1r7ky0e h1, .css-1r7ky0e h2, .css-1r7ky0e h3, .css-1r7ky0e p",
                ".StoryBodyCompanionColumn h1, .StoryBodyCompanionColumn h2, .StoryBodyCompanionColumn h3, .StoryBodyCompanionColumn p",
            ],
        }

        # Terms that indicate non-content elements (from spider analysis)
        self.exclude_terms = [
            "trending",
            "headlines",
            "videos",
            "gallery",
            "opinion",
            "cookies",
            "privacy",
            "terms",
            "conditions",
            "subscribe",
            "newsletter",
            "advertisement",
            "recommended",
            "related",
            "popular",
            "more news",
            "copyright",
            "all rights reserved",
            "social media",
            "follow us",
            "share this",
            "tweet",
            "facebook",
            "instagram",
            "linkedin",
        ]

    def get_selectors(self, domain: str = None) -> list:
        """Get content selectors for a specific domain or general selectors"""
        if domain and domain in self.site_selectors:
            return self.site_selectors[domain] + self.selectors
        return self.selectors

    def should_exclude_content(self, text: str) -> bool:
        """
        Check if the text contains terms that indicate it's not main content

        Args:
            text (str): Text to check

        Returns:
            bool: True if content should be excluded
        """
        if not text or len(text.strip()) < 10:  # Too short to be meaningful content
            return True

        lower_text = text.lower()
        return any(term in lower_text for term in self.exclude_terms)

    def is_likely_header(self, tag_name: str) -> bool:
        """
        Check if a tag is likely a header element

        Args:
            tag_name (str): HTML tag name

        Returns:
            bool: True if it's a header tag
        """
        return tag_name and tag_name.lower() in ["h1", "h2", "h3", "h4", "h5", "h6"]
