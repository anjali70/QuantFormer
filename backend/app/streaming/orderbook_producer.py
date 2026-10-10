import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

from app.config import KAFKA_BOOTSTRAP_SERVERS, ORDERBOOK_TOPIC


def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    price = 100.50
    print(f"Publishing market data to {ORDERBOOK_TOPIC}")

    try:
        while True:
            price += random.uniform(-0.08, 0.08)

            bids = [
                {
                    "price": round(price - 0.10 * (i + 1), 2),
                    "volume": random.randint(400, 1800),
                }
                for i in range(5)
            ]

            asks = [
                {
                    "price": round(price + 0.10 * (i + 1), 2),
                    "volume": random.randint(400, 1800),
                }
                for i in range(5)
            ]

            bid_volume = sum(level["volume"] for level in bids)
            ask_volume = sum(level["volume"] for level in asks)

            event = {
                "type": "market_update",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mid_price": round(price, 2),
                "bids": bids,
                "asks": asks,
                "bid_volume": bid_volume,
                "ask_volume": ask_volume,
                "imbalance": (
                    (bid_volume - ask_volume)
                    / (bid_volume + ask_volume)
                ),
                "spread": round(asks[0]["price"] - bids[0]["price"], 4),
            }

            producer.send(ORDERBOOK_TOPIC, event)
            producer.flush()

            print("Market mid-price:", event["mid_price"])
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Market producer stopped.")

    finally:
        producer.close()


if __name__ == "__main__":
    main()