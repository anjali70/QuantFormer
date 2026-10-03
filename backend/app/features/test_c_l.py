from crash_labels import create_crash_labels


data = [
    {"timestamp": "2026-10-03 10:00:00", "mid_price": 100},
    {"timestamp": "2026-10-03 10:01:00", "mid_price": 101},
    {"timestamp": "2026-10-03 10:02:00", "mid_price": 100},
    {"timestamp": "2026-10-03 10:03:00", "mid_price": 99},
    {"timestamp": "2026-10-03 10:04:00", "mid_price": 98},
    {"timestamp": "2026-10-03 10:05:00", "mid_price": 97},
]


result = create_crash_labels(data)

print(result[["timestamp", "mid_price", "future_price", "crash_label"]])