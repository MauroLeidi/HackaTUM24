from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import SelectedImageIndex,FindImage,SelectedImageUrl,ArticleRequest,ArticleResponse,SearchQueryResponse
from dotenv import load_dotenv
from openai import OpenAI
from utils import *
import logging
import pandas as pd

# Path to the CSV file
CSV_PATH = "./data/df_with_embedding_and_sorted_groups.csv"
# Global variable for tracking the current article group index
articleIndex = 0
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
        elif len(image_urls) > 5:
            image_urls = image_urls[:5]
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
        system_prompt = \
"""
You are a skilled journalist tasked with writing an article for an online newspaper that specializes in Electric Vehicle (EV) content. Your goal is to create a new and engaging article that combines the information from the following articles.

Please generate a new article that:
- Combines key insights from the provided articles into a single, cohesive, and interesting piece. Feel free to select the most interesting information, and filter out what is not necessary.
- Incorporate unique insights and original analysis by including expert opinions, case studies, or interviews with industry leaders. Include at least two quotes or insights from industry experts or urban planners to add depth and originality. Explore less-discussed topics, such as the socio-economic impacts on diverse urban demographics, the role of EVs in rural areas, and the impact of EVs on urban planning or the role of renewable energy in charging infrastructure.
- Tailor content for different audience segments by creating sections that cater to specific groups, such as potential EV buyers, environmental advocates, or automotive enthusiasts. Identify and discuss region-specific challenges or opportunities, such as local government incentives or infrastructure limitations.
- Use up-to-date information and data, mentioning recent model releases, advancements in solid-state batteries, or specific policy changes in major markets. Incorporate recent studies or reports with specific citations and discuss recent policy changes or market predictions to provide a forward-looking perspective.
- Enhance clarity and structure with interactive elements such as infographics, charts, or sidebars to summarize key points or data. Include interactive elements such as infographics or interactive maps to visualize EV infrastructure growth. Use markdown syntax for these elements to ensure proper formatting.
- Promote professionalism and transparency by including information about the author's credentials and expertise in the automotive industry. Disclose any use of AI tools or automation in the article's creation, detailing the AI tools used and their specific contributions to the content.
- Emphasize trust and accuracy by referencing specific studies, data, or expert sources to bolster the article's accuracy and authoritative nature. Ensure all claims are backed by peer-reviewed studies or expert verification. Indicate whether sources for claims were verified by experts or peer-reviewed studies to enhance credibility.
- Include a section on potential future developments in EV technology and urban planning, supported by expert opinions or forecasts.
- Simplify technical jargon by providing definitions or a glossary for technical terms like 'solid-state batteries' to ensure accessibility for all readers.
- Improve clarity by adding a requirement for a summary or key takeaways section at the end to help readers quickly grasp the main points.
- Place the image near the top after the title
- Use the image in markdown format: `![image](<URL OF IMAGE HERE>)`.

Important: Do not include any backticks (```) in your response. Output the markdown directly.
The article should be informative, engaging, and written in a journalistic style. Use markdown syntax for the article, including headings, subheadings, and paragraphs. Insert the image at a location that makes sense, such as in the middle or at the top of the article, where it supports the content. Use the image in markdown format: `![image]<<IMAGE_URL_HERE>>`.

Your output should be a complete article in markdown format, with the image inserted at an appropriate location. The article will be provided <ARTICLE> <\ARTICLE> tags. Within the <ARTICLE> tag there are can also the following tags <TITLE> <\TITLE>, <CONTENT> <\CONTENT> and <DESCRIPTION> <\DESCRIPTION> which will provide the title and content of the article respectively. Note that articles may be provided in various languages but keep your critique in English.
""" 
        
        # Prepare the prompt for ChatGPT
        prompt = \
f"""
The articles are as follows:

{request.articles}

Additionally, here is an image URL: {request.image_url}
"""

        # Instantiate the OpenAI client
        client = OpenAI()

        # Make the API call to generate the article
        logging.info("Sending request to OpenAI API.")
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
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
        find_image_request = FindImage(description=search_query, nimages=10)  # You can set nimages to any number you want
        selected_image_url_response = await find_image(find_image_request)
        image_url = selected_image_url_response.url
        logging.info(f"Selected image URL: {image_url}")

        # Step 3: Generate the final markdown article using the articles and the image URL
        article_response = await generate_article(ArticleRequest(articles=request.articles, image_url=image_url))
        return article_response
    
    except Exception as e:
        logging.error(f"Error occurred in generating full article: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating full article.")


@app.get("/next-article/", response_model=ArticleResponse)
async def next_article():
    """
    Generate the next article by reading from the CSV file, preparing the input for
    generate-full-article, and cycling through groups using articleIndex.
    """
    global articleIndex  # Access the global variable

    try:
        # Step 1: Read the CSV file
        logging.info("Reading CSV file...")
        df = pd.read_csv(CSV_PATH)

        # Ensure the 'group' and 'content' columns exist
        if 'group' not in df.columns or 'content' not in df.columns:
            raise ValueError("CSV must contain 'group' and 'content' columns.")

        # Step 2: Fetch articles for the current group
        current_group = df[df['group'] == articleIndex]
        if current_group.empty:
            raise ValueError(f"No articles found for group {articleIndex}.")

        # Combine content from the group into a single string
        articles_combined = "\n\n".join(
            f"title = {row['title']}\ncontent = {row['content']}"
            for _, row in current_group.iterrows()
        )

        # Step 3: Increment the global article index (cycle 0-9)
        articleIndex = (articleIndex + 1) % 10
        logging.info(f"Moving to the next article group: {articleIndex}")

        # Step 4: Internally call generate-full-article
        article_request = {
            "articles": articles_combined,
            "image_url": ""
        }
        full_article = await generate_full_article(ArticleRequest(**article_request))

        return full_article

    except Exception as e:
        logging.error(f"Error in /next-article endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate the next article.")


# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)