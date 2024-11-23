import base64
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from schemas import SelectedImageIndex,FindImage,SelectedImageUrl,ArticleRequest,ArticleResponse
from dotenv import load_dotenv
from openai import OpenAI
from helpers import *
import logging
import openai  # Ensure that this import is correct

load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")

def fetch_images(query: str, num_images: int = 5) -> List[bytes]:
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
    return images


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

