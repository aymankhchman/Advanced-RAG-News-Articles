import sys
import os
import logging
from newsapi import NewsApiClient
import pandas as pd
import numpy as np 
import yaml
from datetime import datetime


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def extract_data(api_key: str, keyword: str="AAPL", sort_by: str="publishedAt",
                page: int=5):
    
    newsapi = NewsApiClient(api_key=api_key)

    articles = newsapi.get_everything(q=keyword, language="en",
                                    sort_by=sort_by, page=page)



    logger.info(f"article length: {len(articles['articles'])}")

    df = pd.DataFrame(articles["articles"])\
        .drop("source", axis=1)\
        .sort_values(by="publishedAt", ascending=False)\
        .drop_duplicates()
    df["content"] = df["content"].apply(lambda x: np.nan if len(x) < 20 else x)
    df.dropna(axis=0, inplace=True)


    logger.info("saving the data")
    df.to_csv(f"./data/{keyword}_{datetime.now()}.csv", index=False)


if __name__ == "__main__":

    with open("./config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    extract_data(api_key=config["newsapi_key"], keyword=config["keyword"])