# 🚀 NewsExtractor - Quick Start Guide

> **Professional news article extraction with advanced NLP processing**

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Jit-Roy/newsextractor.git
cd newsextractor

# Install dependencies
pip install -r requirements.txt

# Install optional NLP dependencies for advanced features
pip install spacy textblob vaderSentiment rake-nltk langdetect sumy
python -m spacy download en_core_web_sm
python -m textblob.download_corpora
```

## ⚡ Quick Start

### 1. Basic Article Extraction

```python
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.news_extractor import NewsExtractor

# Create extractor
extractor = NewsExtractor()

# Extract article from URL
article = extractor.extract_from_url("https://techcrunch.com/2024/01/15/ai-news")

print(f"Title: {article.title}")
print(f"Author: {article.author}")
print(f"Content: {article.content[:200]}...")
print(f"Word Count: {article.word_count}")
print(f"Reading Time: {article.read_time} minutes")
```

### 2. Advanced NLP Processing

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.news_extractor import NewsExtractor

# Enable NLP processing
extractor = NewsExtractor(enable_nlp=True)
article = extractor.extract_from_url("https://news-site.com/article")

# Access NLP results
print(f"🔑 Keywords: {article.keywords[:5]}")
print(f"😊 Sentiment: {article.sentiment['label']} ({article.sentiment['compound']:.2f})")
print(f"👤 Entities: {article.entities}")
print(f"📝 Summary: {article.nlp_summary}")
```

### 3. Simple Helper Functions

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import TextProcessor

# Quick keyword extraction
keywords = TextProcessor.extract_keywords("Your text content here", max_keywords=10)
print(f"Keywords: {keywords}")
```

## 🌟 Key Features

### ✅ **Core Features**
- **Smart Article Extraction** - Works with any news website
- **Metadata Extraction** - Title, author, date, source, images
- **Content Cleaning** - Removes ads, navigation, boilerplate
- **URL Validation** - Validates and normalizes URLs
- **Error Handling** - Comprehensive error handling and logging

### 🧠 **Advanced NLP Features**
- **Keyword Extraction** - RAKE + spaCy algorithms
- **Sentiment Analysis** - VADER + TextBlob
- **Language Detection** - langdetect with confidence scoring
- **Named Entity Recognition** - spaCy NER pipeline
- **Text Summarization** - Sumy + transformers + custom algorithms
- **Multi-language Support** - Process content in any language

### 🔧 **Professional Features**
- **Modular Architecture** - Clean, maintainable code structure
- **Performance Optimized** - Efficient parsing and processing
- **Concurrent Processing** - Extract multiple articles simultaneously
- **RSS Feed Support** - Extract from RSS/Atom feeds
- **Caching Support** - Built-in caching for better performance

## 📋 Configuration Options

### Basic Configuration

```python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.news_extractor import NewsExtractor

extractor = NewsExtractor(
    language='en',           # Target language for translation
    request_timeout=30,      # HTTP request timeout
    max_retries=3,          # Max retry attempts
    enable_nlp=True,        # Enable NLP processing
    enable_transformers=False  # Use transformer models (requires GPU)
)
```

### Advanced NLP Configuration

```python
from core.nlp_processor import NLPProcessor

nlp = NLPProcessor(
    spacy_model='en_core_web_sm',    # spaCy model
    enable_transformers=False,        # Transformer models
    summarization_method='auto'       # 'auto', 'sumy', 'transformers'
)

# Process text directly
results = nlp.process_article("Title", "Content...")
```

## 🛠️ Available Classes

### Main Classes
- **`NewsExtractor`** - Main extraction engine
- **`Article`** - Article data model with all metadata
- **`Translator`** - Translation services
- **`TrendingTopics`** - Trending news discovery

### Utility Classes
- **`URLValidator`** - URL validation and normalization
- **`TextProcessor`** - Text processing utilities
- **`ContentSelectors`** - Smart content selection

## 🎯 Common Use Cases

### Content Aggregation
```python
urls = ["https://site1.com/article", "https://site2.com/article"]
articles = []

for url in urls:
    try:
        article = extractor.extract_from_url(url)
        articles.append(article)
    except Exception as e:
        print(f"Failed to extract {url}: {e}")
```

### News Analysis Pipeline
```python
# Extract and analyze
article = extractor.extract_from_url(url)

if article.nlp_processed:
    # Categorize by sentiment
    if article.sentiment['label'] == 'positive':
        positive_articles.append(article)
    
    # Filter by keywords
    if any(keyword in article.keywords for keyword in ['AI', 'technology']):
        tech_articles.append(article)
```

### RSS Feed Processing
```python
from core.rss_parser import RSSParser
from core.http_client import HTTPClient

rss_parser = RSSParser(HTTPClient())
entries = rss_parser.parse_feed("https://feeds.techcrunch.com/TechCrunch/")

for entry in entries:
    article = extractor.extract_from_url(entry['url'])
    print(f"📰 {article.title}")
```

## 🔍 Testing Your Installation

```python
# Test basic functionality
python test_nlp_processing.py

# Or test manually
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.news_extractor import NewsExtractor

try:
    extractor = NewsExtractor(enable_nlp=True)
    article = extractor.extract_from_url("https://techcrunch.com")
    print("✅ NewsExtractor is working correctly!")
    print(f"📰 Title: {article.title}")
    print(f"🧠 NLP: {'✅ Enabled' if article.nlp_processed else '❌ Disabled'}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## ⚠️ Troubleshooting

### Common Issues

**1. ModuleNotFoundError for NLP libraries**
```bash
pip install spacy textblob vaderSentiment rake-nltk langdetect sumy
python -m spacy download en_core_web_sm
```

**2. SSL/Network errors**
```python
# Use custom headers
extractor = NewsExtractor(
    custom_headers={
        'User-Agent': 'Mozilla/5.0 (compatible; NewsExtractor/1.0)'
    }
)
```

**3. Rate limiting**
```python
import time

urls = ["url1", "url2", "url3"]
for url in urls:
    article = extractor.extract_from_url(url)
    time.sleep(1)  # Add delay between requests
```

## 📚 Next Steps

1. **Explore Advanced Features** - Try different NLP models and extraction methods
2. **Build Your Application** - Integrate into your news aggregation or analysis project
3. **Scale Up** - Use concurrent processing for large-scale extraction
4. **Customize** - Add domain-specific content selectors or custom NLP pipelines

---

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: See README.md for detailed documentation
- **Examples**: Check the examples in this guide

**🎉 Happy news extracting! 🎉**
