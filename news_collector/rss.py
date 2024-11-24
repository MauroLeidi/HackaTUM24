import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

from utils import batch_validate_articles, extract_article_content, normalize_article


def scrape_rss_feed(url: str,limit: Optional[int] = None) -> List[Dict]:
    """
    Scrape RSS feed and extract links using jjina reader API
    
    Args:
        url (str): URL of the RSS feed
        
    Returns:
        List[Dict]: List of articles with their links and metadata
    """
    try:
        # Fetch the RSS feed
        print(f"Fetching RSS feed from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse XML content
        root = ET.fromstring(response.content)
        
        # Find all item elements
        items = root.findall(".//item")

        if limit is not None:
            items = items[:limit]
        
        # Extract article information
        articles = []
        for item in items:
            article = {
                'title': item.find('title').text if item.find('title') is not None else '',
                'link': item.find('link').text if item.find('link') is not None else '',
                #'full_content': jjina_reader(item.find('link').text) if item.find('link') is not None else '',
                'description': item.find('description').text if item.find('description') is not None else '',
                'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else '',
                'creator': item.find('.//{http://purl.org/dc/elements/1.1/}creator').text 
                          if item.find('.//{http://purl.org/dc/elements/1.1/}creator') is not None else ''
            }
            articles.append(article)
            
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []
    

def get_rss_articles(use_litellm: bool = False) -> List[Dict]:
    rss_urls  = [
        "https://rss.app/feeds/MLuDKqkwFtd2tuMr.xml",
        "https://www.autobild.de/rss/22590661.xml",
        "https://rss.app/feeds/u6rcvfy6PTSf9vQ4.xml"
    ]
    normalized_articles = []
    for rss_url in rss_urls:
        rss_articles = scrape_rss_feed(rss_url)
        for article in rss_articles:
            article_content = extract_article_content(article['link'])
            article['full_content'] = article_content
            article["type"] = "rss"

        rss_results = batch_validate_articles(rss_articles, use_litellm=use_litellm)

        # Print results
        print(f"Found {len(rss_results['valid_articles'])} valid articles")
        print(f"Found {len(rss_results['invalid_articles'])} invalid articles")

        
        for article in rss_results['valid_articles']:
            normalized = normalize_article(article, 'rss')
            if normalized:
                normalized_articles.append(normalized)

    return normalized_articles