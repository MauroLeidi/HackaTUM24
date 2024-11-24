import requests
from datetime import datetime
import json
import os
from utils import extract_article_content, batch_validate_articles, normalize_article

def get_news(search_term=None, market='en-US', count=3):
    api_key = os.getenv("BING_API_KEY")
    """
    Get news using Bing News API
    
    Parameters:
    - api_key: Your Bing API key
    - search_term: What to search for (optional)
    - market: Market code (default 'en-US')
    - count: Number of results (default 10)
    """
    
    # Base endpoint for news search
    base_url = "https://api.bing.microsoft.com/v7.0/news"
    
    # If search term provided, use /search endpoint
    if search_term:
        base_url += "/search"
    
    # Request headers
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Accept': 'application/json'
    }
    
    # Request parameters
    params = {
        'mkt': market,
        'count': count,
        'freshness': 'Month',  # Can be Day, Week, or Month
        # 'cc': 'DE',
        'sortBy': 'Relevance'
    }
    
    # Add search term if provided
    if search_term:
        params['q'] = search_term
    
    try:
        # Make the request
        print(f"Fetching Bing news for '{search_term}'... for the market {market}, sortBy {params['sortBy']}")#cc {params['cc']}
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse the JSON response
        news_data = response.json()
        
        # Extract and format the news articles
        articles = []
        print("num canditate articles: ", len(news_data.get('value', [])))
        for article in news_data.get('value', []):
            articles.append({
                'title': article.get('name'),
                'description': article.get('description'),
                'url': article.get('url'),
                'published': article.get('datePublished'),
                'source': article.get('provider', [{}])[0].get('name'),
                'category': article.get('category', 'Uncategorized')
            })
        
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None


def get_bing_news(n_bing_news, use_litellm, market):
    bing_news = get_news(search_term="electric vehicles", count = n_bing_news, market=market)
    for article in bing_news:
        article_content = extract_article_content(article['url'])
        article['full_content'] = article_content
        article["type"] = "bing"

    bing_news = [article for article in bing_news if article['full_content'] != '' and article['full_content'] is not None]

    bing_news_results = batch_validate_articles(bing_news, use_litellm=use_litellm)
    
    # Print results
    print(f"Found {len(bing_news_results['valid_articles'])} valid articles")
    print(f"Found {len(bing_news_results['invalid_articles'])} invalid articles")

    # When processing your articles:
    normalized_articles = []
    for article in bing_news_results['valid_articles']:
        normalized = normalize_article(article, 'bing')
        if normalized:
            normalized_articles.append(normalized)
    
    return normalized_articles