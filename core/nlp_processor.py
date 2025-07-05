"""
NLP Processor Module
===================

Comprehensive NLP processing for extracted articles including:
- Keyword extraction (RAKE, spaCy)
- Summarization (extractive and abstractive)
- Language detection (langdetect, langid)
- Named Entity Recognition (spaCy)
- Sentiment analysis (TextBlob, VADER)
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Core NLP libraries
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

# Keyword extraction
try:
    from rake_nltk import Rake
    RAKE_AVAILABLE = True
except ImportError:
    RAKE_AVAILABLE = False

# Language detection
try:
    import langdetect
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import langid
    LANGID_AVAILABLE = True
except ImportError:
    LANGID_AVAILABLE = False

# Summarization
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.text_rank import TextRankSummarizer
    from sumy.summarizers.lex_rank import LexRankSummarizer
    from sumy.summarizers.luhn import LuhnSummarizer
    SUMY_AVAILABLE = True
except ImportError:
    SUMY_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class NLPResults:
    """Comprehensive NLP analysis results"""
    entities: Dict[str, List[str]]
    sentiment: Dict[str, Any]
    language: str
    language_confidence: float
    summary: str
    summary_method: str
    readability_score: Optional[float] = None


class NLPProcessor:
    """
    Comprehensive NLP processor with multiple analysis capabilities
    """
    
    def __init__(self, 
                 spacy_model: str = 'en_core_web_sm',
                 enable_transformers: bool = False,
                 summarization_method: str = 'auto'):
        """
        Initialize the NLP processor
        
        Args:
            spacy_model (str): spaCy model to use for NER and processing
            enable_transformers (bool): Whether to use transformer models (requires GPU/high memory)
            summarization_method (str): Preferred summarization method ('auto', 'sumy', 'transformers')
        """
        self.logger = logging.getLogger(__name__)
        self.enable_transformers = enable_transformers
        self.summarization_method = summarization_method
        
        # Initialize spaCy model
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(spacy_model)
                self.logger.debug(f"Loaded spaCy model: {spacy_model}")
            except OSError:
                self.logger.warning(f"spaCy model {spacy_model} not found. NER and advanced features disabled.")
        
        # Initialize sentiment analyzers
        self.vader_analyzer = None
        if VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize RAKE for keyword extraction
        self.rake = None
        if RAKE_AVAILABLE:
            self.rake = Rake()
        
        # Initialize transformer models (lazy loading)
        self.summarizer = None
        self.sentiment_pipeline = None
        
        # Log available features
        self._log_available_features()
    
    def _log_available_features(self):
        """Log which NLP features are available"""
        features = []
        if SPACY_AVAILABLE and self.nlp:
            features.append("spaCy NER")
        if RAKE_AVAILABLE:
            features.append("RAKE keywords")
        if TEXTBLOB_AVAILABLE:
            features.append("TextBlob sentiment")
        if VADER_AVAILABLE:
            features.append("VADER sentiment")
        if LANGDETECT_AVAILABLE:
            features.append("langdetect")
        if LANGID_AVAILABLE:
            features.append("langid")
        if SUMY_AVAILABLE:
            features.append("Sumy summarization")
        if TRANSFORMERS_AVAILABLE:
            features.append("Transformers")
        
        if features:
            self.logger.debug(f"NLP features available: {', '.join(features)}")
        else:
            self.logger.warning("No advanced NLP features available")
    
    def process_article(self, title: str, content: str) -> NLPResults:
        """
        Perform comprehensive NLP analysis on article
        
        Args:
            title (str): Article title
            content (str): Article content
            
        Returns:
            NLPResults: Comprehensive analysis results
        """
        text = f"{title}. {content}" if title else content
        
        # Language detection
        language, lang_confidence = self._detect_language(text)
        
        # Named Entity Recognition
        entities = self._extract_entities(text)
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(text)
        
        # Summarization
        summary, summary_method = self._generate_summary(content, language)
        
        return NLPResults(
            entities=entities,
            sentiment=sentiment,
            language=language,
            language_confidence=lang_confidence,
            summary=summary,
            summary_method=summary_method
        )
    
    def _detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language using multiple methods
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Tuple[str, float]: Language code and confidence
        """
        if not text or len(text.strip()) < 10:
            return 'unknown', 0.0
        
        # Method 1: langdetect (more accurate)
        if LANGDETECT_AVAILABLE:
            try:
                detected_langs = detect_langs(text[:1000])  # Use first 1000 chars
                if detected_langs:
                    top_lang = detected_langs[0]
                    return top_lang.lang, top_lang.prob
            except Exception as e:
                self.logger.debug(f"langdetect failed: {e}")
        
        # Method 2: langid (fallback)
        if LANGID_AVAILABLE:
            try:
                lang, confidence = langid.classify(text[:1000])
                return lang, confidence
            except Exception as e:
                self.logger.debug(f"langid failed: {e}")
        
        return 'unknown', 0.0
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using spaCy
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, List[str]]: Entities grouped by type
        """
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],  # Geopolitical entities
            'MONEY': [],
            'DATE': [],
            'EVENT': [],
            'PRODUCT': []
        }
        
        if not SPACY_AVAILABLE or not self.nlp:
            return entities
        
        try:
            doc = self.nlp(text[:5000])  # Limit for performance
            
            for ent in doc.ents:
                entity_type = ent.label_
                entity_text = ent.text.strip()
                
                if entity_type in entities and entity_text:
                    # Avoid duplicates
                    if entity_text not in entities[entity_type]:
                        entities[entity_type].append(entity_text)
            
            # Limit entities per type
            for entity_type in entities:
                entities[entity_type] = entities[entity_type][:5]
                
        except Exception as e:
            self.logger.debug(f"Entity extraction failed: {e}")
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using multiple methods
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, Any]: Sentiment analysis results
        """
        sentiment = {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 0.0,
            'polarity': 0.0,
            'subjectivity': 0.0,
            'label': 'neutral'
        }
        
        # Method 1: VADER sentiment
        if VADER_AVAILABLE and self.vader_analyzer:
            try:
                vader_scores = self.vader_analyzer.polarity_scores(text[:2000])
                sentiment.update({
                    'compound': vader_scores['compound'],
                    'positive': vader_scores['pos'],
                    'negative': vader_scores['neg'],
                    'neutral': vader_scores['neu']
                })
            except Exception as e:
                self.logger.debug(f"VADER sentiment analysis failed: {e}")
        
        # Method 2: TextBlob sentiment
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text[:2000])
                sentiment.update({
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                })
            except Exception as e:
                self.logger.debug(f"TextBlob sentiment analysis failed: {e}")
        
        # Determine overall sentiment label
        if sentiment['compound'] >= 0.05:
            sentiment['label'] = 'positive'
        elif sentiment['compound'] <= -0.05:
            sentiment['label'] = 'negative'
        else:
            sentiment['label'] = 'neutral'
        
        return sentiment
    
    def _generate_summary(self, text: str, language: str = 'en') -> Tuple[str, str]:
        """
        Generate summary using multiple methods
        
        Args:
            text (str): Text to summarize
            language (str): Language of the text
            
        Returns:
            Tuple[str, str]: Summary and method used
        """
        if not text or len(text.strip()) < 200:
            return "", "none"
        
        # Try different summarization methods
        if self.summarization_method == 'auto':
            methods = ['sumy', 'transformers', 'simple']
        elif self.summarization_method == 'sumy':
            methods = ['sumy', 'simple']
        elif self.summarization_method == 'transformers':
            methods = ['transformers', 'sumy', 'simple']
        else:
            methods = ['simple']
        
        for method in methods:
            try:
                if method == 'sumy':
                    summary = self._summarize_with_sumy(text, language)
                    if summary:
                        return summary, 'sumy'
                elif method == 'transformers':
                    summary = self._summarize_with_transformers(text)
                    if summary:
                        return summary, 'transformers'
                elif method == 'simple':
                    summary = self._summarize_simple(text)
                    if summary:
                        return summary, 'simple'
            except Exception as e:
                self.logger.debug(f"Summarization method {method} failed: {e}")
                continue
        
        return "", "failed"
    
    def _summarize_with_sumy(self, text: str, language: str = 'en') -> str:
        """Summarize using Sumy library"""
        if not SUMY_AVAILABLE:
            return ""
        
        try:
            # Try different summarizers
            summarizers = [
                TextRankSummarizer(),
                LexRankSummarizer(),
                LuhnSummarizer()
            ]
            
            parser = PlaintextParser.from_string(text, Tokenizer(language))
            
            for summarizer in summarizers:
                try:
                    sentences = summarizer(parser.document, 3)  # 3 sentences
                    summary = ' '.join([str(sentence) for sentence in sentences])
                    if summary and len(summary) > 50:
                        return summary
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Sumy summarization failed: {e}")
        
        return ""
    
    def _summarize_with_transformers(self, text: str) -> str:
        """Summarize using transformer models"""
        if not TRANSFORMERS_AVAILABLE or not self.enable_transformers:
            return ""
        
        try:
            # Lazy load summarizer
            if not self.summarizer:
                self.summarizer = pipeline("summarization", 
                                         model="facebook/bart-large-cnn",
                                         device=-1)  # CPU
            
            # Limit text length for transformer
            max_length = min(1024, len(text))
            truncated_text = text[:max_length]
            
            summary = self.summarizer(truncated_text, 
                                    max_length=150, 
                                    min_length=50, 
                                    do_sample=False)
            
            return summary[0]['summary_text'] if summary else ""
            
        except Exception as e:
            self.logger.debug(f"Transformer summarization failed: {e}")
            return ""
    
    def _summarize_simple(self, text: str) -> str:
        """Simple extractive summarization"""
        sentences = text.split('.')
        
        # Filter meaningful sentences
        meaningful_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and not sentence.lower().startswith(('click', 'read more', 'subscribe')):
                meaningful_sentences.append(sentence)
        
        # Return first 2-3 sentences as summary
        if meaningful_sentences:
            summary_sentences = meaningful_sentences[:3]
            return '. '.join(summary_sentences) + '.'
        
        return ""
