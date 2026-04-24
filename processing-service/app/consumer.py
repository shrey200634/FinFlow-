import asyncio
import json
import logging

import httpx
from app.airflow_stub import get_dag_status, trigger_dag
from app.config import (
    ACCOUNT_SERVICE_URL,
    HMAC_SECRET,
    KAFKA_BROKER,
    KAFKA_GROUP_ID,
    KAFKA_TOPIC_CREATED,
)
from app.hmac_auth import generate_headers
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)


async def process_transaction(transaction_id: str, account_id: str):
    logger.info(f"Processing transaction: {transaction_id}")

    # Step 1 — trigger Airflow stub
    dag_result = await trigger_dag(transaction_id)
    dag_run_id = dag_result.get("dag_run_id")

    # Step 2 — poll for status
    status = await get_dag_status(dag_run_id)

    # Step 3 — map DAG status to transaction status
    transaction_status = "COMPLETED" if status == "success" else "FAILED"

    # Step 4 — call Account Service to update transaction
    await update_transaction_status(transaction_id, transaction_status)


async def update_transaction_status(transaction_id: str, status: str):
    url = f"{ACCOUNT_SERVICE_URL}/api/internal/transactions/{transaction_id}/"
    body = json.dumps({"status": status})
    headers = generate_headers(HMAC_SECRET, body)
    headers["Content-Type"] = "application/json"

    try:
        async with httpx.AsyncClient() as client:
            res = await client.patch(url, content=body, headers=headers)
            if res.status_code == 200:
                logger.info(f"Transaction {transaction_id} updated to {status}")
            else:
                logger.error(
                    f"Failed to update transaction {transaction_id}: {res.status_code}"
                )
    except Exception as e:
        logger.error(f"Error calling Account Service: {e}")


def start_consumer():
    logger.info("Starting Kafka consumer...")
    consumer = KafkaConsumer(
        KAFKA_TOPIC_CREATED,
        bootstrap_servers=KAFKA_BROKER,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    logger.info(f"Listening on topic: {KAFKA_TOPIC_CREATED}")

    for message in consumer:
        try:
            data = message.value
            logger.info(f"Received event: {data}")
            transaction_id = data.get("transaction_id")
            account_id = data.get("account_id")

            if not transaction_id:
                logger.warning("Received event with no transaction_id, skipping")
                continue

            asyncio.run(process_transaction(transaction_id, account_id))

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            continue
