import logging
import threading
from contextlib import asynccontextmanager

from app.consumer import start_consumer
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


def start_consumer_thread():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
    logger.info("Kafka consumer thread started")


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_consumer_thread()
    yield
    logger.info("Shutting down Processing Service")


app = FastAPI(
    title="FinFlow Processing Service",
    description="Kafka consumer and payment processing service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "processing-service"}


@app.get("/")
async def root():
    return {"message": "FinFlow Processing Service running"}
