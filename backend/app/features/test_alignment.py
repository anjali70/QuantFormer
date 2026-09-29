from alignment import align_market_and_news


market_data = [
    {"timestamp": "2026-09-29 10:00:01", "mid_price": 100.2},
    {"timestamp": "2026-09-29 10:00:02", "mid_price": 100.4},
    {"timestamp": "2026-09-29 10:00:03", "mid_price": 100.3},
]

news_data = [
    {"timestamp": "2026-09-29 10:00:01", "sentiment_score": 0.7},
    {"timestamp": "2026-09-29 10:00:03", "sentiment_score": -0.2},
]

result = align_market_and_news(market_data, news_data)

print(result)