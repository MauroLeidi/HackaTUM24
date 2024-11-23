import base64
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from schemas import SelectedImageIndex,FindImage,SelectedImageUrl
from dotenv import load_dotenv
from openai import OpenAI
import logging

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
        List[bytes]: List of image byte data for the valid formats.
    """
    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}

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
        print(response)
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
        if url.lower().endswith(valid_extensions):
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
        SelectedImageIndex: Object containing the index of the selected image.
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


# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)