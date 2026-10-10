import asyncio
import json
import logging
import threading

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer

from app.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    ORDERBOOK_TOPIC,
    NEWS_TOPIC,
    RISK_THRESHOLD,
    MODEL_PATH,
)
from app.websocket_manager import manager
from app.risk.risk_engine import RiskEngine


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantformer")

risk_engine = RiskEngine(RISK_THRESHOLD)
stop_event = threading.Event()

latest_news = {
    "headline": "Waiting for news...",
    "sentiment_score": 0.0,
}

latest_market = None


def broadcast_from_thread(event):
    loop = getattr(app.state, "loop", None)

    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(
            manager.broadcast(event),
            loop,
        )


def consume_topic(topic, callback):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda value: json.loads(
                value.decode("utf-8")
            ),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id=f"quantformer-{topic}-consumer",
        )
    except Exception:
        logger.exception("Could not start Kafka consumer: %s", topic)
        return

    try:
        while not stop_event.is_set():
            records = consumer.poll(timeout_ms=500)

            for messages in records.values():
                for message in messages:
                    callback(message.value)

    except Exception:
        logger.exception("Kafka consumer failed: %s", topic)

    finally:
        consumer.close()


def process_news(event):
    global latest_news

    try:
        from app.nlp.finbert import FinBERT

        if not hasattr(process_news, "analyzer"):
            logger.info("Loading FinBERT model...")
            process_news.analyzer = FinBERT()

        result = process_news.analyzer.analyze(
            event.get("headline", "")
        )

        latest_news = {
            "type": "news_update",
            "headline": event.get("headline", ""),
            "timestamp": event.get("timestamp"),
            "sentiment_score": result["sentiment_score"],
            "positive": result["positive"],
            "negative": result["negative"],
            "neutral": result["neutral"],
            "embedding_size": len(result["embedding"]),
        }

        broadcast_from_thread(latest_news)

        logger.info(
            "FinBERT score %.3f: %s",
            result["sentiment_score"],
            event.get("headline", ""),
        )

    except Exception:
        logger.exception("News sentiment processing failed")


def process_market(event):
    global latest_market

    sentiment_score = latest_news.get("sentiment_score", 0.0)
    prediction_source = "demo_fallback"

    try:
        from pathlib import Path

        if Path(MODEL_PATH).exists():
            from app.models.predict import CrashPredictor

            if not hasattr(process_market, "predictor"):
                process_market.predictor = CrashPredictor()

            features = [
                float(event.get("mid_price", 0)),
                float(event.get("bid_volume", 0)),
                float(event.get("ask_volume", 0)),
                float(event.get("imbalance", 0)),
                float(event.get("spread", 0)),
            ]

            probability = process_market.predictor.predict(
                features, sentiment_score
            )
            prediction_source = "trained_demo_model"

        else:
            # Transparent fallback for a dashboard demo.
            probability = max(
                0.0,
                min(1.0, 0.5 - 0.25 * sentiment_score),
            )

    except Exception:
        logger.exception("Prediction failed; using demo fallback")
        probability = max(
            0.0,
            min(1.0, 0.5 - 0.25 * sentiment_score),
        )

    decision = risk_engine.check_risk(probability)

    event.update({
        "sentiment_score": sentiment_score,
        "headline": latest_news.get("headline"),
        "crash_probability": probability,
        "prediction_source": prediction_source,
        "risk_status": decision["status"],
        "risk_message": decision["message"],
    })

    latest_market = event
    broadcast_from_thread(event)


@asynccontextmanager
async def lifespan(application):
    application.state.loop = asyncio.get_running_loop()
    stop_event.clear()

    threads = [
        threading.Thread(
            target=consume_topic,
            args=(ORDERBOOK_TOPIC, process_market),
            daemon=True,
        ),
        threading.Thread(
            target=consume_topic,
            args=(NEWS_TOPIC, process_news),
            daemon=True,
        ),
    ]

    for thread in threads:
        thread.start()

    yield

    stop_event.set()

    for thread in threads:
        thread.join(timeout=2)


app = FastAPI(
    title="QuantFormer API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "QuantFormer",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "kafka": KAFKA_BOOTSTRAP_SERVERS,
    }


@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        if latest_market:
            await websocket.send_json(latest_market)

        while True:
            await asyncio.sleep(30)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception:
        manager.disconnect(websocket)