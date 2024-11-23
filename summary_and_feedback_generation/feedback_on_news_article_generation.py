import sys
sys.path.append("./")
from summary_and_feedback_generation.evaluation_dimensions import (
    get_feedback,
    dimension_name_to_prompt,
    verbal_feedback_to_score,
)
from summary_and_feedback_generation.summary_generation import generate_summary
import os
import pandas as pd
import asyncio
from tqdm import tqdm



async def fill_df_with_feedback_and_summary(path_to_df, save_folder, feedback_only_save_name, feedback_and_summary_save_name, override=False):
    df = pd.read_csv(path_to_df)
    dimension_names = list(dimension_name_to_prompt.keys())
    feedbacks = {dim_nam : [] for dim_nam in dimension_names}
    feedbacks_scores = {dim_nam : [] for dim_nam in dimension_names}
    
    if os.path.exists(os.path.join(save_folder, feedback_only_save_name)) and not override:
        df = pd.read_csv(os.path.join(save_folder, feedback_only_save_name))
    else:
        for i, row in tqdm(df.iterrows(), total=len(df), desc="Generating Feedback"):
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
            
        for column in dimension_names:
            df[f"score/{column}"] = df[f"news_meets_standards/{column}"].map(lambda x: verbal_feedback_to_score[x.lower()])
    
        df.to_csv(os.path.join(save_folder, feedback_only_save_name), index=False)
    
    if os.path.exists(os.path.join(save_folder, feedback_and_summary_save_name)) and not override:
        return
    else:
        above_up_to_date_threshold_df = df[df["score/up-to-date"] >= 0]
        summaries = []
        for i, row in tqdm(above_up_to_date_threshold_df.iterrows(), total=len(above_up_to_date_threshold_df), desc="Generating Summaries"):
            news_dict = {"content": row["content"], "title": row["title"], "description": row["description"]}
            summary = await generate_summary(news_dict)
            summaries.append(summary.summary)
            
        above_up_to_date_threshold_df["ev_summary"] = summaries

        above_up_to_date_threshold_df.to_csv(os.path.join(save_folder, feedback_and_summary_save_name), index=False)


if __name__ == "__main__":
    override = False
    path_to_df = "data/news_articles.csv"
    save_folder = "data"
    feedback_only_save_name = "news_articles_with_feedback.csv"
    feedback_and_summary_save_name = "relevant_news_articles_with_feedback_and_summary.csv"
    asyncio.run(fill_df_with_feedback_and_summary(path_to_df, save_folder, feedback_only_save_name, feedback_and_summary_save_name,override=override))
    
    