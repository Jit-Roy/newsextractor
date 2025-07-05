"""
Setup script for NewsExtractor
"""

from setuptools import setup, find_packages
import os

# Read the README file
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Professional news extraction library with AI-powered analysis"

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
try:
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = ["requests>=2.28.0", "beautifulsoup4>=4.11.0", "lxml>=4.9.0"]

setup(
    name="newsextractor",
    version="1.0.0",
    author="Jit Roy",
    author_email="your.email@example.com",
    description="Simple yet powerful news extraction library with AI summarization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jit-Roy/newsextractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "ai": ["spacy>=3.4.0"],  # For AI-powered summarization
        "async": ["aiohttp>=3.8.0", "aiofiles>=0.8.0"],
    },
    keywords="news extraction scraping nlp translation trending rss",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/newsextractor/issues",
        "Source": "https://github.com/yourusername/newsextractor",
        "Documentation": "https://newsextractor.readthedocs.io/",
    },
)
