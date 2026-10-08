from predict import CrashPredictor


predictor = CrashPredictor()


market_data = [
    100.5,   # mid price
    100.7,   # spread-related price
    1200,    # bid volume
    800,     # ask volume
    0.20     # order book imbalance
]

sentiment_score = -0.6


probability = predictor.predict(
    market_data,
    sentiment_score
)


print("Market Data:", market_data)
print("Sentiment Score:", sentiment_score)
print(
    "Crash Probability:",
    round(probability * 100, 2),
    "%"
)