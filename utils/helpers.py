"""
Text Processing and AI Utilities
==============================

Advanced text processing with spaCy AI models for better extraction and summarization
"""

import hashlib
import time
import re
import string
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
import logging

# Import spaCy for advanced NLP features
try:
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    STOP_WORDS = set()

class TextProcessor:
    """Text processing utilities"""
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10, use_ai: bool = True) -> List[str]:
        """
        Extract important keywords from content using AI models
        
        Args:
            text (str): Text content
            max_keywords (int): Maximum number of keywords to extract
            use_ai (bool): Whether to use AI-based extraction
            
        Returns:
            List[str]: List of extracted keywords
        """
        if not text:
            return []
        
        if use_ai and SPACY_AVAILABLE:
            return TextProcessor._extract_ai_keywords(text, max_keywords)
        else:
            return TextProcessor._extract_simple_keywords(text, max_keywords)
    
    @staticmethod
    def _extract_ai_keywords(content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords using spaCy AI models"""
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(content[:5000])  # Limit content length for performance
            
            # Extract entities and important terms
            keywords = set()
            
            # Add named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'PRODUCT'] and len(ent.text) > 2:
                    keywords.add(ent.text.lower().strip())
            
            # Add important noun phrases
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.strip()
                if 2 <= len(chunk_text.split()) <= 3:  # Keep phrases short but meaningful
                    keywords.add(chunk_text.lower())
            
            # Add important single words
            word_scores = {}
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                    not token.is_stop and 
                    not token.is_punct and 
                    len(token.lemma_) > 2):
                    
                    # Score based on TF-IDF-like approach
                    score = 1.0
                    if token.pos_ == 'PROPN':  # Proper nouns are more important
                        score *= 2.0
                    if token.ent_type_:  # Entities are important
                        score *= 1.5
                    
                    word_scores[token.lemma_.lower()] = score
            
            # Combine and sort
            all_keywords = list(keywords) + list(word_scores.keys())
            keyword_scores = {kw: word_scores.get(kw, 1.0) for kw in all_keywords if kw.strip()}
            
            sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
            return [kw for kw, score in sorted_keywords[:max_keywords]]
            
        except Exception as e:
            logging.warning(f"AI keyword extraction failed: {e}. Falling back to simple method.")
            return TextProcessor._extract_simple_keywords(content, max_keywords)
    
    @staticmethod
    def _extract_simple_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords using simple frequency analysis (fallback method)"""
        # Simple keyword extraction (can be improved with NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know',
            'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
            'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over',
            'such', 'take', 'than', 'them', 'well', 'were', 'what', 'your'
        }
        
        # Filter and count words
        word_count = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_count[word] = word_count.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:max_keywords]]
    
    @staticmethod
    def generate_summary(content: str, max_sentences: int = 3, use_ai: bool = True) -> str:
        """
        Generate an intelligent summary from content using spaCy AI models
        
        Args:
            content (str): Text content to summarize
            max_sentences (int): Maximum number of sentences in summary
            use_ai (bool): Whether to use AI-based summarization
            
        Returns:
            str: Generated summary
        """
        if not content:
            return ""
        
        if use_ai and SPACY_AVAILABLE:
            return TextProcessor._generate_ai_summary(content, max_sentences)
        else:
            return TextProcessor._generate_simple_summary(content, max_sentences)
    
    @staticmethod
    def _generate_ai_summary(content: str, max_sentences: int = 3) -> str:
        """Generate AI-powered summary using spaCy"""
        try:
            # Load spaCy model
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(content)
            
            # Extract sentences and score them
            sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
            if not sentences:
                return ""
            
            # Score sentences based on keyword frequency, position, and length
            sentence_scores = {}
            word_frequencies = TextProcessor._calculate_word_frequencies(doc)
            
            for i, sentence in enumerate(sentences):
                sent_doc = nlp(sentence)
                score = 0
                word_count = 0
                
                # Score based on important words
                for token in sent_doc:
                    if not token.is_stop and not token.is_punct and token.lemma_ in word_frequencies:
                        score += word_frequencies[token.lemma_]
                        word_count += 1
                
                # Normalize by word count
                if word_count > 0:
                    score = score / word_count
                
                # Boost score for early sentences (position importance)
                position_factor = 1.0 - (i / len(sentences)) * 0.3
                score *= position_factor
                
                # Penalize very short or very long sentences
                length_factor = min(1.0, len(sentence.split()) / 20)
                score *= length_factor
                
                sentence_scores[sentence] = score
            
            # Select top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            summary_sentences = [sent[0] for sent in top_sentences[:max_sentences]]
            
            # Maintain original order
            ordered_summary = []
            for sentence in sentences:
                if sentence in summary_sentences:
                    ordered_summary.append(sentence)
            
            return ' '.join(ordered_summary)
            
        except Exception as e:
            logging.warning(f"AI summarization failed: {e}. Falling back to simple method.")
            return TextProcessor._generate_simple_summary(content, max_sentences)
    
    @staticmethod
    def _generate_simple_summary(content: str, max_sentences: int = 3) -> str:
        """Generate a simple summary from content (fallback method)"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return ""
        
        # Take first few sentences as summary
        summary_sentences = sentences[:max_sentences]
        return '. '.join(summary_sentences) + '.'
    
    @staticmethod
    def _calculate_word_frequencies(doc) -> Dict[str, float]:
        """Calculate word frequencies for AI summarization"""
        word_freq = {}
        for token in doc:
            if not token.is_stop and not token.is_punct and len(token.lemma_) > 2:
                word_freq[token.lemma_] = word_freq.get(token.lemma_, 0) + 1
        
        # Normalize frequencies
        max_freq = max(word_freq.values()) if word_freq else 1
        for word in word_freq:
            word_freq[word] = word_freq[word] / max_freq
            
        return word_freq