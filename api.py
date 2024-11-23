import base64
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from schemas import SelectedImageIndex,FindImage,SelectedImageUrl,ArticleRequest,ArticleResponse,SearchQueryResponse
from dotenv import load_dotenv
from openai import OpenAI
from helpers import *
import logging
import openai  # Ensure that this import is correct

# Configure logging at the beginning of the script
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoint: Process description and return selected image
@app.post("/find-image/", response_model=SelectedImageIndex)
async def find_image(request: FindImage):
    """
    Fetches images based on a description, asks ChatGPT to select the best one, and returns its index.

    Args:
    A SelectedImageIndex object containing:
        description (str): Text description (e.g., an article title).
        nimages (int): Number of images to fetch.

    Returns:
        SelectedImageUrl: Object containing the url of the selected image.
    """
    try:
        # Step 1: Fetch images
        image_urls = fetch_images(request.description, request.nimages)
        if not image_urls:
            print('Error in the bing search')
            raise HTTPException(status_code=404, detail="No images found.")

        # Step 3: Prepare prompt and make API call
        prompt = (
            f"You are given {len(image_urls)} images represented as base64 strings, "
            f"and a description: '{request.description}'. Analyze the images and select the most relevant "
            f"one based on the description. Respond with the index (0-based) of the chosen image."
        )

        client = OpenAI()  # Instantiate OpenAI client
        print('Sending images and prompt to chatgpt')
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *[
                             {
                                "type": "image_url",
                                "image_url": {"url": url},  # Use the actual image URL here
                            }
                            for url in image_urls  # `image_urls` is a list of raw image URLs
                        ],
                    ],
                }
            ],
            response_format=SelectedImageIndex,  # Enforce the integer response schema
        )

        # Parse the index from the response
        chosen_index = response.choices[0].message.parsed.index

        # Step 4: Validate the chosen index
        if not (0 <= chosen_index < len(image_urls)):
            logging.warning(
                "There was an issue with image selection. The chosen index (%d) is out of range. "
                "Adjusting by taking modulo to ensure a valid selection.",
                chosen_index,
            )
            chosen_index = chosen_index % len(image_urls)  # Adjust index to a valid range

        # Step 5: Get the selected URL
        selected_url = image_urls[chosen_index]
        logging.info("Selected URL: %s", selected_url)

        # Step 6: Return the selected URL
        return SelectedImageUrl(url=selected_url)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-image-query/", response_model=SearchQueryResponse)
async def generate_image_query(request: ArticleRequest):
    """
    Generates a short description from the article content, suitable for use in a Bing image search.
    """
    try:
        # Use ChatGPT to generate the search query from article content
        search_query = generate_search_query_from_articles(request.articles)
        
        # Return the search query as part of the response
        return SearchQueryResponse(search_query=search_query)
    
    except Exception as e:
        logging.error(f"Error occurred while generating search query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating image search query.")

    
@app.post("/generate-article/", response_model=ArticleResponse)
async def generate_article(request: ArticleRequest):
    """
    Generate a new article by combining content from multiple articles and inserting an image.
    """
    try:
        # Prepare the prompt for ChatGPT
        prompt = f"""
        You are a skilled journalist tasked with writing an article for an online newspaper that specializes in Electric Vehicle (EV) content. Your goal is to create a new and engaging article that combines the information from the following articles. 

        The articles are as follows:
        
        {request.articles}

        Additionally, here is an image URL: {request.image_url}

        Please generate a new article that:
        - Combines key insights from the three articles into a single, cohesive, and interesting piece. Feel free to select the most interesting information, and filter out what is not necessary.
        - The article should be informative, engaging, and written in a journalistic style.
        - Use markdown syntax for the article, including headings, subheadings, and paragraphs.
        - Insert the image at a location that makes sense, such as in the middle or at the top of the article, where it supports the content.
        - Use the image in markdown format: `![image]({request.image_url})`.
        
        Your output should be a complete article in markdown format, with the image inserted at an appropriate location.
        """

        # Instantiate the OpenAI client
        client = OpenAI()

        # Make the API call to generate the article
        logging.info("Sending request to OpenAI API.")
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [{"type": "text", "text": prompt}]},
            ]
        )
        print(response)
        # Extract the generated article
        article = response.choices[0].message.content.strip()  # Directly access 'content'

        return ArticleResponse(article=article)

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating article.")

# API Endpoint: Process description and return selected image
@app.post("/generate-full-article/", response_model=ArticleResponse)
async def generate_full_article(request: ArticleRequest):
    """
    Generate a full article by:
    1. Generating the search query based on the article content.
    2. Fetching images using the search query.
    3. Generating a markdown article with the image included.

    Args:
    A ArticleRequest containing:
        articles (str): Text content of multiple articles.

    Returns:
    ArticleResponse: Object containing the markdown of the generated article with image.
    """
    try:
        # Step 1: Generate the search query from the articles
        search_query_response = await generate_image_query(request)
        search_query = search_query_response.search_query
        logging.info(f"Generated search query: {search_query}")

        # Step 2: Fetch images using the search query
        find_image_request = FindImage(description=search_query, nimages=5)  # You can set nimages to any number you want
        selected_image_url_response = await find_image(find_image_request)
        image_url = selected_image_url_response.url
        logging.info(f"Selected image URL: {image_url}")

        # Step 3: Generate the final markdown article using the articles and the image URL
        article_response = await generate_article(ArticleRequest(articles=request.articles, image_url=image_url))
        return article_response
    
    except Exception as e:
        logging.error(f"Error occurred in generating full article: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating full article.")


# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)