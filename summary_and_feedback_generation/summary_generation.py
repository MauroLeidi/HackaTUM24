from typing import Dict, Any
from pydantic import BaseModel
from jinja2 import Template
from summary_and_feedback_generation.utils import get_completion_litellm_for_burda
import json

class Summary(BaseModel):
    summary: str

### SYSTEM PROMPT ###
SUMMARY_GENERATOR_SYSTEM_PROMPT = \
"""
Summarize the content in a purely textual format (no bullet points or blocks), focusing exclusively on topics related to the field of electric vehicles (EVs). 
Include only the most essential information relevant to EVs, such as technology, infrastructure, market trends, policies, or environmental impact. 
Retain crucial details that provide necessary context, but ensure the summary is concise and straightforward.
the article will be provided <ARTICLE> <\ARTICLE> tags. Within the <ARTICLE> tag there are can also the following tags <TITLE> <\TITLE>, <CONTENT> <\CONTENT> and <DESCRIPTION> <\DESCRIPTION> which will provide the title and content of the article respectively.
As output I would like you to provide the following in the format of a JSON:
{
    "summary": "Your summary", # The summary of the article
}
"""

### FULL USER PROMPT TEMPLATE ###
SUMMARY_GENERATOR_USER_PROMPT_TEMPLATE = \
"""
<ARTICLE>
<TITLE> {{title}} <\TITLE>
<DESCRIPTION> {{description}} <\DESCRIPTION>
<CONTENT> {{content}} <\CONTENT>
<\ARTICLE>
"""


async def generate_summary(news_dict: Dict[str, Any]):
    user_prompt = Template(SUMMARY_GENERATOR_USER_PROMPT_TEMPLATE).render(
        title = news_dict.get("title", "Title Missing"),
        description = news_dict.get("description", "Description Missing"),
        content = news_dict.get("content", "Content Missing"),
    )
    
    completion_fn = get_completion_litellm_for_burda("gpt-4o")
    
    reply = await completion_fn(
        messages=[{"role": "system", "content": SUMMARY_GENERATOR_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        response_format = Summary,
    )
    
    return Summary(**json.loads(reply.choices[0].message.content))