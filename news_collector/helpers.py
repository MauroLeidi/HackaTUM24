from newspaper import Article
from bs4 import BeautifulSoup
import requests
import re
from dotenv import load_dotenv
from openai import OpenAI
import json
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime

load_dotenv(override=True)


def extract_article_content(url):
    """
    Extract just the main article content from a news website.
    
    Args:
        url (str): URL of the news article
        
    Returns:
        dict: Article title, text content, and publish date
    """
    try:
        # Initialize Article object
        article = Article(url)
        article.download()
        article.parse()
        
        # Get the main content
        content = {
            'title': article.title,
            'text': article.text,
            'publish_date': article.publish_date,
        }
        
        # Clean the text content
        content['text'] = re.sub(r'\n+', '\n', content['text'])  # Remove extra newlines
        content['text'] = re.sub(r'\s+', ' ', content['text'])   # Remove extra whitespace
        
        return content['text']
        
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return {}

        
client = OpenAI()

def validate_article(content: Dict) -> Dict:
    """
    Validate if the content is a real article using ChatGPT.
    
    Args:
        content (dict): Dictionary containing article content
        
    Returns:
        dict: Original content with validation results added
    """
    
    # Prepare the prompt
    system_prompt = """Analyze the following text and determine if it's a real article or just website notices (like cookies, privacy policy, etc.).
    You need to base yourself on the full content of the article.
    Respond with a JSON object containing:
    1. "is_article": boolean (true if it's a real article)
    2. "confidence": float (0-1)
    3. "reason": string (brief explanation)
    Only respond with the JSON object, no other text."""

    user_prompt = f"""Title: {content.get('title', 'No title')}
    Content: {content.get('full_content', '')}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1  # Low temperature for more consistent results
        )
        
        # Parse the response
        validation_result = json.loads(response.choices[0].message.content)
        
        # Add validation results to the original content
        content.update({
            'is_valid_article': validation_result['is_article'],
            'validation_confidence': validation_result['confidence'],
            'validation_reason': validation_result['reason']
        })
        
    except Exception as e:
        content.update({
            'is_valid_article': False,
            'validation_confidence': 0.0,
            'validation_reason': f"Error during validation: {str(e)}"
        })
        
    return content

def batch_validate_articles(articles: List[Dict], 
                            confidence_threshold: float = 0.8) -> Dict[str, List[Dict]]:
    """
    Validate multiple articles and separate them into valid and invalid.
    
    Args:
        articles (list): List of article dictionaries
        confidence_threshold (float): Minimum confidence to consider valid
        
    Returns:
        dict: Contains 'valid_articles' and 'invalid_articles' lists
    """
    valid_articles = []
    invalid_articles = []
    
    for article in articles:
        validated_article = validate_article(article)
        
        if (validated_article['is_valid_article'] and 
            validated_article['validation_confidence'] >= confidence_threshold):
            valid_articles.append(validated_article)
        else:
            invalid_articles.append(validated_article)
            
    return {
        'valid_articles': valid_articles,
        'invalid_articles': invalid_articles
    }

def parse_date(date_str: str):
    """
    Parse different date formats into datetime object
    """
    try:
        # Try ISO format (from Bing News API)
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        try:
            # Try RSS format
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, AttributeError):
            return None
        
def normalize_article(article: Dict, source: str) -> Dict:
    """
    Normalize article data from different sources into a consistent format
    
    Args:
        article (Dict): Raw article data
        source (str): Source of the article ('newsapi' or 'rss')
        
    Returns:
        Dict: Normalized article data
    """
    if source == 'bing':
        return {
            'title': article.get('title'),
            'description': article.get('description'),
            'url': article.get('url'),
            'image_url': None,  # Bing News API doesn't provide image URL in basic response
            'published_date': parse_date(article.get('published') or ''),
            'source': article.get('source'),
            'author': None,  # Bing News API doesn't provide author in basic response
            'content': article.get('full_content'),
            'category': article.get('category'),
            'data_source': 'bing'
        }
    elif source == 'rss':
        return {
            'title': article.get('title'),
            'description': article.get('description'),
            'url': article.get('link'),
            'image_url': None,
            'published_date': parse_date(article.get('pubDate') or ''),
            'source': article.get('creator'),
            'author': article.get('author'),
            'content': article.get('full_content'),
            'category': None,  # RSS typically doesn't include category
            'data_source': 'rss'
        }
    
    return {}