# app/services/s3_service.py

import logging
import boto3
from botocore.exceptions import ClientError
from src.app.core.config import settings
from src.app.core.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def generate_presigned_put_url(
        self, object_key: str, content_type: str, expiration: int = 3600
    ) -> str:
        """
        Generates a presigned URL for uploading a file to S3/MinIO.
        Now includes a required Content-Type for security.
        """
        self._ensure_bucket_exists()

        try:
            response = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_key,
                    "ContentType": content_type,  # <-- THE ADDED PARAMETER
                },
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            logger.error(
                f"Failed to generate presigned URL for key {object_key}: {e}",
                exc_info=True,
            )
            raise ServiceUnavailable(
                service="File Storage", detail="Could not generate upload URL."
            ) from e

    def _ensure_bucket_exists(self) -> None:
        """
        Ensures the S3 bucket exists, creating it if necessary.
        This is a convenience for local development.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.info(f"Bucket '{self.bucket_name}' not found. Creating it...")
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Successfully created S3 bucket: {self.bucket_name}")
            else:
                # For other errors (e.g., credentials), re-raise as a service error
                logger.error(
                    f"Failed to check for bucket {self.bucket_name}: {e}", exc_info=True
                )
                raise ServiceUnavailable(
                    service="File Storage", detail="Could not connect to file storage."
                ) from e


# Singleton instance for dependency injection
s3_service = S3Service()
