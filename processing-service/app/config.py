from decouple import config

KAFKA_BROKER = config("KAFKA_BROKER", default="localhost:9092")
KAFKA_TOPIC_CREATED = config("KAFKA_TOPIC_CREATED", default="transaction.created")
KAFKA_TOPIC_UPDATED = config("KAFKA_TOPIC_UPDATED", default="transaction.updated")
KAFKA_GROUP_ID = config("KAFKA_GROUP_ID", default="processing-service")

ACCOUNT_SERVICE_URL = config("ACCOUNT_SERVICE_URL", default="http://localhost:8000")
HMAC_SECRET = config("HMAC_SECRET", default="dev-hmac-secret-change-me")

AIRFLOW_ENABLED = config("AIRFLOW_ENABLED", default=False, cast=bool)
