import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

from app.config import KAFKA_BOOTSTRAP_SERVERS, NEWS_TOPIC


HEADLINES = [
    "Company reports stronger quarterly earnings and higher revenue",
    "Market falls after central bank signals higher interest rates",
    "Technology company announces a major new product",
    "Company warns that future revenue may decline",
    "Investors remain cautious ahead of inflation report",
    "Firm reports better than expected cash flow",
]


def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    print(f"Publishing financial news to {NEWS_TOPIC}")

    try:
        while True:
            event = {
                "type": "news",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "headline": random.choice(HEADLINES),
            }

            producer.send(NEWS_TOPIC, event)
            producer.flush()

            print("News headline:", event["headline"])
            time.sleep(3)

    except KeyboardInterrupt:
        print("News producer stopped.")

    finally:
        producer.close()


if __name__ == "__main__":
    main()