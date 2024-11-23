from pydantic import BaseModel

class SelectedImageIndex(BaseModel):
    index: int

class FindImage(BaseModel):
    description: str
    nimages: int

class SelectedImageUrl(BaseModel):
    url: str
