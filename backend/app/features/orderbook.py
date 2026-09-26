import numpy as np


def calculate_order_book_features(order_book):

    bids = order_book["bids"]
    asks = order_book["asks"]

    bid_volume = sum(
        level["volume"]
        for level in bids
    )

    ask_volume = sum(
        level["volume"]
        for level in asks
    )

    total_volume = bid_volume + ask_volume

    imbalance = (
        (bid_volume - ask_volume) / total_volume
        if total_volume > 0
        else 0
    )

    best_bid = bids[0]["price"]
    best_ask = asks[0]["price"]

    spread = best_ask - best_bid

    return {
        "mid_price": order_book["mid_price"],
        "bid_volume": bid_volume,
        "ask_volume": ask_volume,
        "order_book_imbalance": imbalance,
        "spread": spread
    }