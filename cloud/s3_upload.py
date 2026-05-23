import os
import uuid
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError


@dataclass
class S3UploadResult:
    bucket: Optional[str]
    object_key: Optional[str]
    file_url: Optional[str]
    storage_enabled: bool


class S3Uploader:
    def __init__(self) -> None:
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.enabled = bool(self.bucket_name)
        self.client = None

        if self.enabled:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )

    def upload_bytes(self, file_bytes: bytes, filename: str, content_type: str) -> S3UploadResult:
        if not self.enabled or not self.client or not self.bucket_name:
            return S3UploadResult(
                bucket=None,
                object_key=None,
                file_url=None,
                storage_enabled=False,
            )

        extension = filename.rsplit(".", 1)[-1].lower()
        object_key = f"resumes/{uuid.uuid4().hex}.{extension}"

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to upload resume to S3: {exc}") from exc

        file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_key}"
        return S3UploadResult(
            bucket=self.bucket_name,
            object_key=object_key,
            file_url=file_url,
            storage_enabled=True,
        )
