import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer


SYMBOL = "QTF"
BASE_PRICE = 100.0


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


def generate_order_book():
    mid_price = BASE_PRICE + random.uniform(-1, 1)

    bids = []
    asks = []

    for level in range(1, 11):

        bid_price = round(mid_price - level * 0.01, 2)
        ask_price = round(mid_price + level * 0.01, 2)

        bid_volume = random.randint(100, 5000)
        ask_volume = random.randint(100, 5000)

        bids.append({
            "price": bid_price,
            "volume": bid_volume
        })

        asks.append({
            "price": ask_price,
            "volume": ask_volume
        })

    return {
        "symbol": SYMBOL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mid_price": round(mid_price, 2),
        "bids": bids,
        "asks": asks
    }


def main():

    print("Starting L2 Order Book producer...")

    while True:

        order_book = generate_order_book()

        producer.send(
            "orderbook",
            order_book
        )

        producer.flush()

        print(order_book)

        time.sleep(0.1)


if __name__ == "__main__":
    main()