import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


HEADLINES = [

    "Company reports stronger than expected quarterly earnings",

    "Company revenue falls below analyst expectations",

    "Major institutional investor increases position",

    "Regulators announce investigation into company operations",

    "Company announces major new strategic partnership",

    "Markets react to unexpected interest rate announcement",

    "Analysts downgrade company following weak guidance",

    "Company announces record quarterly revenue",

    "Unexpected supply disruption raises market concerns",

    "Company announces significant share buyback program",

]


def main():

    print("Starting financial news producer...")

    while True:

        headline = random.choice(HEADLINES)

        message = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "MockReuters",
            "headline": headline
        }

        producer.send(
            "news",
            message
        )

        producer.flush()

        print(message)

        time.sleep(random.uniform(2, 5))


if __name__ == "__main__":
    main()