"""
Language Processing Module
=========================

Handles language detection and translation for extracted content
"""

import logging
from typing import Dict, Optional
from core.translator import Translator


class LanguageProcessor:
    """
    Professional language processing with detection and translation capabilities
    """
    
    def __init__(self, target_language: Optional[str] = None):
        """
        Initialize the language processor
        
        Args:
            target_language (str, optional): Target language for translation
        """
        self.target_language = target_language
        self.translator = Translator()  # Always initialize for detection
        self.logger = logging.getLogger(__name__)
    
    def process_content(self, article_data: Dict) -> Dict:
        """
        Process article content for language detection and translation
        
        Args:
            article_data (Dict): Article data dictionary
            
        Returns:
            Dict: Processed article data with language info and translations
        """
        # Always detect language
        detected_language = self._detect_language(article_data)
        article_data['language'] = detected_language
        
        # Translate if a target language is set and different from detected language
        if self.target_language and detected_language != 'unknown' and detected_language != self.target_language:
            article_data = self._translate_content(article_data, detected_language)
        else:
            article_data['translated'] = False
        
        return article_data
    
    def _detect_language(self, article_data: Dict) -> str:
        """
        Detect the language of the article content
        
        Args:
            article_data (Dict): Article data dictionary
            
        Returns:
            str: Detected language code or 'unknown'
        """
        try:
            # Use title and content for detection
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            
            # Create sample text for detection (limit length for API efficiency)
            sample_text = f"{title} {content}"[:500]
            
            if sample_text.strip():
                language = self.translator.detect_language(sample_text)
                self.logger.debug(f"Detected language: {language}")
                return language
            else:
                self.logger.warning("No text available for language detection")
                return 'unknown'
                
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
            return 'unknown'
    
    def _translate_content(self, article_data: Dict, source_language: str) -> Dict:
        """
        Translate article content to target language
        
        Args:
            article_data (Dict): Article data dictionary
            source_language (str): Source language code
            
        Returns:
            Dict: Article data with translated content
        """
        try:
            self.logger.info(f"Translating content from {source_language} to {self.target_language}")
            
            translated = False
            
            # Translate title
            title = article_data.get('title', '')
            if title:
                translated_title = self.translator.translate(
                    title, 
                    target_lang=self.target_language
                )
                if translated_title and translated_title != title:
                    article_data['title'] = translated_title
                    translated = True
                    self.logger.debug("Title translated successfully")
            
            # Translate content
            content = article_data.get('content', '')
            if content:
                # Check content length - some translation services have limits
                if len(content) > 5000:
                    self.logger.warning(f"Content is long ({len(content)} chars), translation may fail")
                
                translated_content = self.translator.translate(
                    content, 
                    target_lang=self.target_language
                )
                if translated_content and translated_content != content:
                    article_data['content'] = translated_content
                    translated = True
                    self.logger.debug("Content translated successfully")
            
            # Translate summary if available
            summary = article_data.get('summary', '')
            if summary:
                translated_summary = self.translator.translate(
                    summary, 
                    target_lang=self.target_language
                )
                if translated_summary and translated_summary != summary:
                    article_data['summary'] = translated_summary
                    translated = True
            
            article_data['translated'] = translated
            
            if translated:
                self.logger.info(f"Successfully translated content from {source_language} to {self.target_language}")
            else:
                self.logger.warning("Translation did not modify any content")
            
            return article_data
            
        except Exception as e:
            self.logger.error(f"Translation failed: {type(e).__name__}: {e}")
            self.logger.debug("Translation error details", exc_info=True)
            # Return original content if translation fails
            article_data['translated'] = False
            return article_data
