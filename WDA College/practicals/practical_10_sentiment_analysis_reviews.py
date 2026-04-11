"""
Practical No 10 — Sentiment analysis for customer reviews and visualization

Aim: Label reviews as Positive / Negative / Neutral with VADER, then plot
counts with matplotlib (seaborn optional).

Dependencies: pip install pandas matplotlib seaborn nltk
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import nltk
import pandas as pd
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer

PRACTICAL_NAME = "Practical 10 — Sentiment analysis & visualization"

reviews = [
    "The product is amazing and works perfectly!",
    "Very disappointed with the quality.",
    "Customer service was okay, not great.",
    "Absolutely fantastic experience, highly recommend!",
    "Worst purchase ever. Waste of money.",
    "The item is decent for the price.",
    "I am extremely happy with this product",
    "Not bad, but could be better",
    "Terrible delivery experience",
    "Excellent quality and fast shipping",
]


def main() -> None:
    print(PRACTICAL_NAME)
    nltk.download("vader_lexicon", quiet=True)

    sid = SentimentIntensityAnalyzer()

    def get_sentiment(review: str) -> str:
        score = sid.polarity_scores(review)["compound"]
        if score >= 0.05:
            return "Positive"
        if score <= -0.05:
            return "Negative"
        return "Neutral"

    df = pd.DataFrame({"Review": reviews})
    df["Sentiment"] = df["Review"].apply(get_sentiment)
    print(df)

    sentiment_counts = df["Sentiment"].value_counts()

    plt.figure(figsize=(6, 4))
    # Avoid deprecated seaborn API: pass hue=x and legend=False
    sns.barplot(
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        hue=sentiment_counts.index,
        palette="viridis",
        legend=False,
    )
    plt.title("Sentiment Analysis of Customer Reviews")
    plt.xlabel("Sentiment")
    plt.ylabel("Number of Reviews")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
