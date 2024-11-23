from feedback_generation.utils import get_completion_litellm_for_burda
from typing import Dict, Any
import json
from jinja2 import Template
from pydantic import BaseModel


# ~~~ EVALUATION DIMENSIONS TEMPLATES ~~~

class NewsRating(BaseModel):
    critique: str
    news_meets_standards: str

# ~~~ Originality, Value, and Purpose Dimension ~~~

# Originality, Value, and Purpose As Instruction
ORIGINALITY_INSTRUCTION = \
"""
**Originality, Value, and Purpose in E-Vehicle Content**
Evaluate whether the article provides unique, original insights or analysis about electric vehicles (E-vehicles), such as innovative technologies, emerging trends, or in-depth coverage of specific models, infrastructure, or market shifts. The content should not merely summarize existing industry information but offer fresh perspectives. Assess whether the article is crafted with the intent to inform and serve the audience, addressing relevant concerns about E-vehicles, sustainability, and their future, rather than focusing on SEO-driven tactics. Look for content that aims to benefit users by answering their specific questions or enhancing their understanding of E-vehicles.
"""

# Originality, Value, and Purpose DIMENSION AS A QUESTION ANSWERING
ORIGINALITY_INSTRUCTION_AS_QA = \
"""
**Originality, Value, and Purpose**
Does the article provide unique, original insights or analysis about E-vehicles, such as new trends, technologies, or innovations in the industry?
Does the content offer substantial value by presenting in-depth information, or does it merely summarize existing knowledge without adding new perspectives?
Is the content created to inform and educate the audience about E-vehicles, or does it prioritize SEO tactics and keyword optimization over delivering genuine value to the reader?
"""

# ~~~  Relevance and Audience Impact Dimension ~~~

#  Relevance and Audience Impact DIMENSION AS INSTRUCTION
RELEVANCE_INSTRUCTION = \
"""
**Evaluation Dimension Relevance and Audience Impact in E-Vehicle Articles**
Consider whether the article is specifically tailored to meet the needs of its target audience, such as potential E-vehicle buyers, environmental enthusiasts, or industry professionals. The content should provide in-depth, first-hand knowledge about E-vehicles and offer valuable insights into topics such as charging networks, vehicle performance, or the environmental impact of electric transportation. Assess whether the article addresses the audience’s concerns or goals—whether they seek information about vehicle choices, cost savings, or environmental benefits. The article should leave the reader feeling satisfied, helping them achieve their objectives without prompting them to seek additional information.
"""

#  Relevance and Audience Impact DIMENSION AS A QUESTION ANSWERING
RELEVANCE_INSTRUCTION_AS_QA = \
"""
**Evaluation Dimension: Relevance and Audience Impact in E-Vehicle Articles**
Is the article tailored to the specific needs of its audience, such as potential E-vehicle buyers, environmental advocates, or automotive enthusiasts?
Does the content demonstrate first-hand knowledge or deep expertise, providing information that fulfills the audience's goals, such as making informed purchasing decisions, learning about E-vehicle performance, or understanding the impact of electric vehicles on the environment?
"""

# ~~~ UP TO DATE DIMENSION ~~~~

# UP TO DATE DIMENSION AS INSTRUCTION
UP_TO_DATE_INFORMATION_INSTRUCTION = \
"""
**Evaluation Dimension: Timeliness and Relevance in E-Vehicle Content**
Evaluate whether the article provides accurate, up-to-date information about E-vehicles, reflecting the current state of the industry, recent technological advancements, and emerging trends. Consider if the article discusses developments from reliable sources, such as recent research, industry news, or newly released models and technologies. Assess whether the content identifies and responds to pressing issues in the E-vehicle landscape, such as policy changes, supply chain challenges, or advancements in charging infrastructure. The article should avoid relying on outdated information or speculations that are no longer relevant to the current market or technological environment.
"""

# UP TO DATE DIMENSION AS A QUESTION ANSWERING
UP_TO_DATE_INFORMATION_INSTRUCTION_QA = \
"""
**Evaluation Dimension: Relevant, Up-to-Date Information in E-Vehicle Articles**
Does the article provide accurate and up-to-date information, reflecting recent advancements, trends, or developments in the E-vehicle industry? Are the sources cited reliable and current?
Does the article address contemporary issues such as new models, policy changes, technological breakthroughs, or environmental challenges, avoiding outdated or irrelevant information?
Does the content offer insights into emerging opportunities or solutions, such as innovations in charging infrastructure, battery technology, or market trends?
"""

# ~~~ Clarity, Engagement, and Structure Dimension ~~~

