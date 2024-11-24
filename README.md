# HackaTUM24 - EV News Platform

## Overview

HackaTUM24 is a solution for the Hubert Burda's challenge, creating an intelligent news platform focused on electric vehicles (EVs). The platform automatically collects, filters, and presents high-quality EV-related news content using advanced AI technologies.

## Features

- 🤖 Automated news collection from multiple sources
- 🔍 Intelligent content filtering and validation
- 📊 KNN clustering for content organization
- 🖼️ AI-powered image selection
- 📊 Prompt Optimization using TextGrad
- 📱 Modern web interface with React
- 🎙️ Podcast content support
- 🎬 Video reel integration

## Architecture

The project consists of three main components:

1. **News Collector**
   - Fetches news from Bing News API and RSS feeds
   - Validates article content
   - Filters relevant EV-related content

2. **Summary and Feedback Generation**
   - Generates concise summaries of articles
   - Evaluates content quality across multiple dimensions
   - Provides automated feedback on articles

3. **Frontend**
   - Modern React-based interface
   - Integrated audio and video support

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