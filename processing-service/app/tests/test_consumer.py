from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.consumer import process_transaction, update_transaction_status


@pytest.mark.asyncio
async def test_process_transaction_completed():
    with patch("app.consumer.trigger_dag", new_callable=AsyncMock) as mock_dag, patch(
        "app.consumer.get_dag_status", new_callable=AsyncMock
    ) as mock_status, patch(
        "app.consumer.update_transaction_status", new_callable=AsyncMock
    ) as mock_update:

        mock_dag.return_value = {"dag_run_id": "finflow_123", "state": "success"}
        mock_status.return_value = "success"

        await process_transaction("tx-123", "acc-456")

        mock_dag.assert_called_once_with("tx-123")
        mock_update.assert_called_once_with("tx-123", "COMPLETED")


@pytest.mark.asyncio
async def test_process_transaction_failed():
    with patch("app.consumer.trigger_dag", new_callable=AsyncMock) as mock_dag, patch(
        "app.consumer.get_dag_status", new_callable=AsyncMock
    ) as mock_status, patch(
        "app.consumer.update_transaction_status", new_callable=AsyncMock
    ) as mock_update:

        mock_dag.return_value = {"dag_run_id": "finflow_123", "state": "failed"}
        mock_status.return_value = "failed"

        await process_transaction("tx-123", "acc-456")

        mock_update.assert_called_once_with("tx-123", "FAILED")


@pytest.mark.asyncio
async def test_update_transaction_status_success():
    with patch("app.consumer.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_instance = AsyncMock()
        mock_instance.patch.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        await update_transaction_status("tx-123", "COMPLETED")
        mock_instance.patch.assert_called_once()


@pytest.mark.asyncio
async def test_update_transaction_status_failure():
    with patch("app.consumer.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_instance = AsyncMock()
        mock_instance.patch.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        await update_transaction_status("tx-123", "COMPLETED")
        mock_instance.patch.assert_called_once()


@pytest.mark.asyncio
async def test_update_transaction_status_exception():
    with patch("app.consumer.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.patch.side_effect = Exception("Connection error")
        mock_client.return_value.__aenter__.return_value = mock_instance

        # should not raise — logs error and continues
        await update_transaction_status("tx-123", "COMPLETED")