# CLARITY, ENGAGEMENT, AND STRUCTURE AS INSTRUCTION
CLARITY_ENGAGEMENT_STRUCTURE_INSTRUCTION = \
"""
**Evaluation Dimension: Clarity, Engagement, and Structure in E-Vehicle Articles**
Assess the clarity and structure of the article, ensuring it is organized in a way that allows the reader to easily navigate through technical details, comparisons, or analysis about E-vehicles. Effective headings should guide the reader through sections such as vehicle performance, battery life, charging infrastructure, and environmental impact. Evaluate whether the article is engaging, ensuring it holds the reader's attention and provides useful insights. Check that the content avoids exaggeration or misleading claims (e.g., unrealistic performance expectations) and presents accurate, practical information about E-vehicles in a straightforward manner
"""

# CLARITY, ENGAGEMENT, AND STRUCTURE AS A QUESTION ANSWERING
CLARITY_ENGAGEMENT_STRUCTURE_INSTRUCTION_QA = \
"""
**Evaluation Dimension: Clarity, Engagement, and Structure**
Is the article clear and well-organized, with effective headings and logical progression that helps readers navigate through technical topics, like battery technology, charging infrastructure, or vehicle performance?
Does the content engage the reader by providing an informative experience that is interesting and helpful, especially for individuals considering E-vehicle purchases or following industry developments?
Are the headings and content free from exaggerated or misleading claims, especially regarding the performance or environmental benefits of E-vehicles?
"""

# ~~~ Quality, Professionalism, and Transparency Dimension ~~~

# QUALITY, PROFESSIONALISM, AND TRANSPARENCY AS INSTRUCTION
QUALITY_PROFESSIONALISM_TRANSPARENCY_INSTRUCTION = \
"""
**Evaluation Dimension: Quality, Professionalism, and Transparency in E-Vehicle Articles**
Evaluate the professionalism and quality of the article, checking for spelling, grammar, and formatting errors, especially in technical sections related to E-vehicle specifications or comparisons. The article should be polished and well-crafted, demonstrating careful attention to detail. Transparency is also crucial—ensure the content includes clear authorship or attribution, with information about the author’s qualifications or expertise in the E-vehicle or automotive industry. If automation or AI tools were used in creating the content, it should be disclosed clearly. Transparency builds trust with the audience, particularly when discussing complex or technical topics.
"""

# QUALITY, PROFESSIONALISM, AND TRANSPARENCY AS A QUESTION ANSWERING
QUALITY_PROFESSIONALISM_TRANSPARENCY_INSTRUCTION_QA = \
"""
**Evaluation Dimension: Quality, Professionalism, and Transparency in E-Vehicle Articles**
Is the article well-produced and polished, free of errors (e.g., spelling, grammar, formatting), and does it demonstrate careful attention to detail when discussing complex aspects of E-vehicles?
Is the article transparent, with clear authorship attribution, qualifications of the writer (e.g., automotive expert or industry analyst), and disclosure of any AI tools or automation used in content creation?
"""

# ~~~ Trust, Accuracy, and Expertise

# TRUST, ACCURACY, AND EXPERTISE AS INSTRUCTION
TRUST_ACCURACY_EXPERTISE_INSTRUCTION = \
"""
**Evaluation Dimension:Trust, Accuracy, and Expertise in E-Vehicle Content**
Examine whether the article is well-researched, free from easily-verifiable factual errors, and based on reliable sources such as manufacturers, industry reports, or expert opinions on E-vehicles. The content should reflect sufficient expertise on the subject, whether from the author or credible industry figures. Verify that the article accurately discusses the latest developments in E-vehicles, including technological advancements, government regulations, and market dynamics. Ensure that the content doesn’t contain misleading or incorrect information that could damage its trustworthiness, especially when dealing with safety, battery technology, or environmental claims.
"""

# TRUST, ACCURACY, AND EXPERTISE AS A QUESTION ANSWERING
TRUST_ACCURACY_EXPERTISE_INSTRUCTION_QA = \
"""
**Evaluation Dimension: Trust, Accuracy, and Expertise**
Does the content reflect accurate, well-researched information, and is it free from easily-verifiable factual errors related to E-vehicle technology, safety features, or market trends?
Is the article created or reviewed by someone with sufficient expertise in the E-vehicle field, such as engineers, industry analysts, or experts with hands-on experience in the electric vehicle sector?
"""


