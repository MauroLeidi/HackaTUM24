import sys
sys.path.append("./")
from news_collector.bingnews import get_bing_news
from news_collector.helpers import normalize_article
from news_collector.rss import get_rss_articles
import pandas as pd

def get_final_news_df(n_bing_news_per_market, use_litellm):
    
    markets = ["en-US", "en-GB", "de-DE", "fr-FR", "it-IT", "es-ES"]
    all_bing_news = []
    for market in markets:
        print("Getting news for market:", market)
        all_bing_news.append(pd.DataFrame(get_bing_news(n_bing_news_per_market, use_litellm, market)))
    all_bing_news = pd.concat(all_bing_news, ignore_index=True)
    rss_news = get_rss_articles()
    df = pd.concat([all_bing_news, pd.DataFrame(rss_news)], ignore_index=True)
    # Sort by date if needed
    df = df.sort_values('published_date', ascending=False).reset_index(drop=True)
    df.drop_duplicates(subset=["url"], inplace=True)
    df.to_csv("data/news_articles.csv", index=False)
    return df

if __name__ == "__main__":
    get_final_news_df(100, use_litellm=False)