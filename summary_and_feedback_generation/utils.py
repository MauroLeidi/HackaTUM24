from litellm import acompletion, aembedding, completion, embedding
import os
from functools import partial

MODEL_NAME_TO_API_VERSION = {
    "text-embedding-ada-002": "2023-05-15",
    "dall-e-3": "2024-02-01",
    "gpt-4o": "2024-08-01-preview"
}

def get_completion_litellm_for_burda(model_name: str, async_f = True):
    assert model_name in MODEL_NAME_TO_API_VERSION.keys(), f"model_name must be one of {MODEL_NAME_TO_API_VERSION.keys()}. If more have been added, please update the MODEL_NAME_TO_API_VERSION dictionary." 
    
    completion_func = completion if not async_f else acompletion
    embedding_func = embedding if not async_f else aembedding
    
    if model_name == "text-embedding-ada-002":
        return partial(embedding_func, api_base = "https://hackatum-2024.openai.azure.com", api_version=MODEL_NAME_TO_API_VERSION[model_name], model = f"azure/{model_name}", api_key = os.getenv("AZURE_API_KEY"))
    return partial(completion_func, api_base = "https://hackatum-2024.openai.azure.com", api_version=MODEL_NAME_TO_API_VERSION[model_name], model = f"azure/{model_name}", api_key = os.getenv("AZURE_API_KEY"))
    
