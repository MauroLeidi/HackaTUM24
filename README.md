# HackaTUM24 - EV News Platform

## Overview

HackaTUM24 is a solution for the Hubert Burda's challenge, creating an intelligent news platform focused on electric vehicles (EVs). The platform automatically collects, filters, and presents high-quality EV-related news content using advanced AI technologies.

## Features

- 🤖 **Advanced News Collection**
  - Automated scraping from Bing News API and RSS feeds
  - Smart parsing of .rst files
  - Multi-source content aggregation

- 🔍 **Intelligent Content Processing**
  - Two-stage content filtering system
  - Quality scoring based on Google's helpful content guidelines
  - LLM-based evaluation across six quality metrics
  - Customized greedy KNN clustering for article grouping

- 📊 **Content Generation & Optimization**
  - AI-powered article generation from clustered content
  - TextGrad-based prompt optimization
  - Automated image search and selection via Bing API
  - Markdown-formatted content creation

- 🎙️ **Multi-Modal Content Production**
  - Automatic podcast generation using Play.ai
  - Video reel creation with Creatomate.com
  - Integrated image-text-audio content pipeline

- 📱 **Modern Web Interface**
  - React-based frontend
  - Responsive design
  - Integrated audio player
  - Video reel viewer
  - Article rating system

## Architecture

The system is built with three main layers:

### 1. Content Collection Layer
- **News Collector Module**
  - Newspaper3k for article scraping
  - Bing Search API integration
  - RSS feed parser
  - Initial content validation
  - Cookie/paywall handling

### 2. Processing & Analysis Layer
- **Content Filtering System**
  - Primary quality filter
  - OpenAI-powered content scoring
  - Secondary standards-based filtering

- **Content Organization**
  - Text summarization pipeline
  - Embedding generation
  - Custom greedy KNN clustering
  - Group optimization for content diversity

### 3. Generation & Distribution Layer
- **Article Generation**
  - Reinforcement learning-based prompt optimization
  - Automated image selection
  - Markdown content formatting
  - Quality assurance checks

- **Multi-Modal Content**
  - Play.ai integration for podcast creation
  - Creatomate.com integration for video reels
  - Content synchronization across formats

- **Frontend Interface**
  - React components for content display
  - Audio/video playback integration
  - User feedback collection system
  - Responsive design implementation

Each layer is designed to work independently while maintaining seamless integration with the others, allowing for easy scaling and maintenance of individual components.

The system uses several AI services and APIs:
- OpenAI for content generation and evaluation
- Bing Search API for news and image collection
- Play.ai for audio conversion
- Creatomate for video reel generation
- TextGrad for prompt optimization

Future enhancements planned:
- Integration of user feedback into the reinforcement learning loop
- Scaling improvements for larger content volumes
- Enhanced trend detection in the EV sector
- Expanded multi-modal content capabilities


## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js "^18.18.0 || ^19.8.0 || >= 20.0.0"
- Conda (recommended for environment management)

### Setting Up the Environment

1. **API Keys Configuration**
```bash
# Copy the example environment file
cp .env-example .env
# Edit .env with your API keys
```

2. **Python Environment Setup**
```bash
# Create and activate conda environment
conda create -n hackatum python=3.11
conda activate hackatum

# Install dependencies
pip install -r pip_requirements.txt
```

## Running the Application

### Backend Setup

1. **Collect News Data**
```bash
python news_collector/news_aggregator.py
```

2. **Score and Filter Articles**
```bash
python feed_filtering/filter_feed.py
```

3. **Run KNN Clustering**
```bash
python knn_clustering/knn_clustering.py
```

4. **Start the API Server**
```bash
python api.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Project Structure

```
└── ./
    ├── frontend/              # React frontend application
    │   └── pages/            # Page components
    ├── news_collector/       # News collection modules
    ├── summary_and_feedback_generation/  # Content processing
    ├── api.py               # FastAPI backend server
    ├── schemas.py           # Data models
    └── utils.py             # Utility functions
```

## API Endpoints

- `/next-article/` - Fetch the next article in the queue
- `/generate-article/` - Generate a new article from existing content
- `/find-image/` - Find relevant images for articles
- `/generate-full-article/` - Create complete articles with images