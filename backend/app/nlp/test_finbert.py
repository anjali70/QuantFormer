from finbert import FinBERT


model = FinBERT()

headline = "Company reports strong quarterly earnings and higher revenue."

result = model.analyze(headline)

print("Headline:", headline)
print("Sentiment:", result["sentiment"])
print("Score:", result["score"])