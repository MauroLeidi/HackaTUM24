import sys
sys.path.append("./")
from feedback_generation.evaluation_dimensions import get_feedback, dimension_name_to_prompt
import os
import pandas as pd
import asyncio
from tqdm import tqdm

async def fill_df_with_feedback(path_to_df, save_folder, save_name):
    df = pd.read_csv(path_to_df)
    dimension_names = list(dimension_name_to_prompt.keys())
    feedbacks = {dim_nam : [] for dim_nam in dimension_names}
    feedbacks_scores = {dim_nam : [] for dim_nam in dimension_names}
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        news_dict = {"content": row["content"], "title": row["title"], "description": row["description"]}
            
        tasks = [
            get_feedback(news_dict, dimension_name)
            for dimension_name in dimension_names
        ]

        # Gather all tasks to run them concurrently
        results = await asyncio.gather(*tasks)
        
        # Append the results to the feedback dictionary
        for dim_name, feedback in zip(dimension_names, results):
            feedbacks[dim_name].append(feedback.critique)
            feedbacks_scores[dim_name].append(feedback.news_meets_standards)
            
            
    for dim_name in dimension_names:
        df[f"critique/{dim_name}"] = feedbacks[dim_name]
        df[f"news_meets_standards/{dim_name}"] = feedbacks_scores[dim_name]
    
    df.to_csv(os.path.join(save_folder, save_name), index=False)
        
if __name__ == "__main__":
    path_to_df = "data/news_articles.csv"
    save_folder = "data"
    save_name = "news_articles_with_feedback.csv"
    asyncio.run(fill_df_with_feedback(path_to_df, save_folder, save_name))
    
    