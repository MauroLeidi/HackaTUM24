import base64
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from schemas import SelectedImageIndex,FindImage
from dotenv import load_dotenv
from openai import OpenAI

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

# Helper: Fetch images from Bing or another search engine
def fetch_images(query: str, num_images: int = 5) -> List[bytes]:
    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": num_images}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch images from Bing.")

    results = response.json()
    image_urls = [img["contentUrl"] for img in results.get("value", [])[:num_images]]

    images = []
    for url in image_urls:
        try:
            img_data = requests.get(url).content
            images.append(img_data)
        except Exception:
            continue  # Skip if the image can't be downloaded
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
        description (str): Text description (e.g., an article title).
        num_images (int): Number of images to fetch.

    Returns:
        SelectedImageIndex: Object containing the index of the selected image.
    """
    try:
        # Step 1: Fetch images
        images = fetch_images(request.description, request.num_images)
        if not images:
            raise HTTPException(status_code=404, detail="No images found.")

        # Step 2: Convert images to base64
        images_base64 = [convert_to_base64(img) for img in images]

        # Step 3: Prepare prompt and make API call
        prompt = (
            f"You are given {len(images_base64)} images represented as base64 strings, "
            f"and a description: '{request.description}'. Analyze the images and select the most relevant "
            f"one based on the description. Respond with the index (0-based) of the chosen image."
        )

        client = OpenAI()  # Instantiate OpenAI client
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
                                "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                            }
                            for img_b64 in images_base64
                        ],
                    ],
                }
            ],
            response_format=SelectedImageIndex,  # Enforce the integer response schema
        )

        # Parse the index from the response
        chosen_index = response.index

        # Step 4: Validate the chosen index
        if not (0 <= chosen_index < len(images)):
            raise HTTPException(status_code=400, detail="Invalid image index returned by GPT.")

        # Step 5: Return the index
        return SelectedImageIndex(index=chosen_index)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)