
from .bingnews import get_bing_news
from .helpers import normalize_article
from .rss import get_rss_articles
import pandas as pd

def get_final_news_df():
    bing_news = get_bing_news()
    rss_news = get_rss_articles()
    df = pd.concat([pd.DataFrame(bing_news), pd.DataFrame(rss_news)], ignore_index=True)
    # Sort by date if needed
    df = df.sort_values('published_date', ascending=False).reset_index(drop=True)
    df.to_csv("data/news_articles.csv", index=False)
    return df