# 🗞️ NewsExtractor

> **News article extraction library with AI-powered analysis**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

NewsExtractor is a comprehensive Python library for extracting, processing, and analyzing news articles from any website with advanced NLP capabilities.

## ✨ Features

- 🚀 **Smart Article Extraction** - Extract clean content from any news website
- 🧠 **AI-Powered Analysis** - Sentiment analysis, keyword extraction, and summarization
- 🌍 **Multi-language Support** - Detect language and translate content
- 📰 **RSS Feed Processing** - Extract articles from RSS/Atom feeds
- 🔍 **Trending News Search** - Search and discover trending news topics
- 📊 **Rich Metadata** - Extract publication dates, authors, images, and more

## 🚀 Quick Start

### Installation

```bash
!git clone https://github.com/Jit-Roy/newsextractor.git
%cd newsextractor
!pip install -r requirements.txt
```

### Basic Article Extraction

```python
from newsextractor import NewsExtractor

# Create extractor
extractor = NewsExtractor(enable_nlp=True)

# Extract article
article = extractor.extract_from_url("https://techcrunch.com/2025/07/04/ready-made-stem-cell-therapies-for-pets-could-be-coming/")

print("📰 CORE ARTICLE DATA:")
print(f"  Article ID: {article.article_id}")
print(f"  Title: {article.title}")
print(f"  Author: {article.author}")
print(f"  URL: {article.url}")
print(f"  Published Date: {article.published_date}")
print(f"  Word Count: {article.word_count}")
print(f"  Reading Time: {article.read_time} minutes")
print(f"  Top Image: {article.top_image}")

print(f"\n🔍 CATEGORIZATION (Reliable):")
print(f"  Source: {article.source}")
print(f"\n👥 NAMED ENTITIES FOUND:")
for entity_type, entities in article.entities.items():
    if entities: 
        print(f"  {entity_type}: {', '.join(entities)}")

print(f"\n🧠 ANALYSIS (AI-Powered):")
print(f"  Language: {article.language}")
print(f"  Sentiment: {article.sentiment}")
print(f"  Summary: {article.nlp_summary}")

print(f"\n📊 ADDITIONAL METADATA:")
print(f"  Publication Name: {article.publication_name}")
print(f"  Meta Description: {article.meta_description}")
print(f"  Canonical Link: {article.canonical_link}")
print(f"  Image URLs: {len(article.image_urls)} images")
print(f"  Video URLs: {len(article.video_urls)} videos")
print(f"  Links: {len(article.links)} external links")
print(f"  Is Paywalled: {article.is_paywalled}")
```
### Advanced NLP Processing

```python
from newsextractor import NewsExtractor

# Enable NLP processing and set the summarization method
# Options are: 'auto', 'sumy', 'transformers', 'simple'

extractor = NewsExtractor(enable_nlp=True, summarization_method='simple')
article = extractor.extract_from_url("https://techcrunch.com/2025/07/04/ready-made-stem-cell-therapies-for-pets-could-be-coming")

# Access NLP results (reliable metadata only)
print(f"😊 Sentiment: {article.sentiment['label']} ({article.sentiment['compound']:.2f})")
print(f"👤 Named Entities by Type:")
for entity_type, entities in article.entities.items():
    if entities:  
        print(f"   {entity_type}: {', '.join(entities)}")
print(f"📝 Summary: {article.nlp_summary}")
print(f"🌐 Language: {article.language}")
```
### Langugage Specific Processing

