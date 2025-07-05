import re
from urllib.parse import urlparse
from typing import List


class URLValidator:
    """URL validation utility"""

    VALID_SCHEMES = ["http", "https"]
    BLOCKED_DOMAINS = [
        "facebook.com",
        "twitter.com",
        "instagram.com",
        "linkedin.com",
        "youtube.com",
        "tiktok.com",
    ]

    def __init__(self):
        self.valid_schemes = self.VALID_SCHEMES
        self.blocked_domains = self.BLOCKED_DOMAINS

    @classmethod
    def is_valid(cls, url: str) -> bool:
        """Check if URL is valid for news extraction"""
        try:
            if not url or not isinstance(url, str):
                return False

            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in cls.VALID_SCHEMES:
                return False

            # Check domain
            if not parsed.netloc:
                return False

            # Check if domain is blocked
            domain = parsed.netloc.lower()
            for blocked in cls.BLOCKED_DOMAINS:
                if blocked in domain:
                    return False

            return True

        except Exception:
            return False

    def validate(self, url: str) -> bool:
        """Instance method for backwards compatibility"""
        return self.is_valid(url)
