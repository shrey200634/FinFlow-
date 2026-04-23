import json
import logging

from decouple import config
from kafka import KafkaProducer

logger = logging.getLogger(__name__)

KAFKA_BROKER = config("KAFKA_BROKER", default="localhost:9092")


def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def publish_event(topic: str, payload: dict):
    try:
        producer = get_producer()
        producer.send(topic, payload)
        producer.flush()
        logger.info(f"Published event to {topic}: {payload}")
    except Exception as e:
        logger.error(f"Failed to publish event to {topic}: {e}")


def publish_transaction_created(transaction):
    publish_event(
        "transaction.created",
        {
            "transaction_id": str(transaction.id),
            "account_id": str(transaction.account.id),
            "amount": str(transaction.amount),
            "transaction_type": transaction.transaction_type,
            "status": transaction.status,
        },
    )


def publish_transaction_updated(transaction):
    publish_event(
        "transaction.updated",
        {
            "transaction_id": str(transaction.id),
            "account_id": str(transaction.account.id),
            "status": transaction.status,
        },
    )
