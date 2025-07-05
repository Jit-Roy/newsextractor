"""
Translation Module
================

Professional translation module with multiple provider support
"""

import requests
import re
import time
from typing import Dict, Optional, List
import logging
from dataclasses import dataclass
from enum import Enum

from utils.exceptions import TranslationError


class TranslationProvider(Enum):
    """Supported translation providers"""

    GOOGLE_FREE = "google_free"
    GOOGLE_PAID = "google_paid"
    MICROSOFT = "microsoft"
    DEEPL = "deepl"


@dataclass
class TranslationResult:
    """
    Translation result data class

    Attributes:
        original_text (str): Original text
        translated_text (str): Translated text
        source_language (str): Detected source language
        target_language (str): Target language
        confidence (float): Translation confidence score
        provider (str): Translation provider used
    """

    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float = 0.0
    provider: str = "unknown"


class Translator:
    """
    Professional translation class with multiple provider support
    """

    def __init__(
        self,
        provider: TranslationProvider = TranslationProvider.GOOGLE_FREE,
        api_key: Optional[str] = None,
        rate_limit_delay: float = 0.1,
        max_retries: int = 3,
    ):
        """
        Initialize translator

        Args:
            provider (TranslationProvider): Translation provider to use
            api_key (str): API key for paid services
            rate_limit_delay (float): Delay between requests
            max_retries (int): Maximum retry attempts
        """
        self.provider = provider
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries

        self.logger = logging.getLogger(__name__)

        # Language detection patterns
        self.language_patterns = {
            "hi": r"[\u0900-\u097F]",  # Devanagari (Hindi)
            "bn": r"[\u0980-\u09FF]",  # Bengali
            "te": r"[\u0C00-\u0C7F]",  # Telugu
            "mr": r"[\u0900-\u097F]",  # Marathi (same as Hindi script)
            "ta": r"[\u0B80-\u0BFF]",  # Tamil
            "gu": r"[\u0A80-\u0AFF]",  # Gujarati
            "kn": r"[\u0C80-\u0CFF]",  # Kannada
            "ml": r"[\u0D00-\u0D7F]",  # Malayalam
            "pa": r"[\u0A00-\u0A7F]",  # Punjabi
            "or": r"[\u0B00-\u0B7F]",  # Oriya
            "as": r"[\u0980-\u09FF]",  # Assamese
            "ur": r"[\u0600-\u06FF]",  # Urdu (Arabic script)
            "ar": r"[\u0600-\u06FF]",  # Arabic
            "zh": r"[\u4E00-\u9FFF]",  # Chinese
            "ja": r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]",  # Japanese
            "ko": r"[\uAC00-\uD7AF]",  # Korean
            "ru": r"[\u0400-\u04FF]",  # Russian
            "th": r"[\u0E00-\u0E7F]",  # Thai
        }

    def translate(
        self, text: str, target_lang: str = "en", source_lang: str = "auto"
    ) -> str:
        """
        Translate text to target language

        Args:
            text (str): Text to translate
            target_lang (str): Target language code
            source_lang (str): Source language code ('auto' for detection)

        Returns:
            str: Translated text
        """
        if not text or not text.strip():
            return text

        # Detect source language if not provided
        if source_lang == "auto":
            try:
                source_lang = self.detect_language(text)
            except Exception as e:
                self.logger.debug(f"Language detection failed, assuming English: {e}")
                source_lang = "en"

        # Skip translation if source and target languages are the same
        if source_lang == target_lang:
            self.logger.debug(
                f"Skipping translation: source ({source_lang}) == target ({target_lang})"
            )
            return text

        try:
            result = self._translate_with_provider(text, target_lang, source_lang)
            return result.translated_text

        except Exception as e:
            self.logger.error(f"Translation failed: {str(e)}")
            return text  # Return original text if translation fails

    def translate_batch(
        self, texts: List[str], target_lang: str = "en", source_lang: str = "auto"
    ) -> List[str]:
        """
        Translate multiple texts

        Args:
            texts (List[str]): List of texts to translate
            target_lang (str): Target language code
            source_lang (str): Source language code

        Returns:
            List[str]: List of translated texts
        """
        translated_texts = []

        for text in texts:
            translated = self.translate(text, target_lang, source_lang)
            translated_texts.append(translated)

            # Rate limiting
            if self.rate_limit_delay > 0:
                time.sleep(self.rate_limit_delay)

        return translated_texts

    def detect_language(self, text: str) -> str:
        """
        Detect language of text

        Args:
            text (str): Text to analyze

        Returns:
            str: Detected language code
        """
        if not text or not text.strip():
            return "unknown"

        # Check for common Indian and other languages first
        for lang_code, pattern in self.language_patterns.items():
            if re.search(pattern, text):
                return lang_code

        # If no non-Latin script detected, check if it's English or other Latin-based language
        # If text contains mostly Latin characters, it's likely English or similar language
        if self._is_latin_script(text):
            return "en"  # Default to English for Latin script content

        return "unknown"

    def is_non_english(self, text: str) -> bool:
        """
        Check if text contains non-English characters

        Args:
            text (str): Text to check

        Returns:
            bool: True if text contains non-English characters
        """
        if not text:
            return False

        # Check for non-Latin scripts
        for pattern in self.language_patterns.values():
            if re.search(pattern, text):
                return True

        return False

    def _translate_with_provider(
        self, text: str, target_lang: str, source_lang: str
    ) -> TranslationResult:
        """
        Translate using the configured provider

        Args:
            text (str): Text to translate
            target_lang (str): Target language
            source_lang (str): Source language

        Returns:
            TranslationResult: Translation result
        """
        for attempt in range(self.max_retries):
            try:
                if self.provider == TranslationProvider.GOOGLE_FREE:
                    return self._translate_google_free(text, target_lang, source_lang)
                elif self.provider == TranslationProvider.GOOGLE_PAID:
                    return self._translate_google_paid(text, target_lang, source_lang)
                elif self.provider == TranslationProvider.MICROSOFT:
                    return self._translate_microsoft(text, target_lang, source_lang)
                elif self.provider == TranslationProvider.DEEPL:
                    return self._translate_deepl(text, target_lang, source_lang)
                else:
                    raise TranslationError(f"Unsupported provider: {self.provider}")

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise TranslationError(
                        f"Translation failed after {self.max_retries} attempts: {str(e)}"
                    )

                self.logger.warning(
                    f"Translation attempt {attempt + 1} failed: {str(e)}"
                )
                time.sleep(2**attempt)  # Exponential backoff

    def _translate_google_free(
        self, text: str, target_lang: str, source_lang: str
    ) -> TranslationResult:
        """
        Translate using Google Translate free API

        Args:
            text (str): Text to translate
            target_lang (str): Target language
            source_lang (str): Source language

        Returns:
            TranslationResult: Translation result
        """
        try:
            # Try different endpoints for better reliability
            endpoints = [
                "https://translate.googleapis.com/translate_a/single",
                "https://translate.google.com/translate_a/single",
            ]

            for base_url in endpoints:
                try:
                    params = {
                        "client": "gtx",
                        "sl": source_lang,
                        "tl": target_lang,
                        "dt": "t",
                        "q": text[:5000],  # Limit text length
                    }

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }

                    response = requests.get(
                        base_url, params=params, headers=headers, timeout=15
                    )
                    response.raise_for_status()

                    result = response.json()

                    # Extract translated text
                    if result and len(result) > 0 and result[0]:
                        translated_text = "".join(
                            [
                                sentence[0]
                                for sentence in result[0]
                                if sentence and sentence[0]
                            ]
                        )

                        # Extract detected source language
                        detected_lang = (
                            result[2] if len(result) > 2 and result[2] else source_lang
                        )

                        return TranslationResult(
                            original_text=text,
                            translated_text=translated_text,
                            source_language=detected_lang,
                            target_language=target_lang,
                            confidence=0.8,
                            provider="google_free",
                        )
                except Exception as endpoint_error:
                    self.logger.debug(f"Endpoint {base_url} failed: {endpoint_error}")
                    continue

            # If all endpoints failed
            raise TranslationError("All Google Free API endpoints failed")

        except Exception as e:
            raise TranslationError(f"Google Free API translation failed: {str(e)}")

    def _translate_google_paid(
        self, text: str, target_lang: str, source_lang: str
    ) -> TranslationResult:
        """
        Translate using Google Cloud Translation API

        Args:
            text (str): Text to translate
            target_lang (str): Target language
            source_lang (str): Source language

        Returns:
            TranslationResult: Translation result
        """
        if not self.api_key:
            raise TranslationError(
                "Google Cloud API key is required for paid translation"
            )

        try:
            url = f"https://translation.googleapis.com/language/translate/v2?key={self.api_key}"

            data = {"q": text, "target": target_lang, "format": "text"}

            if source_lang != "auto":
                data["source"] = source_lang

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            result = response.json()

            if "data" in result and "translations" in result["data"]:
                translation = result["data"]["translations"][0]

                return TranslationResult(
                    original_text=text,
                    translated_text=translation["translatedText"],
                    source_language=translation.get(
                        "detectedSourceLanguage", source_lang
                    ),
                    target_language=target_lang,
                    confidence=1.0,  # High confidence for paid API
                    provider="google_paid",
                )
            else:
                raise TranslationError("Invalid response from Google Cloud API")

        except Exception as e:
            raise TranslationError(f"Google Cloud API translation failed: {str(e)}")

    def _translate_microsoft(
        self, text: str, target_lang: str, source_lang: str
    ) -> TranslationResult:
        """
        Translate using Microsoft Translator API

        Args:
            text (str): Text to translate
            target_lang (str): Target language
            source_lang (str): Source language

        Returns:
            TranslationResult: Translation result
        """
        if not self.api_key:
            raise TranslationError("Microsoft Translator API key is required")

        try:
            url = "https://api.cognitive.microsofttranslator.com/translate"

            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/json",
            }

            params = {"api-version": "3.0", "to": target_lang}

            if source_lang != "auto":
                params["from"] = source_lang

            body = [{"text": text}]

            response = requests.post(
                url, headers=headers, params=params, json=body, timeout=10
            )
            response.raise_for_status()

            result = response.json()

            if result and len(result) > 0:
                translation = result[0]

                return TranslationResult(
                    original_text=text,
                    translated_text=translation["translations"][0]["text"],
                    source_language=translation.get("detectedLanguage", {}).get(
                        "language", source_lang
                    ),
                    target_language=target_lang,
                    confidence=translation.get("detectedLanguage", {}).get(
                        "score", 0.9
                    ),
                    provider="microsoft",
                )
            else:
                raise TranslationError("Invalid response from Microsoft Translator API")

        except Exception as e:
            raise TranslationError(f"Microsoft Translator API failed: {str(e)}")

    def _translate_deepl(
        self, text: str, target_lang: str, source_lang: str
    ) -> TranslationResult:
        """
        Translate using DeepL API

        Args:
            text (str): Text to translate
            target_lang (str): Target language
            source_lang (str): Source language

        Returns:
            TranslationResult: Translation result
        """
        if not self.api_key:
            raise TranslationError("DeepL API key is required")

        try:
            url = "https://api-free.deepl.com/v2/translate"

            data = {
                "auth_key": self.api_key,
                "text": text,
                "target_lang": target_lang.upper(),
            }

            if source_lang != "auto":
                data["source_lang"] = source_lang.upper()

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            result = response.json()

            if "translations" in result and len(result["translations"]) > 0:
                translation = result["translations"][0]

                return TranslationResult(
                    original_text=text,
                    translated_text=translation["text"],
                    source_language=translation.get(
                        "detected_source_language", source_lang
                    ),
                    target_language=target_lang,
                    confidence=0.95,  # High confidence for DeepL
                    provider="deepl",
                )
            else:
                raise TranslationError("Invalid response from DeepL API")

        except Exception as e:
            raise TranslationError(f"DeepL API translation failed: {str(e)}")

    def _is_latin_script(self, text: str) -> bool:
        """
        Check if text primarily uses Latin script (English, Spanish, French, etc.)

        Args:
            text (str): Text to check

        Returns:
            bool: True if text uses primarily Latin script
        """
        if not text:
            return False

        # Remove punctuation and spaces for analysis
        cleaned_text = re.sub(r"[^\w]", "", text)
        if not cleaned_text:
            return False

        # Count Latin characters (basic Latin + Latin-1 supplement)
        latin_chars = sum(
            1 for char in cleaned_text if ord(char) < 592
        )  # Covers most Latin scripts
        total_chars = len(cleaned_text)

        # If more than 80% of characters are Latin script, consider it Latin-based
        return (latin_chars / total_chars) > 0.8 if total_chars > 0 else False

    def _is_likely_english(self, text: str) -> bool:
        """
        Check if text is likely English based on common patterns

        Args:
            text (str): Text to check

        Returns:
            bool: True if text is likely English
        """
        if not text:
            return False

        # Check for common English words
        common_english_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "this",
            "that",
            "these",
            "those",
        }

        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return False

        english_word_count = sum(1 for word in words if word in common_english_words)

        # If more than 20% of words are common English words, likely English
        return english_word_count / len(words) > 0.2

    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get supported languages for translation

        Returns:
            Dict[str, str]: Dictionary mapping language codes to language names
        """
        return {
            "en": "English",
            "hi": "Hindi",
            "bn": "Bengali",
            "te": "Telugu",
            "mr": "Marathi",
            "ta": "Tamil",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "or": "Oriya",
            "as": "Assamese",
            "ur": "Urdu",
            "ar": "Arabic",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ru": "Russian",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "nl": "Dutch",
            "pl": "Polish",
            "th": "Thai",
        }