# ~~~ QUALITY ASSESMENT SYSTEM PROMPT ~~~~
FILTERING_SYSTEM_PROMPT = \
"""
You're a content moderator for a popular online platform. You've been tasked with reviewing articles about electric vehicles to assess if they should be used to generate articles on you own platform. You will be provide with a Evaluation Dimension to Critique on. 
The Evaluation dimension and the instructions to follow will be provide in <EVALUATION DIMENSION> <\EVALUATION DIMENSION> tags and the article will be provided <ARTICLE> <\ARTICLE> tags. Within the <ARTICLE> tag there are can also the following tags <TITLE> <\TITLE>, <CONTENT> <\CONTENT> and <DESCRIPTION> <\DESCRIPTION> which will provide the title and content of the article respectively.
You will need to provide a critique of the article based on the Evaluation Dimension and provide a final assessment of whether the article meets the platform's standards on the Evaluation Dimension.
Once you've critiqued the article, provide a final assessment of whether the article meets the platform's standards on the Evaluation Dimension.
As output I would like you to provide the following in the format of a JSON:
{
    "critique": "Your critique here", # Your critique of the article with respect to the Evaluation Dimension
    "news_meets_standards": "Strongly Disagree/Disagree/Neutral/Agree/Strongly Agree" # You must chose only one of the options based on your critiqu 
}
Note that articles may be provided in various languages but keep your critique in English.
"""



### FULL PROMPT TEMPLATE ###
FILTERING_USER_PROMPT_TEMPLATE = \
"""
<EVALUATION DIMENSION> {{eval_dimension}} <\EVALUATION DIMENSION>
<ARTICLE>
<TITLE> {{title}} <\TITLE>
<DESCRIPTION> {{description}} <\DESCRIPTION>
<CONTENT> {{content}} <\CONTENT>
<\ARTICLE>
"""
#### DICTIONARY OF PROMPTS TO SIMPLIFY CALL ####
dimension_name_to_prompt = {
    "originality-value-purpose": ORIGINALITY_INSTRUCTION,
    "relevance-audiance-impact": RELEVANCE_INSTRUCTION,
    "up-to-date": UP_TO_DATE_INFORMATION_INSTRUCTION,
    "clarity-engagement-structure": CLARITY_ENGAGEMENT_STRUCTURE_INSTRUCTION,
    "quality-professionalism-transparency": QUALITY_PROFESSIONALISM_TRANSPARENCY_INSTRUCTION,
    "trust-accuracy-expertise": TRUST_ACCURACY_EXPERTISE_INSTRUCTION,
}
dimension_name_to_prompt_qa = {
    "originality-value-purpose": ORIGINALITY_INSTRUCTION_AS_QA,
    "relevance-audiance-impact": RELEVANCE_INSTRUCTION_AS_QA,
    "up-to-date": UP_TO_DATE_INFORMATION_INSTRUCTION_QA,
    "clarity-engagement-structure": CLARITY_ENGAGEMENT_STRUCTURE_INSTRUCTION_QA,
    "quality-professionalism-transparency": QUALITY_PROFESSIONALISM_TRANSPARENCY_INSTRUCTION_QA,
    "trust-accuracy-expertise": TRUST_ACCURACY_EXPERTISE_INSTRUCTION_QA,
}


