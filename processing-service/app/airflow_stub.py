import asyncio
import logging

logger = logging.getLogger(__name__)


async def trigger_dag(transaction_id: str) -> dict:
    """
    Stub for Airflow DAG trigger.
    In production this would call:
    POST http://airflow:8080/api/v1/dags/{dag_id}/dagRuns
    """
    logger.info(f"Triggering Airflow DAG for transaction: {transaction_id}")

    # Simulate processing delay
    await asyncio.sleep(1)

    # Mock successful response
    return {
        "dag_run_id": f"finflow_{transaction_id}",
        "state": "success",
        "transaction_id": transaction_id,
    }


async def get_dag_status(dag_run_id: str) -> str:
    """
    Stub for polling DAG run status.
    In production this would call:
    GET http://airflow:8080/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}
    """
    logger.info(f"Checking DAG status for: {dag_run_id}")

    # Simulate polling delay
    await asyncio.sleep(0.5)

    # Always return success for stub
    return "success"
