"""
HTTP Client Module
=================

Handles all HTTP requests with retry logic and error handling
Supports both requests and httpx libraries
"""

import requests
import time
import logging
from typing import Dict, Optional, Union
from utils.exceptions import ExtractionError

# Try to import httpx for additional HTTP client support
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class HTTPClient:
    """
    Professional HTTP client with retry logic and configurable headers
    Supports both requests and httpx libraries
    """
    
    def __init__(self, 
                 request_timeout: int = 30,
                 max_retries: int = 3,
                 custom_headers: Optional[Dict] = None,
                 use_httpx: bool = False):
        """
        Initialize the HTTP client
        
        Args:
            request_timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retry attempts
            custom_headers (dict): Custom HTTP headers
            use_httpx (bool): Whether to use httpx instead of requests
        """
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.use_httpx = use_httpx and HTTPX_AVAILABLE
        
        # Setup default headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if custom_headers:
            self.headers.update(custom_headers)
            
        self.logger = logging.getLogger(__name__)
    
    def fetch_url(self, url: str) -> Union[requests.Response, 'httpx.Response']:
        """
        Fetch URL with retry logic and exponential backoff
        
        Args:
            url (str): URL to fetch
            
        Returns:
            Union[requests.Response, httpx.Response]: HTTP response
            
        Raises:
            ExtractionError: If all retry attempts fail
        """
        if self.use_httpx:
            return self._fetch_with_httpx(url)
        else:
            return self._fetch_with_requests(url)
    
    def _fetch_with_requests(self, url: str) -> requests.Response:
        """Fetch URL using requests library"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, 
                    headers=self.headers,
                    timeout=self.request_timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ExtractionError(
                        f"Failed to fetch URL after {self.max_retries} attempts: {str(e)}"
                    )
                
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _fetch_with_httpx(self, url: str) -> 'httpx.Response':
        """Fetch URL using httpx library"""
        if not HTTPX_AVAILABLE:
            raise ExtractionError("httpx library is not available")
        
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.request_timeout) as client:
                    response = client.get(
                        url,
                        headers=self.headers,
                        follow_redirects=True
                    )
                    response.raise_for_status()
                    return response
                    
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise ExtractionError(
                        f"Failed to fetch URL after {self.max_retries} attempts: {str(e)}"
                    )
                
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def fetch_head(self, url: str, timeout: int = 10) -> requests.Response:
        """
        Fetch only headers of a URL
        
        Args:
            url (str): URL to fetch headers for
            timeout (int): Request timeout in seconds
            
        Returns:
            requests.Response: HTTP response with headers only
        """
        try:
            return requests.head(url, headers=self.headers, timeout=timeout)
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"HEAD request failed for {url}: {e}")
            raise
