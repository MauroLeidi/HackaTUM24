from litellm import acompletion, aembedding, completion, embedding
import os
from functools import partial
from newspaper import Article
import requests
import re
from dotenv import load_dotenv
from openai import OpenAI
import json
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import time

import base64
import os
from typing import List
from fastapi import FastAPI, HTTPException
import requests
from dotenv import load_dotenv
from openai import OpenAI
from helpers import *
import logging


load_dotenv(override=True)

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")

def fetch_images(query: str, num_images: int = 10) -> List[bytes]:
    """
    Fetch images from Bing Image Search API, filtering by specific formats.

    Args:
        query (str): Search query for the images.
        num_images (int): Number of images to fetch.

    Returns:
         images (List(str)): List of image urls in valid format (accepted by chatgpt).
    """
    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    print(headers)

    # Include filetype filters directly in the query
    query_with_filetype = query#f"{query}"

    # Use API parameters for additional filtering
    params = {
        "q": query_with_filetype,  # Filtered query
        "count": num_images,       # Number of results
        "imageType": "Photo",      # Prefer photo images
        "safeSearch": "Moderate",  # Safe search level
    }

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        print('Error withing image generation')
        print(response.text)
        raise HTTPException(status_code=500, detail="Failed to fetch images from Bing.")

    results = response.json()
    image_urls = [img["contentUrl"] for img in results.get("value", [])]
    print(image_urls)
    # Valid file extensions to check against
    valid_extensions = (".png", ".jpeg", ".jpg")

    images = []
    for url in image_urls:
        print(f"current url {url} is valid {url.lower().endswith(valid_extensions)}")
        # Check if the URL ends with a valid image format
        if url.lower().endswith(valid_extensions) and urlIsAlive(url):
            try:
                images.append(url)

                # Stop if we have enough images
                if len(images) >= num_images:
                    break
            except Exception:
                continue  # Skip if the image can't be downloaded
    
    print('Succesfully returned images urls')
    print(f"returning the following images urls: {images}")
    # Ensure we return the number of requested images or fewer if not enough were valid
    return images[:5]


# Helper: Convert image bytes to base64
def convert_to_base64(image_data: bytes) -> str:
    return base64.b64encode(image_data).decode("utf-8")

def generate_search_query_from_articles(articles_content: str) -> str:
    """
    Use ChatGPT to generate a short search query from the given article content.
    
    Args:
        articles_content (str): Full article content to generate the search query.
        
    Returns:
        str: The generated search query to be used in an image search.
    """
    system_prompt = f"""
    You are given the content of an article (or multiple articles). Your task is to generate a short, concise 
    description that can be used in an image search engine like Bing. The search query should describe some tangible object, concering the main 
    topic of the article(s) in a clear way. Please generate a concise description (less than 100 words) that can be used to search for a relevant image."""
    user_prompt = f"The articles content is as follows: {articles_content}"
    
    client = OpenAI()
    try:
        # Send the request to OpenAI using the new interface
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1  # Low temperature for more consistent results
        )
        # Extract and return the generated search query
        #search_query = response['choices'][0]['message']['content'].strip()
        search_query = response.choices[0].message.content
        return search_query
    
    except Exception as e:
        logging.error(f"Error generating search query from OpenAI: {e}")
        raise HTTPException(status_code=500, detail="Error generating image search query.")

def urlIsAlive(image_url):
    # Send GET request to the image URL
    try:
        response = requests.get(image_url)
    except:
        return False
    # Check if the request was successful (status code 200)
    return response.status_code == 200



def get_completion_litellm_for_burda(model_name: str, async_f = True):
    assert model_name in MODEL_NAME_TO_API_VERSION.keys(), f"model_name must be one of {MODEL_NAME_TO_API_VERSION.keys()}. If more have been added, please update the MODEL_NAME_TO_API_VERSION dictionary." 
    
    MODEL_NAME_TO_API_VERSION = {
        "text-embedding-ada-002": "2023-05-15",
        "dall-e-3": "2024-02-01",
        "gpt-4o": "2024-08-01-preview"
    }
    
    completion_func = completion if not async_f else acompletion
    embedding_func = embedding if not async_f else aembedding
    
    if model_name == "text-embedding-ada-002":
        return partial(embedding_func, api_base = "https://hackatum-2024.openai.azure.com", api_version=MODEL_NAME_TO_API_VERSION[model_name], model = f"azure/{model_name}", api_key = os.getenv("AZURE_API_KEY"))
    return partial(completion_func, api_base = "https://hackatum-2024.openai.azure.com", api_version=MODEL_NAME_TO_API_VERSION[model_name], model = f"azure/{model_name}", api_key = os.getenv("AZURE_API_KEY"))
    



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

def validate_article(content: Dict, use_litellm = False, wait_time = 0.75) -> Dict:
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
    time.sleep(wait_time)  # To avoid rate limiting
    try:
        completion_kwargs = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1  # Low temperature for more consistent results
        }
        if use_litellm:
            completion_fn = get_completion_litellm_for_burda("gpt-4o")
            response = completion_fn(**completion_kwargs)
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                **completion_kwargs,
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
                            confidence_threshold: float = 0.8,
                            use_litellm=False) -> Dict[str, List[Dict]]:
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
        validated_article = validate_article(article, use_litellm=use_litellm)
        
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