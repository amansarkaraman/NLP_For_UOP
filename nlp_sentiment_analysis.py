import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER lexicon once
nltk.download("vader_lexicon")

# Read your Excel file
# Change the file name if your file has a different name
df = pd.read_excel("amazon_reviews.xlsx")

# Check the first few rows
print("First 5 rows of data:")
print(df.head())

# Create sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Function to calculate sentiment score
def get_sentiment_score(text):
    if pd.isna(text):
        return 0
    return sia.polarity_scores(str(text))["compound"]

# Function to label sentiment
def get_sentiment_label(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# Apply sentiment analysis
df["sentiment_score"] = df["review_text"].apply(get_sentiment_score)
df["sentiment_label"] = df["sentiment_score"].apply(get_sentiment_label)

# Save results to a new Excel file
output_file = "amazon_reviews_with_sentiment.xlsx"
df.to_excel(output_file, index=False)

print("\nDone.")
print(f"Sentiment analysis completed and saved to: {output_file}")
print(df[["review_text", "sentiment_score", "sentiment_label"]].head(10))