#### FUNCTIONS TO GENERATE PROMPTS ####
async def get_feedback(news_dict: Dict[str,Any], eval_dimension_name: str, as_qa: bool = True) -> Dict:
    dict_of_interest = dimension_name_to_prompt_qa if as_qa else dimension_name_to_prompt
    
    dimension_prompt = dict_of_interest.get(eval_dimension_name.lower(), None)
    if dimension_prompt is None:
        raise ValueError(f"Invalid Evaluation Dimension Name: {eval_dimension_name}. Valid dimension names are: {list(dimension_name_to_prompt.keys())}")
    
    
    user_prompt = Template(FILTERING_USER_PROMPT_TEMPLATE).render(
        eval_dimension = dimension_prompt,
        title = news_dict.get("title", "Title Missing"),
        description = news_dict.get("description", "Description Missing"),
        content = news_dict.get("content", "Content Missing"),
        response_format = NewsRating,
    )
    
    
    completion_fn = get_completion_litellm_for_burda("gpt-4o")
    
    reply = await completion_fn(
        messages=[{"role": "system", "content": FILTERING_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        response_format=NewsRating,
    )
    
    return NewsRating(**json.loads(reply.choices[0].message.content))


if __name__ == "__main__":
    
    bbc_article_title = "EV targets 'will not be weakened' despite pressure"
    bbc_article_content = """
Rules on the percentage of electric vehicles (EVs) car firms must sell will not be weakened, the transport secretary has said, despite growing pressure from the industry.

The mandate will become tougher next year ahead of a complete ban on new diesel and petrol cars in 2035, but car makers have suggested the rules could threaten jobs.

Several senior government ministers and car makers with factories in the UK will hold crunch talks this week about the EV mandate and the slump in car demand.

Louise Haigh said she will look at "flexibilities", but insisted that "the mandate will not be weakened".

"There has been a downturn in demand on a global level so we are absolutely in listening mode - we want to discuss how the current situation is affecting them, but we are not diluting our ambition," the transport secretary told LBC Radio on Sunday.

"I’m meeting with Nissan tomorrow and the business secretary, the energy minister and I are meeting with a number of automotive manufacturers later in the week in order to discuss the challenges that they face on a global scale."

**Industry 'will likely miss' target**
According to the mandate, EVs must make up 22% of a firm's car sales and 10% of their van sales this year. For every car sale that pushes it outside of that mandate, they must pay a £15,000 fine.

There are some existing workarounds in the rules allowing firms to avoid the fines. They can, for example, buy credits from companies which have EV sales above 22% of their total sales.

"There are flexibilities available to them in the current mandate," Haigh told LBC.

"We want to make sure that the flexibilities are appropriate for them... but we absolutely don’t water down our ambition."

The rules get tougher every year ahead of a complete ban of new petrol and diesel car sales by 2035, though Labour said in its manifesto it would bring this forward to 2030 - reinstating the old target - as part of its wider commitments to climate change policy.

The trade association, Society of Motor Manufacturers and Traders (SMMT), has said the industry "will likely miss" this year's targets - calculating that around 18% of UK car sales are currently EVs.

SMMT and car makers say they support the government's long-term aims, but they are looking for some concessions in this week's talks.

One suggestion is that the penalties car makers have to pay for missing the targets should be reduced, the BBC understands.

Meanwhile, the SMMT is calling for government grants for buyers of EVs and tax changes.

It says changes are needed to deal with the plummet in demand, with its data showing that new car registrations in the UK remain a fifth lower than pre-Covid.

A Nissan spokesperson told the BBC it is “committed to playing a full role in the transition to net zero in the UK", but said "changes are required now to reflect the reality of the market, as we continue to work together to encourage more drivers to make the switch”.

A spokesperson for Stellantis - which owns Citroën, Peugeot, Vauxhall and several other car brands - said it is aligned with the objectives of the mandate.

But it added: "To remain efficient in the UK, we are strategically reviewing our operations working with our union partners as previously announced."

In April, Stellantis chief executive Carlos Tavares told The Telegraph newspaper the rules were "terrible" and that it could force the car maker to reduce its presence in the UK.

The Unite union has urged the company to commit to its future at its Luton and Ellesmere Port factories to address the "fear and rumour" it has created through announcing the strategic review.

Unite added it is "already having constructive discussions with government and industry to reform the EV mandate to protect jobs".
    """
    
    unrelated_article_title = "Luxury cars crash in snow chaos - two injured"
    unrelated_article_description = "Two luxury cars collided in a snowstorm in Hugelshofen TG on Thursday. Two people were injured."
    unrelated_article_content = """
On Monday evening, there was a collision between a Bentley and a Mercedes in Hugelshofen TG during a snowstorm. This was confirmed by the Thurgau cantonal police to the BRK News news agency.

According to media spokesman Matthias Graf, two people sustained minor to moderate injuries and had to be taken to hospital. Graf was not yet able to provide details of the exact property damage, but estimates it at several tens of thousands of francs.
    """
    
    
    news_dict = {
        "title": bbc_article_title,
        "content": bbc_article_content,
    }
    
    print("#"*50)
    print("Relavant Article Results:")
    
    feedback = get_feedback(news_dict, "originality", as_qa=True)
    print("+"*50)
    print("Originality:")
    print("critique:")
    print(feedback.critique)
    print("news_meets_standards:", feedback.news_meets_standards)
    print("+"*50)
    
    feedback = get_feedback(news_dict, "relevance", as_qa=True)
    print("Relevance:")
    print("+"*50)
    print("critique:")
    print(feedback.critique)
    print("news_meets_standards:", feedback.news_meets_standards)
    print("+"*50)
    
    feedback = get_feedback(news_dict, "up2date", as_qa=True)
    print("Up to Date:")
    print("+"*50)
    print("critique:")
    print(feedback.critique)
    print("news_meets_standards:", feedback.news_meets_standards)
    print("+"*50)
    print("#"*50)
    
    print("Unrelavant Article Results:")
    
    news_dict = {
        "title": unrelated_article_title,
        "content": unrelated_article_content,
        "description": unrelated_article_description
    }
    
    feedback = get_feedback(news_dict, "originality", as_qa=True)
    print("Originality:")
    print("+"*50)
    print("critique:")
    print(feedback.critique)
    print("news_meets_standards:", feedback.news_meets_standards)
    print("+"*50) 
    
    feedback = get_feedback(news_dict, "relevance", as_qa=True)
    print("Relevance:")
    print("+"*50)
    print("critique:")
    print(feedback.critique)
    print("news_meets_standards:", feedback.news_meets_standards)
    print("+"*50)
    
    feedback = get_feedback(news_dict, "up2date", as_qa=True)
    print("Up to Date:")
    print("+"*50)
    print("critique:")
    print(feedback.critique)
    print("news_meets_standards:", feedback.news_meets_standards)
    print("+"*50)
    
    print("#"*50)