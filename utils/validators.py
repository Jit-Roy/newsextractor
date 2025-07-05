import re
from urllib.parse import urlparse
from typing import List

class URLValidator:
    """URL validation utility"""
    
    def __init__(self):
        self.valid_schemes = ['http', 'https']
        self.blocked_domains = [
            'facebook.com', 'twitter.com', 'instagram.com',
            'linkedin.com', 'youtube.com', 'tiktok.com'
        ]
    
    def is_valid(self, url: str) -> bool:
        """Check if URL is valid for news extraction"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in self.valid_schemes:
                return False
            
            # Check domain
            if not parsed.netloc:
                return False
            
            # Check if domain is blocked
            domain = parsed.netloc.lower()
            for blocked in self.blocked_domains:
                if blocked in domain:
                    return False
            
            return True
            
        except Exception:
            return False