```python
from newsextractor import NewsExtractor

# Create extractor with Bengali language setting
extractor_bengali = NewsExtractor(
    enable_nlp=True, 
    language='bn',  # Bengali language code
    summarization_method='simple'
)

# Extract article from URL with Bengali language processing
test_article = extractor_bengali.extract_from_url("https://techcrunch.com/2025/07/04/ready-made-stem-cell-therapies-for-pets-could-be-coming/")

print("🇧🇩 BENGALI LANGUAGE PROCESSING:")
print(f"Target Language Setting: bn (Bengali)")

print("\n📰 CORE ARTICLE DATA:")
print(f"  Article ID: {test_article.article_id}")
print(f"  Title: {test_article.title}")
print(f"  Author: {test_article.author}")
print(f"  URL: {test_article.url}")
print(f"  Published Date: {test_article.published_date}")
print(f"  Word Count: {test_article.word_count}")
print(f"  Reading Time: {test_article.read_time} minutes")
print(f"  Top Image: {test_article.top_image}")

print(f"\n🔍 CATEGORIZATION (Reliable):")
print(f"  Source: {test_article.source}")
print(f"\n👥 NAMED ENTITIES FOUND:")
for entity_type, entities in test_article.entities.items():
    if entities: 
        print(f"  {entity_type}: {', '.join(entities)}")

print(f"\n🧠 ANALYSIS (AI-Powered):")
print(f"  Detected Language: {test_article.language}")
print(f"  Translation Status: {'Translated' if test_article.translated else 'Original'}")
print(f"  Sentiment: {test_article.sentiment}")
print(f"  Summary: {test_article.nlp_summary}")

print(f"\n📊 ADDITIONAL METADATA:")
print(f"  Publication Name: {test_article.publication_name}")
print(f"  Meta Description: {test_article.meta_description}")
print(f"  Canonical Link: {test_article.canonical_link}")
print(f"  Image URLs: {len(test_article.image_urls)} images")
print(f"  Video URLs: {len(test_article.video_urls)} videos")
print(f"  Links: {len(test_article.links)} external links")
print(f"  Is Paywalled: {test_article.is_paywalled}")
```

### Extracting From RSS Feed

```python
from newsextractor import NewsExtractor

extractor = NewsExtractor()
articles = extractor.extract_from_rss_feed("https://techcrunch.com/feed/")

# Extract full content for each article from RSS
for article in articles[:2]:
    full_article = extractor.extract_from_url(article.url)
    print(f"📰 {full_article.title}")
    print(f"👥 Entities: {full_article.entities}")
    print(f"📝 Summary: {full_article.nlp_summary}")
    print("-" * 50)
```

### Getting Trending News
```python
import os
from newsextractor import NewsSearcher

# Get API key from environment variable
SERPAPI_KEY = os.getenv('SERPAPI_KEY', 'your-serpapi-key-here')

if SERPAPI_KEY == 'your-serpapi-key-here':
    print("⚠️  Please set your SERPAPI_KEY environment variable")
    print("   Example: set SERPAPI_KEY=your-actual-api-key")
    print("   Or create a .env file with SERPAPI_KEY=your-actual-api-key")
else:
    searcher = NewsSearcher(serpapi_key=SERPAPI_KEY)
    trending_articles = searcher.get_trending_news(limit=5)

    for article in trending_articles:
        print(f"🔥 {article.title}")
```

### Search For A Specific News
```python
import os
from newsextractor import NewsSearcher

# Initialize the searcher with your SerpAPI key from environment
SERPAPI_KEY = os.getenv('SERPAPI_KEY', 'your-serpapi-key-here')

if SERPAPI_KEY == 'your-serpapi-key-here':
    print("⚠️  Please set your SERPAPI_KEY environment variable")
    print("   Example: set SERPAPI_KEY=your-actual-api-key")
    print("   Or create a .env file with SERPAPI_KEY=your-actual-api-key")
else:
    searcher = NewsSearcher(serpapi_key=SERPAPI_KEY)
    articles = searcher.search_news_by_keyword("World War 3", limit=3)

    for i, article in enumerate(articles, 1):
        print(f"\n{i}. 📰 {article.title}")
        print(f"   🌐 Source: {article.source}")
        print(f"   📅 Published: {article.published_date}")
        print(f"   🔗 URL: {article.url}")
        
        # Show entities if available
        if article.entities:
            entity_summary = []
            for entity_type, entities in article.entities.items():
                if entities:
                    entity_summary.append(f"{entity_type}: {len(entities)}")
            if entity_summary:
                print(f"   👥 Entities: {', '.join(entity_summary)}")
        
        # Show sentiment if available
        if article.sentiment:
            sentiment_label = article.sentiment.get('label', 'N/A')
            print(f"   😊 Sentiment: {sentiment_label}")
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Jit-Roy/newsextractor.git
cd newsextractor

# Run tests
pytest

# Format code
black .
```

### Project Structure

```
newsextractor/
├── core/                 # Core extraction modules
├── models/              # Data models
├── utils/               # Utility functions
├── tests/               # Test suite
└── requirements.txt     # Dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- 📧 Email: royjit0506@gmail.com