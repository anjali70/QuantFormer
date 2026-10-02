from finbert import FinBERT


model = FinBERT()

headline = "Company reports strong quarterly earnings and higher revenue."

result = model.analyze(headline)

print("Headline:", result["text"])
print("Sentiment Score:", result["sentiment_score"])
print("Embedding Size:", len(result["embedding"]))