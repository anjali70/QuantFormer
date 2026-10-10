import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
)

ORDERBOOK_TOPIC = os.getenv("ORDERBOOK_TOPIC", "orderbook")
NEWS_TOPIC = os.getenv("NEWS_TOPIC", "news")

RISK_THRESHOLD = float(os.getenv("RISK_THRESHOLD", "0.80"))
MODEL_PATH = os.getenv("MODEL_PATH", "quantformer_model.pth")