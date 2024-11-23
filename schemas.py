from pydantic import BaseModel

class SelectedImageIndex(BaseModel):
    index: int

class FindImage(BaseModel):
    description: str
    nimages: int

class SelectedImageUrl(BaseModel):
    url: str

# Define Pydantic models for input and output
class ArticleRequest(BaseModel):
    articles: str  # A single string containing the content of multiple articles
    image_url: str  # The URL of the image to include in the article

class ArticleResponse(BaseModel):
    article: str  # The generated article in markdown format
    
class SearchQueryResponse(BaseModel):
    search_query: str  # The generated search query to find the image
    