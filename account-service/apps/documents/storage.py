import logging
from minio import Minio
from minio.error import S3Error
from decouple import config
from django.http import StreamingHttpResponse

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = config("MINIO_ENDPOINT", default="localhost:9000")
MINIO_ACCESS_KEY = config("MINIO_ACCESS_KEY", default="minioadmin")
MINIO_SECRET_KEY = config("MINIO_SECRET_KEY", default="minioadmin")
MINIO_SECURE = config("MINIO_SECURE", default=False, cast=bool)
BUCKET_NAME = config("MINIO_BUCKET", default="finflow-docs")


def get_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def ensure_bucket_exists(client, bucket: str):
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"Created bucket: {bucket}")
    except S3Error as e:
        logger.error(f"Failed to ensure bucket exists: {e}")
        raise


def upload_file(file_obj, object_key: str, content_type: str, file_size: int):
    try:
        client = get_client()
        ensure_bucket_exists(client, BUCKET_NAME)
        client.put_object(
            BUCKET_NAME,
            object_key,
            file_obj,
            length=file_size,
            content_type=content_type,
        )
        logger.info(f"Uploaded file: {object_key}")
        return BUCKET_NAME, object_key
    except S3Error as e:
        logger.error(f"Failed to upload file: {e}")
        raise


def download_file(bucket: str, object_key: str):
    try:
        client = get_client()
        response = client.get_object(bucket, object_key)
        return response
    except S3Error as e:
        logger.error(f"Failed to download file: {e}")
        raise